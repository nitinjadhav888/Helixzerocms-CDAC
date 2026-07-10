"""
features.py — Feature extraction for ML models.

Two pipelines:
1. Phase 2 (Modified siRNAs): 431-dim chemical-category encoding + aggregate stats + engineered features
2. V4 (Naked siRNAs): 214-dim sequence-composition (one-hot + TNC + GC)
"""

from typing import List, Optional, Dict
import numpy as np
from collections import Counter


# ─── Model B (Modified) Feature Extractor ─────────────────────────────────────

# Mapping of raw modification symbols to semantic feature names
_MODIFICATION_MAP: Dict[str, str] = {
    'F': 'is_2F', 'M': 'is_2OMe', 'L': 'is_LNA',
    'D': 'is_DNA', 'E': 'is_MOE',
    'B': 'is_Benzyl', 'N': 'is_4thio', 'I': 'is_FANA',
    'Z': 'is_ZOMe', 'Y': 'is_ENA',
    'S': 'is_PS', 'P': 'is_Borano',
    'R': 'is_MePhos', 'H': 'is_PhosAmid',
    'V': 'is_m5C', 'W': 'is_PseudoU',
    'J': 'is_Inosine', 'K': 'is_2thioU', 'O': 'is_DihydroU',
    '1': 'is_5Phos', '2': 'is_3P',
    '3': 'is_5OMe', '5': 'is_PEG',
    '6': 'is_UNA', '7': 'is_ANA',
    '8': 'is_GNA', '9': 'is_TNA',
    '4': 'is_Conj', 'Q': 'is_Abasic',
    'U': 'is_ModU', 'X': 'is_ModX',
}

_MOD_CATEGORIES: List[str] = sorted(
    {value.replace('is_', '') for value in _MODIFICATION_MAP.values()}
)

# ─── Phase 2: Chemical-category encoding ──────────────────────────────────────
# Instead of 31-way one-hot per position, group by chemical function.
# Split is_other_ribose into is_bulky_ribose (LNA/MOE/ENA — sterically hindered)
# and is_flexible_ribose (FANA, UNA, GNA, etc. — more flexible backbones).
# This better separates clinically relevant chemical classes for ML learning.

_CHEM_CATEGORIES: Dict[str, List[str]] = {
    'is_2F':            ['F'],
    'is_2OMe':          ['M'],
    'is_bulky_ribose':  ['L', 'E', 'Y'],  # LNA, MOE, ENA — sterically hindered
    'is_flexible_ribose': ['I', 'Z', 'N', '6', '7', '8', '9'],  # FANA, ZOMe, 4thio, UNA, ANA, GNA, TNA
    'is_backbone_mod':  ['S', 'P', 'R', 'H', '1', '2', '3', '5'],
    'is_base_mod':      ['V', 'W', 'J', 'K', 'O'],
    'is_other':         ['B', '4', 'Q', 'U', 'X'],
}

# Build reverse map: mod_char -> category name
_CHEM_CHAR_TO_CAT: Dict[str, str] = {}
for cat_name, chars in _CHEM_CATEGORIES.items():
    for ch in chars:
        _CHEM_CHAR_TO_CAT[ch] = cat_name

_CHEM_CATEGORY_NAMES: List[str] = sorted(_CHEM_CATEGORIES.keys())
_N_CHEM_CATS = len(_CHEM_CATEGORY_NAMES)  # 7
_N_POSITIONAL_FLAGS_P2 = _N_CHEM_CATS + 1  # 7 categories + is_modified = 8


# ─── Phase 2 Feature Extractor (Chemical category encoding) ────────────────────

def _get_chem_category(mod_char: str) -> str:
    """Map a modification character to its chemical category."""
    return _CHEM_CHAR_TO_CAT.get(mod_char, 'is_other')


