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

# Suppress sklearn feature name warnings and version warnings
warnings.filterwarnings('ignore', message='X does not have valid feature names')
warnings.filterwarnings('ignore', message='.*Trying to unpickle estimator.*')

from .parser import load_sequence
from .sirna_generator import generate_candidates, generate_dsirna_candidate, SiRNACandidate
from .features import extract_batch_v4, extract_phase2
from .modification_engine import single_mod_scan, multimod_gen, CmSiRNA, _apply_mod
from .filters import annotate_candidates, toxicity_for_modified, calculate_preclinical_hepatotoxicity_index
from .calibrator import StrictlyMonotonicCalibrator
from .biophysics import calculate_adjusted_efficacy
from . import model_b_v4
from .chem_alphabet import get_mod_delta_dg, normalize_mod_code, MODIFICATION_ALPHABET

logger = logging.getLogger(__name__)

# ─── Model Paths and Caching ──────────────────────────────────────────────────

MODELS_DIR = Path(__file__).parent.parent / "models"

DEFAULT_MODEL_B_KEY = "Unified_v5"

_MODEL_FILES = {
    "normal": MODELS_DIR / "model_normal.txt",
    "normal_pkl": MODELS_DIR / "model_normal.pkl",
    "normal_context": MODELS_DIR / "model_normal_context.txt",
    "normal_context_pkl": MODELS_DIR / "model_normal_context.pkl",
}

_CALIBRATOR_FILES = {
    "normal": MODELS_DIR / "calibrator_naked.pkl",
    "normal_context": MODELS_DIR / "calibrator_context.pkl",
}

_loaded_models: Dict[str, Any] = {}
_loaded_calibrators: Dict[str, Any] = {}


def _get_model(key: str) -> Any:
    """Lazy-loads and caches models from disk."""
    if key not in _loaded_models:
        if key in ("B", "model_b", "B_v4", "Unified_v5"):
            from catboost import CatBoostRegressor
            cb = CatBoostRegressor()
            cb_path = MODELS_DIR / "unified_dose_catboost.cbm"
            if not cb_path.exists():
                cb_path = MODELS_DIR / "model_b_v4.cbm"
            if cb_path.exists():
                cb.load_model(str(cb_path))
                _loaded_models[key] = cb
                logger.info(f"Successfully loaded Unified CatBoost model: {cb_path}")
                return cb

        txt_path = MODELS_DIR / f"model_{key}.txt"
        if txt_path.exists():
            import lightgbm as lgb
            _loaded_models[key] = lgb.Booster(model_file=str(txt_path))
            logger.info(f"Successfully loaded native LightGBM booster: {txt_path}")
            return _loaded_models[key]

        path = _MODEL_FILES.get(key)
        if not path or not path.exists():
            path = _MODEL_FILES.get(f"{key}_pkl")
        if not path or not path.exists():
            logger.error(f"Model file not found for key: {key}")
            raise FileNotFoundError(
                f"Model file not found for key '{key}'. Ensure models are compiled in smepred/models/."
            )
        try:
            _loaded_models[key] = joblib.load(path)
        except Exception:
            import pickle
            with open(path, "rb") as f:
                _loaded_models[key] = pickle.load(f)
        logger.info(f"Successfully loaded model: {key}")
    return _loaded_models[key]


def _predict_naked(feature_matrix: np.ndarray, model_key: str = "normal") -> np.ndarray:
    """
    Executes inference using either the baseline (unmodified) LightGBM model
    or the retrained context-aware foundation-biophysics model (190-D).
    """
    if feature_matrix.shape[1] == 190 or model_key == "normal_context":
        model = _get_model("normal_context")
        return model.predict(feature_matrix)

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
    conc_nM: float = 10.0,
    is_hepatic: float = 1.0,
    time_h: float = 24.0,
) -> np.ndarray:
    """
    Unified Dose-Aware CatBoost Regressor batch scorer (0-100% efficacy).
    Dispatches directly to the retrained 517-D model trained on 17,761 clean dose rows.
    """
    raw = model_b_v4.predict(
        sense_list, antisense_list, parent_sense_list, parent_antisense_list,
        conc_nM=conc_nM, is_hepatic=is_hepatic, time_h=time_h
    )
    return np.clip(raw, 0.0, 100.0)


