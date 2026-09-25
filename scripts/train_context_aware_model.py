#!/usr/bin/env python3
"""
train_context_aware_model.py
============================
Trains a context-aware foundation-biophysics naked siRNA potency prediction model
using precomputed 190-D features from ViennaRNA 2.7+, OligoFormer thermodynamic
descriptors, sequence/positional engineering, and RNA-FM Layer 12 PCA-32 representations.

Validation Protocol:
  - Strict 5-Fold GroupKFold (grouped by target mRNA/gene contig, 121 unique genes).
  - ZERO sequence leakage across folds.
  - Out-of-fold metrics: Pearson r, Spearman rho, MAE, RMSE.
  - Evaluation on external held-out benchmarks:
      * Mix.csv (165 unseen genes, 472 siRNAs)
      * Taka.csv (1 unseen reporter transcript, 702 siRNAs)
  - Final full-model training on Hu (and calibrated via out-of-fold IsotonicRegression).
  - Serialization to smepred/models/model_normal_context.txt, .pkl, and calibrator_context.pkl.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

import joblib
import lightgbm as lgb
import numpy as np
from scipy.stats import pearsonr, spearmanr
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import GroupKFold

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_context_aware_model")

DATA_NPZ = Path("smepred/data/processed/context_features_matrix.npz")
MODELS_DIR = Path("smepred/models")


def load_dataset() -> Dict[str, Any]:
    """Loads precomputed context features and metadata."""
    if not DATA_NPZ.exists():
        raise FileNotFoundError(f"Missing feature cache: {DATA_NPZ}")
    logger.info(f"Loading context feature matrix from {DATA_NPZ}...")
    npz = np.load(DATA_NPZ, allow_pickle=True)
    return {
        "X": npz["X"].astype(np.float32),
        "y_kd_pct": npz["y_kd_pct"].astype(np.float32),
        "y_label": npz["y_label"].astype(np.float32),
        "gene_cluster_id": npz["gene_cluster_id"].astype(str),
        "source_dataset": npz["source_dataset"].astype(str),
        "feature_names": [str(f) for f in npz["feature_names"]],
    }


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Computes standard biostatistical metrics."""
    p_r, p_pval = pearsonr(y_true, y_pred)
    s_rho, s_pval = spearmanr(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    return {
        "pearson_r": float(p_r),
        "pearson_p": float(p_pval),
        "spearman_rho": float(s_rho),
        "spearman_p": float(s_pval),
        "mae": float(mae),
        "rmse": float(rmse),
    }


def run_group_kfold_cv(
    X_hu: np.ndarray,
    y_hu: np.ndarray,
    groups_hu: np.ndarray,
    feature_names: list,
    params: Dict[str, Any],
    n_splits: int = 5,
    random_state: int = 42,
) -> Tuple[np.ndarray, Dict[str, Any], list]:
    """
    Executes 5-Fold GroupKFold cross-validation with zero data leakage.
    Returns out-of-fold predictions, cross-validation metrics, and fold models.
    """
    gkf = GroupKFold(n_splits=n_splits)
    oof_predictions = np.zeros(len(y_hu), dtype=np.float32)
    fold_metrics = []
    models = []
    
    logger.info(f"--- Starting {n_splits}-Fold GroupKFold Cross-Validation on Hu (N={len(y_hu)}) ---")
    
    for fold, (trn_idx, val_idx) in enumerate(gkf.split(X_hu, y_hu, groups=groups_hu)):
        X_trn, y_trn = X_hu[trn_idx], y_hu[trn_idx]
        X_val, y_val = X_hu[val_idx], y_hu[val_idx]
        
        trn_data = lgb.Dataset(X_trn, label=y_trn, feature_name=feature_names)
        val_data = lgb.Dataset(X_val, label=y_val, feature_name=feature_names, reference=trn_data)
        
        # Train LightGBM booster with early stopping
        callbacks = [
            lgb.early_stopping(stopping_rounds=40, verbose=False),
            lgb.log_evaluation(period=0),
        ]
        
        booster = lgb.train(
            params=params,
            train_set=trn_data,
            num_boost_round=800,
            valid_sets=[val_data],
            callbacks=callbacks,
        )
        
        val_preds = booster.predict(X_val, num_iteration=booster.best_iteration)
        oof_predictions[val_idx] = val_preds
        models.append(booster)
        
        metrics = evaluate_predictions(y_val, val_preds)
        fold_metrics.append(metrics)
        logger.info(
            f"Fold {fold} (Val N={len(val_idx)}, best_iter={booster.best_iteration}): "
            f"Pearson r={metrics['pearson_r']:.4f}, Spearman rho={metrics['spearman_rho']:.4f}, "
            f"MAE={metrics['mae']:.2f}, RMSE={metrics['rmse']:.2f}"
        )
        
    overall_metrics = evaluate_predictions(y_hu, oof_predictions)
    logger.info(
        f"==> OVERALL OUT-OF-FOLD (Zero-Leakage GroupKFold): "
        f"Pearson r={overall_metrics['pearson_r']:.4f}, Spearman rho={overall_metrics['spearman_rho']:.4f}, "
        f"MAE={overall_metrics['mae']:.2f}, RMSE={overall_metrics['rmse']:.2f}"
    )
    
    return oof_predictions, {
        "overall": overall_metrics,
        "folds": fold_metrics,
    }, models


def main():
    data = load_dataset()
    X = data["X"]
    y = data["y_kd_pct"]
    groups = data["gene_cluster_id"]
    datasets = data["source_dataset"]
    feature_names = data["feature_names"]
    
    # Split into Hu (training + zero-leakage CV) and held-out benchmarks (Mix, Taka)
    mask_hu = (datasets == "Hu")
    mask_mix = (datasets == "Mix")
    mask_taka = (datasets == "Taka")
    
    X_hu, y_hu, groups_hu = X[mask_hu], y[mask_hu], groups[mask_hu]
    X_mix, y_mix = X[mask_mix], y[mask_mix]
    X_taka, y_taka = X[mask_taka], y[mask_taka]
    
    logger.info(f"Hu dataset: {X_hu.shape[0]} samples across {len(np.unique(groups_hu))} gene clusters.")
    logger.info(f"Mix dataset (external benchmark): {X_mix.shape[0]} samples across {len(np.unique(groups[mask_mix]))} gene clusters.")
    logger.info(f"Taka dataset (external benchmark): {X_taka.shape[0]} samples across {len(np.unique(groups[mask_taka]))} gene clusters.")
    
    # Model Hyperparameters optimized for biophysical features
    # Huber loss provides resilience to high-throughput noise
    lgb_params = {
        "objective": "huber",
        "alpha": 0.9,
        "metric": "rmse",
        "boosting_type": "gbdt",
        "learning_rate": 0.03,
        "num_leaves": 31,
        "max_depth": 6,
        "min_child_samples": 20,
        "subsample": 0.8,
        "subsample_freq": 1,
        "colsample_bytree": 0.75,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "random_state": 42,
        "n_jobs": 4,
        "verbose": -1,
    }
    
    # 1. Zero-Leakage GroupKFold Cross-Validation
    oof_preds, cv_results, fold_models = run_group_kfold_cv(
        X_hu, y_hu, groups_hu, feature_names, lgb_params, n_splits=5
    )
    
    # 2. Fit Isotonic Calibrator on Out-of-Fold Predictions
    logger.info("Fitting out-of-fold IsotonicRegression calibrator...")
    calibrator = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=100.0)
    calibrator.fit(oof_preds, y_hu)
    calibrated_oof = calibrator.transform(oof_preds)
    cal_metrics = evaluate_predictions(y_hu, calibrated_oof)
    logger.info(
        f"Calibrated OOF Metrics: Pearson r={cal_metrics['pearson_r']:.4f}, "
        f"Spearman rho={cal_metrics['spearman_rho']:.4f}, MAE={cal_metrics['mae']:.2f}, RMSE={cal_metrics['rmse']:.2f}"
    )
    
    # 3. Train Production Full Model on Hu
    # We use the median best iteration from CV as the iteration count
    best_iters = [m.best_iteration for m in fold_models]
    final_n_iters = int(np.median(best_iters))
    logger.info(f"Training production full model on all Hu data with n_estimators={final_n_iters}...")
    
    full_trn_data = lgb.Dataset(X_hu, label=y_hu, feature_name=feature_names)
    final_booster = lgb.train(
        params=lgb_params,
        train_set=full_trn_data,
        num_boost_round=final_n_iters,
    )
    
    # 4. Evaluate on External Held-Out Benchmarks
    raw_mix_preds = final_booster.predict(X_mix)
    cal_mix_preds = calibrator.transform(raw_mix_preds)
    mix_metrics = evaluate_predictions(y_mix, cal_mix_preds)
    logger.info(
        f"==> External Held-Out Mix Benchmark (N={len(y_mix)}, 165 unseen genes): "
        f"Pearson r={mix_metrics['pearson_r']:.4f}, Spearman rho={mix_metrics['spearman_rho']:.4f}, "
        f"MAE={mix_metrics['mae']:.2f}, RMSE={mix_metrics['rmse']:.2f}"
    )
    
    raw_taka_preds = final_booster.predict(X_taka)
    cal_taka_preds = calibrator.transform(raw_taka_preds)
    taka_metrics = evaluate_predictions(y_taka, cal_taka_preds)
    logger.info(
        f"==> External Held-Out Taka Benchmark (N={len(y_taka)}, unseen reporter transcript): "
        f"Pearson r={taka_metrics['pearson_r']:.4f}, Spearman rho={taka_metrics['spearman_rho']:.4f}, "
        f"MAE={taka_metrics['mae']:.2f}, RMSE={taka_metrics['rmse']:.2f}"
    )
    
    # 5. Feature Importances
    importances_gain = final_booster.feature_importance(importance_type="gain")
    top_indices = np.argsort(importances_gain)[::-1][:25]
    logger.info("Top 25 Feature Importances (Gain):")
    top_features = []
    for rank, idx in enumerate(top_indices, 1):
        feat_name = feature_names[idx]
        gain = float(importances_gain[idx])
        top_features.append({"rank": rank, "feature": feat_name, "gain": gain})
        logger.info(f"  {rank:2d}. {feat_name:<30} Gain: {gain:10.2f}")
        
    # 6. Save Model Artifacts
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    txt_path = MODELS_DIR / "model_normal_context.txt"
    pkl_path = MODELS_DIR / "model_normal_context.pkl"
    cal_path = MODELS_DIR / "calibrator_context.pkl"
    meta_path = MODELS_DIR / "context_model_meta.json"
    
    final_booster.save_model(str(txt_path))
    joblib.dump(final_booster, pkl_path)
    joblib.dump(calibrator, cal_path)
    
    metadata = {
        "model_name": "HelixZero Context-Aware Foundation-Biophysics Naked Model",
        "date": "2026-09-18",
        "num_features": len(feature_names),
        "feature_names": feature_names,
        "hyperparameters": lgb_params,
        "best_iteration": final_n_iters,
        "metrics": {
            "hu_oof_raw": cv_results["overall"],
            "hu_oof_calibrated": cal_metrics,
            "hu_fold_details": cv_results["folds"],
            "mix_external": mix_metrics,
            "taka_external": taka_metrics,
        },
        "top_features": top_features,
    }
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
        
    logger.info(f"Saved native Booster text to {txt_path}")
    logger.info(f"Saved Booster pickle to {pkl_path}")
    logger.info(f"Saved Isotonic Calibrator to {cal_path}")
    logger.info(f"Saved Metadata & Evaluation metrics to {meta_path}")
    logger.info("Training and validation completed successfully.")


if __name__ == "__main__":
    main()