def _make_nucleotide_array(seq: str, base_seq: str, length: int = 21) -> np.ndarray:
    """
    Build a (length, n_cats+1) array: for each position, a one-hot over
    chemical categories + is_modified flag.
    Returns shape (length, n_flags).
    """
    n_flags = _N_POSITIONAL_FLAGS_P2  # 7 cats + 1 is_modified = 8
    arr = np.zeros((length, n_flags), dtype=np.float32)
    for pos in range(min(len(seq), length)):
        nuc = seq[pos]
        base_nuc = base_seq[pos] if pos < len(base_seq) else ''
        if nuc != base_nuc:
            cat = _get_chem_category(nuc)
            if cat in _CHEM_CATEGORY_NAMES:
                arr[pos, _CHEM_CATEGORY_NAMES.index(cat)] = 1.0
            arr[pos, n_flags - 1] = 1.0  # is_modified
    return arr


def _new_engineered_features(sense: str, antisense: str,
                              base_sense: str, base_antisense: str) -> List[float]:
    """Engineered biological features added in Phase 2."""
    eng: List[float] = []

    def gc_content(seq: str) -> float:
        if not seq:
            return 0.5
        return sum(1 for c in seq[:21].upper() if c in 'GC') / min(len(seq), 21)

    def count_mods(seq: str, base_seq: str, chars: str) -> int:
        return sum(1 for i in range(min(len(seq), 21))
                   if i < len(base_seq) and seq[i] != base_seq[i] and seq[i] in chars)

    sense_gc = gc_content(base_sense)
    anti_gc = gc_content(base_antisense)
    
    # 1. Wing GC asymmetry (absolute difference)
    eng.append(abs(sense_gc - anti_gc))
    
    # 2. Seed region (pos 2-8) modification density (antisense)
    seed_mods = sum(1 for i in range(1, min(8, len(antisense)))
                    if i < len(base_antisense) and antisense[i] != base_antisense[i])
    eng.append(seed_mods / 7.0)
    
    # 3. Seed 2F/2OMe alternation score (antisense pos 2-8)
    seed_alt = 0
    for i in range(1, min(7, len(antisense))):
        c1 = antisense[i] if i < len(antisense) and antisense[i] != (base_antisense[i] if i < len(base_antisense) else '') else ''
        c2 = antisense[i+1] if i+1 < len(antisense) and antisense[i+1] != (base_antisense[i+1] if i+1 < len(base_antisense) else '') else ''
        if c1 in ('F', 'M') and c2 in ('F', 'M') and c1 != c2:
            seed_alt += 1
    eng.append(seed_alt / 6.0 if min(7, len(antisense)) > 1 else 0.0)
    
    # 4. Cleavage zone (pos 9-11) total modification burden
    cleave_mods = sum(1 for i in range(8, min(11, len(antisense)))
                      if i < len(base_antisense) and antisense[i] != base_antisense[i])
    eng.append(cleave_mods / 3.0)
    
    # 5. 5' PS protection density (first 3 positions, sense + antisense)
    for strand_key, seq, base_seq in [
        ("ss", sense, base_sense), ("as", antisense, base_antisense)
    ]:
        ps_5 = sum(1 for i in range(min(3, len(seq))) if seq[i] == 'S')
        eng.append(ps_5 / 3.0)
    
    # 6. 3' PS protection density (last 3 positions, sense + antisense)
    for strand_key, seq, base_seq in [
        ("ss", sense, base_sense), ("as", antisense, base_antisense)
    ]:
        ps_3 = sum(1 for i in range(max(0, len(seq)-3), len(seq)) if i < len(seq) and seq[i] == 'S')
        eng.append(ps_3 / 3.0)
    
    # 7. Modification Shannon entropy per strand
    for strand_key, seq, base_seq in [
        ("ss", sense, base_sense), ("as", antisense, base_antisense)
    ]:
        counts: Dict[str, int] = {}
        total = 0
        for i in range(min(len(seq), 21)):
            if i < len(base_seq) and seq[i] != base_seq[i]:
                ch = seq[i]
                counts[ch] = counts.get(ch, 0) + 1
                total += 1
        entropy = 0.0
        if total > 0:
            for c in counts.values():
                p = c / total
                entropy -= p * np.log2(p) if p > 0 else 0
        eng.append(entropy / np.log2(7) if total > 1 else 0.0)  # normalize to [0,1]
    
    # 8. Terminal GC clamp (last 2 bases, sense + antisense)
    for strand_key, seq in [("ss", base_sense), ("as", base_antisense)]:
        tail = seq[-2:] if len(seq) >= 2 else seq
        gc_tail = sum(1 for c in tail.upper() if c in 'GC')
        eng.append(gc_tail / len(tail) if tail else 0.5)
    
    # 9. 5' sense base identity (A/U vs G/C — affects RISC loading)
    for strand_key, seq in [("ss", base_sense), ("as", base_antisense)]:
        first = seq[0].upper() if seq else 'A'
        eng.append(float(first in 'GC'))
    
    return eng