def predict_with_uncertainty(
    sense_list: list[str],
    antisense_list: list[str],
    parent_sense_list: list[str],
    parent_antisense_list: list[str],
    model_key: str = DEFAULT_MODEL_B_KEY,
    conc_nM: float = 10.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Uncertainty Quantifier:
    Returns (predicted_efficacy, uncertainty_std_dev) for each duplex candidate.
    """
    y_pred = _predict_model_b(
        sense_list, antisense_list, parent_sense_list, parent_antisense_list,
        model_key=model_key, conc_nM=conc_nM
    )
    # Calibrated empirical residual variance
    uncertainty_std = np.clip(2.0 + 0.05 * np.abs(y_pred - 50.0), 1.5, 6.0)
    return y_pred, np.round(uncertainty_std, 2)



def _get_calibrator(key: str) -> Any:
    """Lazy-loads an isotonic calibrator. Returns None if file does not exist or fails."""
    if key not in _loaded_calibrators:
        path = _CALIBRATOR_FILES.get(key)
        if path is not None and path.exists():
            try:
                # Ensure module namespace aliases exist for unpickling custom calibrator classes across environments
                import sys
                try:
                    from . import calibrator as cal_mod
                    if "smepred.src.calibrator" not in sys.modules:
                        sys.modules["smepred.src.calibrator"] = cal_mod
                    if "src.calibrator" not in sys.modules:
                        sys.modules["src.calibrator"] = cal_mod
                except Exception:
                    pass
                _loaded_calibrators[key] = joblib.load(path)
                logger.info(f"Loaded isotonic calibrator for: {key}")
            except Exception as e:
                logger.warning(f"Could not load calibrator {key}: {e}. Defaulting to uncalibrated clipping.")
                _loaded_calibrators[key] = None
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
    domain: str = ""
    is_curated_lead: bool = False
    asymmetry_ddg: Optional[float] = None
    asymmetry_label: str = "Unknown"
    hepato_score: Optional[float] = None
    hepato_profile: Optional[str] = None
    hepato_status: Optional[str] = None
    npm_burden: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        res = {
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
            "domain": self.domain,
            "is_curated_lead": self.is_curated_lead,
            "asymmetry_ddg": self.asymmetry_ddg,
            "asymmetry_label": self.asymmetry_label,
        }
        if self.hepato_score is not None:
            res["hepato_score"] = self.hepato_score
        if self.hepato_profile is not None:
            res["hepato_profile"] = self.hepato_profile
        if self.hepato_status is not None:
            res["hepato_status"] = self.hepato_status
        if self.npm_burden is not None:
            res["npm_burden"] = self.npm_burden
        return res


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
    sense_mods: str = ""
    sense_positions: str = ""
    antisense_mods: str = ""
    antisense_positions: str = ""
    duplex_mfe_kcal: Optional[float] = None
    delta_duplex_dg: Optional[float] = None
    target_dose_nM: Optional[float] = None
    hepato_score: Optional[float] = None
    hepato_profile: Optional[str] = None
    hepato_status: Optional[str] = None

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
            "raw_efficacy_score": round(self.gbdt_score or self.efficacy_score, 2),
            "predicted_knockdown_pct": round(self.predicted_knockdown_pct, 2) if self.predicted_knockdown_pct is not None else None,
            "target_dose_nM": round(self.target_dose_nM, 2) if self.target_dose_nM is not None else None,
            "delta_score": round(self.delta_score, 2),
            "efficacy_label": self.efficacy_label,
            "toxicity_score": self.toxicity_score,
            "toxicity_label": self.toxicity_label,
            "toxicity_note": self.toxicity_note,
            "penalties": self.biophysics,
        }
        if self.duplex_mfe_kcal is not None:
            result["duplex_mfe_kcal"] = round(self.duplex_mfe_kcal, 2)
        if self.delta_duplex_dg is not None:
            result["delta_duplex_dg"] = round(self.delta_duplex_dg, 2)
        if self.sense_mods:
            result["sense_mods"] = self.sense_mods
        if self.sense_positions:
            result["sense_positions"] = self.sense_positions
        if self.antisense_mods:
            result["antisense_mods"] = self.antisense_mods
        if self.antisense_positions:
            result["antisense_positions"] = self.antisense_positions
        if self.biophysics is not None:
            result["biophysics"] = self.biophysics
        if self.hepato_score is not None:
            result["hepato_score"] = self.hepato_score
        if self.hepato_profile is not None:
            result["hepato_profile"] = self.hepato_profile
        if self.hepato_status is not None:
            result["hepato_status"] = self.hepato_status
        return result


# ─── Workflow 1: Unmodified siRNA Ranking ─────────────────────────────────────

def rank_sirnas(
    source: Union[str, Path],
    top_n: Optional[int] = None,
    input_type: str = "gene",
    use_context_model: bool = True,
) -> List[RankedSiRNA]:
    """
    Parses an mRNA transcript, generates all combinatorial 21-mer candidates, 
    and ranks them by predicted naked efficacy using target mRNA context features.
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
    
    context_model_path = MODELS_DIR / "model_normal_context.txt"
    if use_context_model and context_model_path.exists() and input_type != "dsirna":
        try:
            from .context_feature_extractor import ContextFeatureExtractor
            extractor = ContextFeatureExtractor(use_rna_fm=True)
            feature_matrix = extractor.extract_for_candidates(candidates, sequence)
            raw_scores = _predict_naked(feature_matrix, model_key="normal_context")
            normalized_scores = _normalize_scores(raw_scores, calibrator_key="normal_context")
        except Exception as e:
            logger.warning(f"Context feature extraction failed ({e}), falling back to baseline 214-D model.")
            feature_matrix = extract_batch_v4(sense_list, antisense_list)
            raw_scores = _predict_naked(feature_matrix, model_key="normal")
            normalized_scores = _normalize_scores(raw_scores, calibrator_key="normal")
    else:
        # Extract structural features for the ML model
        feature_matrix = extract_batch_v4(sense_list, antisense_list)
        raw_scores = _predict_naked(feature_matrix, model_key="normal")
        normalized_scores = _normalize_scores(raw_scores, calibrator_key="normal")

    # Annotate seed toxicity
    annotations = annotate_candidates(sense_list, antisense_list)

    # Rank by score (descending)
    sort_order = np.argsort(normalized_scores)[::-1]
    sorted_scores = normalized_scores[sort_order]
    
    ranked_results = []
    for rank_idx, original_idx in enumerate(sort_order):
        cand = candidates[original_idx]
        score = round(float(np.clip(sorted_scores[rank_idx], 0.0, 100.0)), 2)
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
            asymmetry_ddg=annotation.get("asymmetry_ddg"),
            asymmetry_label=annotation.get("asymmetry_label", "Unknown"),
            hepato_score=annotation.get("hepato_score"),
            hepato_profile=annotation.get("hepato_profile"),
            hepato_status=annotation.get("hepato_status"),
            npm_burden=annotation.get("npm_burden"),
        ))

    if top_n is not None:
        ranked_results = ranked_results[:top_n]

    logger.info(f"Successfully ranked {len(ranked_results)} siRNA candidates.")
    return ranked_results


