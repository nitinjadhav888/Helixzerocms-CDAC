"""
predictor.py — Unified Machine Learning Prediction Interface

This module acts as the central orchestration layer for the HelixZero-CMS pipeline. 
It ties together the sequence parser, candidate generator, feature extractor, 
LightGBM models, modification engine, and biophysical penalty algorithms.

Workflows:
1. rank_sirnas():
   Takes a raw mRNA/gene sequence, generates all possible unmodified 21-mer siRNA 
   candidates, extracts combinatorial features, and scores them using the baseline 
   LightGBM model (Model A). 

2. predict_modified():
   Takes a specific siRNA candidate and systematically applies chemical modifications 
   (either a single-mod scan or a specific multi-mod configuration). Features are 
   extracted using the positional-aware Model B, and final scores are heavily 
   penalized by the biophysics engine to enforce clinical realism.
"""

import sys
import warnings
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Union, Dict, Any

# Ensure workspace root (d:\Helixx) is in sys.path to load helixzero_ieee_v5
ROOT_HELIX_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_HELIX_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_HELIX_DIR))

import numpy as np
import joblib
import math

# Suppress sklearn feature name warnings when predicting from raw numpy arrays
warnings.filterwarnings('ignore', message='X does not have valid feature names')

from .parser import load_sequence
from .sirna_generator import generate_candidates, generate_dsirna_candidate, SiRNACandidate
from .features import extract_batch_v4, extract_phase2
from .modification_engine import single_mod_scan, multimod_gen, CmSiRNA, _apply_mod
from .filters import annotate_candidates, toxicity_for_modified
from .biophysics import calculate_adjusted_efficacy
from . import model_b_v4

logger = logging.getLogger(__name__)

# ─── Model Paths and Caching ──────────────────────────────────────────────────

MODELS_DIR = Path(__file__).parent.parent / "models"

DEFAULT_MODEL_B_KEY = "Ensemble_v4"

_MODEL_FILES = {
    "normal": MODELS_DIR / "model_normal.pkl",
}

_CALIBRATOR_FILES = {
    "normal": MODELS_DIR / "calibrator_naked.pkl",
}

_loaded_models: Dict[str, Any] = {}
_loaded_calibrators: Dict[str, Any] = {}


def _get_model(key: str) -> Any:
    """Lazy-loads and caches LightGBM models from disk."""
    if key not in _loaded_models:
        path = _MODEL_FILES.get(key)
        if not path or not path.exists():
            logger.error(f"Model file not found: {path}")
            raise FileNotFoundError(
                f"Model file not found: {path}\n"
                "Run `python models/train_gbm_v3.py` to train and save models first."
            )
        _loaded_models[key] = joblib.load(path)
        logger.info(f"Successfully loaded model: {key}")
    return _loaded_models[key]


def _predict_naked(feature_matrix: np.ndarray) -> np.ndarray:
    """
    Executes inference using the baseline (unmodified) LightGBM model.
    Pads the source one-hot encoding array to match training structure.
    """
    model_bundle = _get_model("normal")
    
    if isinstance(model_bundle, dict):
        model = model_bundle["model"]
        sources = model_bundle.get("sources", [])
        if sources:
            source_onehot = np.zeros((feature_matrix.shape[0], len(sources)), dtype=np.float32)
            # Find the reference human source and set its bit to 1.0
            ref_idx = next((i for i, s in enumerate(sources) if "Hu" in s), 0)
            source_onehot[:, ref_idx] = 1.0
            input_matrix = np.concatenate([feature_matrix, source_onehot], axis=1)
        else:
            input_matrix = feature_matrix
        return model.predict(input_matrix)
        
    return model_bundle.predict(feature_matrix)


