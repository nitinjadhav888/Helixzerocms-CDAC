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

MODELS_DIR = Path(__file__).parent.parent / "models"
CB_PARAMS = dict(iterations=1000, depth=10, learning_rate=0.05,
                  l2_leaf_reg=5, loss_function="RMSE",
                  random_seed=42, verbose=False, early_stopping_rounds=50)


def group_split(rows, val_stride=10, val_offset=4):
    keys = pd.Series([r.group_key for r in rows])
    eff = pd.Series([r.efficacy for r in rows])
    grp_mean = eff.groupby(keys).mean().sort_values(ascending=False)
    val_groups = set(grp_mean.index[val_offset::val_stride])
    is_val = keys.isin(val_groups).to_numpy()
    return [r for r, v in zip(rows, is_val) if not v], [r for r, v in zip(rows, is_val) if v]


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

    train_rows, val_rows = group_split(rows)
    print(f"  grouped split: train={len(train_rows):,} val={len(val_rows):,}")

    print("\nFeaturizing (this includes RNA-FM lookup + ViennaRNA)...")
    X_tr, y_tr = featurize(train_rows)
    X_va, y_va = featurize(val_rows)
    X_ex, y_ex_potency = featurize_external(external)
    print(f"  Train features: {X_tr.shape}, Val features: {X_va.shape}")

    print("\nTraining v3 CatBoost model...")
    m = CatBoostRegressor(**CB_PARAMS)
    m.fit(X_tr, y_tr, eval_set=(X_va, y_va))

    pred_va = m.predict(X_va)
    sp_va, _ = spearmanr(y_va, pred_va)
    mae_va = mean_absolute_error(y_va, pred_va)

    pred_ex = m.predict(X_ex)
    sp_ex, p_ex = spearmanr(pred_ex, y_ex_potency)

    print(f"\n=== RESULTS ===")
    print(f"In-distribution val   (N={len(val_rows)}):  Spearman={sp_va:.4f}  MAE={mae_va:.3f}")
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
            "rnafm_sense": features_v3.N_FM_PER_STRAND,
            "rnafm_antisense": features_v3.N_FM_PER_STRAND,
            "vienna_thermo": features_v3.N_VIENNA,
        },
        "cb_params": {k: v for k, v in CB_PARAMS.items() if k != "verbose"},
        "training_rows": len(train_rows),
        "source_breakdown": pd.Series([r.source for r in train_rows]).value_counts().to_dict(),
        "in_distribution_val": {"n": len(val_rows), "spearman": float(sp_va), "mae": float(mae_va)},
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
    }
    meta_path = MODELS_DIR / "model_b_v3_meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved metadata to {meta_path}")


if __name__ == "__main__":
    main()
