"""
tune_model_b_v2.py -- Hyperparameter search for the model_b_v2 blend
(CatBoost legacy-schema + CatBoost v2-multislot-schema components).

train_model_b_v2.py intentionally used a single fixed CatBoost config
(depth=6, lr=0.05, default l2_leaf_reg) on both sides of its ablation, for a
fair controlled comparison -- see model_b_v2_multislot_ablation.md. This
script is the deliberate follow-up: search each component's hyperparameters
independently, then sweep the blend weight, using the SAME data source
(load_all_real_sources) and SAME leakage-free grouped split (group_split)
as training, for direct comparability against the existing baseline
(models/model_b_v2_meta.json: in-distribution Spearman 0.489 n=4269,
external IC50 Spearman 0.197 n=32 not significant).

Selection criterion: in-distribution validation Spearman ONLY. The external
IC50 holdout (n=32) is reported at the end for honesty, but is deliberately
NOT used to pick hyperparameters -- it is already not statistically
significant at n=32, so optimizing against it would be tuning to noise, not
signal. See ablation doc's external-IC50 section for why.

Saves tuned artifacts under distinct _tuned names -- does NOT overwrite the
existing model_b_v2_{legacy,multislot}.cbm / model_b_v2_meta.json production
integration checkpoint. Promotion to production names is a separate,
deliberate step after reviewing these results.
"""
from __future__ import annotations
import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from scipy.stats import spearmanr
from sklearn.metrics import mean_absolute_error

from smepred.scripts.data.patent_sources import load_all_real_sources
from smepred.scripts.train_model_b_v2 import group_split, featurize, featurize_external

MODELS_DIR = Path(__file__).parent.parent / "models"

# Search space -- reproducible fixed sample (seed=42), not a full grid, to keep
# runtime bounded (~20-40s/fit observed locally). 12 combos/component = 24 fits.
DEPTHS = [4, 6, 8, 10]
LEARNING_RATES = [0.02, 0.03, 0.05, 0.08, 0.1]
L2_LEAF_REGS = [1, 3, 5, 10]
N_SAMPLES_PER_COMPONENT = 12


def sample_configs(seed=42, n=N_SAMPLES_PER_COMPONENT):
    rng = random.Random(seed)
    grid = [(d, lr, l2) for d in DEPTHS for lr in LEARNING_RATES for l2 in L2_LEAF_REGS]
    # Always include the current production baseline config as a reference point.
    baseline = (6, 0.05, 3)
    sampled = rng.sample([c for c in grid if c != baseline], n - 1)
    return [baseline] + sampled


def search_component(name, X_tr, y_tr, X_va, y_va, configs):
    results = []
    best = None
    for depth, lr, l2 in configs:
        t0 = time.time()
        m = CatBoostRegressor(iterations=1000, depth=depth, learning_rate=lr,
                               l2_leaf_reg=l2, loss_function="RMSE", random_seed=42,
                               verbose=False, early_stopping_rounds=50)
        m.fit(X_tr, y_tr, eval_set=(X_va, y_va))
        pred = m.predict(X_va)
        sp, _ = spearmanr(y_va, pred)
        mae = mean_absolute_error(y_va, pred)
        dt = time.time() - t0
        row = dict(depth=depth, learning_rate=lr, l2_leaf_reg=l2,
                   best_iteration=m.get_best_iteration(), spearman=float(sp),
                   mae=float(mae), fit_seconds=round(dt, 1))
        results.append(row)
        print(f"  [{name}] depth={depth} lr={lr} l2={l2} -> "
              f"Spearman={sp:.4f} MAE={mae:.3f} ({dt:.0f}s, best_iter={m.get_best_iteration()})")
        if best is None or sp > best[1]:
            best = (m, sp, row)
    return best, results


def sweep_blend_weight(pred_legacy, pred_v2, y_va):
    best_w, best_sp = None, -2.0
    rows = []
    for w in np.arange(0.0, 1.01, 0.05):
        pred = w * pred_legacy + (1 - w) * pred_v2
        sp, _ = spearmanr(y_va, pred)
        rows.append((round(float(w), 2), float(sp)))
        if sp > best_sp:
            best_sp, best_w = sp, round(float(w), 2)
    return best_w, best_sp, rows


