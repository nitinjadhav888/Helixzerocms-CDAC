"""
model_b_v3.py -- Serving wrapper for the enriched Model B v3 CatBoost
(v2 multi-slot + RNA-FM embeddings + ViennaRNA thermodynamics).

Promoted to default model key on 2026-07-13 after validation showed
+11% Spearman improvement over v2 and first-time-significant external
IC50 (p=0.028). See docs/validations/model_b_v3_enrichment.md.
"""
from __future__ import annotations
from pathlib import Path
from typing import List

import numpy as np
from catboost import CatBoostRegressor

from .chem_schema import promote_legacy_string
from . import features_v3

MODELS_DIR = Path(__file__).parent.parent / "models"

_cache: dict = {}


def _load():
    if "model" in _cache:
        return _cache["model"]
    m = CatBoostRegressor()
    m.load_model(str(MODELS_DIR / "model_b_v3.cbm"))
    _cache["model"] = m
    return m


def predict_from_slots(sense_slots: List[list], anti_slots: List[list]) -> np.ndarray:
    """Scores true multi-slot candidates using v3 enriched features."""
    m = _load()
    X = features_v3.batch_features_v3(sense_slots, anti_slots)
    return np.clip(m.predict(X), 0.0, 100.0)


def predict(sense_list: List[str], antisense_list: List[str],
            base_sense_list: List[str], base_antisense_list: List[str]) -> np.ndarray:
    """Scores legacy single-char modified candidates by promoting to slots first."""
    sense_slots = [promote_legacy_string(s, bs) for s, bs in zip(sense_list, base_sense_list)]
    anti_slots = [promote_legacy_string(a, ba) for a, ba in zip(antisense_list, base_antisense_list)]
    return predict_from_slots(sense_slots, anti_slots)
