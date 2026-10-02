"""
scripts/extract_clean_cmsirnadb_features.py
Extracts 581-dimensional feature matrix for the 17,761 clean dose rows in cmsirnadb_full.csv.
Saves:
- cmsirnadb_clean_features_X.npy (N x 581)
- cmsirnadb_clean_targets_Y.npy (N)
- cmsirnadb_clean_meta.csv (N rows metadata)
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from smepred.src import features_v4, chem_schema

DATA_DIR = ROOT / "smepred" / "data" / "processed"
CSV_PATH = DATA_DIR / "cmsirnadb_full.csv"

OUT_X_PATH = DATA_DIR / "cmsirnadb_clean_features_X.npy"
OUT_Y_PATH = DATA_DIR / "cmsirnadb_clean_targets_Y.npy"
OUT_META_PATH = DATA_DIR / "cmsirnadb_clean_meta.csv"

def main():
    print(f"Loading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"Total rows in raw lake: {len(df)}")
    
    # Filter to clean rows where concentration_nM is valid and > 0
    clean_mask = df["concentration_nM"].notnull() & (df["concentration_nM"] > 0) & df["efficacy"].notnull()
    clean_df = df[clean_mask].copy().reset_index(drop=True)
    N = len(clean_df)
    print(f"Filtered to {N} clean rows with verified non-null dose.")
    
    # Parse slots
    print("Promoting strings to NucSlot representation...")
    t0 = time.time()
    s_slots = [chem_schema.promote_legacy_string(s, bs) for s, bs in zip(clean_df["sense"], clean_df["base_sense"])]
    as_slots = [chem_schema.promote_legacy_string(a, ba) for a, ba in zip(clean_df["antisense"], clean_df["base_antisense"])]
    print(f"Slot promotion complete in {time.time() - t0:.2f}s.")
    
    # Batch feature extraction in chunks of 500
    chunk_size = 500
    all_chunks = []
    print(f"Extracting 577 base features across {N} rows in chunks of {chunk_size}...")
    t_feat_start = time.time()
    
    for i in range(0, N, chunk_size):
        chunk_s = s_slots[i:i + chunk_size]
        chunk_as = as_slots[i:i + chunk_size]
        X_chunk = features_v4.batch_features_v4(chunk_s, chunk_as)
        all_chunks.append(X_chunk)
        if (i // chunk_size) % 5 == 0 or (i + chunk_size >= N):
            elapsed = time.time() - t_feat_start
            pct = min(100.0, (i + len(chunk_s)) / N * 100)
            print(f"  Processed {i + len(chunk_s)}/{N} ({pct:.1f}%) in {elapsed:.1f}s...")
            
    X_base = np.vstack(all_chunks)
    print(f"Base feature matrix extracted: shape={X_base.shape} in {time.time() - t_feat_start:.2f}s.")
    
    # Extract covariates (4 features)
    # 1. log10(concentration_nM)
    log_conc = np.log10(clean_df["concentration_nM"].values.astype(np.float32)).reshape(-1, 1)
    
    # 2. log10(concentration_nM / 10.0) -> relative to standard clinical 10 nM
    log_conc_rel = (log_conc - 1.0).astype(np.float32)
    
    # 3. time_h / 24.0 (incubation normalized)
    time_h_norm = (clean_df["time_h"].fillna(24.0).values.astype(np.float32) / 24.0).reshape(-1, 1)
    
    # 4. is_hepatic indicator
    hepatic_cells = {"Hep3B", "Primary human hepatocytes", "Primary Cynomolgus Monkey Hepatocytes", "HepG2", "Huh7"}
    is_hepatic = clean_df["cell_type"].isin(hepatic_cells).astype(np.float32).values.reshape(-1, 1)
    
    # Combine into 581-dim matrix
    X_total = np.hstack([X_base, log_conc, log_conc_rel, time_h_norm, is_hepatic])
    Y_total = clean_df["efficacy"].values.astype(np.float32)
    
    print(f"Total unified feature matrix: shape={X_total.shape}, Y shape={Y_total.shape}")
    
    # Save arrays
    print(f"Saving to {OUT_X_PATH} and {OUT_Y_PATH}...")
    np.save(OUT_X_PATH, X_total)
    np.save(OUT_Y_PATH, Y_total)
    clean_df.to_csv(OUT_META_PATH, index=False)
    print("Feature extraction and caching COMPLETE!")

if __name__ == "__main__":
    main()
