"""
model_b_v4.py -- Serving wrapper for the Unified Dose-Aware & Cell-Aware CatBoost Regressor
(v2 multi-slot + RNA-FM embeddings + ViennaRNA thermodynamics + concentration/time/cell covariates).
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
    # Check for unified_dose_catboost.cbm first, then model_b_v4.cbm
    model_path = MODELS_DIR / "unified_dose_catboost.cbm"
    if not model_path.exists():
        model_path = MODELS_DIR / "model_b_v4.cbm"
    m.load_model(str(model_path))
    _cache["model"] = m
    return m


def predict_from_slots(
    sense_slots: List[list], anti_slots: List[list],
    conc_nM: float = 10.0, is_hepatic: float = 1.0, time_h: float = 24.0
) -> np.ndarray:
    """Scores true multi-slot candidates using unified 517-D dose-aware joint features."""
    m = _load()
    X = features_v4.batch_unified_features(
        sense_slots, anti_slots,
        conc_nM=conc_nM, is_hepatic=is_hepatic, time_h=time_h
    )
    return np.clip(m.predict(X), 0.0, 100.0)


def predict(
    sense_list: List[str], antisense_list: List[str],
    base_sense_list: List[str], base_antisense_list: List[str],
    conc_nM: float = 10.0, is_hepatic: float = 1.0, time_h: float = 24.0
) -> np.ndarray:
    """Scores legacy single-char modified candidates by promoting to slots first."""
    sense_slots = [promote_legacy_string(s, bs) for s, bs in zip(sense_list, base_sense_list)]
    anti_slots = [promote_legacy_string(a, ba) for a, ba in zip(antisense_list, base_antisense_list)]
    return predict_from_slots(
        sense_slots, anti_slots,
        conc_nM=conc_nM, is_hepatic=is_hepatic, time_h=time_h
    )

