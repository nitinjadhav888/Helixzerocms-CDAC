"""
helixzero.models.hierarchical_engine
====================================
Production Wrapper for IEEE v5 Hierarchical Bi-Level Potency Engine.

Architecture:
- Stage 1: Module 2 CatBoost Engine -> Predicts intrinsic biological affinity (pIC50).
- Stage 2: Module 3 CatBoost Engine -> Models concentration-dependent Hill knockdown dynamics.
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from catboost import CatBoostRegressor

from helixzero.ontology.tokenizer import CanonicalNucSlot
from helixzero.featurizers.multislot_featurizer import MultiSlotFeaturizer

IEEE_MODELS_DIR = Path(__file__).parent.parent.parent / "helixzero_ieee_v5" / "models"
MOD2_PATH = IEEE_MODELS_DIR / "module2_potency_pIC50.cbm"
MOD3_PATH = IEEE_MODELS_DIR / "module3_assay_response.cbm"


class HierarchicalEngine:
    """
    Two-stage bi-level engine modeling intrinsic potency and dose-dependent knockdown.
    """

    def __init__(
        self,
        mod2_path: Optional[Path] = None,
        mod3_path: Optional[Path] = None
    ):
        self.mod2_path = mod2_path or MOD2_PATH
        self.mod3_path = mod3_path or MOD3_PATH
        
        if not self.mod2_path.exists() or not self.mod3_path.exists():
            raise FileNotFoundError(f"Hierarchical checkpoints missing in {IEEE_MODELS_DIR}")
        
        self.mod2 = CatBoostRegressor()
        self.mod2.load_model(str(self.mod2_path))

        self.mod3 = CatBoostRegressor()
        self.mod3.load_model(str(self.mod3_path))

        self.featurizer = MultiSlotFeaturizer()

    def predict_candidate(
        self,
        sense_slots: List[CanonicalNucSlot],
        anti_slots: List[CanonicalNucSlot],
        conc_nM: float = 10.0
    ) -> Tuple[float, float, float, float]:
        """
        Runs hierarchical prediction.
        Returns:
            (pIC50, ic50_nM, knockdown_pct, hill_slope)
        """
        X_base = self.featurizer.featurize(sense_slots, anti_slots).reshape(1, -1)
        pIC50 = float(self.mod2.predict(X_base)[0])
        
        # Convert pIC50 (-log10(M)) to IC50 (nM): [M] = 10^-pIC50, [nM] = 10^(9 - pIC50)
        ic50_nM = float(np.power(10.0, 9.0 - pIC50))
        
        # Stage 2: Knockdown % at target concentration
        log_conc = np.log10(float(conc_nM) + 1e-6)
        X_mod3 = np.hstack([np.array([[pIC50]], dtype=np.float32), np.array([[log_conc]], dtype=np.float32), X_base])
        kd_pct = float(np.clip(self.mod3.predict(X_mod3)[0], 0.0, 100.0))
        
        # Compute empirical Hill slope
        # E = 100 * C^h / (IC50^h + C^h) => h = log(E / (100 - E)) / log(C / IC50)
        if 5.0 < kd_pct < 95.0 and abs(conc_nM - ic50_nM) > 1e-4:
            ratio_kd = kd_pct / (100.0 - kd_pct)
            ratio_conc = conc_nM / max(1e-6, ic50_nM)
            if ratio_conc > 0 and ratio_conc != 1.0:
                h = math_h = np.log(max(1e-4, ratio_kd)) / np.log(max(1e-4, ratio_conc))
                hill_slope = float(np.clip(math_h, 0.4, 2.8))
            else:
                hill_slope = 1.0
        else:
            hill_slope = 1.0

        return round(pIC50, 3), round(ic50_nM, 3), round(kd_pct, 2), round(hill_slope, 2)

    def predict_batch(
        self,
        batch_sense_slots: List[List[CanonicalNucSlot]],
        batch_anti_slots: List[List[CanonicalNucSlot]],
        concs_nM: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Batch prediction returning (pIC50_arr, ic50_nM_arr, kd_pct_arr).
        """
        X_base = self.featurizer.featurize_batch(batch_sense_slots, batch_anti_slots)
        pIC50_arr = self.mod2.predict(X_base).astype(np.float32)
        ic50_nM_arr = np.power(10.0, 9.0 - pIC50_arr).astype(np.float32)

        log_concs = np.log10(concs_nM + 1e-6).reshape(-1, 1).astype(np.float32)
        X_mod3 = np.hstack([pIC50_arr.reshape(-1, 1), log_concs, X_base])
        kd_pct_arr = np.clip(self.mod3.predict(X_mod3), 0.0, 100.0).astype(np.float32)

        return pIC50_arr, ic50_nM_arr, kd_pct_arr
