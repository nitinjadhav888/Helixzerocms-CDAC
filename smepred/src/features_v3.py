"""
features_v3.py -- Enriched feature extractor combining v2 multi-slot
features (444-dim) with PCA-reduced RNA-FM embeddings (64-dim) and
ViennaRNA thermodynamic features (5-dim). Total: 513-dim.

RNA-FM embeddings (640-dim) are pre-computed and PCA-reduced to 32-dim
per strand (64-dim total), preserving ~81% of variance.

ViennaRNA: MFE of each strand, duplex MFE, and mean base-pair distance.
"""
from __future__ import annotations
import pickle
from pathlib import Path
from typing import List, Optional

import numpy as np
import joblib

from .chem_schema import NucSlot
from .features_v2 import (
    N_POS_TOTAL as _N_POS,
    _N_ENGINEERED as _N_ENG_V2,
    N_FEATURES as _N_V2,
    build_features_v2,
    batch_features_v2,
)

MODELS_DIR = Path(__file__).parent.parent / "models"
CACHE_FILE = MODELS_DIR / "rnafm_embeddings.pkl"
PCA_FILE = MODELS_DIR / "rnafm_pca_32.pkl"

# PCA-reduced RNA-FM: 32-dim per strand (sense + antisense = 64)
N_FM_DIM = 32
N_FM = N_FM_DIM * 2  # 64

# ViennaRNA: 5 features
N_VIENNA = 5

N_FEATURES_V3 = _N_V2 + N_FM + N_VIENNA  # 444 + 64 + 5 = 513

_cache_fm: Optional[dict] = None
_cache_pca: Optional = None


def _load_caches():
    global _cache_fm, _cache_pca
    if _cache_fm is None:
        with open(CACHE_FILE, "rb") as f:
            _cache_fm = pickle.load(f)
    if _cache_pca is None:
        _cache_pca = joblib.load(PCA_FILE)
    return _cache_fm, _cache_pca


def _clean_seq(bases: str) -> str:
    cleaned = bases.upper().replace("T", "U")
    cleaned = "".join(c for c in cleaned if c in "ACGU")
    return cleaned


def _rnafm_features(sense_slots: List[NucSlot], anti_slots: List[NucSlot]) -> np.ndarray:
    """PCA-reduced RNA-FM embeddings: 32-dim sense + 32-dim antisense = 64-dim."""
    cache, pca = _load_caches()
    s_seq = _clean_seq("".join(s.base for s in sense_slots))
    a_seq = _clean_seq("".join(s.base for s in anti_slots))

    def _embed(seq: str) -> np.ndarray:
        emb = cache.get(seq, np.zeros(640, dtype=np.float32))
        return pca.transform(emb.reshape(1, -1))[0].astype(np.float32)

    return np.concatenate([_embed(s_seq), _embed(a_seq)])


def _vienna_features(sense_slots: List[NucSlot], anti_slots: List[NucSlot]) -> np.ndarray:
    """ViennaRNA thermodynamic features: 5-dim."""
    import RNA
    s_seq = _clean_seq("".join(s.base for s in sense_slots))
    a_seq = _clean_seq("".join(s.base for s in anti_slots))
    feats = []
    # 1. Sense strand MFE (normalized to [0,1])
    _, mfe_s = RNA.fold_compound(s_seq).mfe()
    feats.append(max(-50.0, min(0.0, float(mfe_s))) / -50.0)
    # 2. Antisense strand MFE
    _, mfe_a = RNA.fold_compound(a_seq).mfe()
    feats.append(max(-50.0, min(0.0, float(mfe_a))) / -50.0)
    # 3. Duplex MFE (sense + antisense)
    duplex = RNA.duplexfold(s_seq, a_seq)
    feats.append(max(-70.0, min(0.0, float(duplex.energy))) / -70.0)
    # 4. Mean base-pair distance (ensemble diversity)
    fc_d = RNA.fold_compound(s_seq + "&" + a_seq)
    fc_d.pf()
    feats.append(min(50.0, fc_d.mean_bp_distance()) / 50.0)
    # 5. GC content of combined duplex
    combined = s_seq + a_seq
    gc = sum(1 for b in combined if b in "GC") / max(1, len(combined))
    feats.append(gc)
    return np.array(feats, dtype=np.float32)


def build_features_v3(sense_slots: List[NucSlot], anti_slots: List[NucSlot]) -> np.ndarray:
    """Build the full 513-dim feature vector."""
    v2 = build_features_v2(sense_slots, anti_slots)
    fm = _rnafm_features(sense_slots, anti_slots)
    vr = _vienna_features(sense_slots, anti_slots)
    return np.concatenate([v2, fm, vr])


def batch_features_v3(sense_slots_list, anti_slots_list) -> np.ndarray:
    return np.stack([
        build_features_v3(ss, as_)
        for ss, as_ in zip(sense_slots_list, anti_slots_list)
    ])