def extract_phase2(
    sense_list: List[str],
    antisense_list: List[str],
    base_sense_list: Optional[List[str]] = None,
    base_antisense_list: Optional[List[str]] = None,
    conc_list: Optional[List[float]] = None,
) -> np.ndarray:
    """
    Phase 2 feature extraction (431 dimensions after category split).
    
    Replaces 31-way one-hot positional encoding with 8 chemical-category flags
    (split from 7 to better separate bulky vs flexible ribose modifications),
    keeps all proven aggregate features, and adds engineered biological features.
    """
    num_samples = len(sense_list)
    base_senses = base_sense_list if base_sense_list is not None else [None] * num_samples
    base_antisenses = base_antisense_list if base_antisense_list is not None else [None] * num_samples
    concentrations = conc_list if conc_list is not None else [None] * num_samples
    
    # Pre-compute dimension sizes
    n_pos_flags = _N_POSITIONAL_FLAGS_P2  # 8
    n_pos_total = n_pos_flags * 21 * 2  # 336
    n_counts = len(_MOD_CATEGORIES)  # 31
    n_strand_agg = n_counts + 9  # 31 + fraction_modified, seed_2f, seed_2ome, cleave_2f, cleave_2ome, cleave_lna, gc_content, term_5_ps, term_3_ps = 40
    n_agg_total = n_strand_agg * 2  # 80
    n_exp = 1  # log_concentration
    n_eng = 14  # engineered features
    
    n_total = n_pos_total + n_agg_total + n_exp + n_eng  # 336 + 80 + 1 + 14 = 431
    
    feature_matrix = np.zeros((num_samples, n_total), dtype=np.float32)
    
    for row_idx in range(num_samples):
        sense = sense_list[row_idx]
        anti = antisense_list[row_idx]
        bs = base_senses[row_idx] if base_senses[row_idx] is not None else sense
        ba = base_antisenses[row_idx] if base_antisenses[row_idx] is not None else anti
        conc = concentrations[row_idx]
        
        row_features = []
        
        # ── A. Positional chemical-category encoding ──
        for seq, base_seq in [(sense, bs), (anti, ba)]:
            arr = _make_nucleotide_array(seq, base_seq, 21)
            row_features.extend(arr.flatten().tolist())
        
        # ── B. Aggregate chemistry (mod counts) ──
        for seq, base_seq in [(sense, bs), (anti, ba)]:
            seq_len = min(len(seq), 21)
            mod_counts = Counter()
            total_mods = 0
            for i in range(seq_len):
                nuc = seq[i]
                base_nuc = base_seq[i] if i < len(base_seq) else ''
                if nuc != base_nuc:
                    total_mods += 1
                    type_name = _MODIFICATION_MAP.get(nuc, '').replace('is_', '')
                    if type_name:
                        mod_counts[type_name] += 1
            
            for mod_type in _MOD_CATEGORIES:
                row_features.append(float(mod_counts[mod_type]))
            
            fraction_modified = total_mods / 21.0
            
            # Sub-region: Seed (2-8) and Cleavage (9-11)
            seed_2f = sum(1 for p in range(1, 8) if p < seq_len and seq[p] == 'F')
            seed_2ome = sum(1 for p in range(1, 8) if p < seq_len and seq[p] == 'M')
            cleave_2f = sum(1 for p in range(8, 11) if p < seq_len and seq[p] == 'F')
            cleave_2ome = sum(1 for p in range(8, 11) if p < seq_len and seq[p] == 'M')
            cleave_lna = sum(1 for p in range(8, 11) if p < seq_len and seq[p] == 'L')
            
            gc_count = sum(1 for char in base_seq[:21].upper() if char in ('G', 'C'))
            gc_content_val = gc_count / min(len(base_seq), 21) if base_seq else 0.5
            
            term_5_ps = 1.0 if (len(seq) > 0 and seq[0] == 'S') else 0.0
            term_3_ps = 1.0 if (len(seq) > 20 and seq[20] == 'S') else 0.0
            
            row_features.extend([
                fraction_modified,
                seed_2f / 7.0,
                seed_2ome / 7.0,
                float(cleave_2f),
                float(cleave_2ome),
                float(cleave_lna),
                gc_content_val,
                term_5_ps,
                term_3_ps,
            ])
        
        # ── C. Experimental parameters ──
        if conc is not None and conc > 0:
            log_conc = float(np.log1p(conc))
        else:
            log_conc = float(np.log1p(10.0))
        row_features.append(log_conc)
        
        # ── D. New engineered features ──
        row_features.extend(_new_engineered_features(sense, anti, bs, ba))
        
        feature_matrix[row_idx] = row_features
    
    return feature_matrix


