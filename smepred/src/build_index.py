"""
build_index.py -- Fast 2-bit Transcriptome Index Builder

Builds human_transcriptome.idx.pkl from human_transcriptome.fasta
using fast array vectorization.
"""
import sys
import pickle
import logging
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TXT_PATH = DATA_DIR / "human_transcriptome.fasta"
IDX_PATH = DATA_DIR / "human_transcriptome.idx.pkl"

_LUT = np.full(256, 255, dtype=np.uint64)
_LUT[ord('A')] = 0
_LUT[ord('C')] = 1
_LUT[ord('G')] = 2
_LUT[ord('T')] = 3
_LUT[ord('U')] = 3


def build():
    if not TXT_PATH.exists():
        logger.error(f"FASTA file not found at {TXT_PATH}")
        return

    logger.info(f"Reading FASTA file from {TXT_PATH}...")
    seqs = []
    with open(TXT_PATH, "r", encoding="utf-8") as f:
        current_seq = []
        for line in f:
            if line.startswith(">"):
                if current_seq:
                    seqs.append("".join(current_seq))
                current_seq = []
            else:
                current_seq.append(line.strip().upper())
        if current_seq:
            seqs.append("".join(current_seq))

    full_sequence = ("N" * 15).join(seqs)
    total_mrnas = len(seqs)
    logger.info(f"Loaded {total_mrnas:,} mRNA transcripts ({len(full_sequence):,} bases).")

    logger.info("Extracting packed 15-mer slicer set...")

    k15_chunks = []
    CHUNK_SIZE = 50000

    for c_start in range(0, total_mrnas, CHUNK_SIZE):
        chunk_seqs = seqs[c_start : c_start + CHUNK_SIZE]
        chunk_str = ("N" * 15).join(chunk_seqs)
        arr = _LUT[np.frombuffer(chunk_str.encode('ascii'), dtype=np.uint8)]
        N = len(arr)
        if N < 15:
            continue

        valid_mask_15 = (arr[:N - 14] < 4)
        for i in range(1, 15):
            valid_mask_15 &= (arr[i : N - 14 + i] < 4)

        valid_idx_15 = np.where(valid_mask_15)[0]
        if len(valid_idx_15) > 0:
            k15_arr = np.zeros(len(valid_idx_15), dtype=np.uint64)
            for i in range(15):
                k15_arr |= (arr[valid_idx_15 + i].astype(np.uint64) << (2 * (14 - i)))
            u_k15 = np.unique(k15_arr)
            k15_chunks.append(u_k15)
            del k15_arr, valid_idx_15, valid_mask_15, u_k15

        processed = min(c_start + CHUNK_SIZE, total_mrnas)
        logger.info(f"Processed {processed:,} / {total_mrnas:,} transcripts...")

    if k15_chunks:
        all_k15 = np.unique(np.concatenate(k15_chunks))
        k15_set = set(all_k15.tolist())
    else:
        k15_set = set()

    k7_counts = {}
    k6_counts = {}

    logger.info(f"Saving pre-built index pickle file to {IDX_PATH}...")
    with open(IDX_PATH, "wb") as f:
        pickle.dump((full_sequence, k15_set, k7_counts, k6_counts), f)

    logger.info(f"SUCCESS: Saved {len(k15_set):,} 15-mer keys to {IDX_PATH}.")


if __name__ == "__main__":
    build()
