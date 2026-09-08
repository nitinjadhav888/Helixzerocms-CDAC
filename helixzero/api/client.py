"""
helixzero.api.client
====================
Unified High-Level Enterprise Client Interface for HelixZero.

Provides clean, single-line calls for:
- End-to-end multi-model potency prediction.
- 3D Argonaute-2 structural docking and catalytic alignment.
- Thermodynamic and immunological biophysical analysis.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Union
from pathlib import Path

from helixzero.ontology.tokenizer import parse_sirna_sequence, CanonicalNucSlot
from helixzero.api.schemas import (
    siRNACandidate,
    PredictionResult,
    Ago2DockingReport,
    BiophysicalReport
)
from helixzero.featurizers.biophysics_featurizer import BiophysicsFeaturizer
from helixzero.structural_docking.docking_engine import Ago2DockingEngine
from helixzero.models.ensemble import MetaStackingEnsemble


class HelixZero:
    """
    Unified Production Engine for Therapeutic Chemically Modified siRNA Design.
    """

    def __init__(self):
        self.biophysics_engine = BiophysicsFeaturizer()
        self.docking_engine = Ago2DockingEngine()
        self.ensemble = MetaStackingEnsemble()

    def predict(
        self,
        sense_seq: str,
        anti_seq: str,
        sense_mods: str = "",
        anti_mods: str = "",
        sense_positions: str = "",
        anti_positions: str = "",
        conc_nM: float = 10.0,
        target_gene: Optional[str] = None,
        candidate_id: str = "siRNA_candidate",
        include_docking: bool = True,
        include_biophysics: bool = True,
        export_docked_pdb: Optional[str] = None
    ) -> PredictionResult:
        """
        Runs complete predictive and mechanistic pipeline for a therapeutic candidate.
        """
        # 1. Parse canonical ontology
        s_slots = parse_sirna_sequence(sense_seq, sense_mods, sense_positions)
        a_slots = parse_sirna_sequence(anti_seq, anti_mods, anti_positions)

        # 2. Multi-Model Ensemble Potency Prediction
        (
            final_kd,
            pIC50,
            ic50_nM,
            hill_slope,
            pred_cb,
            pred_hier,
            pred_gnn,
            ci_95
        ) = self.ensemble.predict(s_slots, a_slots, conc_nM=conc_nM)

        # 3. Biophysical Analysis
        bio_report = None
        if include_biophysics:
            bio_report = self.biophysics_engine.analyze(sense_seq, anti_seq, s_slots, a_slots)

        # 4. 3D Argonaute-2 Structural Docking
        dock_report = None
        if include_docking:
            dock_report = self.docking_engine.dock_candidate(
                s_slots,
                a_slots,
                candidate_id=candidate_id,
                export_pdb_path=export_docked_pdb
            )

        return PredictionResult(
            candidate_id=candidate_id,
            target_gene=target_gene or "Unspecified",
            concentration_nM=conc_nM,
            predicted_pIC50=pIC50,
            predicted_ic50_nM=ic50_nM,
            predicted_knockdown_pct=final_kd,
            hill_slope=hill_slope,
            confidence_interval_95=ci_95,
            catboost_knockdown_pct=pred_cb,
            hierarchical_knockdown_pct=pred_hier,
            gnn_knockdown_pct=pred_gnn,
            ensemble_uncertainty=round(abs(ci_95[1] - ci_95[0]) / 3.92, 2),
            biophysics=bio_report,
            docking=dock_report
        )

    def dock(
        self,
        sense_seq: str,
        anti_seq: str,
        sense_mods: str = "",
        anti_mods: str = "",
        export_pdb_path: Optional[str] = None
    ) -> Ago2DockingReport:
        """
        Runs standalone 3D Argonaute-2 docking for a candidate.
        """
        s_slots = parse_sirna_sequence(sense_seq, sense_mods)
        a_slots = parse_sirna_sequence(anti_seq, anti_mods)
        return self.docking_engine.dock_candidate(s_slots, a_slots, export_pdb_path=export_pdb_path)

    def analyze_biophysics(
        self,
        sense_seq: str,
        anti_seq: str,
        sense_mods: str = "",
        anti_mods: str = ""
    ) -> BiophysicalReport:
        """
        Runs standalone thermodynamic and immunological analysis.
        """
        s_slots = parse_sirna_sequence(sense_seq, sense_mods)
        a_slots = parse_sirna_sequence(anti_seq, anti_mods)
        return self.biophysics_engine.analyze(sense_seq, anti_seq, s_slots, a_slots)
