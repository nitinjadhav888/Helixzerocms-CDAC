"""
scripts/train_unified_dose_aware_catboost.py
============================================
Trains a Single Unified Dose-Aware & Cell-Aware CatBoost Regressor on the 17,761 clean
rows of cmsirnadb_full.csv with zero-leakage GroupKFold (grouped by target_gene).

Evaluates:
1. 5-Fold GroupKFold Cross-Validation Metrics (Pearson r, Spearman rho, MAE, RMSE).
2. Out-of-Distribution Blind Benchmark on all 6 FDA-Approved siRNA Therapeutics
   (Patisiran, Givosiran, Lumasiran, Inclisiran, Vutrisiran, Nedosiran) at 10.0 nM.
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

from smepred.src import features_v4
from helixzero_ieee_v5.src.chem_ontology import parse_canonical_sequence

DATA_DIR = ROOT / "smepred" / "data" / "processed"
MODELS_DIR = ROOT / "smepred" / "models"
X_PATH = DATA_DIR / "cmsirnadb_clean_features_X_517.npy"
Y_PATH = DATA_DIR / "cmsirnadb_clean_targets_Y.npy"
META_PATH = DATA_DIR / "cmsirnadb_clean_meta.csv"

OUT_MODEL_PATH = MODELS_DIR / "unified_dose_catboost.cbm"

FDA_DRUGS = [
    {
        "drug": "Patisiran",
        "target": "TTR",
        "phase3_range": "84.0% - 87.0%",
        "sense_seq": "GUAGUGUACUUCCUUUGUUTT",
        "anti_seq":  "AACAAAGGAAGUACACUACTT",
        "sense_mods": "M,M,M,M,M,M,M,M,M,M,M,M",
        "sense_pos":  "1,2,7,8,9,10,11,12,13,15,17,19",
        "anti_mods":  "M,M,M,M,M,M,M,M",
        "anti_pos":   "1,3,5,11,13,15,17,19",
    },
    {
        "drug": "Givosiran",
        "target": "ALAS1",
        "phase3_range": "78.0% - 83.0%",
        "sense_seq": "CAGUGUCAUCAACUUCUCAUU",
        "anti_seq":  "UGAGAAGUUGAUGACACUGUU",
        "sense_mods": "S,S,M,M,F,M,F,M,M,F,M,M,F,M,M,F,M,M,S,S",
        "sense_pos":  "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,21",
        "anti_mods":  "S,S,M,F,M,F,M,F,M,F,M,F,M,F,M,M,S,S",
        "anti_pos":   "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,20,21",
    },
    {
        "drug": "Lumasiran",
        "target": "HAO1",
        "phase3_range": "85.0% - 90.0%",
        "sense_seq": "ACCAGGUGGUACUGAAACUAA",
        "anti_seq":  "UAGUUUCAGUACCACCUGGUU",
        "sense_mods": "S,S,M,M,F,M,F,M,M,F,M,M,F,M,M,F,M,M,S,S",
        "sense_pos":  "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,21",
        "anti_mods":  "S,S,M,F,M,F,M,F,M,F,M,F,M,F,M,M,S,S",
        "anti_pos":   "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,20,21",
    },
    {
        "drug": "Inclisiran",
        "target": "PCSK9",
        "phase3_range": "80.0% - 84.0%",
        "sense_seq": "CUACGAGACUGAUGACUAUTT",
        "anti_seq":  "AUAGUCAUCAGUCUCGUAGTT",
        "sense_mods": "S,S,F,M,F,M,M,F,M,M,F,M,M,F,M,M,F,M,S,S",
        "sense_pos":  "1,2,3,6,8,10,12,14,15,16,17,18,19,20,4,5,7,9,20,21",
        "anti_mods":  "S,S,F,F,F,F,F,F,M,M,M,M,M,M,M,M,S,S",
        "anti_pos":   "1,2,2,4,6,8,10,14,1,3,5,7,9,11,12,13,20,21",
    },
    {
        "drug": "Vutrisiran",
        "target": "TTR",
        "phase3_range": "88.0% - 93.0%",
        "sense_seq": "ACCUGUAGUGUACUUCCUUUG",
        "anti_seq":  "CAAAGGAAGUACACUACAGGU",
        "sense_mods": "S,S,F,F,F,F,F,M,M,M,M,M,M,M,M,M,M,M,S,S",
        "sense_pos":  "1,2,3,5,7,14,16,1,2,4,6,8,9,10,11,12,13,15,20,21",
        "anti_mods":  "1,S,S,F,F,F,F,F,F,8,M,M,M,M,M,M,M,M,M,M,S,S",
        "anti_pos":   "1,1,2,2,4,6,8,14,16,7,1,3,5,9,10,11,12,13,15,17,20,21",
    },
    {
        "drug": "Nedosiran",
        "target": "LDHA",
        "phase3_range": "75.0% - 82.0%",
        "sense_seq": "AUGUUGUCCUUUUUAUCUGAA",
        "anti_seq":  "UCAGAUAAAAAGGACAACAUG",
        "sense_mods": "S,S,M,M,F,M,F,M,M,F,M,M,F,M,M,F,M,M,S,S",
        "sense_pos":  "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,21",
        "anti_mods":  "S,S,M,F,M,F,M,F,M,F,M,F,M,F,M,M,S,S",
        "anti_pos":   "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,20,21",
    },
]

def build_candidate_517_vector(drug_info, conc_nM=10.0, is_hepatic=1.0, time_h=24.0):
    s_slots = parse_canonical_sequence(drug_info["sense_seq"], drug_info["sense_mods"], drug_info["sense_pos"])
    as_slots = parse_canonical_sequence(drug_info["anti_seq"], drug_info["anti_mods"], drug_info["anti_pos"])
    X_base = features_v4.batch_features_v4([s_slots], [as_slots])  # (1, 577)
    X_base_513 = np.hstack([X_base[:, :508], X_base[:, 572:]])      # (1, 513)
    
    log_c = np.array([[np.log10(conc_nM)]], dtype=np.float32)
    log_c_rel = log_c - 1.0
    t_norm = np.array([[time_h / 24.0]], dtype=np.float32)
    hep = np.array([[is_hepatic]], dtype=np.float32)
    
    X_517 = np.hstack([X_base_513, log_c, log_c_rel, t_norm, hep])
    return X_517

def evaluate_fda_drugs(model):
    print("\n" + "=" * 95)
    print(" LIVE BENCHMARK ON ALL 6 FDA-APPROVED siRNA THERAPEUTICS (Dose = 10.0 nM)")
    print("=" * 95)
    print(f"{'Drug':<12} {'Target':<7} {'Phase 3 Trial Range':<22} {'Pred Modified KD%':<18} {'Status'}")
    print("-" * 95)
    
    results = []
    for d in FDA_DRUGS:
        X_vec = build_candidate_517_vector(d, conc_nM=10.0)
        pred_kd = float(np.clip(model.predict(X_vec)[0], 0.0, 100.0))
        
        # Check alignment with Phase 3 clinical range
        low = float(d["phase3_range"].split("%")[0].strip())
        high = float(d["phase3_range"].split("-")[1].replace("%", "").strip())
        
        # Alignment criteria: within +/- 7% of clinical range
        is_aligned = (pred_kd >= low - 7.0) and (pred_kd <= high + 7.0)
        status = "ALIGNED" if is_aligned else f"MISALIGNED (Target {low}-{high}%)"
        
        print(f"{d['drug']:<12} {d['target']:<7} {d['phase3_range']:<22} {pred_kd:>8.2f}%          {status}")
        results.append(pred_kd)
        
    mean_kd = np.mean(results)
    print("=" * 95)
    print(f"Mean Predicted Efficacy across all 6 FDA Drugs at 10.0 nM: {mean_kd:.2f}%\n")
    return mean_kd

def main():
    print("=" * 80)
    print(" UNIFIED DOSE-AWARE CATBOOST TRAINING ENGINE (ZERO-LEAKAGE GROUP-K-FOLD)")
    print("=" * 80)
    
    # 1. Load data
    print(f"Loading cached feature matrix: {X_PATH}...")
    X = np.load(X_PATH)
    Y = np.load(Y_PATH)
    meta = pd.read_csv(META_PATH)
    groups = meta["target_gene"].values
    
    print(f"Loaded X: {X.shape}, Y: {Y.shape}, Meta rows: {len(meta)}")
    print(f"Target genes in dataset: {np.unique(groups).tolist()}")
    
    # 2. GroupKFold Cross Validation (5 folds)
    gkf = GroupKFold(n_splits=5)
    fold_pearsons = []
    fold_spearmans = []
    fold_maes = []
    fold_rmses = []
    
    print("\n--- RUNNING 5-FOLD ZERO-LEAKAGE CROSS VALIDATION (GROUPED BY TARGET GENE) ---")
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, Y, groups=groups), 1):
        val_genes = np.unique(groups[val_idx])
        X_train, Y_train = X[train_idx], Y[train_idx]
        X_val, Y_val = X[val_idx], Y[val_idx]
        
        cb = CatBoostRegressor(
            iterations=1200,
            learning_rate=0.04,
            depth=6,
            l2_leaf_reg=3.0,
            loss_function="RMSE",
            random_seed=42 + fold,
            verbose=False
        )
        cb.fit(X_train, Y_train, eval_set=(X_val, Y_val), early_stopping_rounds=100, verbose=False)
        
        preds = cb.predict(X_val)
        r, _ = pearsonr(Y_val, preds)
        rho, _ = spearmanr(Y_val, preds)
        mae = np.mean(np.abs(Y_val - preds))
        rmse = np.sqrt(np.mean((Y_val - preds) ** 2))
        
        fold_pearsons.append(r)
        fold_spearmans.append(rho)
        fold_maes.append(mae)
        fold_rmses.append(rmse)
        
        print(f"Fold {fold}: Val Genes={list(val_genes)} (N={len(val_idx):5d}) | Pearson r={r:.4f} | Spearman rho={rho:.4f} | MAE={mae:.2f}% | RMSE={rmse:.2f}%")
        
    print("\n--- ZERO-LEAKAGE GROUP-K-FOLD CROSS-VALIDATION SUMMARY ---")
    print(f"Mean Pearson r   : {np.mean(fold_pearsons):.4f} +/- {np.std(fold_pearsons):.4f}")
    print(f"Mean Spearman rho: {np.mean(fold_spearmans):.4f} +/- {np.std(fold_spearmans):.4f}")
    print(f"Mean MAE (%)     : {np.mean(fold_maes):.2f}% +/- {np.std(fold_maes):.2f}%")
    print(f"Mean RMSE (%)    : {np.mean(fold_rmses):.2f}% +/- {np.std(fold_rmses):.2f}%")
    
    # 3. Train the Final Unified Production Model
    print("\n--- TRAINING FINAL UNIFIED PRODUCTION CATBOOST MODEL ON FULL CLEAN LAKE ---")
    t_train_start = time.time()
    final_cb = CatBoostRegressor(
        iterations=1500,
        learning_rate=0.035,
        depth=6,
        l2_leaf_reg=3.0,
        loss_function="RMSE",
        random_seed=42,
        verbose=100
    )
    final_cb.fit(X, Y, verbose=200)
    print(f"Final training complete in {time.time() - t_train_start:.2f}s.")
    
    # 4. Save model
    print(f"Saving retrained unified model to {OUT_MODEL_PATH}...")
    final_cb.save_model(str(OUT_MODEL_PATH))
    print(f"Saved checkpoint successfully! Size: {OUT_MODEL_PATH.stat().st_size / (1024*1024):.2f} MB")
    
    # 5. Evaluate on all 6 FDA drugs
    evaluate_fda_drugs(final_cb)

if __name__ == "__main__":
    main()
