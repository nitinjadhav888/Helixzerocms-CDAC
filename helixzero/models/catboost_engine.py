"""
helixzero.models.catboost_engine
================================
Production Wrapper for CatBoost Multi-Slot Chemotype Potency Engine.
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import numpy as np
from catboost import CatBoostRegressor

from helixzero.ontology.tokenizer import CanonicalNucSlot
from helixzero.featurizers.multislot_featurizer import MultiSlotFeaturizer

MODEL_V4_PATH = Path(__file__).parent.parent.parent / "smepred" / "models" / "model_b_v4.cbm"


class CatBoostEngine:
    """
    CatBoost 577-dimensional multi-slot chemotype potency predictor.
    """

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or MODEL_V4_PATH
        if not self.model_path.exists():
            raise FileNotFoundError(f"CatBoost model checkpoint not found at {self.model_path}")
        
        self.model = CatBoostRegressor()
        self.model.load_model(str(self.model_path))
        self.featurizer = MultiSlotFeaturizer()

    def predict_candidate(
        self,
        sense_slots: List[CanonicalNucSlot],
        anti_slots: List[CanonicalNucSlot]
    ) -> float:
        """Predicts knockdown efficacy percentage (0.0 to 100.0%)."""
        feat = self.featurizer.featurize(sense_slots, anti_slots).reshape(1, -1)
        pred = float(self.model.predict(feat)[0])
        return float(np.clip(pred, 0.0, 100.0))

    def predict_batch(
        self,
        batch_sense_slots: List[List[CanonicalNucSlot]],
        batch_anti_slots: List[List[CanonicalNucSlot]]
    ) -> np.ndarray:
        """Predicts knockdown efficacy percentages for a batch of candidates."""
        mat = self.featurizer.featurize_batch(batch_sense_slots, batch_anti_slots)
        preds = self.model.predict(mat)
        return np.clip(preds, 0.0, 100.0).astype(np.float32)
