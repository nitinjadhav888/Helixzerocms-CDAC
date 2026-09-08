"""
HelixZero: Enterprise AI Platform for Modified siRNA Therapeutics Discovery.
=============================================================================
Unified suite combining:
- Multi-Slot Chemotype Gradient Boosted Engines
- Hierarchical Bi-Level Dose-Response Mechanics (pIC50 -> Hill Curve)
- Stereochemical Molecular Graph Neural Networks (GNN)
- Real 3D Human Argonaute-2 (hAgo2 PDB 4W5N) Structural Docking & Steric Clash Modeling
- Thermodynamic & Immunological Biophysical Optimization
"""

from helixzero.api.client import HelixZero
from helixzero.api.schemas import (
    siRNACandidate,
    PredictionResult,
    Ago2DockingReport,
    BiophysicalReport
)
from helixzero.ontology.tokenizer import parse_sirna_sequence, CanonicalNucSlot

# Primary singleton instance for quick usage
_default_engine = None

def get_engine() -> HelixZero:
    global _default_engine
    if _default_engine is None:
        _default_engine = HelixZero()
    return _default_engine

def predict(
    sense_seq: str,
    anti_seq: str,
    sense_mods: str = "",
    anti_mods: str = "",
    sense_positions: str = "",
    anti_positions: str = "",
    conc_nM: float = 10.0,
    target_gene: str = "Target",
    candidate_id: str = "siRNA_candidate",
    include_docking: bool = True,
    include_biophysics: bool = True,
    export_docked_pdb: str = None,
    **kwargs
) -> PredictionResult:
    """Convenience top-level prediction function."""
    return get_engine().predict(
        sense_seq=sense_seq,
        anti_seq=anti_seq,
        sense_mods=sense_mods,
        anti_mods=anti_mods,
        sense_positions=sense_positions,
        anti_positions=anti_positions,
        conc_nM=conc_nM,
        target_gene=target_gene,
        candidate_id=candidate_id,
        include_docking=include_docking,
        include_biophysics=include_biophysics,
        export_docked_pdb=export_docked_pdb
    )

def dock(
    sense_seq: str,
    anti_seq: str,
    sense_mods: str = "",
    anti_mods: str = "",
    export_pdb_path: str = None,
    **kwargs
) -> Ago2DockingReport:
    """Convenience top-level 3D Ago2 docking function."""
    return get_engine().dock(
        sense_seq=sense_seq,
        anti_seq=anti_seq,
        sense_mods=sense_mods,
        anti_mods=anti_mods,
        export_pdb_path=export_pdb_path
    )

__all__ = [
    "HelixZero",
    "get_engine",
    "predict",
    "dock",
    "parse_sirna_sequence",
    "CanonicalNucSlot",
    "siRNACandidate",
    "PredictionResult",
    "Ago2DockingReport",
    "BiophysicalReport",
]
