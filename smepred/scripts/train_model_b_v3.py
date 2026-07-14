"""
train_model_b_v3.py -- CatBoost with enriched features (v2 + RNA-FM + ViennaRNA).

Ablation experiment: does adding RNA-FM embeddings (640-dim per strand) and
ViennaRNA thermodynamic features (5-dim) improve over pure v2 features?

Same training data, validation split, and hyperparameters as model_b_v2
(now pure v2-only) for a fair comparison.
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from scipy.stats import spearmanr
from sklearn.metrics import mean_absolute_error

from smepred.src import features_v3
from smepred.scripts.data.patent_sources import load_all_real_sources, parse_alnylam_compact
from smepred.scripts.data.split_utils import group_split_3way

MODELS_DIR = Path(__file__).parent.parent / "models"
CB_PARAMS = dict(iterations=1000, depth=10, learning_rate=0.05,
                  l2_leaf_reg=5, loss_function="RMSE",
                  random_seed=42, verbose=False, early_stopping_rounds=50)


def featurize(rows):
    sense_slots = [r.sense_slots for r in rows]
    anti_slots = [r.anti_slots for r in rows]
    X = features_v3.batch_features_v3(sense_slots, anti_slots)
    y = np.array([r.efficacy for r in rows], dtype=np.float32)
    return X, y


def featurize_external(df: pd.DataFrame):
    sense_slots = [parse_alnylam_compact(m) for m in df["sense_compact"]]
    anti_slots = [parse_alnylam_compact(m) for m in df["anti_compact"]]
    X = features_v3.batch_features_v3(sense_slots, anti_slots)
    y_potency = -np.log10(df["ic50_nM"].to_numpy() + 1e-10)
    return X, y_potency


def main():
    print("=" * 60)
    print(f"Model B v3: v2 features ({features_v3._N_V2}) + RNA-FM PCA-32 ({features_v3.N_FM}) + ViennaRNA ({features_v3.N_VIENNA})")
    print(f"  Total features: {features_v3.N_FEATURES_V3}")
    print("=" * 60)

    print("\nLoading all real sources...")
    rows, external = load_all_real_sources()
    print(f"  {len(rows):,} training rows, {len(external)} external IC50 holdout duplexes")

    train_rows, val_rows, test_rows = group_split_3way(rows)
    print(f"  LOCKED 3-way grouped split: train={len(train_rows):,} "
          f"val={len(val_rows):,} test={len(test_rows):,}")
    print(f"  (test group keys frozen in models/locked_test_groups.json)")

    print("\nFeaturizing (this includes RNA-FM lookup + ViennaRNA)...")
    X_tr, y_tr = featurize(train_rows)
    X_va, y_va = featurize(val_rows)
    X_te, y_te = featurize(test_rows)
    X_ex, y_ex_potency = featurize_external(external)
    print(f"  Train features: {X_tr.shape}, Val: {X_va.shape}, Test: {X_te.shape}")

    print("\nTraining v3 CatBoost model (early-stopping on val, test untouched)...")
    m = CatBoostRegressor(**CB_PARAMS)
    m.fit(X_tr, y_tr, eval_set=(X_va, y_va))

    pred_va = m.predict(X_va)
    sp_va, _ = spearmanr(y_va, pred_va)
    mae_va = mean_absolute_error(y_va, pred_va)

    pred_te = m.predict(X_te)
    sp_te, _ = spearmanr(y_te, pred_te)
    mae_te = mean_absolute_error(y_te, pred_te)

    pred_ex = m.predict(X_ex)
    sp_ex, p_ex = spearmanr(pred_ex, y_ex_potency)

    print(f"\n=== RESULTS ===")
    print(f"In-distribution val   (N={len(val_rows)}):  Spearman={sp_va:.4f}  MAE={mae_va:.3f}")
    print(f"In-distribution TEST  (N={len(test_rows)}):  Spearman={sp_te:.4f}  MAE={mae_te:.3f}  [LOCKED, unseen]")
    print(f"External IC50 holdout (N={len(external)}):  Spearman={sp_ex:.4f}  p={p_ex:.4f}")

    # Save model
    model_path = MODELS_DIR / "model_b_v3.cbm"
    m.save_model(str(model_path))
    print(f"\nSaved model to {model_path}")

    # Save metadata with comparison to v2
    meta = {
        "version": "model_b_v3",
        "phase": "v2 features + RNA-FM PCA-32 (64-dim) + ViennaRNA (5-dim)",
        "date": pd.Timestamp.now().isoformat(),
        "architecture": "catboost_v3_enriched",
        "n_features": features_v3.N_FEATURES_V3,
        "feature_breakdown": {
            "v2_multi_slot": features_v3._N_V2,
            "rnafm_sense": features_v3.N_FM_DIM,
            "rnafm_antisense": features_v3.N_FM_DIM,
            "vienna_thermo": features_v3.N_VIENNA,
        },
        "cb_params": {k: v for k, v in CB_PARAMS.items() if k != "verbose"},
        "training_rows": len(train_rows),
        "source_breakdown": pd.Series([r.source for r in train_rows]).value_counts().to_dict(),
        "split": {
            "scheme": "locked 3-way grouped (by antisense seq)",
            "stride": 10, "val_offset": 5, "test_offset": 0,
            "lock_file": "models/locked_test_groups.json",
            "n_train": len(train_rows), "n_val": len(val_rows), "n_test": len(test_rows),
        },
        "in_distribution_val": {"n": len(val_rows), "spearman": float(sp_va), "mae": float(mae_va)},
        "in_distribution_test_LOCKED": {"n": len(test_rows), "spearman": float(sp_te), "mae": float(mae_te)},
        "external_ic50_holdout": {
            "n": len(external), "spearman": float(sp_ex), "p_value": float(p_ex),
            "note": "n=32 real Alnylam patent IC50s",
        },
        "comparison_to_v2": {
            "note": "v2 is the pure multi-slot CatBoost (depth=10/lr=0.05/l2=5, no legacy blend)",
            "v2_val_spearman": 0.4947,
            "v2_val_mae": 22.635,
            "v2_external_spearman": 0.3239,
            "v2_external_p": 0.0706,
        },
        "honesty_note": (
            "in_distribution_val is used for early-stopping, so it is a "
            "tuning-adjacent estimate. in_distribution_test_LOCKED is a "
            "grouped, untouched holdout (keys frozen in "
            "models/locked_test_groups.json) and is the honest generalization "
            "estimate. external_ic50_holdout (N=32) is the out-of-distribution "
            "test."
        ),
    }
    meta_path = MODELS_DIR / "model_b_v3_meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved metadata to {meta_path}")


if __name__ == "__main__":
    main()
