"""
helixzero.api.schemas
====================
Enterprise Pydantic and Dataclass Schemas for HelixZero Production Engine.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class siRNACandidate:
    """Input payload for a therapeutic siRNA duplex candidate."""
    sense_seq: str
    anti_seq: str
    sense_mods: str = ""
    anti_mods: str = ""
    sense_positions: str = ""
    anti_positions: str = ""
    conc_nM: float = 10.0
    target_gene: Optional[str] = None
    cell_type: Optional[str] = None


@dataclass
class BiophysicalReport:
    """Thermodynamic and enzymatic stability metrics."""
    delta_G_duplex_kcal: float
    delta_G_open_kcal: float
    terminal_asymmetry_ddG: float
    gc_content_pct: float
    ps_linkages_count: int
    mod_density_pct: float
    serum_stability_index: float
    immunogenicity_risk: str  # LOW, MODERATE, HIGH
    tlr_motifs_detected: List[str] = field(default_factory=list)
    risc_loading_asymmetry: str = "FAVORS_ANTISENSE"  # FAVORS_ANTISENSE, BALANCED, FAVORS_SENSE


@dataclass
class Ago2DockingReport:
    """3D atomistic interaction metrics inside Human Argonaute-2 (PDB 4W5N)."""
    mid_anchor_distance_A: float       # Tyr529/Lys533 to guide 5'-phosphate (optimal: < 3.5 Å)
    piwi_cleavage_distance_A: float    # Asp597/Glu637 to g10-g11 scissile bond (optimal: < 4.5 Å)
    paz_anchor_distance_A: float       # PAZ pocket to guide 3' dinucleotide (optimal: < 4.0 Å)
    steric_clash_score: float          # Van der Waals overlap energy (lower is better, < 5.0 is clean)
    estimated_binding_dG_kcal: float   # Empirical Ago2-guide binding free energy estimate
    pocket_contacts_count: int         # Total hydrogen bonds and salt bridges in Ago2 active site
    docked_pdb_path: Optional[str] = None
    catalytic_alignment_status: str = "OPTIMAL" # OPTIMAL, MINOR_CLASH, INHIBITED_STERIC


@dataclass
class PredictionResult:
    """Consolidated predictive and mechanistic outputs from HelixZero."""
    candidate_id: str
    target_gene: str
    concentration_nM: float
    
    # Quantitative Potency Readouts
    predicted_pIC50: float
    predicted_ic50_nM: float
    predicted_knockdown_pct: float
    hill_slope: float
    confidence_interval_95: List[float] # [lower_pct, upper_pct]
    
    # Model Contributions (Multi-Model Ensemble)
    catboost_knockdown_pct: float
    hierarchical_knockdown_pct: float
    gnn_knockdown_pct: float
    ensemble_uncertainty: float
    
    # Mechanistic & Biophysical Modules
    biophysics: Optional[BiophysicalReport] = None
    docking: Optional[Ago2DockingReport] = None
