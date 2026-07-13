"""
model_b_v2.py -- Serving wrapper for the multi-slot Model B v2 CatBoost.

Pure v2-only (no legacy blend). The legacy-schema CatBoost component was
removed 2026-07-13: the blend weight sweep showed it added ~0.004 Spearman
(noise-level) while depending on the buggy single-char encoding that can't
represent independent PS+sugar at one position. Now a single CatBoost model
using the v2 multi-slot feature extractor (features_v2.py, 444-dim).

Bridges the legacy single-char candidate strings that modification_engine.py
still generates into the multi-slot schema via chem_schema.promote_legacy_string,
so today's candidate generator can already be scored by this model; true
multi-slot candidate GENERATION (e.g. independently varying PS backbone and
sugar chemistry at one position) remains follow-up work.
"""
from __future__ import annotations
from pathlib import Path
from typing import List

import numpy as np
from catboost import CatBoostRegressor

from .chem_schema import promote_legacy_string
from . import features_v2

MODELS_DIR = Path(__file__).parent.parent / "models"

_cache: dict = {}


def _load():
    if "model" in _cache:
        return _cache["model"]
    m = CatBoostRegressor()
    m.load_model(str(MODELS_DIR / "model_b_v2_multislot.cbm"))
    _cache["model"] = m
    return m


def predict_from_slots(sense_slots: List[list], anti_slots: List[list]) -> np.ndarray:
    """Scores true multi-slot candidates (0-100 efficacy)."""
    m = _load()
    X_v2 = features_v2.batch_features_v2(sense_slots, anti_slots)
    return np.clip(m.predict(X_v2), 0.0, 100.0)


def predict(sense_list: List[str], antisense_list: List[str],
            base_sense_list: List[str], base_antisense_list: List[str]) -> np.ndarray:
    """Scores legacy single-char modified candidates (0-100 efficacy) by
    promoting them to slots first (lossy: legacy alphabet can't express
    independent PS+sugar -- see promote_legacy_string docstring)."""
    sense_slots = [promote_legacy_string(s, bs) for s, bs in zip(sense_list, base_sense_list)]
    anti_slots = [promote_legacy_string(a, ba) for a, ba in zip(antisense_list, base_antisense_list)]
    return predict_from_slots(sense_slots, anti_slots)