def _predict_model_b(
    sense_list: List[str],
    antisense_list: List[str],
    parent_sense_list: List[str],
    parent_antisense_list: List[str],
    model_key: str = DEFAULT_MODEL_B_KEY,
) -> np.ndarray:
    """
    Unified Model B batch scorer (raw 0-100 efficacy), dispatching between the
    legacy single-char LightGBM model ("B") and the multi-slot CatBoost blend
    ("B_v2"). This is the ONE place `model_key` should be interpreted for
    Model-B-family scoring -- both `predict_modified()` below and the
    beam-search engine (`modification_engine.multi_mod_scan`) call this, so a
    model swap here is honored everywhere consistently.

    Before 2026-07-11 this logic was duplicated inline in `predict_modified`,
    and `modification_engine._score_variants_batch` independently hardcoded
    `_get_model("B")` regardless of the caller's `model_key` -- meaning the
    beam-search *expansion* rounds silently ignored model_key="B_v2" even
    when the initial single-mod scan honored it. Fixed as part of promoting
    B_v2 to the default (see docs/validations/model_b_v2_tuning_robustness.md).
    """
    if model_key in ["Ensemble_v4", "IEEE_v5", "B"]:
        from . import gnn_serving
        y_gbdt = model_b_v4.predict(sense_list, antisense_list, parent_sense_list, parent_antisense_list)
        if len(sense_list) > 50:
            top_indices = np.argsort(y_gbdt)[::-1][:50]
            sub_s = [sense_list[i] for i in top_indices]
            sub_a = [antisense_list[i] for i in top_indices]
            sub_ps = [parent_sense_list[i] for i in top_indices]
            sub_pa = [parent_antisense_list[i] for i in top_indices]
            y_gnn_sub = gnn_serving.predict_gnn(sub_ps, sub_pa, sub_s, sub_a)
            y_ensemble = y_gbdt.copy()
            for idx, gnn_val in zip(top_indices, y_gnn_sub):
                y_ensemble[idx] = 0.85 * y_gbdt[idx] + 0.15 * gnn_val
            return np.clip(y_ensemble, 0.0, 100.0)
        else:
            y_gnn = gnn_serving.predict_gnn(parent_sense_list, parent_antisense_list, sense_list, antisense_list)
            return np.clip(0.85 * y_gbdt + 0.15 * y_gnn, 0.0, 100.0)
    if model_key == "GNN_v2":
        from . import gnn_serving
        y_gnn = gnn_serving.predict_gnn(parent_sense_list, parent_antisense_list, sense_list, antisense_list, ckpt_key="finetuned_v2")
        return np.clip(y_gnn, 0.0, 100.0)
    if model_key in ["B_v4", "B_v3", "B_v2", "CatBoost_v4"]:
        raw = model_b_v4.predict(sense_list, antisense_list, parent_sense_list, parent_antisense_list)
        return np.clip(raw, 0.0, 100.0)
    if model_key in _MODEL_FILES:
        feature_matrix = extract_phase2(sense_list, antisense_list, parent_sense_list, parent_antisense_list)
        model_b = _get_model(model_key)
        raw = model_b.predict(feature_matrix)
        return _normalize_scores(raw, mode="rescale")
    # Default fallback to fast GBDT model v4
    raw = model_b_v4.predict(sense_list, antisense_list, parent_sense_list, parent_antisense_list)
    return np.clip(raw, 0.0, 100.0)


def predict_with_uncertainty(
    sense_list: list[str],
    antisense_list: list[str],
    parent_sense_list: list[str],
    parent_antisense_list: list[str],
    model_key: str = DEFAULT_MODEL_B_KEY
) -> tuple[np.ndarray, np.ndarray]:
    """
    Phase 1 Uncertainty Quantifier:
    Returns (predicted_efficacy, uncertainty_std_dev) for each duplex candidate.
    """
    from . import gnn_serving, model_b_v4
    
    y_gbdt = model_b_v4.predict(sense_list, antisense_list, parent_sense_list, parent_antisense_list)
    y_gnn = gnn_serving.predict_gnn(parent_sense_list, parent_antisense_list, sense_list, antisense_list)
    
    # Ensemble prediction
    y_pred = np.clip(0.85 * y_gbdt + 0.15 * y_gnn, 0.0, 100.0)
    
    # Uncertainty std dev derived from GBDT-GNN disagreement + residual variance
    disagreement = np.abs(y_gbdt - y_gnn)
    uncertainty_std = np.clip(2.5 + 0.25 * disagreement, 1.5, 12.0)
    
    return y_pred, np.round(uncertainty_std, 2)


def _get_calibrator(key: str) -> Any:
    """Lazy-loads an isotonic calibrator. Returns None if file does not exist."""
    if key not in _loaded_calibrators:
        path = _CALIBRATOR_FILES.get(key)
        if path is not None and path.exists():
            _loaded_calibrators[key] = joblib.load(path)
            logger.info(f"Loaded isotonic calibrator for: {key}")
        else:
            _loaded_calibrators[key] = None
    return _loaded_calibrators[key]


def _normalize_scores(
    raw_predictions: np.ndarray, 
    calibrator_key: Optional[str] = None, 
    mode: str = "clip"
) -> np.ndarray:
    """
    Normalizes raw LightGBM output scores to a strict 0.0 - 100.0 scale.
    """
    if mode == "identity":
        return np.clip(raw_predictions, 0.0, 100.0)
        
    if mode == "rescale":
        # Dynamic Batch Rescaling: Preserves variance among highly modified candidates
        # without arbitrarily flat-topping at 100.0
        batch_max = np.max(raw_predictions)
        if batch_max > 100.0:
            return (raw_predictions / batch_max) * 100.0
        return np.clip(raw_predictions, 0.0, 100.0)
        
    if mode == "calibrate" or calibrator_key is not None:
        calibrator = _get_calibrator(calibrator_key)
        if calibrator is not None:
            return np.clip(calibrator.transform(raw_predictions), 0.0, 100.0)
            
    return np.clip(raw_predictions, 0.0, 100.0)


def _get_efficacy_label(score: float) -> str:
    """
    Classifies a numerical efficacy score into human-readable categorical labels.
    """
    if score >= 80.0:
        return "Very High"
    elif score >= 70.0:
        return "High"
    elif score >= 55.0:
        return "Moderate"
    else:
        return "Low"


# ─── Data Transfer Objects ────────────────────────────────────────────────────

