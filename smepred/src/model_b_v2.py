"""
model_b_v2.py -- Serving wrapper for the multi-slot Model B (see
scripts/train_model_b_v2.py for training, docs/validations/
model_b_v2_multislot_ablation.md for validation). Kept as an explicit,
separately-selectable path (model_key="B_v2") rather than silently replacing
the deployed "B" model, since its raw-score calibration hasn't been
re-validated against the live API's rescaling assumptions yet.

Bridges the legacy single-char candidate strings that modification_engine.py
still generates into the multi-slot schema via chem_schema.promote_legacy_string,
so today's candidate generator can already be scored by this model; true
multi-slot candidate GENERATION (e.g. independently varying PS backbone and
sugar chemistry at one position) remains follow-up work.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import List

import numpy as np
from catboost import CatBoostRegressor

from .chem_schema import promote_legacy_string, slots_to_legacy_string
from .features import extract_phase2
from . import features_v2

MODELS_DIR = Path(__file__).parent.parent / "models"

_cache: dict = {}


def _load():
    if "legacy" in _cache:
        return _cache["legacy"], _cache["v2"], _cache["w_legacy"]
    m_legacy = CatBoostRegressor()
    m_legacy.load_model(str(MODELS_DIR / "model_b_v2_legacy.cbm"))
    m_v2 = CatBoostRegressor()
    m_v2.load_model(str(MODELS_DIR / "model_b_v2_multislot.cbm"))
    with open(MODELS_DIR / "model_b_v2_meta.json") as f:
        w_legacy = json.load(f)["blend_weights"]["legacy"]
    _cache.update(legacy=m_legacy, v2=m_v2, w_legacy=w_legacy)
    return m_legacy, m_v2, w_legacy


def predict_from_slots(sense_slots: List[list], anti_slots: List[list]) -> np.ndarray:
    """Scores true multi-slot candidates (0-100 efficacy). Use this when the
    candidate already carries independent sugar/linkage/terminal/conjugate
    state (e.g. from multislot_designer.py) -- no fidelity loss."""
    m_legacy, m_v2, w_legacy = _load()
    legacy_s = [slots_to_legacy_string(s) for s in sense_slots]
    legacy_a = [slots_to_legacy_string(s) for s in anti_slots]
    base_s = ["".join(s.base for s in sl) for sl in sense_slots]
    base_a = ["".join(s.base for s in sl) for sl in anti_slots]
    X_legacy = extract_phase2(legacy_s, legacy_a, base_s, base_a)
    X_v2 = features_v2.batch_features_v2(sense_slots, anti_slots)
    return w_legacy * m_legacy.predict(X_legacy) + (1 - w_legacy) * m_v2.predict(X_v2)


def predict(sense_list: List[str], antisense_list: List[str],
            base_sense_list: List[str], base_antisense_list: List[str]) -> np.ndarray:
    """Scores legacy single-char modified candidates (0-100 efficacy) by
    promoting them to slots first (lossy: legacy alphabet can't express
    independent PS+sugar -- see promote_legacy_string docstring)."""
    sense_slots = [promote_legacy_string(s, bs) for s, bs in zip(sense_list, base_sense_list)]
    anti_slots = [promote_legacy_string(a, ba) for a, ba in zip(antisense_list, base_antisense_list)]
    return predict_from_slots(sense_slots, anti_slots)
