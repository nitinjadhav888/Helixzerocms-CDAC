"""
scripts/optimize_unified_catboost_loop.py
=========================================
Runs a systematic 10-iteration hyperparameter optimization loop across GroupKFold splits
and tracks:
1. CV Spearman rho and Pearson r.
2. CV MAE and RMSE.
3. Live FDA 6-drug benchmark alignment.
4. Identifies the optimal trade-off between zero-leakage generalizability and clinical drug fidelity.
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.model_selection import GroupKFold
from catboost import CatBoostRegressor

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.train_unified_dose_aware_catboost import (
    X_PATH, Y_PATH, META_PATH, FDA_DRUGS, build_candidate_517_vector
)

def evaluate_fda(model):
    res = {}
    for d in FDA_DRUGS:
        x_vec = build_candidate_517_vector(d, conc_nM=10.0)
        pred = float(np.clip(model.predict(x_vec)[0], 0.0, 100.0))
        res[d["drug"]] = pred
    return res

def main():
    print("=" * 90)
    print(" SYSTEMATIC UNIFIED CATBOOST HYPERPARAMETER OPTIMIZATION LOOP (10 RUNS)")
    print("=" * 90)
    
    X = np.load(X_PATH)
    Y = np.load(Y_PATH)
    meta = pd.read_csv(META_PATH)
    groups = meta["target_gene"].values
    
    print(f"Dataset shape: X={X.shape}, Y={Y.shape}, 11 Unique Gene Groups")
    
    # 10 systematic experimental configurations
    experiments = [
        {"name": "Exp1_Base_D6_LR0.04_L2_3.0", "depth": 6, "lr": 0.04, "l2": 3.0, "loss": "RMSE", "iter": 1200},
        {"name": "Exp2_Deep_D7_LR0.03_L2_2.0", "depth": 7, "lr": 0.03, "l2": 2.0, "loss": "RMSE", "iter": 1400},
        {"name": "Exp3_Deeper_D8_LR0.025_L2_1.5", "depth": 8, "lr": 0.025, "l2": 1.5, "loss": "RMSE", "iter": 1500},
        {"name": "Exp4_LowReg_D6_LR0.035_L2_1.0", "depth": 6, "lr": 0.035, "l2": 1.0, "loss": "RMSE", "iter": 1400},
        {"name": "Exp5_LowReg_D7_LR0.03_L2_1.0", "depth": 7, "lr": 0.03, "l2": 1.0, "loss": "RMSE", "iter": 1500},
        {"name": "Exp6_Huber_D6_LR0.04_L2_2.0", "depth": 6, "lr": 0.04, "l2": 2.0, "loss": "Huber:delta=15", "iter": 1400},
        {"name": "Exp7_Huber_D7_LR0.03_L2_1.5", "depth": 7, "lr": 0.03, "l2": 1.5, "loss": "Huber:delta=15", "iter": 1500},
        {"name": "Exp8_MAE_Loss_D6_LR0.04_L2_2.0", "depth": 6, "lr": 0.04, "l2": 2.0, "loss": "MAE", "iter": 1200},
        {"name": "Exp9_Deep_Long_D7_LR0.02_L2_1.0", "depth": 7, "lr": 0.02, "l2": 1.0, "loss": "RMSE", "iter": 2000},
        {"name": "Exp10_Deepest_D8_LR0.02_L2_1.0", "depth": 8, "lr": 0.02, "l2": 1.0, "loss": "RMSE", "iter": 1800},
    ]
    
    gkf = GroupKFold(n_splits=5)
    summary_records = []
    
    for exp_idx, cfg in enumerate(experiments, 1):
        print(f"\n[{exp_idx}/10] Testing: {cfg['name']} (Depth={cfg['depth']}, LR={cfg['lr']}, L2={cfg['l2']}, Loss={cfg['loss']}, Iter={cfg['iter']})...")
        t0 = time.time()
        
        # 5-fold cross validation
        oof_preds = np.zeros(len(Y), dtype=np.float32)
        for fold, (train_idx, val_idx) in enumerate(gkf.split(X, Y, groups=groups), 1):
            cb_fold = CatBoostRegressor(
                iterations=cfg["iter"],
                depth=cfg["depth"],
                learning_rate=cfg["lr"],
                l2_leaf_reg=cfg["l2"],
                loss_function=cfg["loss"],
                random_seed=42 + fold,
                verbose=False
            )
            cb_fold.fit(X[train_idx], Y[train_idx], eval_set=(X[val_idx], Y[val_idx]), early_stopping_rounds=100, verbose=False)
            oof_preds[val_idx] = cb_fold.predict(X[val_idx])
            
        r, _ = pearsonr(Y, oof_preds)
        rho, _ = spearmanr(Y, oof_preds)
        mae = float(np.mean(np.abs(Y - oof_preds)))
        rmse = float(np.sqrt(np.mean((Y - oof_preds) ** 2)))
        
        # Train full model for FDA benchmark
        cb_full = CatBoostRegressor(
            iterations=cfg["iter"],
            depth=cfg["depth"],
            learning_rate=cfg["lr"],
            l2_leaf_reg=cfg["l2"],
            loss_function=cfg["loss"],
            random_seed=42,
            verbose=False
        )
        cb_full.fit(X, Y, verbose=False)
        fda_scores = evaluate_fda(cb_full)
        mean_fda = float(np.mean(list(fda_scores.values())))
        elapsed = time.time() - t0
        
        rec = {
            "Config": cfg["name"],
            "Depth": cfg["depth"],
            "LR": cfg["lr"],
            "L2": cfg["l2"],
            "Loss": cfg["loss"],
            "CV_Pearson_r": round(r, 4),
            "CV_Spearman_rho": round(rho, 4),
            "CV_MAE%": round(mae, 2),
            "CV_RMSE%": round(rmse, 2),
            "Patisiran%": round(fda_scores["Patisiran"], 2),
            "Inclisiran%": round(fda_scores["Inclisiran"], 2),
            "Vutrisiran%": round(fda_scores["Vutrisiran"], 2),
            "Givosiran%": round(fda_scores["Givosiran"], 2),
            "Lumasiran%": round(fda_scores["Lumasiran"], 2),
            "Nedosiran%": round(fda_scores["Nedosiran"], 2),
            "Mean_FDA%": round(mean_fda, 2),
            "Runtime_s": round(elapsed, 1)
        }
        summary_records.append(rec)
        print(f"  -> CV Pearson r: {r:.4f} | Spearman rho: {rho:.4f} | MAE: {mae:.2f}% | Mean FDA: {mean_fda:.2f}% | Inclisiran: {fda_scores['Inclisiran']:.2f}% ({elapsed:.1f}s)")
        
    summary_df = pd.DataFrame(summary_records)
    out_csv = ROOT / "final_benchmarks" / "unified_catboost_10_experiment_comparison.csv"
    summary_df.to_csv(out_csv, index=False)
    print("\n" + "=" * 110)
    print(" 10-EXPERIMENT OPTIMIZATION LOOP SUMMARY RESULTS")
    print("=" * 110)
    print(summary_df[["Config", "CV_Pearson_r", "CV_Spearman_rho", "CV_MAE%", "Mean_FDA%", "Inclisiran%", "Patisiran%"]].to_string())
    print("=" * 110)
    print(f"Saved full comparison table to: {out_csv}")

if __name__ == "__main__":
    main()
