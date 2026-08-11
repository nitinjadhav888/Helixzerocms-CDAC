"""
model_b_v4.py -- Serving wrapper for the joint Model B v4 CatBoost
(v2 multi-slot + RNA-FM embeddings + RNA-Ernie embeddings + ViennaRNA thermodynamics).
"""
from __future__ import annotations
from pathlib import Path
from typing import List

import numpy as np
from catboost import CatBoostRegressor

from .chem_schema import promote_legacy_string
from . import features_v4

MODELS_DIR = Path(__file__).parent.parent / "models"

_cache: dict = {}


def _load():
    if "model" in _cache:
        return _cache["model"]
    m = CatBoostRegressor()
    m.load_model(str(MODELS_DIR / "model_b_v4.cbm"))
    _cache["model"] = m
    return m


def predict_from_slots(sense_slots: List[list], anti_slots: List[list]) -> np.ndarray:
    """Scores true multi-slot candidates using v4 joint features."""
    m = _load()
    X = features_v4.batch_features_v4(sense_slots, anti_slots)
    return np.clip(m.predict(X), 0.0, 100.0)


def predict(sense_list: List[str], antisense_list: List[str],
            base_sense_list: List[str], base_antisense_list: List[str]) -> np.ndarray:
    """Scores legacy single-char modified candidates by promoting to slots first."""
    sense_slots = [promote_legacy_string(s, bs) for s, bs in zip(sense_list, base_sense_list)]
    anti_slots = [promote_legacy_string(a, ba) for a, ba in zip(antisense_list, base_antisense_list)]
    return predict_from_slots(sense_slots, anti_slots)