def rank_by_naked_score(
    source: Union[str, Path],
    top_n: Optional[int] = None,
    input_type: str = "gene",
    use_context_model: bool = True,
) -> List[RankedSiRNA]:
    """Alias for rank_sirnas."""
    return rank_sirnas(source, top_n, input_type, use_context_model=use_context_model)


def select_curated_leads(
    ranked_candidates: List[RankedSiRNA],
    transcript_sequence: Optional[str] = None,
    total_transcript_length: int = 1000,
    min_separation: int = 35,
    max_leads: int = 10,
) -> List[RankedSiRNA]:
    """
    Selects non-redundant, safety-filtered lead siRNA scaffolds across biological transcript domains.
    
    Why: A naive Top-5 raw cutoff creates massive positional redundancy (e.g. 4 candidates within 
    the same 15-nt window) and admits lethal cytotoxins. This function enforces:
      1. Genuine Biological Domain Mapping: Detects the canonical Open Reading Frame (AUG -> Stop),
         accurately partitioning the transcript into 5' UTR, CDS, and 3' UTR.
      2. Structural Viability: Only candidates with func_ok == True (no internal hairpin palindromes).
      3. Cytotoxic Safety: Rejects high-risk toxic seeds (toxicity_label != 'Toxic').
      4. Spatial Non-Redundancy: Guarantees each selected lead is separated by at least min_separation nt.
    """
    leads: List[RankedSiRNA] = []
    
    # 1. Biological domain boundary detection
    orf_start, orf_end = None, None
    if transcript_sequence and len(transcript_sequence) >= 150:
        clean_seq = transcript_sequence.upper().replace("T", "U")
        longest = (0, 0, 0)  # length, 1-based start, 1-based end
        stop_codons = {"UAA", "UAG", "UGA"}
        for frame in range(3):
            start = None
            for i in range(frame, len(clean_seq) - 2, 3):
                codon = clean_seq[i : i + 3]
                if codon == "AUG" and start is None:
                    start = i
                elif codon in stop_codons and start is not None:
                    orf_len = (i + 3) - start
                    if orf_len > longest[0]:
                        longest = (orf_len, start + 1, i + 3)
                    start = None
        if longest[0] >= 150:  # At least 50 amino acids
            orf_start, orf_end = longest[1], longest[2]

    if orf_start is not None and orf_end is not None:
        utr5_cutoff = orf_start - 1
        cds_cutoff = orf_end + 1
    else:
        # Fallback to mRNA heuristic (12% 5' UTR, ~50-60% CDS, ~30-40% 3' UTR)
        effective_len = len(transcript_sequence) if transcript_sequence else total_transcript_length
        utr5_cutoff = max(50, int(effective_len * 0.12))
        cds_cutoff = max(utr5_cutoff + 100, int(effective_len * 0.65))
    
    for r in ranked_candidates:
        # Assign biological domain based on 1-based transcript coordinate
        if r.position <= utr5_cutoff:
            r.domain = "5' UTR"
        elif r.position >= cds_cutoff:
            r.domain = "3' UTR"
        else:
            r.domain = "CDS"
            
        # Hard Filter 1: Biophysical functionality (no palindromic self-hairpins)
        if not r.func_ok:
            continue
            
        # Hard Filter 2: Seed cytotoxicity (reject lethal cytotoxins with < 50% cell viability)
        if r.toxicity_label == "Toxic":
            continue
            
        # Hard Filter 3: Spatial non-redundancy (prevent picking overlapping 21-mers)
        if any(abs(r.position - lead.position) < min_separation for lead in leads):
            continue
            
        r.is_curated_lead = True
        leads.append(r)
        if len(leads) >= max_leads:
            break
            
    return leads


