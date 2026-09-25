"""
extract_all_context_features.py — Batch Feature Extraction for 57-nt Target mRNA Context Dataset

Extracts and caches the complete 190-D feature matrix across all 3,535 records in
smepred/data/processed/oligoformer_57nt_context_dataset.parquet:
1. ViennaRNA accessibility & thermodynamics (9-D)
2. OligoFormer nearest-neighbor td parameters (24-D)
3. Sequence and context composition & positional one-hot (92-D)
4. RNA-FM foundation model embeddings with PCA-32 projections (65-D)

Saves the complete dataset matrix and fitted PCA transformers to:
- smepred/data/processed/context_features_matrix.npz
- smepred/models/context_rnafm_pca_32.joblib
"""

import time
import sys
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import joblib

from smepred.src.context_feature_extractor import ContextFeatureExtractor, compute_viennarna_features, compute_sequence_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_PATH = Path("smepred/data/processed/oligoformer_57nt_context_dataset.parquet")
OUT_NPZ = Path("smepred/data/processed/context_features_matrix.npz")
MODELS_DIR = Path("smepred/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def build_feature_names() -> list[str]:
    vienna_names = [
        "dg_open", "dg_duplex", "ddg", "seed_dg_duplex", "dg_end5", "dg_end3",
        "end_diff", "mfe_target_local", "mfe_guide_local",
    ]
    td_names = [f"td_{i}" for i in range(24)]
    seq_stat_names = [
        "guide_gc", "target_gc", "flank5_gc", "flank3_gc", "seed_gc",
        "target_minus_guide_gc", "has_5p_u", "has_3p_a",
        "guide_u_pct", "guide_a_pct", "guide_g_pct", "guide_c_pct",
        "target_u_pct", "target_a_pct", "target_g_pct", "target_c_pct",
    ]
    onehot_names = []
    nucs = ["A", "C", "G", "U"]
    for pos in range(1, 20):
        for nuc in nucs:
            onehot_names.append(f"guide_pos_{pos}_{nuc}")

    mrna_pca_names = [f"mrna_pca_{i}" for i in range(32)]
    guide_pca_names = [f"guide_pca_{i}" for i in range(32)]
    fm_names = mrna_pca_names + guide_pca_names + ["cosine_sim_guide_target"]

    return vienna_names + td_names + seq_stat_names + onehot_names + fm_names


def main():
    logger.info(f"Loading preprocessed dataset from {DATA_PATH}...")
    df = pd.read_parquet(DATA_PATH)
    logger.info(f"Loaded {len(df)} samples across {df['gene_cluster_id'].nunique()} gene clusters.")

    feature_names = build_feature_names()
    logger.info(f"Target feature dimensionality: {len(feature_names)}")

    t0 = time.time()
    extractor = ContextFeatureExtractor(use_rna_fm=True, pca_dim=32)
    X = extractor.extract_features_from_df(df, batch_size=32, fit_pca=True)
    t_elapsed = time.time() - t0

    logger.info(f"Extraction completed in {t_elapsed:.1f}s ({t_elapsed/len(df):.3f}s/sample).")
    logger.info(f"Feature matrix shape: {X.shape}")

    # Integrity verification
    assert X.shape == (len(df), len(feature_names)), f"Shape mismatch: {X.shape} vs expected {(len(df), len(feature_names))}"
    nan_count = int(np.isnan(X).sum())
    inf_count = int(np.isinf(X).sum())
    assert nan_count == 0, f"Found {nan_count} NaNs in feature matrix!"
    assert inf_count == 0, f"Found {inf_count} Infs in feature matrix!"
    logger.info("Integrity check PASSED: 0 NaNs, 0 Infs.")

    # Save to NPZ
    np.savez_compressed(
        OUT_NPZ,
        X=X,
        y_label=df["label"].values.astype(np.float32),
        y_kd_pct=df["knockdown_pct"].values.astype(np.float32),
        y_binary=df["y"].values.astype(np.int32),
        gene_cluster_id=df["gene_cluster_id"].values.astype(str),
        source_dataset=df["source_dataset"].values.astype(str),
        siRNA=df["siRNA"].values.astype(str),
        mRNA=df["mRNA"].values.astype(str),
        feature_names=np.array(feature_names, dtype=str),
    )
    logger.info(f"Saved feature archive to {OUT_NPZ} ({OUT_NPZ.stat().st_size:,} bytes).")

    print("\n" + "=" * 65)
    print("✅ FULL CONTEXT-AWARE FEATURE MATRIX GENERATION COMPLETE")
    print("=" * 65)
    print(f"  Samples:                 {X.shape[0]:,}")
    print(f"  Features:                {X.shape[1]}")
    print(f"  ViennaRNA & Biophysics:  33 dims")
    print(f"  Sequence Engineering:    92 dims")
    print(f"  RNA-FM PCA Embeddings:   65 dims")
    print(f"  Output Archive:          {OUT_NPZ}")
    print(f"  Time Elapsed:            {t_elapsed:.1f}s")
    print("=" * 65)


if __name__ == "__main__":
    main()
