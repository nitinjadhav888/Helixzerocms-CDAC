"""
prepare_context_dataset.py — Prepare 57-nt Target mRNA Context Dataset for Model Retraining

Processes and merges Hu.csv, Mix.csv, and Taka.csv from smepred/data/oligoformer/:
1. Validates sequence lengths (19-nt siRNA guide, 57-nt target window).
2. Verifies exact target alignment (mRNA[19:38] is the reverse complement of guide).
3. Clusters overlapping target windows into unique transcript/gene contigs for zero-leakage GroupKFold.
4. Unpacks the 24-dimensional thermodynamic vector (td).
5. Exports standardized datasets to smepred/data/processed/.
"""

import logging
from pathlib import Path
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path("smepred/data/oligoformer")
OUT_DIR = Path("smepred/data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

COMPLEMENT = str.maketrans("ACGU", "UGCA")

def reverse_complement(seq: str) -> str:
    clean = seq.strip().upper().replace("T", "U")
    return clean.translate(COMPLEMENT)[::-1]

def cluster_transcripts(df: pd.DataFrame, prefix: str, min_overlap: int = 20) -> list[str]:
    """
    Graph-based connected component clustering for tiled 57-nt target windows.
    Assigns each siRNA to a unique gene/transcript cluster.
    """
    mrnas = df["mRNA"].str.replace("X", "").tolist()
    n = len(mrnas)
    adj = {i: set() for i in range(n)}
    
    k = min_overlap
    kmer_to_ids = {}
    for i, seq in enumerate(mrnas):
        for j in range(len(seq) - k + 1):
            kmer = seq[j:j+k]
            if kmer not in kmer_to_ids:
                kmer_to_ids[kmer] = []
            kmer_to_ids[kmer].append(i)
            
    for kmer, ids in kmer_to_ids.items():
        if len(ids) > 1:
            for idx_a in ids:
                for idx_b in ids:
                    if idx_a != idx_b:
                        adj[idx_a].add(idx_b)
                        adj[idx_b].add(idx_a)
                        
    visited = set()
    cluster_labels = [""] * n
    cluster_idx = 1
    
    for i in range(n):
        if i not in visited:
            component = []
            queue = [i]
            visited.add(i)
            while queue:
                curr = queue.pop(0)
                component.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        
            cluster_name = f"{prefix}_gene_{cluster_idx:03d}"
            for idx in component:
                cluster_labels[idx] = cluster_name
            cluster_idx += 1
            
    return cluster_labels


def process_dataset(fname: str, prefix: str) -> pd.DataFrame:
    fpath = DATA_DIR / fname
    logger.info(f"Loading {fname} from {fpath}...")
    df = pd.read_csv(fpath)
    
    # 1. Clean sequences
    df["siRNA"] = df["siRNA"].str.strip().str.upper().str.replace("T", "U")
    df["mRNA"] = df["mRNA"].str.strip().str.upper().str.replace("T", "U")
    
    # Verify sequence lengths
    assert (df["siRNA"].str.len() == 19).all(), f"Non-19nt siRNA found in {fname}"
    assert (df["mRNA"].str.len() == 57).all(), f"Non-57nt mRNA found in {fname}"
    
    # 2. Extract 5' flank, target site, and 3' flank
    df["target_site"] = df["mRNA"].str.slice(19, 38)
    df["flank_5p"] = df["mRNA"].str.slice(0, 19)
    df["flank_3p"] = df["mRNA"].str.slice(38, 57)
    
    # Verify reverse complementarity
    expected_targets = df["siRNA"].apply(reverse_complement)
    mismatch_rate = (df["target_site"] != expected_targets).mean()
    logger.info(f"{fname}: target site reverse complement match rate = {100.0 * (1.0 - mismatch_rate):.2f}%")
    
    # 3. Cluster into transcripts/genes
    df["gene_cluster_id"] = cluster_transcripts(df, prefix)
    n_genes = df["gene_cluster_id"].nunique()
    logger.info(f"{fname}: identified {n_genes} unique transcript/gene clusters.")
    
    # 4. Standardize labels
    df["label"] = df["label"].astype(float)
    df["knockdown_pct"] = (df["label"] * 100.0).round(2)
    df["source_dataset"] = prefix
    
    # 5. Unpack 24-D thermodynamic vector (td)
    td_cols = [f"td_{i}" for i in range(24)]
    td_matrix = np.vstack(df["td"].apply(lambda s: [float(x.strip()) for x in str(s).split(",")]))
    td_df = pd.DataFrame(td_matrix, columns=td_cols, index=df.index)
    
    df = pd.concat([df, td_df], axis=1)
    return df


def main():
    datasets = [
        ("Hu.csv", "Hu"),
        ("Mix.csv", "Mix"),
        ("Taka.csv", "Taka"),
    ]
    
    processed_dfs = []
    for fname, prefix in datasets:
        processed_dfs.append(process_dataset(fname, prefix))
        
    unified_df = pd.concat(processed_dfs, ignore_index=True)
    logger.info(f"Unified dataset shape: {unified_df.shape[0]} rows, {unified_df.shape[1]} columns")
    logger.info(f"Unique gene clusters overall: {unified_df['gene_cluster_id'].nunique()}")
    
    # Export unified parquet and csv
    out_parquet = OUT_DIR / "oligoformer_57nt_context_dataset.parquet"
    out_csv = OUT_DIR / "oligoformer_57nt_context_dataset.csv"
    
    unified_df.to_parquet(out_parquet, index=False)
    unified_df.to_csv(out_csv, index=False)
    logger.info(f"Saved processed dataset to {out_parquet} ({out_parquet.stat().st_size:,} bytes)")
    logger.info(f"Saved processed dataset to {out_csv} ({out_csv.stat().st_size:,} bytes)")
    
    # Also export separate benchmarks for cross-dataset evaluation
    for prefix in ["Hu", "Mix", "Taka"]:
        sub_df = unified_df[unified_df["source_dataset"] == prefix].copy()
        sub_pq = OUT_DIR / f"dataset_{prefix.lower()}_57nt.parquet"
        sub_df.to_parquet(sub_pq, index=False)
        logger.info(f"Saved {prefix} partition to {sub_pq} ({len(sub_df)} rows)")

    print("\n" + "=" * 65)
    print("✅ 57-NT CONTEXT DATASET PREPARATION COMPLETE")
    print("=" * 65)
    print(f"Total unified samples: {len(unified_df):,}")
    print(f"Hu.csv samples:       {len(unified_df[unified_df['source_dataset'] == 'Hu']):,}")
    print(f"Mix.csv samples:      {len(unified_df[unified_df['source_dataset'] == 'Mix']):,}")
    print(f"Taka.csv samples:     {len(unified_df[unified_df['source_dataset'] == 'Taka']):,}")
    print(f"Total Gene Clusters:  {unified_df['gene_cluster_id'].nunique()}")
    print("=" * 65)

if __name__ == "__main__":
    main()