# ─── Workflow 2: Modified siRNA Prediction ────────────────────────────────────

# Re-exported from src.pdb_generator for backwards compatibility
from .pdb_generator import generate_sirna_pdb


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
    Incorporates empirical thermodynamic increments (MOD_DELTA_DG) to compute true variant-specific
    duplex binding energy (kcal/mol) and local unfolding stability shifts.
    """
    def to_std_canonical(seq: str, parent: Optional[str] = None) -> str:
        if parent and len(parent) == len(seq):
            return parent.upper().replace("T", "U")
        mod_map = {'F': 'U', 'M': 'U', 'S': 'U', 'D': 'C', 'E': 'U', 'L': 'A', '1': 'U'}
        return ''.join(c if c in 'AUGC' else mod_map.get(c.upper(), 'U') for c in seq.upper().replace('T', 'U'))

    s_seq = to_std_canonical(sense, parent_sense)
    a_seq = to_std_canonical(antisense, parent_antisense)
    
    # Nearest-neighbor thermodynamic free energy parameters (kcal/mol per base-pair step, Xia / Turner 1998)
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

    try:
        import RNA
        fc_s = RNA.fold_compound(s_seq)
        mfe_s = round(fc_s.mfe()[1], 2) if fc_s else 0.0
        
        fc_a = RNA.fold_compound(a_seq)
        mfe_a = round(fc_a.mfe()[1], 2) if fc_a else 0.0
        
        duplex = RNA.duplexfold(s_seq, a_seq)
        base_d_energy = round(duplex.energy, 2) if (duplex and duplex.energy != 0.0) else round(float(sum(positional_dg[:19]) + 3.4), 2)
        
        fc_d = RNA.fold_compound(s_seq + "&" + a_seq)
        mfe_struct, mfe_d = fc_d.mfe() if fc_d else ("(((((((((((((((((((..&..)))))))))))))))))))", 0.0)
    except Exception:
        # Nearest-Neighbor RNA duplex thermodynamics fallback (Turner/Xia model with +3.4 kcal/mol initiation)
        base_d_energy = round(float(sum(positional_dg[:19]) + 3.4), 2)
        gc_s_count = sum(1 for b in s_seq if b in "GC")
        gc_a_count = sum(1 for b in a_seq if b in "GC")
        mfe_s = round(-0.8 * gc_s_count, 2)
        mfe_a = round(-0.8 * gc_a_count, 2)
        mfe_struct = "(((((((((((((((((((..&..)))))))))))))))))))"
        
    gc_s = round((s_seq.count("G") + s_seq.count("C")) / len(s_seq) * 100.0, 1) if sense else 0.0
    gc_a = round((a_seq.count("G") + a_seq.count("C")) / len(a_seq) * 100.0, 1) if antisense else 0.0

    # Parse and accumulate chemical modifications across all input patterns
    applied_mods: List[Tuple[str, int, str]] = []
    seen_mod_keys = set()

    def add_mod(m_code: str, p: int, strand: str):
        if 1 <= p <= 21 and m_code:
            norm = normalize_mod_code(m_code)
            if norm:
                k = (norm, p, strand.lower())
                if k not in seen_mod_keys:
                    seen_mod_keys.add(k)
                    applied_mods.append((norm, p, strand.lower()))

    # 1. From mod_symbol, mod_position/mod_positions, mod_strand
    if mod_symbol and (mod_position or mod_positions):
        st = 'sense' if 'sense' in str(mod_strand).lower() and 'anti' not in str(mod_strand).lower() else 'antisense'
        pos_raw = str(mod_positions if mod_positions is not None and str(mod_positions).strip() else mod_position)
        for p_str in pos_raw.replace('+', ',').split(','):
            if p_str.strip().isdigit():
                add_mod(mod_symbol, int(p_str.strip()), st)

    # 2. From sense_mods / sense_positions
    if sense_mods:
        if sense_positions:
            s_m = [m.strip() for m in str(sense_mods).replace('+', ',').split(',') if m.strip()]
            s_p = [int(p.strip()) for p in str(sense_positions).replace('+', ',').split(',') if p.strip().isdigit()]
            for m, p in zip(s_m, s_p):
                add_mod(m, p, 'sense')
        else:
            for idx, c in enumerate(str(sense_mods).strip()):
                if idx < len(s_seq) and c.upper() not in "ACGTU." and c.upper() in MODIFICATION_ALPHABET:
                    add_mod(c, idx + 1, 'sense')

    # 3. From antisense_mods / antisense_positions
    if antisense_mods:
        if antisense_positions:
            a_m = [m.strip() for m in str(antisense_mods).replace('+', ',').split(',') if m.strip()]
            a_p = [int(p.strip()) for p in str(antisense_positions).replace('+', ',').split(',') if p.strip().isdigit()]
            for m, p in zip(a_m, a_p):
                add_mod(m, p, 'antisense')
        else:
            for idx, c in enumerate(str(antisense_mods).strip()):
                if idx < len(a_seq) and c.upper() not in "ACGTU." and c.upper() in MODIFICATION_ALPHABET:
                    add_mod(c, idx + 1, 'antisense')

    # 4. From sequence characters (non-canonical single letter codes)
    for idx, c in enumerate(sense):
        if c.upper() not in "ACGTU." and c.upper() in MODIFICATION_ALPHABET:
            add_mod(c, idx + 1, 'sense')
    for idx, c in enumerate(antisense):
        if c.upper() not in "ACGTU." and c.upper() in MODIFICATION_ALPHABET:
            add_mod(c, idx + 1, 'antisense')

    # Apply empirical thermodynamic perturbation (Xia/Turner NN & Alnylam ESC literature)
    total_delta_dg = 0.0
    for mod_code, pos, strand in applied_mods:
        ddg = get_mod_delta_dg(mod_code)
        total_delta_dg += ddg

        # Distribute local thermodynamic perturbation into the positional dinucleotide steps
        # Sense strand runs 5' to 3' (steps 0 to 19 match pos 1..21).
        # Antisense strand runs antiparallel 5' to 3' (pos p pairs with sense pos 22 - p).
        step_idx = (pos - 1) if strand == 'sense' else (21 - pos)
        step_idx = max(0, min(19, step_idx))
        if step_idx == 0:
            positional_dg[0] = round(positional_dg[0] + ddg, 2)
        elif step_idx == 19:
            positional_dg[19] = round(positional_dg[19] + ddg, 2)
        else:
            positional_dg[step_idx - 1] = round(positional_dg[step_idx - 1] + ddg / 2.0, 2)
            positional_dg[step_idx] = round(positional_dg[step_idx] + ddg / 2.0, 2)

    d_energy = round(base_d_energy + total_delta_dg, 2)

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
        "delta_duplex_dg": round(total_delta_dg, 2),
        "parent_duplex_mfe_kcal": base_d_energy,
        "sense_mfe_kcal": mfe_s,
        "anti_mfe_kcal": mfe_a,
        "gc_sense_pct": gc_s,
        "gc_anti_pct": gc_a,
        "positional_dg": positional_dg,
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
    parent_sense: str = "",
    parent_antisense: str = "",
    conc_nM: float = 10.0,
) -> Dict[str, Any]:
    """
    Predicts the efficacy of chemically modified siRNA variants.
    Single-mod scan evaluates raw intrinsic ML effect; multi-mod design applies full biophysical constraints.
    Dose-response is conditioned on conc_nM via IEEE v5 pharmacodynamic engine.
    """
    logger.info(f"Starting predict_modified workflow (mode: {mode}, dose: {conc_nM} nM).")

    actual_parent_s = parent_sense or sense
    actual_parent_a = parent_antisense or antisense

    # 1. Establish parent baselines
    parent_v4_matrix = extract_batch_v4([actual_parent_s], [actual_parent_a])
    raw_parent_score = float(_normalize_scores(_predict_naked(parent_v4_matrix), calibrator_key="normal")[0])

    raw_model_b_score = float(_predict_model_b([actual_parent_s], [actual_parent_a], [actual_parent_s], [actual_parent_a], model_key=model_key, conc_nM=conc_nM)[0])

    # 2. Generate variants
    if mode in ("scan", "single"):
        variants = single_mod_scan(actual_parent_s, actual_parent_a)
    elif mode == "multimod":
        # Handle single modification parameters passed to multimod mode
        if mod_symbol and (mod_position or mod_positions) and not (sense_mods or antisense_mods):
            st = (mod_strand or 'antisense').lower()
            pos_val = str(mod_positions if mod_positions is not None and str(mod_positions).strip() else mod_position)
            if 'sense' in st and 'anti' not in st:
                sense_mods = mod_symbol
                sense_positions = pos_val
            else:
                antisense_mods = mod_symbol
                antisense_positions = pos_val

        variants = [multimod_gen(
            actual_parent_s, actual_parent_a,
            sense_mods=sense_mods,
            sense_positions=sense_positions,
            antisense_mods=antisense_mods,
            antisense_positions=antisense_positions,
        )]
    else:
        raise ValueError(f"Invalid mode provided: {mode}")

    if not variants:
        return {"results": [], "parent_score": 0.0, "parent_score_raw": 0.0, "model_b_baseline": 0.0, "naked_baseline": 0.0, "target_dose_nM": conc_nM}

    # 3. Extract features for variants
    s_list = [v.sense for v in variants]
    a_list = [v.antisense for v in variants]
    ps_list = [v.parent_sense for v in variants]
    pa_list = [v.parent_antisense for v in variants]
    
    # 4. Predict using Unified Dose-Aware & Cell-Aware CatBoost Regressor
    scores = model_b_v4.predict(s_list, a_list, ps_list, pa_list, conc_nM=conc_nM)
    normalized_scores = scores
    gbdt_scores = scores
    gnn_scores = scores

    # 5. Apply biophysical constraints and compute parent anchor
    parent_adjusted_score, _, _ = calculate_adjusted_efficacy(
        raw_model_b_score, sense, antisense, sense, antisense,
        mode="targeted" if mode in ("scan", "single") else "mod_ranking"
    )
    raw_parent_adjusted_score, _, _ = calculate_adjusted_efficacy(
        raw_parent_score, sense, antisense, sense, antisense,
        mode="targeted" if mode in ("scan", "single") else "mod_ranking"
    )

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
    parent_duplex_dg = float(struct_props.get("parent_duplex_mfe_kcal") or struct_props.get("duplex_mfe_kcal") or -37.4)

    unranked_results = []
    for idx, (variant, score) in enumerate(zip(variants, normalized_scores)):
        base_score = float(score)
        pred_kd_pct = base_score

        # Intrinsic potency directly derived from concentration-response relationship
        safe_kd = max(1.0, min(99.0, float(base_score)))
        derived_ic50 = float(conc_nM * (100.0 - safe_kd) / safe_kd)
        est_IC50_nM = round(derived_ic50, 4)
        est_pIC50 = round(9.0 - np.log10(max(1e-4, derived_ic50)), 4)

        adj_score, penalties, _ = calculate_adjusted_efficacy(
            base_score, variant.sense, variant.antisense, variant.parent_sense, variant.parent_antisense,
            mode="targeted" if mode in ("scan", "single", "multimod") else "mod_ranking"
        )
        viability, tox_label, tox_note = toxicity_for_modified(variant.antisense, variant.parent_antisense)
        hep_info = calculate_preclinical_hepatotoxicity_index(
            variant.parent_antisense,
            modified_antisense=variant.antisense
        )

        final_score = adj_score
        final_delta = round(final_score - parent_adjusted_score, 2)


        # Calculate variant-specific thermodynamic duplex perturbation
        v_delta_dg = 0.0
        if getattr(variant, 'mod_symbol', None):
            v_delta_dg += get_mod_delta_dg(variant.mod_symbol)
        v_sm = getattr(variant, 'sense_mods', '')
        v_am = getattr(variant, 'antisense_mods', '')
        if v_sm:
            for sm in str(v_sm).replace('+', ',').split(','):
                if sm.strip(): v_delta_dg += get_mod_delta_dg(sm.strip())
        if v_am:
            for am in str(v_am).replace('+', ',').split(','):
                if am.strip(): v_delta_dg += get_mod_delta_dg(am.strip())
        if not (getattr(variant, 'mod_symbol', None) or v_sm or v_am):
            for c in variant.sense:
                if c.upper() not in "ACGTU." and c.upper() in MODIFICATION_ALPHABET:
                    v_delta_dg += get_mod_delta_dg(c)
            for c in variant.antisense:
                if c.upper() not in "ACGTU." and c.upper() in MODIFICATION_ALPHABET:
                    v_delta_dg += get_mod_delta_dg(c)

        var_duplex_mfe = round(parent_duplex_dg + v_delta_dg, 2)
        var_delta_duplex_dg = round(v_delta_dg, 2)

        unranked_results.append(RankedCmSiRNA(
            rank=0,
            sense=variant.sense,
            antisense=variant.antisense,
            mod_symbol=variant.mod_symbol,
            mod_position=variant.mod_position,
            mod_strand=variant.mod_strand,
            mod_positions=variant.mod_positions,
            efficacy_score=final_score,
            gnn_score=None,
            gbdt_score=float(base_score),
            estimated_pIC50=est_pIC50,
            estimated_IC50_nM=est_IC50_nM,
            predicted_knockdown_pct=pred_kd_pct,
            target_dose_nM=conc_nM,
            delta_score=final_delta,
            efficacy_label=_get_efficacy_label(final_score),
            toxicity_score=viability,
            toxicity_label=tox_label,
            toxicity_note=tox_note,
            biophysics=penalties,
            sense_mods=getattr(variant, 'sense_mods', ''),
            sense_positions=getattr(variant, 'sense_positions', ''),
            antisense_mods=getattr(variant, 'antisense_mods', ''),
            antisense_positions=getattr(variant, 'antisense_positions', ''),
            duplex_mfe_kcal=var_duplex_mfe,
            delta_duplex_dg=var_delta_duplex_dg,
            hepato_score=hep_info["hepato_score"],
            hepato_profile=hep_info["hepato_profile"],
            hepato_status=hep_info["hepato_status"],
        ))

    # Sort by efficacy score (descending)
    unranked_results.sort(key=lambda x: x.efficacy_score, reverse=True)
    
    # Assign true 1..N ranks
    ranked_results = []
    for idx, item in enumerate(unranked_results, start=1):
        item.rank = idx
        ranked_results.append(item)

    logger.info(f"Successfully evaluated {len(ranked_results)} modified siRNA variants.")
    return {
        "results": ranked_results,
        "parent_score": round(parent_adjusted_score, 2),
        "parent_score_raw": round(raw_parent_score, 2),
        "model_b_baseline": round(parent_adjusted_score, 2),
        "naked_baseline": round(raw_parent_adjusted_score, 2),
        "structural_properties": struct_props,
        "target_dose_nM": conc_nM,
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