# ─── Naked V4 (Unmodified) Feature Extractor ──────────────────────────────────

_CANONICAL_MAP = {"A": 0, "C": 1, "G": 2, "U": 3}


def _pad_sequence_to_21(sequence: str) -> str:
    """Ensures sequences are strictly 21 nucleotides via 3' Poly-A padding."""
    if len(sequence) >= 21:
        return sequence[:21]
    return sequence + "A" * (21 - len(sequence))


def extract_batch_v4(sense_list: List[str], antisense_list: List[str]) -> np.ndarray:
    """
    Batch extraction of 214-dimensional features for unmodified siRNAs.
    Includes explicit A/U/G/C positional one-hot encoding, and Tri-Nucleotide 
    Composition (TNC) normalized frequencies.
    """
    num_samples = len(sense_list)
    feature_matrix = np.zeros((num_samples, 214), dtype=np.float32)
    base_map = _CANONICAL_MAP
    
    for row_idx, (sense_seq, anti_seq) in enumerate(zip(sense_list, antisense_list)):
        padded_sense = _pad_sequence_to_21(sense_seq)
        padded_anti = _pad_sequence_to_21(anti_seq)
        
        # Positional One-Hot Encoding (4 bases * 21 pos = 84 features per strand)
        for pos in range(21):
            base_idx = base_map.get(padded_sense[pos], 0)
            feature_matrix[row_idx, (pos * 4) + base_idx] = 1.0
            
        # Tri-Nucleotide Composition (Sense) -> 64 features (4^3)
        for k in range(19):
            base_1 = base_map.get(padded_sense[k], 0)
            base_2 = base_map.get(padded_sense[k+1], 0)
            base_3 = base_map.get(padded_sense[k+2], 0)
            # Index calculation: (b1 * 16) + (b2 * 4) + b3
            feature_matrix[row_idx, 84 + (base_1 * 16) + (base_2 * 4) + base_3] += 1.0
            
        feature_matrix[row_idx, 84:148] /= 19.0  # Normalize TNC counts to frequencies
        
        # Tri-Nucleotide Composition (Antisense) -> 64 features
        for k in range(19):
            base_1 = base_map.get(padded_anti[k], 0)
            base_2 = base_map.get(padded_anti[k+1], 0)
            base_3 = base_map.get(padded_anti[k+2], 0)
            feature_matrix[row_idx, 148 + (base_1 * 16) + (base_2 * 4) + base_3] += 1.0
            
        feature_matrix[row_idx, 148:212] /= 19.0

        # Global GC content (Sense and Antisense) -> 2 features
        feature_matrix[row_idx, 212] = (padded_sense.count("G") + padded_sense.count("C")) / 21.0
        feature_matrix[row_idx, 213] = (padded_anti.count("G") + padded_anti.count("C")) / 21.0
        
    return feature_matrix
