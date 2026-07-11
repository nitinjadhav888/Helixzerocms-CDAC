"""
robustness_check_tuned.py -- Sanity check for tune_model_b_v2.py's result
before trusting it: refit the SAME winning config (depth=10, lr=0.05, l2=5,
blend_w_legacy=0.40 -- see models/model_b_v2_tuned_meta.json) across multiple
DIFFERENT grouped-split offsets (val_offset=0..9, val_stride=10 fixed), not
just the single offset=4 split used for the original search and every prior
result in this project. If in-distribution and external-IC50 Spearman are
stable across offsets, the tuned result is a real effect, not this-particular-
split luck. If external Spearman swings wildly (e.g. some offsets
significant, others not, no consistent direction), that is the honest
answer too -- report it, don't cherry-pick the offset that looks best.
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
from catboost import CatBoostRegressor
from scipy.stats import spearmanr
from sklearn.metrics import mean_absolute_error

from smepred.scripts.data.patent_sources import load_all_real_sources
from smepred.scripts.train_model_b_v2 import group_split, featurize, featurize_external

MODELS_DIR = Path(__file__).parent.parent / "models"
WINNING_PARAMS = dict(iterations=1000, depth=10, learning_rate=0.05, l2_leaf_reg=5,
                       loss_function="RMSE", random_seed=42, verbose=False,
                       early_stopping_rounds=50)
BLEND_W_LEGACY = 0.40
OFFSETS = list(range(10))  # val_stride=10 -> exactly 10 disjoint offsets, full coverage


def main():
    print("Loading all real sources (once, reused across all offsets)...")
    rows, external = load_all_real_sources()
    print(f"  {len(rows):,} rows, {len(external)} external IC50 duplexes\n")

    results = []
    for offset in OFFSETS:
        train_rows, val_rows = group_split(rows, val_stride=10, val_offset=offset)
        X_tr_leg, X_tr_v2, y_tr = featurize(train_rows)
        X_va_leg, X_va_v2, y_va = featurize(val_rows)
        X_ex_leg, X_ex_v2, y_ex = featurize_external(external)

        m_legacy = CatBoostRegressor(**WINNING_PARAMS)
        m_legacy.fit(X_tr_leg, y_tr, eval_set=(X_va_leg, y_va))
        m_v2 = CatBoostRegressor(**WINNING_PARAMS)
        m_v2.fit(X_tr_v2, y_tr, eval_set=(X_va_v2, y_va))

        pred_va = BLEND_W_LEGACY * m_legacy.predict(X_va_leg) + (1 - BLEND_W_LEGACY) * m_v2.predict(X_va_v2)
        sp_va, _ = spearmanr(y_va, pred_va)
        mae_va = mean_absolute_error(y_va, pred_va)

        pred_ex = BLEND_W_LEGACY * m_legacy.predict(X_ex_leg) + (1 - BLEND_W_LEGACY) * m_v2.predict(X_ex_v2)
        sp_ex, p_ex = spearmanr(pred_ex, y_ex)

        row = dict(offset=offset, n_val=len(val_rows), spearman_val=float(sp_va), mae_val=float(mae_va),
                   spearman_external=float(sp_ex), p_external=float(p_ex))
        results.append(row)
        print(f"  offset={offset}: n_val={len(val_rows)} in-dist Spearman={sp_va:.4f} MAE={mae_va:.3f} | "
              f"external Spearman={sp_ex:.4f} p={p_ex:.4f}")

    sp_vals = [r["spearman_val"] for r in results]
    sp_exts = [r["spearman_external"] for r in results]
    p_exts = [r["p_external"] for r in results]
    n_significant = sum(1 for p in p_exts if p < 0.05)

    print(f"\n=== Summary across {len(OFFSETS)} offsets (val_stride=10, full coverage, no overlap) ===")
    print(f"  In-distribution Spearman: mean={np.mean(sp_vals):.4f} std={np.std(sp_vals):.4f} "
          f"min={min(sp_vals):.4f} max={max(sp_vals):.4f}")
    print(f"  External IC50 Spearman:   mean={np.mean(sp_exts):.4f} std={np.std(sp_exts):.4f} "
          f"min={min(sp_exts):.4f} max={max(sp_exts):.4f}")
    print(f"  External significant (p<0.05) at {n_significant}/{len(OFFSETS)} offsets")
    print(f"  (the offset=4 result reported in model_b_v2_tuned_meta.json was: "
          f"Spearman=0.3546 p=0.0465)")

    with open(MODELS_DIR.parent / "docs" / "validations" / "tuned_robustness_check.json", "w") as f:
        json.dump({
            "purpose": "Check whether tune_model_b_v2.py's external-IC50 significance (offset=4 only) "
                       "holds across other grouped-split offsets, or was this-split luck.",
            "winning_params": WINNING_PARAMS, "blend_w_legacy": BLEND_W_LEGACY,
            "per_offset_results": results,
            "summary": {
                "in_distribution_spearman_mean": float(np.mean(sp_vals)),
                "in_distribution_spearman_std": float(np.std(sp_vals)),
                "external_spearman_mean": float(np.mean(sp_exts)),
                "external_spearman_std": float(np.std(sp_exts)),
                "external_significant_count": n_significant,
                "external_significant_total": len(OFFSETS),
            },
        }, f, indent=2)
    print("\nSaved smepred/docs/validations/tuned_robustness_check.json")


if __name__ == "__main__":
    main()
