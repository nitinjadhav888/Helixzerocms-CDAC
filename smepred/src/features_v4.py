"""
features_v4.py -- Joint feature extractor combining v2 multi-slot
features (444-dim) with both RNA-FM PCA-32 embeddings (64-dim) and
RNA-Ernie PCA-32 embeddings (64-dim), plus ViennaRNA thermodynamics (5-dim).
Total: 577-dim.
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
FM_CACHE_FILE = MODELS_DIR / "rnafm_embeddings.pkl"
FM_PCA_FILE = MODELS_DIR / "rnafm_pca_32.pkl"
ERNIE_CACHE_FILE = MODELS_DIR / "rnaernie_embeddings.pkl"
ERNIE_PCA_FILE = MODELS_DIR / "rnaernie_pca_32.pkl"
VIENNA_CACHE_FILE = MODELS_DIR / "vienna_features_cache.pkl"

# Dimensions
N_FM_DIM = 32
N_FM = N_FM_DIM * 2  # 64

N_ERNIE_DIM = 32
N_ERNIE = N_ERNIE_DIM * 2  # 64

N_VIENNA = 5

N_FEATURES_V4 = _N_V2 + N_FM + N_ERNIE + N_VIENNA  # 444 + 64 + 64 + 5 = 577

# Caches
_cache_fm: Optional[dict] = None
_cache_fm_pca: Optional = None

_cache_ernie: Optional[dict] = None
_cache_ernie_pca: Optional = None

_vienna_cache: Optional[dict] = None
_vienna_cache_dirty = 0


def _load_fm_caches():
    global _cache_fm, _cache_fm_pca
    if _cache_fm is None:
        if FM_CACHE_FILE.exists():
            with open(FM_CACHE_FILE, "rb") as f:
                _cache_fm = pickle.load(f)
        else:
            _cache_fm = {}
    if _cache_fm_pca is None:
        if FM_PCA_FILE.exists():
            _cache_fm_pca = joblib.load(FM_PCA_FILE)
        else:
            _cache_fm_pca = None
    return _cache_fm, _cache_fm_pca


def _load_ernie_caches():
    global _cache_ernie, _cache_ernie_pca
    if _cache_ernie is None:
        if ERNIE_CACHE_FILE.exists():
            with open(ERNIE_CACHE_FILE, "rb") as f:
                _cache_ernie = pickle.load(f)
        else:
            _cache_ernie = {}
    if _cache_ernie_pca is None:
        if ERNIE_PCA_FILE.exists():
            _cache_ernie_pca = joblib.load(ERNIE_PCA_FILE)
        else:
            _cache_ernie_pca = None
    return _cache_ernie, _cache_ernie_pca


def _load_vienna_cache():
    global _vienna_cache
    if _vienna_cache is None:
        if VIENNA_CACHE_FILE.exists():
            with open(VIENNA_CACHE_FILE, "rb") as f:
                _vienna_cache = pickle.load(f)
        else:
            _vienna_cache = {}
    return _vienna_cache


def _save_vienna_cache():
    if _vienna_cache is not None:
        with open(VIENNA_CACHE_FILE, "wb") as f:
            pickle.dump(_vienna_cache, f)


def _clean_seq(bases: str) -> str:
    cleaned = bases.upper().replace("T", "U")
    cleaned = "".join(c for c in cleaned if c in "ACGU")
    return cleaned


def _rnafm_features(sense_slots: List[NucSlot], anti_slots: List[NucSlot]) -> np.ndarray:
    """PCA-reduced RNA-FM embeddings: 32-dim sense + 32-dim antisense = 64-dim."""
    cache, pca = _load_fm_caches()
    s_seq = _clean_seq("".join(s.base for s in sense_slots))
    a_seq = _clean_seq("".join(s.base for s in anti_slots))

    def _embed(seq: str) -> np.ndarray:
        if cache and pca and seq in cache:
            emb = cache[seq]
            return pca.transform(emb.reshape(1, -1))[0].astype(np.float32)
        return np.zeros(N_FM_DIM, dtype=np.float32)

    return np.concatenate([_embed(s_seq), _embed(a_seq)])


def _rnaernie_features(sense_slots: List[NucSlot], anti_slots: List[NucSlot]) -> np.ndarray:
    """PCA-reduced RNA-Ernie embeddings: 32-dim sense + 32-dim antisense = 64-dim."""
    cache, pca = _load_ernie_caches()
    s_seq = _clean_seq("".join(s.base for s in sense_slots))
    a_seq = _clean_seq("".join(s.base for s in anti_slots))

    def _embed(seq: str) -> np.ndarray:
        if cache and pca and seq in cache:
            emb = cache[seq]
            return pca.transform(emb.reshape(1, -1))[0].astype(np.float32)
        return np.zeros(N_ERNIE_DIM, dtype=np.float32)

    return np.concatenate([_embed(s_seq), _embed(a_seq)])


def _vienna_features(sense_slots: List[NucSlot], anti_slots: List[NucSlot]) -> np.ndarray:
    """ViennaRNA thermodynamic features: 5-dim (disk-cached per seq pair)."""
    import RNA
    s_seq = _clean_seq("".join(s.base for s in sense_slots)).upper().replace("T", "U")
    a_seq = _clean_seq("".join(s.base for s in anti_slots)).upper().replace("T", "U")
    cache = _load_vienna_cache()
    key = (s_seq, a_seq)

    if key in cache:
        return cache[key]

    feats = []
    try:
        fc_s = RNA.fold_compound(s_seq)
        mfe_s = fc_s.mfe()[1] if fc_s else 0.0
    except Exception:
        mfe_s = 0.0
    feats.append(max(-50.0, min(0.0, float(mfe_s))) / -50.0)

    try:
        fc_a = RNA.fold_compound(a_seq)
        mfe_a = fc_a.mfe()[1] if fc_a else 0.0
    except Exception:
        mfe_a = 0.0
    feats.append(max(-50.0, min(0.0, float(mfe_a))) / -50.0)

    try:
        duplex = RNA.duplexfold(s_seq, a_seq)
        d_energy = duplex.energy if duplex else 0.0
    except Exception:
        d_energy = 0.0
    feats.append(max(-70.0, min(0.0, float(d_energy))) / -70.0)

    try:
        fc_d = RNA.fold_compound(s_seq + "&" + a_seq)
        if fc_d:
            fc_d.pf()
            bp_dist = fc_d.mean_bp_distance()
        else:
            bp_dist = 0.0
    except Exception:
        bp_dist = 0.0
    feats.append(min(1.0, float(bp_dist) / 21.0))

    # 5. GC content of duplex
    combined = s_seq + a_seq
    gc = sum(1 for b in combined if b in "GC") / max(1, len(combined))
    feats.append(float(gc))

    out = np.array(feats, dtype=np.float32)
    cache[key] = out
    global _vienna_cache_dirty
    _vienna_cache_dirty += 1
    if _vienna_cache_dirty >= 2000:
        _save_vienna_cache()
        _vienna_cache_dirty = 0
    return out


def build_features_v4(sense_slots: List[NucSlot], anti_slots: List[NucSlot]) -> np.ndarray:
    """Build the full 577-dim feature vector."""
    v2 = build_features_v2(sense_slots, anti_slots)
    fm = _rnafm_features(sense_slots, anti_slots)
    ernie = _rnaernie_features(sense_slots, anti_slots)
    vr = _vienna_features(sense_slots, anti_slots)
    return np.concatenate([v2, fm, ernie, vr])


def batch_features_v4(sense_slots_list, anti_slots_list) -> np.ndarray:
    return np.stack([
        build_features_v4(ss, as_)
        for ss, as_ in zip(sense_slots_list, anti_slots_list)
    ])
