"""
precompute_rnafm_embeddings.py -- Precompute RNA-FM embeddings for all
training sequences. Saves to disk so training doesn't need GPU/RNA-FM.

Strategy: For each unique base sequence (sense + antisense) in the training
data, run RNA-FM and save the mean-pooled final-layer embedding (640-dim).
Two embeddings per duplex: sense_fm + antisense_fm = 1280-dim total.
"""
from __future__ import annotations
import json
import pickle
from pathlib import Path
from typing import Set, Tuple

import numpy as np
import torch

from smepred.scripts.data.patent_sources import load_all_real_sources

MODELS_DIR = Path(__file__).parent.parent / "models"
CACHE_FILE = MODELS_DIR / "rnafm_embeddings.pkl"


def _load_rnafm():
    import fm
    model, alphabet = fm.pretrained.rna_fm_t12()
    model.eval()
    batch_converter = alphabet.get_batch_converter()
    return model, batch_converter


def _embed_sequences(
    sequences: Set[str],
    model,
    batch_converter,
    batch_size: int = 64,
    device: str = "cpu",
) -> dict:
    """Embed a set of unique sequences via RNA-FM, returning {seq: embedding}."""
    seq_list = sorted(sequences)
    embeddings = {}
    model = model.to(device)

    for i in range(0, len(seq_list), batch_size):
        batch = seq_list[i : i + batch_size]
        data = [(f"seq{j}", s) for j, s in enumerate(batch)]
        _, _, tokens = batch_converter(data)
        tokens = tokens.to(device)

        with torch.no_grad():
            results = model(tokens, repr_layers=[12])
            # Layer 12, shape: [batch, seq_len+2, 640]
            reprs = results["representations"][12]
            # Mean pool over actual sequence positions (skip BOS/EOS tokens)
            # BOS at index 0, EOS at last index
            for j, seq in enumerate(batch):
                seq_len = len(seq)
                # Tokens are [BOS, seq[0], seq[1], ..., seq[N-1], EOS]
                pool = reprs[j, 1 : seq_len + 1].mean(dim=0).cpu().numpy()
                embeddings[seq] = pool.astype(np.float32)

        if (i + batch_size) % 512 == 0 or (i + batch_size) >= len(seq_list):
            print(f"  embedded {min(i + batch_size, len(seq_list))}/{len(seq_list)} sequences")

    return embeddings


def main():
    print("Loading training data...")
    rows, external = load_all_real_sources()
    all_rows = rows  # only train rows, not external holdout

    def _clean_seq(bases: str) -> str:
        """Normalize to RNA: replace T with U, remove non-ACGU chars, strip DNA prefixes."""
        cleaned = bases.upper().replace("T", "U")
        # Remove non-standard characters that might confuse RNA-FM alphabet
        cleaned = "".join(c for c in cleaned if c in "ACGU")
        return cleaned

    # Collect unique base sequences
    unique_seqs: Set[str] = set()
    for r in all_rows:
        s_sense = _clean_seq("".join(s.base for s in r.sense_slots))
        s_anti = _clean_seq("".join(s.base for s in r.anti_slots))
        unique_seqs.add(s_sense)
        unique_seqs.add(s_anti)

    print(f"Unique sequences to embed: {len(unique_seqs)}")
    print(f"  from {len(all_rows):,} total training rows")

    # Also add external holdout sequences
    for _, r in external.iterrows():
        unique_seqs.add(_clean_seq(r["sense_compact"]))
        unique_seqs.add(_clean_seq(r["anti_compact"]))
    print(f"After adding external holdout: {len(unique_seqs)} unique")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    print("Loading RNA-FM model...")
    model, batch_converter = _load_rnafm()

    print("Embedding sequences...")
    embeddings = _embed_sequences(unique_seqs, model, batch_converter, device=device)

    print(f"Saving {len(embeddings)} embeddings to {CACHE_FILE}...")
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(embeddings, f)

    # Verify
    sample_seq = next(iter(unique_seqs))
    print(f"Sample: {sample_seq} -> {embeddings[sample_seq].shape}")
    print("Done.")


if __name__ == "__main__":
    main()
