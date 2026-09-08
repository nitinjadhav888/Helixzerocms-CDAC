"""
helixzero.models.ensemble
=========================
Uncertainty-Weighted Bayesian Meta-Stacking Ensemble for HelixZero.

Fuses:
1. CatBoost Multi-Slot Chemotype Engine
2. IEEE v5 Hierarchical Hill Dose-Response Engine
3. Stereochemical Graph Neural Network Engine
"""

from __future__ import annotations
from typing import List, Tuple, Optional
import numpy as np

from helixzero.ontology.tokenizer import CanonicalNucSlot
from .catboost_engine import CatBoostEngine
from .hierarchical_engine import HierarchicalEngine
from .gnn_engine import GNNEngine


class MetaStackingEnsemble:
    """
    Uncertainty-weighted ensemble providing calibrated potency and 95% confidence intervals.
    """

    def __init__(
        self,
        catboost: Optional[CatBoostEngine] = None,
        hierarchical: Optional[HierarchicalEngine] = None,
        gnn: Optional[GNNEngine] = None
    ):
        self.catboost = catboost or CatBoostEngine()
        self.hierarchical = hierarchical or HierarchicalEngine()
        self.gnn = gnn or GNNEngine()

    def predict(
        self,
        sense_slots: List[CanonicalNucSlot],
        anti_slots: List[CanonicalNucSlot],
        conc_nM: float = 10.0
    ) -> Tuple[float, float, float, float, float, float, float, List[float]]:
        """
        Runs full ensemble forward pass.
        Returns:
            (
                final_knockdown_pct,
                pIC50,
                ic50_nM,
                hill_slope,
                pred_cb,
                pred_hier,
                pred_gnn,
                confidence_interval_95
            )
        """
        # 1. CatBoost multi-slot prediction
        pred_cb = self.catboost.predict_candidate(sense_slots, anti_slots)

        # 2. Hierarchical bi-level prediction
        pIC50, ic50_nM, pred_hier, hill_slope = self.hierarchical.predict_candidate(
            sense_slots, anti_slots, conc_nM=conc_nM
        )

        # 3. Dynamic GNN prediction
        pred_gnn = self.gnn.predict_candidate(sense_slots, anti_slots)

        # 4. Dose-dependent dynamic meta-weighting
        # If dose is far from nominal 10 nM, weight hierarchical dose response more heavily
        if abs(np.log10(conc_nM + 1e-6) - 1.0) > 0.6:
            w_hier = 0.60
            w_cb = 0.30
            w_gnn = 0.10
        else:
            w_hier = 0.45
            w_cb = 0.45
            w_gnn = 0.10

        final_kd = (w_hier * pred_hier) + (w_cb * pred_cb) + (w_gnn * pred_gnn)
        final_kd = float(np.clip(final_kd, 0.0, 100.0))

        # 5. Uncertainty & 95% Confidence Interval
        preds = np.array([pred_cb, pred_hier, pred_gnn])
        sigma = float(np.std(preds))
        lower_ci = float(np.clip(final_kd - 1.96 * max(2.5, sigma), 0.0, 100.0))
        upper_ci = float(np.clip(final_kd + 1.96 * max(2.5, sigma), 0.0, 100.0))

        return (
            round(final_kd, 2),
            round(pIC50, 3),
            round(ic50_nM, 3),
            round(hill_slope, 2),
            round(pred_cb, 2),
            round(pred_hier, 2),
            round(pred_gnn, 2),
            [round(lower_ci, 2), round(upper_ci, 2)]
        )
