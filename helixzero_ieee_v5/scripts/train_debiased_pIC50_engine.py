"""
helixzero_ieee_v5/scripts/train_debiased_pIC50_engine.py
=========================================================
Trains the de-biased HelixZero IEEE Module 2 Potency Engine
(module2_potency_pIC50_debiased.cbm) on the expanded dataset
with strict 5-Fold GroupKFold cross-validation grouped by antisense sequence.
"""

from __future__ import annotations
import sys
import logging
import time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import GroupKFold
from catboost import CatBoostRegressor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TrainPotencyEngine")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
IEEE_DIR = ROOT_DIR / "helixzero_ieee_v5"
DATA_FILE = IEEE_DIR / "data" / "ieee_v5_potency_debiased_master.csv"
MODELS_DIR = IEEE_DIR / "models"
OUT_MODEL = MODELS_DIR / "module2_potency_pIC50_debiased.cbm"
LEGACY_MODEL = MODELS_DIR / "module2_potency_pIC50.cbm"

sys.path.insert(0, str(ROOT_DIR))
from smepred.src import features_v4
from helixzero_ieee_v5.src.chem_ontology import parse_canonical_sequence


def main():
    start_t = time.time()
    logger.info(f"Loading de-biased dataset from {DATA_FILE}...")
    df = pd.read_csv(DATA_FILE)
    N = len(df)
    logger.info(f"Dataset loaded: {N:,} rows.")

    sense_seqs = df["sense_seq"].tolist()
    anti_seqs = df["anti_seq"].tolist()
    sense_mods = [str(x) if pd.notna(x) else "" for x in df["sense_mods"]]
    anti_mods = [str(x) if pd.notna(x) else "" for x in df["anti_mods"]]
    y_true = df["pIC50"].values.astype(np.float32)
    groups = np.array(anti_seqs)

    logger.info("Extracting 577-dimensional multi-modal features via features_v4...")
    s_slots_list = [parse_canonical_sequence(s, sm) for s, sm in zip(sense_seqs, sense_mods)]
    as_slots_list = [parse_canonical_sequence(a, am) for a, am in zip(anti_seqs, anti_mods)]
    
    # Batch feature extraction
    X = features_v4.batch_features_v4(s_slots_list, as_slots_list)
    logger.info(f"Features extracted successfully: X.shape = {X.shape}")

    # 1. Evaluate Legacy Model on the new de-biased dataset for comparison
    logger.info("Benchmarking Legacy Model (module2_potency_pIC50.cbm)...")
    if LEGACY_MODEL.exists():
        legacy_mod2 = CatBoostRegressor()
        legacy_mod2.load_model(LEGACY_MODEL)
        legacy_preds = legacy_mod2.predict(X)
        leg_pr, _ = pearsonr(y_true, legacy_preds)
        leg_sr, _ = spearmanr(y_true, legacy_preds)
        leg_mae = mean_absolute_error(y_true, legacy_preds)
        leg_rmse = root_mean_squared_error(y_true, legacy_preds)
        logger.info(f"Legacy Model Baseline -> Pearson r: {leg_pr:.4f} | Spearman rho: {leg_sr:.4f} | MAE: {leg_mae:.4f} | RMSE: {leg_rmse:.4f}")
        logger.info(f"Legacy Pred Range: {legacy_preds.min():.2f} - {legacy_preds.max():.2f}")

    # 2. Strict 5-Fold GroupKFold Cross-Validation (Zero Sequence Leakage)
    logger.info("Executing 5-Fold GroupKFold (grouped by unique antisense sequence)...")
    gkf = GroupKFold(n_splits=5)
    oof_preds = np.zeros(N, dtype=np.float32)
    fold_metrics = []

    cat_params = {
        "iterations": 1000,
        "learning_rate": 0.04,
        "depth": 8,
        "l2_leaf_reg": 4.0,
        "loss_function": "RMSE",
        "od_type": "Iter",
        "od_wait": 60,
        "random_seed": 42,
        "verbose": 0
    }

    for fold, (tr_idx, val_idx) in enumerate(gkf.split(X, y_true, groups=groups), 1):
        X_tr, y_tr = X[tr_idx], y_true[tr_idx]
        X_val, y_val = X[val_idx], y_true[val_idx]
        
        # Verify zero sequence overlap between train and val
        val_seqs = set(groups[val_idx])
        tr_seqs = set(groups[tr_idx])
        assert len(val_seqs.intersection(tr_seqs)) == 0, f"Sequence leakage detected in Fold {fold}!"

        model = CatBoostRegressor(**cat_params)
        model.fit(X_tr, y_tr, eval_set=(X_val, y_val), verbose=False)
        
        val_pred = model.predict(X_val)
        oof_preds[val_idx] = val_pred
        
        pr, _ = pearsonr(y_val, val_pred)
        sr, _ = spearmanr(y_val, val_pred)
        mae = mean_absolute_error(y_val, val_pred)
        rmse = root_mean_squared_error(y_val, val_pred)
        
        fold_metrics.append((pr, sr, mae, rmse))
        logger.info(f"  Fold {fold}/5: Pearson r = {pr:.4f} | Spearman ρ = {sr:.4f} | MAE = {mae:.4f} | RMSE = {rmse:.4f}")

    # Overall OOF Metrics
    oof_pr, _ = pearsonr(y_true, oof_preds)
    oof_sr, _ = spearmanr(y_true, oof_preds)
    oof_mae = mean_absolute_error(y_true, oof_preds)
    oof_rmse = root_mean_squared_error(y_true, oof_preds)

    logger.info("="*75)
    logger.info("OUT-OF-FOLD (OOF) 5-FOLD GROUPKFOLD SUMMARY:")
    logger.info(f"  • Pearson Correlation (r)  : {oof_pr:.4f}")
    logger.info(f"  • Spearman Rank Corr (ρ)   : {oof_sr:.4f}")
    logger.info(f"  • Mean Absolute Error (MAE): {oof_mae:.4f} pIC50 units")
    logger.info(f"  • Root Mean Sq Error (RMSE): {oof_rmse:.4f} pIC50 units")
    logger.info(f"  • OOF Predicted Range      : {oof_preds.min():.2f} - {oof_preds.max():.2f}")
    logger.info("="*75)

    # 3. Train Final Full Production Model
    logger.info(f"Fitting final production model on all {N:,} samples...")
    final_model = CatBoostRegressor(**cat_params)
    final_model.fit(X, y_true, verbose=False)
    
    final_model.save_model(OUT_MODEL)
    logger.info(f"✅ Final de-biased model checkpoint saved to: {OUT_MODEL}")
    
    elapsed = time.time() - start_t
    logger.info(f"Pipeline completed in {elapsed:.1f}s.")


if __name__ == "__main__":
    main()