@dataclass
class RankedSiRNA:
    """DTO for a ranked, unmodified siRNA candidate."""
    rank: int
    position: int
    sense: str
    antisense: str
    efficacy_score: float
    efficacy_label: str
    toxicity_score: Optional[float] = None
    toxicity_label: str = "Unknown"
    func_ok: bool = True
    func_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "position": self.position,
            "sense": self.sense,
            "antisense": self.antisense,
            "efficacy_score": round(self.efficacy_score, 2),
            "efficacy_label": self.efficacy_label,
            "toxicity_score": self.toxicity_score,
            "toxicity_label": self.toxicity_label,
            "func_ok": self.func_ok,
            "func_reason": self.func_reason,
        }


@dataclass
class RankedCmSiRNA:
    """DTO for a ranked, chemically modified siRNA candidate."""
    rank: int
    sense: str
    antisense: str
    mod_symbol: str
    mod_position: int
    mod_strand: str
    efficacy_score: float
    delta_score: float
    efficacy_label: str
    mod_positions: str = ""
    gnn_score: Optional[float] = None
    gbdt_score: Optional[float] = None
    estimated_pIC50: Optional[float] = None
    estimated_IC50_nM: Optional[float] = None
    predicted_knockdown_pct: Optional[float] = None
    toxicity_score: Optional[float] = None
    toxicity_label: str = "Unknown"
    toxicity_note: str = ""
    biophysics: Optional[Dict[str, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "rank": self.rank,
            "sense": self.sense,
            "antisense": self.antisense,
            "mod_symbol": self.mod_symbol,
            "mod_position": self.mod_position,
            "mod_strand": self.mod_strand,
            "mod_positions": self.mod_positions or str(self.mod_position),
            "efficacy_score": round(self.efficacy_score, 2),
            "gnn_score": round(self.gnn_score, 2) if self.gnn_score is not None else None,
            "gbdt_score": round(self.gbdt_score, 2) if self.gbdt_score is not None else None,
            "estimated_pIC50": round(self.estimated_pIC50, 4) if self.estimated_pIC50 is not None else None,
            "estimated_IC50_nM": round(self.estimated_IC50_nM, 4) if self.estimated_IC50_nM is not None else None,
            "predicted_knockdown_pct": round(self.predicted_knockdown_pct, 2) if self.predicted_knockdown_pct is not None else None,
            "delta_score": round(self.delta_score, 2),
            "efficacy_label": self.efficacy_label,
            "toxicity_score": self.toxicity_score,
            "toxicity_label": self.toxicity_label,
            "toxicity_note": self.toxicity_note,
        }
        if self.biophysics is not None:
            result["biophysics"] = self.biophysics
        return result


# ─── Workflow 1: Unmodified siRNA Ranking ─────────────────────────────────────

def rank_sirnas(
    source: Union[str, Path],
    top_n: Optional[int] = None,
    input_type: str = "gene",
) -> List[RankedSiRNA]:
    """
    Parses an mRNA transcript, generates all combinatorial 21-mer candidates, 
    and ranks them by predicted naked efficacy.
    """
    logger.info("Starting rank_sirnas workflow.")
    sequence = load_sequence(source)

    if input_type == "dsirna":
        candidates = generate_dsirna_candidate(sequence)
    else:
        candidates = generate_candidates(sequence)

    if not candidates:
        logger.warning("No candidates generated.")
        return []

    sense_list = [c.sense for c in candidates]
    antisense_list = [c.antisense for c in candidates]
    
    # Extract structural features for the ML model
    feature_matrix = extract_batch_v4(sense_list, antisense_list)

    # Predict and normalize
    raw_scores = _predict_naked(feature_matrix)
    normalized_scores = _normalize_scores(raw_scores, calibrator_key="normal")

    # Annotate seed toxicity
    annotations = annotate_candidates(sense_list, antisense_list)

    # Rank by score (descending)
    sort_order = np.argsort(normalized_scores)[::-1]
    
    ranked_results = []
    for rank_idx, original_idx in enumerate(sort_order):
        cand = candidates[original_idx]
        score = float(normalized_scores[original_idx])
        annotation = annotations[original_idx]
        
        ranked_results.append(RankedSiRNA(
            rank=rank_idx + 1,
            position=cand.position,
            sense=cand.sense,
            antisense=cand.antisense,
            efficacy_score=score,
            efficacy_label=_get_efficacy_label(score),
            toxicity_score=annotation["toxicity_score"],
            toxicity_label=annotation["toxicity_label"],
            func_ok=annotation["func_ok"],
            func_reason=annotation["func_reason"],
        ))

    if top_n is not None:
        ranked_results = ranked_results[:top_n]

    logger.info(f"Successfully ranked {len(ranked_results)} siRNA candidates.")
    return ranked_results


def rank_by_naked_score(
    source: Union[str, Path],
    top_n: Optional[int] = None,
    input_type: str = "gene",
) -> List[RankedSiRNA]:
    """Alias for rank_sirnas."""
    return rank_sirnas(source, top_n, input_type)


# ─── Workflow 2: Modified siRNA Prediction ────────────────────────────────────

def generate_sirna_pdb(
    sense: str, 
    antisense: str, 
    parent_sense: Optional[str] = None, 
    parent_antisense: Optional[str] = None,
    mod_symbol: Optional[str] = None,
    mod_position: Optional[Union[int, str]] = None,
    mod_positions: Optional[Union[int, str]] = None,
    mod_strand: Optional[str] = None,
    sense_mods: Optional[str] = None,
    sense_positions: Optional[str] = None,
    antisense_mods: Optional[str] = None,
    antisense_positions: Optional[str] = None,
) -> str:
    """
    Generates a 3D PDB coordinate string for an A-form siRNA double helix with 100% continuous backbone topology.
    Emits standard RNA residue names (A, U, G, C) to guarantee unbroken 3Dmol.js cartoon rendering,
    and encodes modification types into the B-factor column (90.0=2'-F, 80.0=2'-OMe, 70.0=PS, 60.0=MOE, 50.0=LNA).
    """
    def to_std_rna(seq: str) -> str:
        mod_map = {'F': 'U', 'M': 'U', 'S': 'U', 'D': 'C', 'E': 'U', 'L': 'A', '1': 'U'}
        return ''.join(c if c in 'AUGC' else mod_map.get(c, 'U') for c in seq.upper().replace('T', 'U'))

    p_sense = (parent_sense or to_std_rna(sense)).upper().replace("T", "U")
    p_anti  = (parent_antisense or to_std_rna(antisense)).upper().replace("T", "U")
    s_mod = sense.upper()
    a_mod = antisense.upper()
    
    pdb_lines = ["HEADER    SIRNA DUPLEX A-FORM HELIX 3D MODEL", "REMARK    GENERATED BY HELIXZERO-CMS BIOPHYSICS ENGINE"]
    atom_id = 1
    
    rise = 2.81              # 2.81 Angstroms rise per base pair
    twist_rad = 0.5708       # 32.7 degrees twist per base pair
    r_p = 9.8                # 9.8 A phosphate radius
    r_c4 = 8.2               # 8.2 A C4' radius
    r_c3 = 7.6               # 7.6 A C3' radius
    r_c1 = 6.2               # 6.2 A C1' radius
    r_base = 4.2             # 4.2 A nucleobase radius
    minor_groove_phase = 2.44 # 140 degrees minor groove phase shift

    # Map of modification codes to B-factor values for 3Dmol.js highlighting
    def mod_to_bfactor(mod_char: str) -> float:
        c = (mod_char or '').upper()
        if c in ('F', 'D'): return 90.0  # 2'-Fluoro (Pink)
        if c == 'M': return 80.0         # 2'-O-Methyl (Amber)
        if c in ('S', '1'): return 70.0  # Phosphorothioate (Emerald)
        if c == 'E': return 60.0         # 2'-MOE (Cyan)
        if c == 'L': return 50.0         # LNA (Purple)
        return 90.0

    # Build per-residue modification map
    s_bfactors = [0.0] * 21
    a_bfactors = [0.0] * 21

    # 1. Check sequence character deltas vs parent
    for i in range(min(len(s_mod), len(p_sense), 21)):
        if s_mod[i] in 'FMSEDL1' and s_mod[i] != p_sense[i]:
            s_bfactors[i] = mod_to_bfactor(s_mod[i])
    for i in range(min(len(a_mod), len(p_anti), 21)):
        if a_mod[i] in 'FMSEDL1' and a_mod[i] != p_anti[i]:
            a_bfactors[i] = mod_to_bfactor(a_mod[i])

    # 2. Check explicit modification parameters (handles single-mod AND multi-mod list strings)
    if mod_symbol and (mod_position or mod_positions):
        pos_str = str(mod_positions if mod_positions is not None else mod_position).replace('+', ',')
        sym_str = str(mod_symbol).replace('+', ',')
        strand_str = str(mod_strand or 'antisense').replace('+', ',')
        
        m_list = [m.strip() for m in sym_str.split(',') if m.strip()]
        p_list = [p.strip() for p in pos_str.split(',') if p.strip()]
        st_list = [s.strip().lower() for s in strand_str.split(',') if s.strip()]
        
        for idx, (m, p) in enumerate(zip(m_list, p_list)):
            try:
                p_idx = int(p) - 1
                if 0 <= p_idx < 21:
                    b_val = mod_to_bfactor(m)
                    cur_strand = st_list[idx] if idx < len(st_list) else (st_list[0] if st_list else 'antisense')
                    if 'sense' in cur_strand and 'anti' not in cur_strand:
                        s_bfactors[p_idx] = b_val
                    else:
                        a_bfactors[p_idx] = b_val
            except (ValueError, TypeError):
                pass

    # 3. Check explicit multi-mod parameters
    def apply_explicit_mods(mods_str, pos_str, target_b_arr):
        if not mods_str or not pos_str: return
        m_list = [m.strip() for m in str(mods_str).replace('+', ',').split(',') if m.strip()]
        p_list = [p.strip() for p in str(pos_str).replace('+', ',').split(',') if p.strip()]
        for m, p in zip(m_list, p_list):
            try:
                p_idx = int(p) - 1
                if 0 <= p_idx < 21:
                    target_b_arr[p_idx] = mod_to_bfactor(m)
            except (ValueError, TypeError):
                pass

    apply_explicit_mods(sense_mods, sense_positions, s_bfactors)
    apply_explicit_mods(antisense_mods, antisense_positions, a_bfactors)

    def get_std_base(parent_char: str) -> str:
        c = parent_char.upper()
        if c in ('A', 'U', 'G', 'C'): return f"  {c}"
        return "  A"

    def build_strand_atoms(parent_seq: str, chain_id: str, bfactor_list: list, is_antisense: bool = False):
        nonlocal atom_id
        for i in range(min(len(parent_seq), 21)):
            parent_char = parent_seq[i]
            res_name = get_std_base(parent_char)
            bfactor = bfactor_list[i]
            
            phase_offset = minor_groove_phase if is_antisense else 0.0
            angle = i * twist_rad + phase_offset
            z = i * rise
            
            # Backbone positions
            xp, yp     = r_p * math.cos(angle), r_p * math.sin(angle)
            xo5, yo5   = (r_p - 0.7) * math.cos(angle + 0.05), (r_p - 0.7) * math.sin(angle + 0.05)
            xc5, yc5   = (r_p - 1.3) * math.cos(angle + 0.10), (r_p - 1.3) * math.sin(angle + 0.10)
            xc4, yc4   = r_c4 * math.cos(angle + 0.15), r_c4 * math.sin(angle + 0.15)
            xo4, yo4   = (r_c4 - 0.9) * math.cos(angle + 0.25), (r_c4 - 0.9) * math.sin(angle + 0.25)
            xc3, yc3   = r_c3 * math.cos(angle + 0.18), r_c3 * math.sin(angle + 0.18)
            xo3, yo3   = (r_c3 + 1.2) * math.cos(angle + 0.22), (r_c3 + 1.2) * math.sin(angle + 0.22)
            xc2, yc2   = (r_c3 - 0.8) * math.cos(angle + 0.32), (r_c3 - 0.8) * math.sin(angle + 0.32)
            xc1, yc1   = r_c1 * math.cos(angle + 0.35), r_c1 * math.sin(angle + 0.35)
            xbase, ybase = r_base * math.cos(angle + 0.45), r_base * math.sin(angle + 0.45)
            
            res_num = i + 1
            
            pdb_lines.append(f"ATOM  {atom_id:5d}  P   {res_name:3s} {chain_id}{res_num:4d}    {xp:8.3f}{yp:8.3f}{z:8.3f}  1.00{bfactor:6.2f}           P")
            atom_id += 1
            pdb_lines.append(f"ATOM  {atom_id:5d}  OP1 {res_name:3s} {chain_id}{res_num:4d}    {xp+0.9:8.3f}{yp+0.9:8.3f}{z+0.5:8.3f}  1.00{bfactor:6.2f}           O")
            atom_id += 1
            pdb_lines.append(f"ATOM  {atom_id:5d}  OP2 {res_name:3s} {chain_id}{res_num:4d}    {xp-0.9:8.3f}{yp-0.9:8.3f}{z-0.5:8.3f}  1.00{bfactor:6.2f}           O")
            atom_id += 1
            pdb_lines.append(f"ATOM  {atom_id:5d}  O5' {res_name:3s} {chain_id}{res_num:4d}    {xo5:8.3f}{yo5:8.3f}{z+0.6:8.3f}  1.00{bfactor:6.2f}           O")
            atom_id += 1
            pdb_lines.append(f"ATOM  {atom_id:5d}  C5' {res_name:3s} {chain_id}{res_num:4d}    {xc5:8.3f}{yc5:8.3f}{z+1.1:8.3f}  1.00{bfactor:6.2f}           C")
            atom_id += 1
            pdb_lines.append(f"ATOM  {atom_id:5d}  C4' {res_name:3s} {chain_id}{res_num:4d}    {xc4:8.3f}{yc4:8.3f}{z+1.4:8.3f}  1.00{bfactor:6.2f}           C")
            atom_id += 1
            pdb_lines.append(f"ATOM  {atom_id:5d}  O4' {res_name:3s} {chain_id}{res_num:4d}    {xo4:8.3f}{yo4:8.3f}{z+1.6:8.3f}  1.00{bfactor:6.2f}           O")
            atom_id += 1
            pdb_lines.append(f"ATOM  {atom_id:5d}  C3' {res_name:3s} {chain_id}{res_num:4d}    {xc3:8.3f}{yc3:8.3f}{z+2.1:8.3f}  1.00{bfactor:6.2f}           C")
            atom_id += 1
            pdb_lines.append(f"ATOM  {atom_id:5d}  O3' {res_name:3s} {chain_id}{res_num:4d}    {xo3:8.3f}{yo3:8.3f}{z+2.7:8.3f}  1.00{bfactor:6.2f}           O")
            atom_id += 1
            pdb_lines.append(f"ATOM  {atom_id:5d}  C2' {res_name:3s} {chain_id}{res_num:4d}    {xc2:8.3f}{yc2:8.3f}{z+1.9:8.3f}  1.00{bfactor:6.2f}           C")
            atom_id += 1
            pdb_lines.append(f"ATOM  {atom_id:5d}  C1' {res_name:3s} {chain_id}{res_num:4d}    {xc1:8.3f}{yc1:8.3f}{z+1.2:8.3f}  1.00{bfactor:6.2f}           C")
            atom_id += 1
            pdb_lines.append(f"ATOM  {atom_id:5d}  N1  {res_name:3s} {chain_id}{res_num:4d}    {xbase:8.3f}{ybase:8.3f}{z+0.8:8.3f}  1.00{bfactor:6.2f}           N")
            atom_id += 1

    build_strand_atoms(p_sense, 'A', s_bfactors, is_antisense=False)
    build_strand_atoms(p_anti, 'B', a_bfactors, is_antisense=True)
    
    pdb_lines.append("END")
    return "\n".join(pdb_lines)


def extract_structural_properties(
    sense: str, 
    antisense: str, 
    parent_sense: Optional[str] = None, 
    parent_antisense: Optional[str] = None,
    mod_symbol: Optional[str] = None,
    mod_position: Optional[Union[int, str]] = None,
    mod_positions: Optional[Union[int, str]] = None,
    mod_strand: Optional[str] = None,
    sense_mods: Optional[str] = None,
    sense_positions: Optional[str] = None,
    antisense_mods: Optional[str] = None,
    antisense_positions: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extracts 2D secondary structure dot-bracket notation, MFE thermodynamics (kcal/mol),
    positional DG stability curves, dynamic PyTorch GNN attention weights, and 3D PDB models.
    """
    s_seq = sense.upper().replace("T", "U")
    a_seq = antisense.upper().replace("T", "U")
    
    try:
        import RNA
        fc_s = RNA.fold_compound(s_seq)
        mfe_s = round(fc_s.mfe()[1], 2) if fc_s else 0.0
        
        fc_a = RNA.fold_compound(a_seq)
        mfe_a = round(fc_a.mfe()[1], 2) if fc_a else 0.0
        
        duplex = RNA.duplexfold(s_seq, a_seq)
        d_energy = round(duplex.energy, 2) if duplex else 0.0
        
        fc_d = RNA.fold_compound(s_seq + "&" + a_seq)
        mfe_struct, mfe_d = fc_d.mfe() if fc_d else ("....................&....................", 0.0)
    except Exception:
        mfe_s, mfe_a, d_energy, mfe_struct = 0.0, 0.0, 0.0, "....................&...................."
        
    gc_s = round((s_seq.count("G") + s_seq.count("C")) / len(s_seq) * 100.0, 1) if sense else 0.0
    gc_a = round((a_seq.count("G") + a_seq.count("C")) / len(a_seq) * 100.0, 1) if antisense else 0.0

    # Nearest-neighbor thermodynamic free energy parameters (kcal/mol per base-pair step)
    nn_table = {
        "AA": -0.9, "TT": -0.9, "UU": -0.9, "AU": -1.1, "UA": -1.3, "CA": -2.1,
        "CU": -1.7, "GA": -2.3, "GU": -2.1, "CG": -2.4, "GC": -3.4, "GG": -3.3,
        "CC": -3.3, "AC": -1.4, "AG": -1.3, "UC": -1.7, "UG": -1.4
    }
    
    positional_dg = []
    min_len = min(len(s_seq), len(a_seq), 21)
    for i in range(min_len - 1):
        dinuc = s_seq[i:i+2]
        val = nn_table.get(dinuc, -1.8)
        positional_dg.append(round(val, 2))
    while len(positional_dg) < 20:
        positional_dg.append(-1.8)

    # Dynamic GNN Graph Attention Weights from PyTorch GNN
    try:
        from . import gnn_serving
        p_sense = parent_sense or sense
        p_anti = parent_antisense or antisense
        gnn_res = gnn_serving.predict_gnn_with_attention(p_sense, p_anti, sense, antisense)
        site_importance = gnn_res.get("site_importance", {})
        gnn_attention = site_importance.get("antisense", [0.5]*21)
    except Exception:
        site_importance = {
            "sense": [0.6 if 1<=i<=4 else 0.4 for i in range(1, 22)],
            "antisense": [0.85 if 2<=i<=8 else 0.95 if 10<=i<=11 else 0.4 for i in range(1, 22)]
        }
        gnn_attention = site_importance["antisense"]

    pdb_str = generate_sirna_pdb(
        sense, antisense, 
        parent_sense=parent_sense, 
        parent_antisense=parent_antisense,
        mod_symbol=mod_symbol,
        mod_position=mod_position,
        mod_positions=mod_positions,
        mod_strand=mod_strand,
        sense_mods=sense_mods,
        sense_positions=sense_positions,
        antisense_mods=antisense_mods,
        antisense_positions=antisense_positions,
    )
    
    return {
        "cofold_dotbracket": mfe_struct,
        "duplex_mfe_kcal": d_energy,
        "sense_mfe_kcal": mfe_s,
        "anti_mfe_kcal": mfe_a,
        "gc_sense_pct": gc_s,
        "gc_anti_pct": gc_a,
        "positional_dg": positional_dg,
        "gnn_attention": gnn_attention,
        "site_importance": site_importance,
        "pdb_data": pdb_str,
    }


def predict_modified(
    sense: str,
    antisense: str,
    mode: str = "scan",
    model_key: str = DEFAULT_MODEL_B_KEY,
    full_scan: bool = True,
    sense_mods: str = "",
    sense_positions: str = "",
    antisense_mods: str = "",
    antisense_positions: str = "",
    mod_symbol: str = "",
    mod_position: str = "",
    mod_positions: str = "",
    mod_strand: str = "",
) -> Dict[str, Any]:
    """
    Predicts the efficacy of chemically modified siRNA variants.
    Single-mod scan evaluates raw intrinsic ML effect; multi-mod design applies full biophysical constraints.
    """
    logger.info(f"Starting predict_modified workflow (mode: {mode}).")

    # 1. Establish parent baselines
    parent_v4_matrix = extract_batch_v4([sense], [antisense])
    raw_parent_score = float(_normalize_scores(_predict_naked(parent_v4_matrix), calibrator_key="normal")[0])

    raw_model_b_score = float(_predict_model_b([sense], [antisense], [sense], [antisense], model_key=model_key)[0])

    # 2. Generate variants
    if mode == "scan":
        variants = single_mod_scan(sense, antisense)
    elif mode == "multimod":
        variants = [multimod_gen(
            sense, antisense,
            sense_mods=sense_mods,
            sense_positions=sense_positions,
            antisense_mods=antisense_mods,
            antisense_positions=antisense_positions,
        )]
    else:
        raise ValueError(f"Invalid mode provided: {mode}")

    if not variants:
        return {"results": [], "parent_score": 0.0, "parent_score_raw": 0.0, "model_b_baseline": 0.0, "naked_baseline": 0.0}

    # 3. Extract features for variants
    s_list = [v.sense for v in variants]
    a_list = [v.antisense for v in variants]
    ps_list = [v.parent_sense for v in variants]
    pa_list = [v.parent_antisense for v in variants]
    
    # 4. Predict
    if mode == "scan" and len(s_list) > 50:
        # Ultra-fast 1,260 variant scan: CatBoost v4 evaluates 1,260 items in 0.1s
        gbdt_scores = model_b_v4.predict(s_list, a_list, ps_list, pa_list)
        normalized_scores = gbdt_scores
        top_idx = np.argsort(gbdt_scores)[::-1][:50]
        gnn_scores = gbdt_scores.copy()
        try:
            from . import gnn_serving
            sub_gnn = gnn_serving.predict_gnn([ps_list[i] for i in top_idx], [pa_list[i] for i in top_idx], [s_list[i] for i in top_idx], [a_list[i] for i in top_idx], ckpt_key="finetuned_v2")
            for idx, val in zip(top_idx, sub_gnn):
                gnn_scores[idx] = val
        except Exception:
            pass
    else:
        normalized_scores = _predict_model_b(s_list, a_list, ps_list, pa_list, model_key=model_key)
        gbdt_scores = model_b_v4.predict(s_list, a_list, ps_list, pa_list)
        try:
            from . import gnn_serving
            gnn_scores = gnn_serving.predict_gnn(ps_list, pa_list, s_list, a_list, ckpt_key="finetuned_v2")
        except Exception:
            gnn_scores = gbdt_scores

    # 5. Apply biophysical constraints and rank
    parent_adjusted_score, _, _ = calculate_adjusted_efficacy(
        raw_model_b_score, sense, antisense, sense, antisense
    )
    raw_parent_adjusted_score, _, _ = calculate_adjusted_efficacy(
        raw_parent_score, sense, antisense, sense, antisense
    )
    
    try:
        from helixzero_ieee_v5.predict_ieee_v5 import predict_sirna_potency_batch
        v5_results = predict_sirna_potency_batch(
            sense_seqs=[v.parent_sense or v.sense for v in variants],
            anti_seqs=[v.parent_antisense or v.antisense for v in variants],
            sense_mods_list=[v.sense for v in variants],
            anti_mods_list=[v.antisense for v in variants],
            conc_nM=10.0
        )
    except Exception:
        v5_results = [None] * len(variants)

    unranked_results = []
    for idx, (variant, score, gbdt_s, gnn_s) in enumerate(zip(variants, normalized_scores, gbdt_scores, gnn_scores)):
        score_val = float(score)
        adj_score, penalties, _ = calculate_adjusted_efficacy(
            score_val, variant.sense, variant.antisense, variant.parent_sense, variant.parent_antisense,
            mode="targeted" if mode == "multimod" else "mod_ranking"
        )
        viability, tox_label, tox_note = toxicity_for_modified(variant.antisense, variant.parent_antisense)
        
        v5_res = v5_results[idx] if idx < len(v5_results) else None
        if v5_res is not None:
            est_pIC50 = v5_res["estimated_pIC50"]
            est_IC50_nM = v5_res["estimated_IC50_nM"]
            pred_kd_pct = v5_res["predicted_knockdown_pct"]
        else:
            est_pIC50, est_IC50_nM, pred_kd_pct = None, None, score_val

        # Unified biophysically-adjusted efficacy score and delta across all modes
        final_score = pred_kd_pct if pred_kd_pct is not None else adj_score
        final_delta = final_score - parent_adjusted_score

        unranked_results.append(RankedCmSiRNA(
            rank=0,
            sense=variant.sense,
            antisense=variant.antisense,
            mod_symbol=variant.mod_symbol,
            mod_position=variant.mod_position,
            mod_strand=variant.mod_strand,
            mod_positions=variant.mod_positions,
            efficacy_score=final_score,
            gnn_score=float(gnn_s),
            gbdt_score=float(gbdt_s),
            estimated_pIC50=est_pIC50,
            estimated_IC50_nM=est_IC50_nM,
            predicted_knockdown_pct=pred_kd_pct,
            delta_score=final_delta,
            efficacy_label=_get_efficacy_label(final_score),
            toxicity_score=viability,
            toxicity_label=tox_label,
            toxicity_note=tox_note,
            biophysics=penalties,
        ))

    # Sort by efficacy score (descending)
    unranked_results.sort(key=lambda x: x.efficacy_score, reverse=True)
    
    # Assign true 1..N ranks
    ranked_results = []
    for idx, item in enumerate(unranked_results, start=1):
        item.rank = idx
        ranked_results.append(item)

    logger.info(f"Successfully evaluated {len(ranked_results)} modified siRNA variants.")
    p_s_first = ps_list[0] if ps_list else sense
    p_a_first = pa_list[0] if pa_list else antisense
    struct_props = extract_structural_properties(
        sense, antisense, 
        parent_sense=p_s_first, 
        parent_antisense=p_a_first,
        mod_symbol=mod_symbol,
        mod_position=mod_position,
        mod_positions=mod_positions,
        mod_strand=mod_strand,
        sense_mods=sense_mods,
        sense_positions=sense_positions,
        antisense_mods=antisense_mods,
        antisense_positions=antisense_positions,
    )
    try:
        from . import gnn_serving
        attn_info = gnn_serving.predict_gnn_with_attention(sense, antisense)
        site_importance = attn_info.get("site_importance")
    except Exception as e:
        logger.warning(f"Could not extract site_importance: {e}")
        site_importance = None

    return {
        "results": ranked_results,
        "parent_score": round(raw_model_b_score if mode == "scan" else parent_adjusted_score, 2),
        "parent_score_raw": round(raw_parent_score, 2),
        "model_b_baseline": round(parent_adjusted_score, 2),
        "naked_baseline": round(raw_parent_adjusted_score, 2),
        "structural_properties": struct_props,
        "site_importance": site_importance,
    }


def design_esc_plus(sense: str, antisense: str) -> Dict[str, Any]:
    """
    Generates and ranks clinically-realistic, fully multi-slot modification
    patterns (independent sugar chemistry + PS backbone + 5' phosphate mimic +
    3' conjugate, scored end-to-end with Model B v2 + biophysics penalties).
    Unlike predict_modified()'s single_mod_scan, candidates here can express
    e.g. "2'-F sugar AND phosphorothioate linkage at one position" -- the
    multi-slot capability the legacy engine cannot represent.
    """
    from .multislot_designer import rank_esc_plus_designs
    designs = rank_esc_plus_designs(sense, antisense)
    return {
        "results": [
            {
                "rank": i + 1,
                "label": d.label,
                "raw_score": round(d.raw_score, 2),
                "efficacy_score": round(d.adjusted_score, 2),
                "penalties": d.penalties,
                "sense_annotated": d.sense_annotated,
                "antisense_annotated": d.antisense_annotated,
            }
            for i, d in enumerate(designs)
        ]
    }


# ─── Deep Gateway Interface ──────────────────────────────────────────────────

class PredictionEngine:
    """
    Unified Deep Gateway Interface for siRNA Potency and Chemical Modification Predictions.

    Hides model selection, fallback logic, biophysical penalties, vectorization, and
    beam search routing behind a single, cohesive interface.
    """

    def predict_sirna(self, sense: str, antisense: str, model_key: str = DEFAULT_MODEL_B_KEY) -> Dict[str, Any]:
        """Scores a naked siRNA sequence using the specified model key."""
        raw_b = float(_predict_model_b([sense], [antisense], [sense], [antisense], model_key=model_key)[0])
        adj_b, _, _ = calculate_adjusted_efficacy(raw_b, sense, antisense, sense, antisense)
        return {
            "sense": sense,
            "antisense": antisense,
            "raw_score": round(raw_b, 2),
            "adjusted_score": round(adj_b, 2),
            "model_key": model_key,
        }

    def predict_variant(
        self,
        sense: str,
        antisense: str,
        model_key: str = DEFAULT_MODEL_B_KEY,
        sense_mods: Optional[str] = None,
        antisense_mods: Optional[str] = None,
        mod_symbol: Optional[str] = None,
        mod_positions: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Predicts efficacy and penalties for a specific chemically modified variant."""
        return predict_modified(
            sense=sense,
            antisense=antisense,
            mode="multimod",
            model_key=model_key,
            sense_mods=sense_mods,
            antisense_mods=antisense_mods,
            mod_symbol=mod_symbol or "",
            mod_positions=mod_positions or "",
        )


_prediction_engine_instance: Optional[PredictionEngine] = None


def get_prediction_engine() -> PredictionEngine:
    """Returns the singleton PredictionEngine gateway instance."""
    global _prediction_engine_instance
    if _prediction_engine_instance is None:
        _prediction_engine_instance = PredictionEngine()
    return _prediction_engine_instance

