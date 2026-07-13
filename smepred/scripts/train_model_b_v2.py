"""
train_model_b_v2.py -- Production retrain of Model B v2 on the multi-slot
chemistry schema (src/chem_schema.py, src/features_v2.py), combining every
real (non-synthetic) source available: CMsiRNAdb + US10240152B2 (Alnylam) +
US11697812B2 (Dicerna). See scripts/data/patent_sources.py for per-source
notation handling and docs/validations/model_b_v2_multislot_ablation.md for
the literature grounding and controlled ablation this design is based on.

v2-only (no legacy blend): The legacy-schema CatBoost component has been
removed as of 2026-07-13. The blend weight sweep showed the legacy component
added ~0.004 Spearman (noise-level) while depending on the buggy single-char
encoding that can't represent independent PS+sugar at one position.

Validation: rows are grouped by antisense base sequence before splitting
(no duplex family straddles train/val -- fixes a confirmed leakage bug in
the previous split), and a disjoint set of 32 duplexes with a REAL measured
IC50 is held out end-to-end as a genuine external test.

Model: single CatBoost model using the v2 multi-slot feature extractor
(444-dim, literature-grounded). Hyperparameters: depth=10, lr=0.05, l2=5
(from the tuning sweep that previously chose the blend, now used natively).
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from scipy.stats import spearmanr
from sklearn.metrics import mean_absolute_error

from smepred.src import features_v2
from smepred.scripts.data.patent_sources import load_all_real_sources, parse_alnylam_compact

MODELS_DIR = Path(__file__).parent.parent / "models"
# Depth=10, lr=0.05, l2=5 from the tuning sweep that validated these as optimal
# for the v2 multi-slot schema (see model_b_v2_tuning_robustness.md).
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
    X_v2 = features_v2.batch_features_v2(sense_slots, anti_slots)
    y = np.array([r.efficacy for r in rows], dtype=np.float32)
    return X_v2, y


def featurize_external(df: pd.DataFrame):
    sense_slots = [parse_alnylam_compact(m) for m in df["sense_compact"]]
    anti_slots = [parse_alnylam_compact(m) for m in df["anti_compact"]]
    X_v2 = features_v2.batch_features_v2(sense_slots, anti_slots)
    y_potency = -np.log10(df["ic50_nM"].to_numpy() + 1e-10)
    return X_v2, y_potency


def main():
    print("Loading all real sources...")
    rows, external = load_all_real_sources()
    print(f"  {len(rows):,} training rows, {len(external)} external IC50 holdout duplexes")

    train_rows, val_rows = group_split(rows)
    print(f"  grouped split: train={len(train_rows):,} val={len(val_rows):,}")

    print("Featurizing...")
    X_tr_v2, y_tr = featurize(train_rows)
    X_va_v2, y_va = featurize(val_rows)
    X_ex_v2, y_ex_potency = featurize_external(external)

    print("Training v2 multi-slot CatBoost model (no legacy blend)...")
    m_v2 = CatBoostRegressor(**CB_PARAMS)
    m_v2.fit(X_tr_v2, y_tr, eval_set=(X_va_v2, y_va))

    pred_va = m_v2.predict(X_va_v2)
    sp_va, _ = spearmanr(y_va, pred_va)
    mae_va = mean_absolute_error(y_va, pred_va)

    pred_ex = m_v2.predict(X_ex_v2)
    sp_ex, p_ex = spearmanr(pred_ex, y_ex_potency)

    print(f"\nIn-distribution val   (N={len(val_rows)}):  Spearman={sp_va:.4f}  MAE={mae_va:.3f}")
    print(f"External IC50 holdout (N={len(external)}):  Spearman={sp_ex:.4f}  p={p_ex:.4f}")

    m_v2.save_model(str(MODELS_DIR / "model_b_v2_multislot.cbm"))

    meta = {
        "version": "model_b_v2_pure",
        "phase": "Multi-slot CatBoost (no legacy blend), depth=10/lr=0.05/l2=5",
        "date": pd.Timestamp.now().isoformat(),
        "architecture": "catboost_v2_multislot_only",
        "cb_params": {k: v for k, v in CB_PARAMS.items() if k != "verbose"},
        "training_rows": len(train_rows),
        "source_breakdown": pd.Series([r.source for r in train_rows]).value_counts().to_dict(),
        "in_distribution_val": {"n": len(val_rows), "spearman": float(sp_va), "mae": float(mae_va)},
        "external_ic50_holdout": {
            "n": len(external), "spearman": float(sp_ex), "p_value": float(p_ex),
            "note": "n=32 real Alnylam patent IC50s, never used in training; "
                    "not individually significant at this sample size -- directional only.",
        },
        "known_limitations": [
            "Table 13 (32/39 duplexes) excluded: antisense strand unrecoverable "
            "without re-fetching US10240152B2 source text.",
            "Candidate generation (modification_engine.py) still emits the legacy "
            "single-char alphabet; promote_legacy_string() bridges it for scoring "
            "but multi-slot candidate GENERATION is follow-up work.",
        ],
        "previous_config": {
            "version": "model_b_v2_tuned",
            "architecture": "blend(legacy_schema_catboost, v2_multislot_catboost)",
            "blend_weights": {"legacy": 0.4, "v2_multislot": 0.6},
            "reason_for_deprecation": "Legacy component added ~0.004 Spearman (noise) "
                "while depending on buggy single-char encoding. Pure v2 is cleaner "
                "and statistically equivalent.",
        },
    }
    with open(MODELS_DIR / "model_b_v2_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f"\nSaved model_b_v2_multislot.cbm + model_b_v2_meta.json to {MODELS_DIR}")


if __name__ == "__main__":
    main()
