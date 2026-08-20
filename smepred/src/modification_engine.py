"""
modification_engine.py — Chemical Modification Generator

This module applies chemical modifications to siRNA candidates. It supports
three distinct operation modes:

1. Single-Modification Scan
   Systematically applies each of the 30 chemical modification symbols to every 
   position (1-21) on both strands of a parent siRNA. This generates an exhaustive 
   1260-variant library to identify the single most effective modification point.

2. MultiModGen (Targeted Custom Modifications)
   Allows the user or downstream algorithms to apply specific modifications to 
   targeted positions across both strands simultaneously.

3. Beam Search Scan
   An intelligent, iterative search algorithm that combines top-performing single 
   modifications into multi-mod combinations, scoring them in rounds to find the 
   global biophysical optimum without brute-forcing millions of combinations.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Any, Set, Dict
import numpy as np

from .biophysics import calculate_adjusted_efficacy

logger = logging.getLogger(__name__)

# ─── Load Modification Definitions ──────────────────────────────────────────────

_MOD_FILE = Path(__file__).parent.parent / "data" / "modification_codes.json"
if _MOD_FILE.exists():
    try:
        with _MOD_FILE.open("r", encoding="utf-8") as _f:
            _MOD_DATA = json.load(_f)
        CANONICAL_SYMBOLS: Set[str] = set(_MOD_DATA["canonical_symbols"])
        MODIFICATION_SYMBOLS: Set[str] = set(_MOD_DATA["modification_symbols"])
    except Exception as e:
        logger.warning(f"Could not load modification codes from {_MOD_FILE}: {e}")
        CANONICAL_SYMBOLS: Set[str] = {"A", "C", "G", "U", "T"}
        MODIFICATION_SYMBOLS: Set[str] = {"M", "F", "D", "X", "8", "2", "4", "m", "f", "s", "p", "a", "c", "g", "u"}
else:
    CANONICAL_SYMBOLS: Set[str] = {"A", "C", "G", "U", "T"}
    MODIFICATION_SYMBOLS: Set[str] = {"M", "F", "D", "X", "8", "2", "4", "m", "f", "s", "p", "a", "c", "g", "u"}


# ─── Data Transfer Objects ────────────────────────────────────────────────────

@dataclass
class CmSiRNA:
    """
    Represents a Chemically Modified siRNA (cm-siRNA) variant.
    
    Attributes:
        sense (str): The chemically modified sense strand.
        antisense (str): The chemically modified antisense strand.
        mod_symbol (str): The symbol(s) representing the applied chemistry.
        mod_position (int): The 1-based index of the primary modification.
        mod_strand (str): The strand on which the modification occurs.
        parent_sense (str): The unmodified biological sense strand.
        parent_antisense (str): The unmodified biological antisense strand.
        mod_positions (str): Comma-separated list of all modified positions (for multi-mod).
        efficacy_score (float): The final biophysically adjusted efficacy score.
        delta_score (float): Efficacy improvement/loss relative to the parent.
        penalties (dict): Breakdown of biophysical penalties applied.
    """
    sense: str
    antisense: str
    mod_symbol: str
    mod_position: int
    mod_strand: str
    parent_sense: str
    parent_antisense: str
    mod_positions: str = ""
    efficacy_score: float = 0.0
    delta_score: float = 0.0
    penalties: Optional[Dict[str, float]] = None
    estimated_pIC50: Optional[float] = None
    estimated_IC50_nM: Optional[float] = None
    predicted_knockdown_pct: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "sense": self.sense,
            "antisense": self.antisense,
            "mod_symbol": self.mod_symbol,
            "mod_position": self.mod_position,
            "mod_strand": self.mod_strand,
            "parent_sense": self.parent_sense,
            "parent_antisense": self.parent_antisense,
            "mod_positions": self.mod_positions,
        }
        if self.efficacy_score:
            result["efficacy_score"] = self.efficacy_score
        if self.delta_score:
            result["delta_score"] = self.delta_score
        if self.penalties:
            result["penalties"] = self.penalties
        if self.estimated_pIC50 is not None:
            result["estimated_pIC50"] = round(self.estimated_pIC50, 4)
        if self.estimated_IC50_nM is not None:
            result["estimated_IC50_nM"] = round(self.estimated_IC50_nM, 4)
        if self.predicted_knockdown_pct is not None:
            result["predicted_knockdown_pct"] = round(self.predicted_knockdown_pct, 2)
        return result


# ─── Helper Functions ─────────────────────────────────────────────────────────

def _apply_mod(sequence: str, position_1based: int, symbol: str) -> str:
    """
    Replaces a specific nucleotide with a chemical modification symbol.
    """
    if not (1 <= position_1based <= len(sequence)):
        logger.error(f"Position {position_1based} out of bounds for sequence length {len(sequence)}")
        raise ValueError(
            f"Position {position_1based} is out of range for sequence of length {len(sequence)}."
        )
    zero_indexed = position_1based - 1
    return sequence[:zero_indexed] + symbol + sequence[zero_indexed + 1:]


def _normalize_mod_symbol(symbol: str) -> str:
    sym = symbol.strip()
    if sym in MODIFICATION_SYMBOLS | CANONICAL_SYMBOLS:
        return sym
    up = sym.upper()
    if any(k in up for k in ('2F', 'FLUORO', '2\'-F')) or up == 'F': return 'F'
    if any(k in up for k in ('2OME', 'METHYL', '2\'-OME', 'OMET')) or up == 'M': return 'M'
    if any(k in up for k in ('PS', 'PHOSPHOROTHIOATE', 'THIO')) or up in ('S', '1'): return 'S'
    if any(k in up for k in ('MOE', 'METHOXYETHYL')) or up == 'E': return 'E'
    if any(k in up for k in ('LNA', 'LOCKED')) or up == 'L': return 'L'
    if any(k in up for k in ('DEOXY', 'DNA')) or up == 'D': return 'D'
    if 'UNA' in up or up == '6': return '6'
    if 'GNA' in up or up == '8': return '8'
    if 'TNA' in up or up == '9': return '9'
    return sym


def _parse_multimod_input(mod_symbols_str: str, positions_str: str) -> List[Tuple[str, List[int]]]:
    """
    Parses modification inputs with robust support for:
    1. Single modification for multiple positions (e.g., mods="M", pos="1,2,3,4,5...21")
    2. Semicolon/double-comma groups (e.g., mods="M; F; S", pos="1,2,3; 4,5,6; 20,21")
    3. Comma-separated or plus-separated pairs (e.g., mods="M+F", pos="1+2" or mods="M, F", pos="2, 6")
    """
    m_str = str(mod_symbols_str or "").strip()
    p_str = str(positions_str or "").strip()
    if not m_str or not p_str:
        return []

    # Unify delimiters
    p_clean = p_str.replace("+", ",").replace("|", ",").replace(" ", "")
    m_clean = m_str.replace("+", ",").replace("|", ",").replace(" ", "")

    def safe_int_list(s: str) -> List[int]:
        res = []
        for part in s.replace(";", ",").split(","):
            part = part.strip()
            if part.isdigit():
                res.append(int(part))
        return res

    # Detect grouped delimiter
    if ";" in p_clean:
        pos_groups = [p.strip() for p in p_clean.split(";") if p.strip()]
        mod_groups = [m.strip() for m in (m_clean.split(";") if ";" in m_clean else m_clean.split(",")) if m.strip()]
    elif ",," in p_clean:
        pos_groups = [p.strip() for p in p_clean.split(",,") if p.strip()]
        mod_groups = [m.strip() for m in (m_clean.split(",,") if ",," in m_clean else m_clean.split(",")) if m.strip()]
    else:
        m_parts = [m.strip() for m in m_clean.split(",") if m.strip()]
        if len(m_parts) == 1:
            pos_list = safe_int_list(p_clean)
            clean_sym = _normalize_mod_symbol(m_parts[0])
            return [(clean_sym, pos_list)]
        else:
            mod_groups = m_parts
            p_parts = [p.strip() for p in p_clean.split(",") if p.strip()]
            if len(mod_groups) == len(p_parts):
                pos_groups = p_parts
            else:
                pos_groups = [p_clean]

    if len(mod_groups) == 1 and len(pos_groups) > 1:
        mod_groups = mod_groups * len(pos_groups)

    if len(mod_groups) != len(pos_groups):
        all_positions = safe_int_list(p_clean)
        clean_symbol = _normalize_mod_symbol(mod_groups[0])
        return [(clean_symbol, all_positions)]

    parsed_instructions = []
    for symbol, pos_string in zip(mod_groups, pos_groups):
        clean_symbol = _normalize_mod_symbol(symbol)
        if clean_symbol not in MODIFICATION_SYMBOLS | CANONICAL_SYMBOLS:
            logger.warning(f"Unknown modification symbol: '{symbol}', mapping to 2'-OMe")
            clean_symbol = "M"
            
        parsed_positions = safe_int_list(pos_string)
        if parsed_positions:
            parsed_instructions.append((clean_symbol, parsed_positions))
        
    return parsed_instructions


# ─── Mode 1: Single-Modification Scan ─────────────────────────────────────────

def single_mod_scan(
    sense: str,
    antisense: str,
    target_symbols: Optional[List[str]] = None,
) -> List[CmSiRNA]:
    """
    Generates an exhaustive single-modification combinatorial library.
    """
    if target_symbols is None:
        clinical_standard = ["F", "M", "D", "S", "1", "E", "L"]
        exotic = [s for s in sorted(MODIFICATION_SYMBOLS) if s not in clinical_standard]
        target_symbols = clinical_standard + exotic

    generated_variants: List[CmSiRNA] = []

    for symbol in target_symbols:
        # Scan sense strand
        for pos in range(1, len(sense) + 1):
            if not _is_positionally_valid(symbol, pos, len(sense)):
                continue
            modified_sense = _apply_mod(sense, pos, symbol)
            generated_variants.append(CmSiRNA(
                sense=modified_sense,
                antisense=antisense,
                mod_symbol=symbol,
                mod_position=pos,
                mod_strand="sense",
                parent_sense=sense,
                parent_antisense=antisense,
            ))
            
        # Scan antisense strand
        for pos in range(1, len(antisense) + 1):
            if not _is_positionally_valid(symbol, pos, len(antisense)):
                continue
            modified_antisense = _apply_mod(antisense, pos, symbol)
            generated_variants.append(CmSiRNA(
                sense=sense,
                antisense=modified_antisense,
                mod_symbol=symbol,
                mod_position=pos,
                mod_strand="antisense",
                parent_sense=sense,
                parent_antisense=antisense,
            ))

    return generated_variants


# ─── Mode 2: Targeted MultiModGen ─────────────────────────────────────────────

def multimod_gen(
    sense: str,
    antisense: str,
    sense_mods: str = "",
    sense_positions: str = "",
    antisense_mods: str = "",
    antisense_positions: str = "",
) -> CmSiRNA:
    """
    Applies precise, targeted modifications simultaneously across both strands.
    """
    mutable_sense = list(sense)
    mutable_antisense = list(antisense)

    if sense_mods:
        if sense_positions:
            sense_instructions = _parse_multimod_input(sense_mods, sense_positions)
            for symbol, positions in sense_instructions:
                for pos in positions:
                    if 1 <= pos <= len(mutable_sense):
                        mutable_sense[pos - 1] = symbol
        else:
            # Compact 1-char per position mask (e.g. MMMMMMFMFFFMMMMMMMMMM)
            for i in range(min(len(mutable_sense), len(sense_mods))):
                symbol = sense_mods[i]
                if symbol != sense[i]:
                    mutable_sense[i] = symbol

    if antisense_mods:
        if antisense_positions:
            antisense_instructions = _parse_multimod_input(antisense_mods, antisense_positions)
            for symbol, positions in antisense_instructions:
                for pos in positions:
                    if 1 <= pos <= len(mutable_antisense):
                        mutable_antisense[pos - 1] = symbol
        else:
            # Compact 1-char per position mask (e.g. MFMMDM2MMMMMMFMFMMMMMMM)
            for i in range(min(len(mutable_antisense), len(antisense_mods))):
                symbol = antisense_mods[i]
                if symbol != antisense[i]:
                    mutable_antisense[i] = symbol

    return CmSiRNA(
        sense="".join(mutable_sense),
        antisense="".join(mutable_antisense),
        mod_symbol="multi",
        mod_position=0,
        mod_strand="both",
        parent_sense=sense,
        parent_antisense=antisense,
    )


# ─── Mode 3: Combinatorial Beam Search Scan ───────────────────────────────────

_TERMINAL_5PRIME_ONLY = {'1', '3'}      # 5'-Phosphate/5'-VP, 5'-OMe cap (pos 1 only)
_TERMINAL_3PRIME_ONLY = {'2'}           # 3'-Phosphate (pos 21 only)
_CONJUGATES = {'4', '5'}                # GalNAc / Cholesterol conjugates (terminal ends only)

def _is_positionally_valid(symbol: str, pos: int, seq_len: int) -> bool:
    """Enforces strict chemical positional constraints for terminal/conjugate modifications."""
    if symbol in _TERMINAL_5PRIME_ONLY and pos != 1:
        return False
    if symbol in _TERMINAL_3PRIME_ONLY and pos != seq_len:
        return False
    if symbol in _CONJUGATES and pos not in (1, seq_len):
        return False
    return True


def _is_chemically_viable(mod_sense: str, parent_sense: str, mod_anti: str, parent_anti: str) -> bool:
    """
    Enforces strict chemical synthesis viability rules:
    1. Terminus-only modifications ('1', '3') must exist strictly at pos 1. Max 1 instance per strand.
    2. 3'-terminus modifications ('2') must exist strictly at pos 21. Max 1 instance per strand.
    3. Conjugates ('4', '5') must exist strictly at terminal ends (pos 1 or 21). Max 1 instance per strand.
    4. Max 2 consecutive bulky rigid modifications (LNA 'L', MOE 'E', ENA 'Y').
    """
    for strand, parent in [(mod_sense, parent_sense), (mod_anti, parent_anti)]:
        n = len(strand)
        c_5p = 0
        c_3p = 0
        c_conj = 0
        c_bulky = 0
        for i, char in enumerate(strand):
            parent_char = parent[i] if i < len(parent) else char
            if char != parent_char:
                pos = i + 1
                if char in _TERMINAL_5PRIME_ONLY:
                    if pos != 1: return False
                    c_5p += 1
                    if c_5p > 1: return False
                if char in _TERMINAL_3PRIME_ONLY:
                    if pos != n: return False
                    c_3p += 1
                    if c_3p > 1: return False
                if char in _CONJUGATES:
                    if pos not in (1, n): return False
                    c_conj += 1
                    if c_conj > 1: return False
                if char in ('L', 'Y', 'E'):
                    c_bulky += 1
                    if c_bulky >= 3: return False
                else:
                    c_bulky = 0
            else:
                c_bulky = 0
    return True


def multi_mod_scan(
    sense: str,
    antisense: str,
    max_mods: int = 2,
    beam_width: int = 20,
    model_key: str = "B_v2",
    full_scan: bool = True,
    single_results: Optional[List[Any]] = None,
    parent_score: Optional[float] = None,
    seed_variant: Optional[Any] = None,
    calibrator_key: Optional[str] = None,
    normalize_mode: str = "clip",
    fda_core_only: bool = True,
) -> List[CmSiRNA]:
    """
    Heuristically explores the vast combinatoric space of multi-modified siRNAs.
    Uses an iterative beam search to stack highly effective modifications while 
    pruning sub-optimal branches to avoid computational explosion.
    """
    # Lazy imports required to prevent circular dependency with predictor.py
    from .predictor import predict_modified, _get_model, _normalize_scores, _predict_model_b
    from .features import extract_phase2
    from .biophysics import calculate_adjusted_efficacy
    from collections import defaultdict

    logger.info(f"Starting combinatorial beam search (FDA Core Only: {fda_core_only}).")

    if single_results is None:
        prediction_output = predict_modified(
            sense, antisense, mode="scan", model_key=model_key, full_scan=full_scan
        )
        parent_score = prediction_output.get("parent_score_raw", prediction_output["parent_score"])
        single_results = prediction_output["results"]
    elif parent_score is None:
        raise ValueError("parent_score must be provided when single_results is pre-calculated.")

    # Filter to FDA-Approved Core Palette (2'-OMe 'M', 2'-F 'F', 2'-deoxy 'D', PS 'S', 5'-Phos '1')
    FDA_CORE_SYMBOLS = {'M', 'F', 'D', 'S', '1'}
    if fda_core_only and single_results:
        fda_filtered = [r for r in single_results if all(c in FDA_CORE_SYMBOLS for c in r.mod_symbol.replace('+', ''))]
        if fda_filtered:
            single_results = fda_filtered
            logger.info(f"Restricted beam search to {len(single_results)} FDA-approved core single modifications.")

    # Calculate baseline for delta comparisons
    parent_adjusted_score, _, _ = calculate_adjusted_efficacy(
        parent_score, sense, antisense, sense, antisense
    )

    def _score_variants_batch(variants: List[CmSiRNA], chunk_size: int = 200) -> List[CmSiRNA]:
        """Internal helper to batch-score variants using Model B, in chunks to limit memory.

        Uses the caller's `model_key` (closed over from `multi_mod_scan`'s
        argument) via the unified `_predict_model_b` dispatcher, so beam-search
        expansion rounds use the SAME model as the initial single-mod scan.
        Before 2026-07-11 this hardcoded `_get_model("B")` unconditionally,
        silently ignoring `model_key="B_v2"` during expansion -- fixed as part
        of promoting B_v2 to the default model (see
        docs/validations/model_b_v2_tuning_robustness.md)."""
        if not variants:
            return []

        scored_variants = []

        # For beam search expansion rounds, use fast CatBoost model to score thousands of permutations instantly.
        # Deep PyTorch GNN / Ensemble scoring is re-applied to the final top 100 candidates at the end.
        eval_model_key = "CatBoost_v4" if model_key in ["Ensemble_v4", "GNN_v2", "IEEE_v5"] else model_key

        for i in range(0, len(variants), chunk_size):
            chunk = variants[i:i + chunk_size]
            s_list = [v.sense for v in chunk]
            a_list = [v.antisense for v in chunk]
            ps_list = [v.parent_sense for v in chunk]
            pa_list = [v.parent_antisense for v in chunk]

            normalized_scores = _predict_model_b(s_list, a_list, ps_list, pa_list, model_key=eval_model_key)

            for variant, raw_score in zip(chunk, normalized_scores):
                adj_score, penalties, _ = calculate_adjusted_efficacy(
                    float(raw_score), variant.sense, variant.antisense,
                    variant.parent_sense, variant.parent_antisense
                )
                variant.efficacy_score = round(adj_score, 2)
                variant.delta_score = round(adj_score - parent_adjusted_score, 2)
                variant.penalties = penalties
                scored_variants.append(variant)

        return scored_variants

    # Initialize the beam with diverse, high-performing single modifications
    mod_groups: Dict[str, List[Any]] = defaultdict(list)
    for result in single_results:
        mod_groups[result.mod_symbol].append(result)

    for symbol in mod_groups:
        mod_groups[symbol].sort(key=lambda r: r.efficacy_score, reverse=True)

    diversified_beam = []
    max_entries = max(len(lst) for lst in mod_groups.values())
    
    # Round-robin selection ensures chemical diversity in the starting beam
    for rank in range(max_entries):
        for symbol in sorted(mod_groups.keys()):
            if rank < len(mod_groups[symbol]):
                diversified_beam.append(mod_groups[symbol][rank])
            if len(diversified_beam) >= beam_width:
                break
        if len(diversified_beam) >= beam_width:
            break

    initial_beam: List[CmSiRNA] = []
    if seed_variant is not None:
        initial_beam.append(seed_variant)
        
    for result in diversified_beam:
        if len(initial_beam) >= beam_width:
            break
        variant = CmSiRNA(
            sense=result.sense,
            antisense=result.antisense,
            mod_symbol=result.mod_symbol,
            mod_position=result.mod_position,
            mod_strand=result.mod_strand,
            parent_sense=sense,
            parent_antisense=antisense,
        )
        variant.efficacy_score = result.efficacy_score
        variant.delta_score = result.delta_score
        initial_beam.append(variant)

    # Begin Expansion Rounds
    current_beam = _score_variants_batch(initial_beam)
    current_beam.sort(key=lambda x: x.efficacy_score, reverse=True)
    all_evaluated_variants = list(current_beam)

    # Pairing pool drawn from single-mod scan results across all 21 positions
    pairing_pool = sorted(single_results, key=lambda r: r.efficacy_score, reverse=True)[:beam_width * 3]

    history_best_scores = [current_beam[0].efficacy_score if current_beam else 0.0]

    for iteration in range(2, max_mods + 1):
        round_best_score = current_beam[0].efficacy_score if current_beam else 0.0
        history_best_scores.append(round_best_score)
        round_candidates = []
        explored_pairs = set()

        def _generate_signature(v: Any) -> tuple:
            return (
                getattr(v, 'mod_symbol', ''), 
                getattr(v, 'mod_position', 0), 
                getattr(v, 'mod_strand', ''), 
                getattr(v, 'mod_positions', '')
            )

        for base_variant in current_beam:
            for addon_variant in pairing_pool:
                sig_1 = _generate_signature(base_variant)
                sig_2 = _generate_signature(addon_variant)
                pair_signature = tuple(sorted([sig_1, sig_2]))
                
                if pair_signature in explored_pairs:
                    continue
                    
                explored_pairs.add(pair_signature)

                # Merge modifications
                mutable_sense = list(base_variant.parent_sense)
                mutable_antisense = list(base_variant.parent_antisense)
                tracking_symbols = []
                tracking_positions = []
                tracking_strands = []

                # Restore base variant modifications
                for i in range(len(sense)):
                    if base_variant.sense[i] != base_variant.parent_sense[i]:
                        mutable_sense[i] = base_variant.sense[i]
                        tracking_symbols.append(base_variant.sense[i])
                        tracking_positions.append(i + 1)
                        tracking_strands.append("sense")
                        
                for i in range(len(antisense)):
                    if base_variant.antisense[i] != base_variant.parent_antisense[i]:
                        mutable_antisense[i] = base_variant.antisense[i]
                        tracking_symbols.append(base_variant.antisense[i])
                        tracking_positions.append(i + 1)
                        tracking_strands.append("antisense")

                # Apply new addon modification
                if addon_variant.mod_strand == "sense":
                    if mutable_sense[addon_variant.mod_position - 1] != sense[addon_variant.mod_position - 1]:
                        continue  # Position already modified, skip clash
                    mutable_sense[addon_variant.mod_position - 1] = addon_variant.mod_symbol
                else:
                    if mutable_antisense[addon_variant.mod_position - 1] != antisense[addon_variant.mod_position - 1]:
                        continue
                    mutable_antisense[addon_variant.mod_position - 1] = addon_variant.mod_symbol
                    
                tracking_symbols.append(addon_variant.mod_symbol)
                tracking_positions.append(addon_variant.mod_position)
                tracking_strands.append(addon_variant.mod_strand)

                # Check chemical viability (terminal position limits, single-instance 5'-VP/conjugates, steric bulky limits)
                if not _is_chemically_viable("".join(mutable_sense), sense, "".join(mutable_antisense), antisense):
                    continue

                round_candidates.append(CmSiRNA(
                    sense="".join(mutable_sense),
                    antisense="".join(mutable_antisense),
                    mod_symbol="+".join(tracking_symbols),
                    mod_position=tracking_positions[0],
                    mod_positions=",".join(str(p) for p in tracking_positions),
                    mod_strand="+".join(tracking_strands),
                    parent_sense=sense,
                    parent_antisense=antisense,
                ))

        scored_candidates = _score_variants_batch(round_candidates)
        scored_candidates.sort(key=lambda v: v.efficacy_score, reverse=True)
        
        current_beam = scored_candidates[:beam_width]
        all_evaluated_variants.extend(scored_candidates)

    # Deduplicate based on exact sequence string to prevent permutations clogging the top 100
    unique_variants = {}
    for v in all_evaluated_variants:
        seq_key = v.sense + "|" + v.antisense
        # If we somehow have identical sequences with different scores, keep the highest
        if seq_key not in unique_variants or v.efficacy_score > unique_variants[seq_key].efficacy_score:
            unique_variants[seq_key] = v
            
    final_variants = list(unique_variants.values())
    final_variants.sort(key=lambda v: v.efficacy_score, reverse=True)
    
    # If model_key is IEEE_v5, Ensemble_v4, or GNN_v2, score the final top 100 variants using that model
    if model_key in ["IEEE_v5", "Ensemble_v4", "GNN_v2"] and final_variants:
        top_candidates = final_variants[:100]
        
        if model_key == "IEEE_v5":
            try:
                from helixzero_ieee_v5.predict_ieee_v5 import predict_sirna_potency_batch
                s_seqs = [v.parent_sense or v.sense for v in top_candidates]
                a_seqs = [v.parent_antisense or v.antisense for v in top_candidates]
                s_mods = [v.sense for v in top_candidates]
                a_mods = [v.antisense for v in top_candidates]
                v5_batch_res = predict_sirna_potency_batch(
                    sense_seqs=s_seqs, anti_seqs=a_seqs,
                    sense_mods_list=s_mods, anti_mods_list=a_mods,
                    conc_nM=10.0
                )
                for variant, v5_res in zip(top_candidates, v5_batch_res):
                    variant.estimated_pIC50 = v5_res["estimated_pIC50"]
                    variant.estimated_IC50_nM = v5_res["estimated_IC50_nM"]
                    variant.predicted_knockdown_pct = v5_res["predicted_knockdown_pct"]
                    variant.efficacy_score = round(v5_res["predicted_knockdown_pct"], 2)
                    variant.delta_score = round(v5_res["predicted_knockdown_pct"] - parent_adjusted_score, 2)
            except Exception as e:
                logger.error(f"IEEE v5 candidate batch scoring failed: {e}")
        else:
            s_list = [v.sense for v in top_candidates]
            a_list = [v.antisense for v in top_candidates]
            ps_list = [v.parent_sense for v in top_candidates]
            pa_list = [v.parent_antisense for v in top_candidates]
            
            target_scores = _predict_model_b(s_list, a_list, ps_list, pa_list, model_key=model_key)
            for variant, raw_score in zip(top_candidates, target_scores):
                adj_score, penalties, _ = calculate_adjusted_efficacy(
                    float(raw_score), variant.sense, variant.antisense,
                    variant.parent_sense, variant.parent_antisense
                )
                variant.efficacy_score = round(adj_score, 2)
                variant.delta_score = round(adj_score - parent_adjusted_score, 2)
                variant.penalties = penalties
            
        final_variants.sort(key=lambda v: v.efficacy_score, reverse=True)
    
    logger.info(f"Beam search complete. Evaluated {len(all_evaluated_variants)} total permutations in fast mode. Returning {len(final_variants)} unique sequences.")
    return final_variants