def main():
    print("Loading all real sources...")
    rows, external = load_all_real_sources()
    print(f"  {len(rows):,} training rows, {len(external)} external IC50 holdout duplexes")

    train_rows, val_rows = group_split(rows)
    print(f"  grouped split: train={len(train_rows):,} val={len(val_rows):,}")

    print("Featurizing...")
    X_tr_leg, X_tr_v2, y_tr = featurize(train_rows)
    X_va_leg, X_va_v2, y_va = featurize(val_rows)
    X_ex_leg, X_ex_v2, y_ex_potency = featurize_external(external)

    configs = sample_configs()
    print(f"\nSearching {len(configs)} configs per component "
          f"(baseline depth=6/lr=0.05/l2=3 included as config #1)...")

    print("\n-- legacy-schema component --")
    (best_m_legacy, best_sp_legacy, best_row_legacy), results_legacy = search_component(
        "legacy", X_tr_leg, y_tr, X_va_leg, y_va, configs)

    print("\n-- v2-multislot-schema component --")
    (best_m_v2, best_sp_v2, best_row_v2), results_v2 = search_component(
        "v2", X_tr_v2, y_tr, X_va_v2, y_va, configs)

    print(f"\nBest legacy config: {best_row_legacy}")
    print(f"Best v2 config:      {best_row_v2}")

    pred_va_legacy = best_m_legacy.predict(X_va_leg)
    pred_va_v2 = best_m_v2.predict(X_va_v2)
    best_w, best_sp_blend, blend_sweep = sweep_blend_weight(pred_va_legacy, pred_va_v2, y_va)
    pred_va_blend = best_w * pred_va_legacy + (1 - best_w) * pred_va_v2
    mae_blend = mean_absolute_error(y_va, pred_va_blend)
    print(f"\nBest blend weight (legacy): {best_w} -> in-distribution Spearman={best_sp_blend:.4f} MAE={mae_blend:.3f}")

    pred_ex_legacy = best_m_legacy.predict(X_ex_leg)
    pred_ex_v2 = best_m_v2.predict(X_ex_v2)
    pred_ex_blend = best_w * pred_ex_legacy + (1 - best_w) * pred_ex_v2
    sp_ex, p_ex = spearmanr(pred_ex_blend, y_ex_potency)
    print(f"External IC50 holdout (N={len(external)}, reported only, NOT used for selection): "
          f"Spearman={sp_ex:.4f} p={p_ex:.4f}")

    baseline_meta_path = MODELS_DIR / "model_b_v2_meta.json"
    baseline = json.loads(baseline_meta_path.read_text()) if baseline_meta_path.exists() else None

    print("\n=== Comparison: baseline (untuned, fixed config) vs tuned ===")
    if baseline:
        b_id, b_ex = baseline["in_distribution_val"], baseline["external_ic50_holdout"]
        print(f"  Baseline: in-dist Spearman={b_id['spearman']:.4f} MAE={b_id['mae']:.3f} | "
              f"external Spearman={b_ex['spearman']:.4f} p={b_ex['p_value']:.4f}")
    print(f"  Tuned:    in-dist Spearman={best_sp_blend:.4f} MAE={mae_blend:.3f} | "
          f"external Spearman={sp_ex:.4f} p={p_ex:.4f}")

    best_m_legacy.save_model(str(MODELS_DIR / "model_b_v2_legacy_tuned.cbm"))
    best_m_v2.save_model(str(MODELS_DIR / "model_b_v2_multislot_tuned.cbm"))

    meta = {
        "version": "model_b_v2_tuned",
        "phase": "Hyperparameter-tuned multi-slot chemistry schema blend",
        "date": pd.Timestamp.now().isoformat(),
        "architecture": "blend(legacy_schema_catboost, v2_multislot_catboost)",
        "search_space": {"depth": DEPTHS, "learning_rate": LEARNING_RATES, "l2_leaf_reg": L2_LEAF_REGS,
                          "n_samples_per_component": N_SAMPLES_PER_COMPONENT, "seed": 42},
        "selection_criterion": "in_distribution_val_spearman_only (external IC50 n=32 not used for selection, reported only)",
        "best_legacy_config": best_row_legacy,
        "best_v2_config": best_row_v2,
        "blend_weights": {"legacy": best_w, "v2_multislot": round(1 - best_w, 2)},
        "blend_weight_sweep": blend_sweep,
        "training_rows": len(train_rows),
        "in_distribution_val": {"n": len(val_rows), "spearman": float(best_sp_blend), "mae": float(mae_blend)},
        "external_ic50_holdout": {
            "n": len(external), "spearman": float(sp_ex), "p_value": float(p_ex),
            "note": "n=32 real Alnylam patent IC50s, never used in training or hyperparameter "
                    "selection; not individually significant at this sample size -- directional only.",
        },
        "baseline_comparison": baseline,
        "full_search_results": {"legacy": results_legacy, "v2": results_v2},
    }
    with open(MODELS_DIR / "model_b_v2_tuned_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f"\nSaved model_b_v2_{{legacy,multislot}}_tuned.cbm + model_b_v2_tuned_meta.json to {MODELS_DIR}")
    print("(Did NOT overwrite the existing model_b_v2_{legacy,multislot}.cbm / model_b_v2_meta.json "
          "production-integration checkpoint -- promotion is a separate step.)")


if __name__ == "__main__":
    main()
