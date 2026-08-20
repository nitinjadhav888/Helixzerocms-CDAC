"""
biophysics.py — Biophysical Penalty Engine

Calculates biophysical penalties that adjust the raw Machine Learning efficacy score.
While the ML model predicts raw silencing efficacy, it is often ignorant of real-world 
biological constraints (e.g., nuclease degradation, innate immune response, thermodynamic 
flaws). This engine enforces those physical realities.

Penalties are scaled and subtracted from the raw score, natively ranking well-balanced 
multi-mod designs above those that are over-modified (steric hindrance) or 
under-protected (degradation vulnerability).
"""

import re
import math
import logging
from typing import Dict, List, Tuple, FrozenSet, Optional, Any

from .utils import calculate_gc_percentage, has_internal_palindrome

logger = logging.getLogger(__name__)

__all__ = [
    "calculate_adjusted_efficacy",
    "calculate_nuclease_penalty",
    "calculate_immuno_penalty",
    "calculate_risc_penalty",
    "calculate_thermo_penalty",
    "calculate_serum_penalty",
    "calculate_synthesis_penalty",
]

# Set of 2' ribose modifications providing nuclease resistance
_MOD_2PRIME: FrozenSet[str] = frozenset("FMLEBD89Y")


def _has_homopolymer(sequence: str, consecutive_limit: int = 5) -> bool:
    """
    Checks for contiguous homopolymer runs (e.g., AAAAA or UUUUU).
    
    Why: Homopolymer runs cause ribosomal slippage during transcription and 
    create highly rigid localized structures that resist RISC unwinding.
    """
    upper_seq = sequence.upper()
    for base in ("A", "U", "G", "C"):
        if base * consecutive_limit in upper_seq:
            logger.debug(f"Homopolymer run of {base} detected.")
            return True
    return False


def calculate_nuclease_penalty(
    sense: str, antisense: str, base_sense: str, base_antisense: str
) -> Tuple[float, Dict[str, float]]:
    """
    Calculates the penalty for inadequate endonuclease resistance.
    
    Why: Unprotected RNA is rapidly cleaved by endogenous RNases in the bloodstream. 
    This function specifically evaluates endonuclease defence by checking the density 
    of 2' ribose modifications and the presence of phosphorothioate (PS) backbone linkages.
    
    Validated against Alnylam AT3 siRNA clinical design (Sakamuri et al. 2020, ChemBioChem):
    The optimal validated PS pattern is 4 PS on antisense (pos 0,1,20,21) + 2 PS on sense 
    (pos 0,1). Fewer or mis-positioned PS insertions lose significant nuclease stability.
    
    Args:
        sense (str): The modified sense strand.
        antisense (str): The modified antisense strand.
        base_sense (str): The unmodified parent sense strand.
        base_antisense (str): The unmodified parent antisense strand.
        
    Returns:
        Tuple[float, Dict[str, float]]: The penalty score (0.0 to 20.0) and details dict.
    """
    total_penalty = 0.0
    details = {}

    # --- PS backbone coverage (total count) ---
    ps_count = (sense + antisense).count("S")
    if ps_count == 0:
        total_penalty += 5.0
        details["Lack of PS backbone"] = 5.0
    elif ps_count < 3:
        total_penalty += 3.0
        details["Insufficient PS backbone (<3)"] = 3.0

    # --- Alnylam validated PS distribution pattern (Sakamuri et al. 2020) ---
    # Clinical design: 4 PS on antisense (positions 0,1,20,21) + 2 PS on sense (positions 0,1)
    # This positional pattern is the most nuclease-stable validated in clinical siRNA.
    as_terminal_ps = sum(1 for i in [0, 1, 20, 21] if i < len(antisense) and antisense[i] == "S")
    ss_terminal_ps = sum(1 for i in [0, 1] if i < len(sense) and sense[i] == "S")
    if ps_count >= 3:  # Only flag positional issues if there are PS mods at all
        if as_terminal_ps < 2:
            total_penalty += 2.0
            details["AS terminal PS coverage suboptimal (<2 at pos 0,1,20,21)"] = 2.0
        if ss_terminal_ps < 1:
            total_penalty += 1.0
            details["Sense terminal PS missing (pos 0 or 1)"] = 1.0

    # --- Internal PS over-density penalty ---
    # Dense internal PS (body region) impairs RISC loading and causes
    # non-specific protein binding (Sakamuri 2020). Termini-only pattern
    # (Alnylam AT3) puts PS at AS pos 0,1,20,21; internal >3 is excessive.
    as_body_ps = sum(1 for i in range(2, min(19, len(antisense))) if antisense[i] == "S")
    if as_body_ps > 3:
        total_penalty += 2.0
        details["Internal PS over-density in AS body (>3)"] = 2.0

    # --- 2'-mod density ---
    combined_strands = sense + antisense
    mod_count = sum(1 for char in combined_strands if char in _MOD_2PRIME)
    density = mod_count / 42.0  # 21 nt per strand * 2 strands
    
    if density < 0.2:
        total_penalty += 4.0
        details["Low 2'-mod density (<20%)"] = 4.0
    elif density < 0.4:
        total_penalty += 2.0
        details["Suboptimal 2'-mod density (<40%)"] = 2.0

    return min(total_penalty, 20.0), details


def calculate_immuno_penalty(
    sense: str, antisense: str, base_sense: str, base_antisense: str
) -> Tuple[float, Dict[str, float]]:
    """
    Calculates the penalty for immunostimulatory features.
    
    Why: Foreign RNA triggers the innate immune system (specifically TLR7/8) to induce 
    an interferon response, causing severe toxicity. Unmodified Uridines, especially in 
    GU-rich motifs, are primary ligands for these receptors. We check for these motifs 
    and penalize them unless masked by modifications.
    
    Args:
        sense (str): The modified sense strand.
        antisense (str): The modified antisense strand.
        base_sense (str): The unmodified parent sense strand.
        base_antisense (str): The unmodified parent antisense strand.
        
    Returns:
        float: The penalty score (0.0 to 28.0).
    """
    total_penalty = 0.0
    details = {}

    # Unmodified U in antisense seed (positions 2-8) is a strong TLR signal
    for i in range(1, min(8, len(antisense), len(base_antisense))):
        if base_antisense[i] == "U" and antisense[i] == base_antisense[i]:
            total_penalty += 2.0
            details[f"Unmodified U in AS seed (pos {i+1})"] = 2.0

    # Unmodified U in antisense tail (positions 9-21) is a secondary TLR signal
    for i in range(8, min(len(antisense), len(base_antisense))):
        if base_antisense[i] == "U" and antisense[i] == base_antisense[i]:
            total_penalty += 0.5
            details[f"Unmodified U in AS tail (pos {i+1})"] = 0.5

    # Unmodified U in sense strand (passenger strand is rapidly degraded, so lower weight)
    for i in range(min(len(sense), len(base_sense))):
        if base_sense[i] == "U" and sense[i] == base_sense[i]:
            total_penalty += 1.0
            details[f"Unmodified U in Sense (pos {i+1})"] = 1.0

    # Hierarchical search for GU-rich motifs (TLR8 ligands)
    # Expanded list validated against Goodchild 2009, Judge 2005, Heil 2004, Hornung 2005
    base_combined = list(base_sense + base_antisense)
    mod_combined = list(sense + antisense)
    covered_mask = [False] * len(base_combined)

    for motif in ["GUUGU", "GUGU", "UGU", "UUG", "UGGC", "GUUC", "GUCCUUCAA", "UGUGU"]:
        motif_len = len(motif)
        
        # Build search string masking already-penalized motifs
        search_str = "".join(
            base_combined[i] if not covered_mask[i] else "."
            for i in range(len(base_combined))
        )
        
        idx = 0
        while True:
            idx = search_str.find(motif, idx)
            if idx == -1:
                break
                
            # If the window is still entirely unmodified, apply penalty
            region_mod = mod_combined[idx : idx + motif_len]
            region_base = base_combined[idx : idx + motif_len]
            if all(m == region_base[j] for j, m in enumerate(region_mod)):
                total_penalty += 3.0
                details[f"Unmasked TLR motif '{motif}'"] = details.get(f"Unmasked TLR motif '{motif}'", 0.0) + 3.0
                for j in range(idx, idx + motif_len):
                    covered_mask[j] = True
            idx += 1

    # AU-rich motifs (TLR8 agonists — Hornung 2005, Forsbach 2008)
    for motif in ["AUUU", "UAUU", "AAUU"]:
        motif_len = 4
        search_str = "".join(
            base_combined[i] if not covered_mask[i] else "."
            for i in range(len(base_combined))
        )
        idx = 0
        while True:
            idx = search_str.find(motif, idx)
            if idx == -1:
                break
            region_mod = mod_combined[idx : idx + 4]
            region_base = base_combined[idx : idx + 4]
            if all(m == region_base[j] for j, m in enumerate(region_mod)):
                total_penalty += 2.0
                details[f"Unmasked TLR motif '{motif}'"] = details.get(f"Unmasked TLR motif '{motif}'", 0.0) + 2.0
                for j in range(idx, idx + 4):
                    covered_mask[j] = True
            idx += 1

    # Over-methylation advisory: Extreme 2'-OMe saturation causes off-target tox
    if (sense + antisense).count("M") > 24:
        total_penalty += 4.0
        details["Extreme 2'-OMe saturation (>24)"] = 4.0

    return min(total_penalty, 28.0), details


def calculate_risc_penalty(
    sense: str, antisense: str, base_sense: str, base_antisense: str
) -> Tuple[float, Dict[str, float]]:
    """
    Calculates the penalty for impaired RISC loading or Ago2 slicer activity.
    
    Why: Heavy or bulky chemical modifications (like LNA or MOE) in the critical 
    seed region or cleavage site physically obstruct the Ago2 protein from anchoring 
    onto the RNA. This algorithm enforces positional chemistry constraints.
    
    Args:
        sense (str): The modified sense strand.
        antisense (str): The modified antisense strand.
        base_sense (str): The unmodified parent sense strand.
        base_antisense (str): The unmodified parent antisense strand.
        
    Returns:
        float: The penalty score (Range: -10.0 to +60.0). Can be negative (beneficial).
    """
    total_penalty = 0.0
    details = {}

    # 5'-phosphate ("1") is strictly required for the Ago2 MID domain anchor
    if antisense[0] != "1":
        total_penalty += 5.0
        details["Missing 5'-phosphate anchor"] = 5.0

    # Bulky modifications in the seed region (2-8) impair target recognition.
    # Only genuinely bulky/modified-backbone sugars are penalized — standard
    # 2'-F and 2'-OMe (ESC chemistry, all FDA-approved siRNAs) are NOT bulky.
    # Hoerter & Walter 2007 (RNA 13:1887) confirms 2'-OMe at AS 5'-end is
    # protective against exonucleolytic degradation, not disruptive to RISC.
    # UNA ("6") at position 7 is exempt (Bramsen 2010 — therapeutic off-target
    # disruption). GNA ("8") has its own specific rules below.
    _BULKY_SEED_MODS: FrozenSet[str] = frozenset(
        "L"   # LNA — locked ribose, rigid
        "E"   # MOE — large 2'-O-methoxyethyl side chain
        "B"   # Benzyl — aromatic ribose substituent
        "Y"   # ENA — ethylene-bridged, rigid
        "9"   # TNA — threose backbone, shifted register
        "D"   # DNA — B-form helix, suboptimal in A-form seed
    )
    # GNA ("8") has its own positional rules below (+4 early, -2 late)
    # and is NOT included here to avoid double-counting.
    seed_mods = sum(
        1 for i in range(1, min(8, len(antisense), len(base_antisense)))
        if antisense[i] in _BULKY_SEED_MODS
        and antisense[i] != base_antisense[i]
        and not (antisense[i] == "6" and i == 6)
    )
    if seed_mods > 0:
        total_penalty += seed_mods * 2.0
        details[f"Bulky seed modifications ({seed_mods})"] = seed_mods * 2.0

    # ── Elmén 2005 (PMC546170): LNA at antisense 5' position abolishes activity ──
    # Tested in siLNA8-11 (firefly), siLNA15 (Renilla), siLNA20 (NPY) — all dead
    # Even 5'-phosphorylation did not rescue lost activity
    # Separate from and additive with the 5'-phosphate check above
    if antisense[0] == "L":
        total_penalty += 8.0
        details["LNA at AS 5' pos (abolishes activity, Elmén 2005)"] = 8.0

    # LNA ("L") in early seed positions 2-4 creates rigid helix incompatible with Ago2
    for i in range(1, min(4, len(antisense))):
        if antisense[i] == "L":
            total_penalty += 5.0
            details[f"LNA in early seed (pos {i+1})"] = 5.0

    # ── Elmén 2005 Fig 3: LNA at AS positions 10, 12, 14 disrupts catalytic cleft ──
    # These positions flank the Ago2 cleavage site (between pos 10-11)
    # Position 10 (directly at cleavage) is most damaging; 14 is more variable.
    _LNA_CLEFT_WEIGHTS = {9: 4.0, 11: 3.0, 13: 2.0}  # 0-indexed → paper's 10,12,14
    for i, w in _LNA_CLEFT_WEIGHTS.items():
        if i < len(antisense) and antisense[i] == "L":
            total_penalty += w
            details[f"LNA at catalytic cleft (AS pos {i+1}, weight={w:.0f}, Elmén 2005)"] = w

    # MOE ("E") is bulky and disrupts the central catalytic cleft (positions 3-12)
    # Positions 1-2 and 13+ are clinically validated in Inclisiran (FDA 2021)
    for i in range(2, min(12, len(antisense))):
        if antisense[i] == "E":
            total_penalty += 3.0
            details[f"MOE in catalytic cleft (pos {i+1})"] = 3.0

    # GNA ("8") is disruptive in the early seed (2-5), but therapeutically
    # beneficial at exactly position 7 (ESC+ design, Schlegel 2022).
    # Only position 7 has clinical proof of off-target seed-disruption benefit.
    for i in range(1, min(5, len(antisense))):
        if antisense[i] == "8":
            total_penalty += 4.0
            details[f"GNA in early seed (pos {i+1})"] = 4.0
    if len(antisense) > 6 and antisense[6] == "8":
        total_penalty -= 2.0
        details["GNA at pos 7 (therap. bonus, off-target disruption)"] = -2.0

    # ENA ("Y") causes severe steric clash in the seed, and over-stabilization in the body
    for i in range(1, min(8, len(antisense))):
        if antisense[i] == "Y":
            total_penalty += 4.0
            details[f"ENA in seed (pos {i+1})"] = 4.0
    for i in range(8, min(14, len(antisense))):
        if antisense[i] == "Y":
            total_penalty += 2.0
            details[f"ENA over-stabilization (pos {i+1})"] = 2.0

    # TNA ("9") backbone shift disrupts Ago2 register in seed, but position 7 is exempt
    for i in range(1, min(6, len(antisense))):
        if antisense[i] == "9":
            total_penalty += 3.0
            details[f"TNA in seed (pos {i+1})"] = 3.0
    for i in range(7, min(14, len(antisense))):
        if antisense[i] == "9":
            total_penalty += 1.0
            details[f"TNA in body (pos {i+1})"] = 1.0

    # 2'-F on pyrimidines maintains A-form helix geometry across the siRNA duplex.
    # ESC chemistry places 2'-F on both strands; checking only antisense would
    # miss sense-strand 2'-F coverage which contributes to duplex stability.
    def _f_on_pyrimidines(strand, base_strand):
        max_len = min(len(strand), len(base_strand))
        return sum(1 for i in range(max_len) if strand[i] == "F" and base_strand[i] in "UC")
    def _total_pyrimidines(base_strand):
        return sum(1 for b in base_strand if b in "UC")
    
    combined_f = _f_on_pyrimidines(sense, base_sense) + _f_on_pyrimidines(antisense, base_antisense)
    combined_py = _total_pyrimidines(base_sense) + _total_pyrimidines(base_antisense)
    
    if combined_py > 0:
        if (combined_f / combined_py) < 0.2:
            total_penalty += 6.0
            details["Low 2'-F pyrimidine coverage across duplex (<20%)"] = 6.0
        elif (combined_f / combined_py) < 0.4:
            total_penalty += 3.0
            details["Suboptimal 2'-F pyrimidine coverage across duplex (<40%)"] = 3.0

    # Exotic modification micro-penalties to break ties and reflect biological uncertainty
    exotic_mods = frozenset("BJVINOPRHKZQWX7")
    exotic_count = sum(1 for char in antisense if char in exotic_mods)
    if exotic_count > 0:
        total_penalty += exotic_count * 1.0
        details[f"Exotic modifications ({exotic_count})"] = exotic_count * 1.0
        
    if "B" in antisense:
        total_penalty += 1.0
        details["B modification penalty"] = 1.0
    if "J" in antisense:
        total_penalty += 1.0
        details["J modification penalty"] = 1.0

    return min(max(total_penalty, -10.0), 60.0), details


def calculate_thermo_penalty(
    sense: str, antisense: str, base_sense: str, base_antisense: str
) -> Tuple[float, Dict[str, float]]:
    """
    Calculates the penalty for thermodynamically unfavorable sequences.
    
    Why: Extreme GC content, homopolymers, and internal palindromes create 
    hyper-stable secondary structures (like hairpins) that resist unwinding 
    by the RISC helicase.
    """
    total_penalty = 0.0
    details = {}
    base_seq = base_sense.upper()

    gc_content = calculate_gc_percentage(base_seq)
    # Heavily modified siRNAs (PS + 2'-F/OMe) tolerate wider GC ranges
    # than unmodified RNA. Penalties reduced and ranges widened per
    # modern clinical evidence (patisiran GC=33%, inclisiran GC=42%).
    if gc_content < 25.0 or gc_content > 72.0:
        total_penalty += 6.0
        details[f"Extreme GC Content ({gc_content:.1f}%)"] = 6.0
    elif gc_content < 32.0 or gc_content > 62.0:
        total_penalty += 3.0
        details[f"Suboptimal GC Content ({gc_content:.1f}%)"] = 3.0

    if has_internal_palindrome(base_seq):
        total_penalty += 5.0
        details["Internal Palindrome detected"] = 5.0

    if _has_homopolymer(base_seq):
        total_penalty += 5.0
        details["Homopolymer run detected"] = 5.0

    # Schwarz/Khvorova 2003: Thermodynamic asymmetry for RISC strand loading.
    # RISC loads the strand with the weaker (more AU-rich) 5' end.
    # Using RNA nearest-neighbor ΔG at 37°C (Xia et al. 1998) instead of simple GC-count,
    # because ΔG captures sequence-context effects (e.g., AG vs GA have different stabilities).
    _RNA_NN_DG = {
        'AA': -0.93, 'AU': -1.10, 'AC': -2.24, 'AG': -2.08,
        'UA': -1.33, 'UU': -0.93, 'UC': -1.43, 'UG': -2.70,
        'CA': -1.78, 'CU': -1.70, 'CC': -2.70, 'CG': -2.36,
        'GA': -1.70, 'GU': -1.78, 'GC': -2.08, 'GG': -2.70,
    }
    def _terminus_dg(seq: str, n: int = 4) -> float:
        s = seq[:n].upper().replace('T', 'U')
        return sum(_RNA_NN_DG.get(s[i:i+2], -1.5) for i in range(len(s) - 1))
    sense_5p_dg = _terminus_dg(base_sense)
    guide_5p_dg = _terminus_dg(base_antisense)
    # Sense 5' end should be more stable (more negative ΔG) than guide 5' end
    # If guide end is more stable (more negative), RISC may load sense strand
    if sense_5p_dg >= guide_5p_dg:
        total_penalty += 3.0
        details[f"Thermodynamic asymmetry: sense ΔG ({sense_5p_dg:.2f}) >= guide ΔG ({guide_5p_dg:.2f})"] = 3.0

    if re.search(r"[GC]{6}", base_seq):
        total_penalty += 3.0
        details["GC-heavy block detected (6+)"] = 3.0

    return min(total_penalty, 20.0), details


def calculate_serum_penalty(
    sense: str, antisense: str, base_sense: str, base_antisense: str
) -> Tuple[float, Dict[str, float]]:
    """
    Calculates the penalty for poor serum stability at the termini.
    
    Why: Exonucleases rapidly digest RNA from the 5' and 3' exposed ends in serum. 
    This checks for terminal protections, such as phosphorothioates ("S"), 
    5'-phosphates ("1"), or GalNAc conjugates ("4") acting as steric shields.

    GalNAc conjugate position rules validated by Weingärtner et al. 2020 
    (Molecular Therapy: Nucleic Acids, Silence Therapeutics):
    - GalNAc at antisense 5' end → COMPLETELY INACTIVE regardless of valency
    - GalNAc at both sense termini (5' AND 3') → 3-4× superior in vivo potency
    - Single GalNAc unit alone → significantly reduced activity vs. 2+ units
    """
    total_penalty = 0.0
    details = {}

    # --- CRITICAL: GalNAc at antisense 5' is experimentally proven to abolish activity ---
    # Weingärtner et al. 2020: "5' antisense GalNAc conjugates were inactive" in all valencies
    if antisense[0] == "4":
        total_penalty += 40.0
        details["FATAL: GalNAc at AS 5' end abolishes activity (Weingärtner 2020)"] = 40.0

    # --- Unprotected antisense termini ---
    # Only conjugates ("4") and cap analogs block exonucleases at the 5' terminus.
    # 2'-sugar mods (F, M, L, E, etc.) do NOT protect against 5'→3' exonucleases.
    if antisense[0] in ("4",):
        pass  # Conjugate protecting 5' terminus
    elif antisense[0] not in ("S", "1"):
        total_penalty += 4.0
        details["Unprotected AS 5' terminus"] = 4.0
    if len(antisense) > 20 and antisense[20] not in ("S", "1"):
        total_penalty += 3.0
        details["Unprotected AS 3' terminus"] = 3.0

    # --- Unprotected sense termini ---
    if sense[0] not in ("S", "4"):
        total_penalty += 3.0
        details["Unprotected Sense 5' terminus"] = 3.0
    if len(sense) > 20 and sense[20] not in ("S", "4"):
        total_penalty += 2.0
        details["Unprotected Sense 3' terminus"] = 2.0

    # --- GalNAc valency and position bonus/penalty (Weingärtner et al. 2020) ---
    galnac_count = (sense + antisense).count("4")
    sense_5p_galnac = sense[0] == "4"
    sense_3p_galnac = len(sense) > 20 and sense[20] == "4"

    if galnac_count == 1 and sense[0] == "4":
        # Single GalNAc at sense 5' — active but suboptimal; paper shows 3-4x less potent in vivo
        total_penalty += 3.0
        details["Single GalNAc only — reduced in vivo potency (Weingärtner 2020)"] = 3.0
    elif sense_5p_galnac and sense_3p_galnac:
        # Dual-terminal sense GalNAc — the novel superior design from paper
        # 3-4x better than triantennary at 0.3 mg/kg; improved lysosomal stability
        total_penalty -= 5.0
        details["Dual-terminal Sense GalNAc bonus (3-4x potency, Weingärtner 2020)"] = -5.0

    return min(max(total_penalty, -5.0), 60.0), details


def calculate_synthesis_penalty(
    sense: str, antisense: str, base_sense: str, base_antisense: str
) -> Tuple[float, Dict[str, float]]:
    """
    Calculates the penalty for Solid-Phase Oligonucleotide Synthesis (SPOS) manufacturability.
    
    Why: A sequence scoring 90 on biological fitness is commercially worthless if it cannot 
    be reliably synthesized at scale. SPOS builds 3'->5'. Coupling efficiency drops compound 
    exponentially across 20 steps. Problematic motifs cause premature termination, 
    aggregation, or HPLC purification failures.
    
    Validated against modern ESC+ manufacturing constraints (Alnylam 2020+):
    - Standard 6-PS ESC+ chemistry must NOT be penalized.
    - 2'-modified RNA is immune to traditional DNA depurination rules.
    """
    total_penalty = 0.0
    details = {}
    
    # Strip modification symbols to get pure base sequences for motif checks
    clean_sense = ''.join(c for c in sense if c in 'AUCG')
    clean_anti = ''.join(c for c in antisense if c in 'AUCG')
    
    strands_to_check = [
        ("Sense", clean_sense, sense),
        ("Antisense", clean_anti, antisense),
    ]
    
    for strand_name, base_seq, mod_seq in strands_to_check:
        upper_base = base_seq.upper()
        
        # Rule 1: G-Run Detection (G-Quadruplex Risk)
        # >=4 consecutive Gs physically clog CPG column pores.
        # Pon & Yu 2004, Nucleosides Nucleotides
        if re.search(r'G{5,}', upper_base):
            total_penalty += 8.0
            details[f"Severe G-run (5+) in {strand_name}"] = 8.0
        elif re.search(r'G{4}', upper_base):
            total_penalty += 4.0
            details[f"G-run (4) in {strand_name}"] = 4.0
        
        # Rule 2: Consecutive GC Block Detection
        # >=6 contiguous G/C causes hyperstacking and HPLC aggregation.
        if re.search(r'[GC]{6,}', upper_base):
            total_penalty += 4.0
            details[f"GC block (6+) in {strand_name}"] = 4.0
        
        # Rule 3: Homopolymer Run Detection (Non-G)
        # Poly-A/U coupling slippage, Poly-C i-motifs. 5+ identical bases.
        # G-runs excluded here (handled by Rule 1 with higher penalty).
        if re.search(r'([AUC])\1{4,}', upper_base):
            total_penalty += 3.0
            details[f"Non-G homopolymer (5+) in {strand_name}"] = 3.0
        
        # Rule 4: Depurination Risk (DNA-SPECIFIC ONLY)
        # MODERN SCIENCE: 2'-modified RNA (F, M, L, etc.) is sterically protected
        # against acid-catalyzed depurination. This rule ONLY applies to 
        # unmodified DNA ('D') insertions (LeProust 2010, Caruthers 2022).
        dna_runs = re.findall(r'D{4,}', mod_seq)
        if dna_runs:
            max_dna_run = max(len(run) for run in dna_runs)
            if max_dna_run >= 6:
                total_penalty += 4.0
                details[f"DNA depurination risk ({max_dna_run} 'D's) in {strand_name}"] = 4.0
            else:
                total_penalty += 2.0
                details[f"Minor DNA stretch in {strand_name}"] = 2.0
        
        # Rule 5: Consecutive Bulky Modification Coupling Stress
        # LNA/MOE/ENA have reduced coupling efficiency due to steric hindrance.
        # Consecutive instances cause step-wise yield drops that compound.
        bulky_consec = 0
        max_bulky_consec = 0
        for char in mod_seq:
            if char in ('L', 'E', 'Y'):
                bulky_consec += 1
                max_bulky_consec = max(max_bulky_consec, bulky_consec)
            else:
                bulky_consec = 0
        if max_bulky_consec >= 4:
            total_penalty += 6.0
            details[f"Severe bulky mod stacking ({max_bulky_consec} consec) in {strand_name}"] = 6.0
        elif max_bulky_consec >= 3:
            total_penalty += 4.0
            details[f"Bulky mod stacking (3 consec) in {strand_name}"] = 4.0
        
        # Rule 7: Self-Complementary / Hairpin Risk (Hybridization)
        # After synthesis, strands must anneal cleanly. 5-bp internal palindromes
        # cause hairpins that block duplex formation (different threshold from 
        # thermo domain which checks 4-bp).
        if has_internal_palindrome(upper_base, half_length=5):
            total_penalty += 3.0
            details[f"Synthesis hairpin risk (5-bp palindrome) in {strand_name}"] = 3.0
    
    # Rule 6: Phosphorothioate (PS) Desulfurization Impurity Risk
    # Checked GLOBALLY (across both strands) as they are pooled for annealing.
    # MODERN THRESHOLD: Standard ESC+ uses exactly 6 PS. We only penalize
    # non-standard high PS densities that burden HPLC purification (Alnylam AT3).
    total_ps = (sense + antisense).count("S")
    if total_ps > 15:
        total_penalty += 4.0
        details[f"Extreme PS overload ({total_ps} total)"] = 4.0
    elif total_ps > 10:
        total_penalty += 2.0
        details[f"High PS density ({total_ps} total)"] = 2.0
    
    return min(total_penalty, 25.0), details


# Scaling factor defines how aggressively biophysical penalties diminish the ML score.
# Calibrated to 0.18 based on published Alnylam ESC+ / Khvorova lab design literature
# so that top clinically-modified cm-siRNAs retain 78%-90% efficacy scores.
def reverse_complement_rna(seq: str) -> str:
    """Computes reverse complement of RNA/DNA sequence."""
    trans = str.maketrans("ACGTUacgtu", "UGCAAugcaa")
    clean = re.sub(r'[^ACGTUacgtu]', '', seq).upper()
    return clean[::-1].translate(trans)


def calculate_target_complementarity_gate(
    antisense: str,
    target_mrna_window: Optional[str] = None
) -> Tuple[float, Dict[str, any]]:
    """
    Calculates position-weighted target complementarity gate multiplier (f_gate).
    
    Position Weighting:
    - Seed Region (antisense pos 2-8): Weight = 2.5 per mismatch (crucial for RISC loading & target cleavage)
    - Non-Seed Region (antisense pos 1, 9-21): Weight = 1.0 per mismatch (tolerates minor slop)
    
    Weighted Mismatch Formula:
    M_weighted = 2.5 * M_seed + 1.0 * M_nonseed
    
    Gating Multiplier (f_gate):
    If M_weighted > 3.0: f_gate = exp(-1.2 * (M_weighted - 3.0))
    Else: f_gate = 1.0
    """
    if not target_mrna_window:
        return 1.0, {"gate_status": "target_implicit_100%_match", "mismatches_weighted": 0.0}

    as_clean = re.sub(r'[^ACGTUacgtu]', '', antisense).upper()
    target_clean = re.sub(r'[^ACGTUacgtu]', '', target_mrna_window).upper()
    
    expected_target = reverse_complement_rna(as_clean)
    win_len = min(len(expected_target), len(target_clean))
    
    if win_len < 15:
        return 1.0, {"gate_status": "target_window_too_short", "mismatches_weighted": 0.0}

    best_weighted_mismatches = 999.0
    best_details = {}

    for start_idx in range(len(target_clean) - win_len + 1):
        target_sub = target_clean[start_idx : start_idx + win_len]
        m_seed = 0
        m_nonseed = 0
        
        for i in range(win_len):
            as_pos = i + 1
            if expected_target[i] != target_sub[i]:
                if 2 <= as_pos <= 8:
                    m_seed += 1
                else:
                    m_nonseed += 1

        m_weighted = 2.5 * m_seed + 1.0 * m_nonseed
        if m_weighted < best_weighted_mismatches:
            best_weighted_mismatches = m_weighted
            best_details = {
                "m_seed": m_seed,
                "m_nonseed": m_nonseed,
                "m_weighted": round(m_weighted, 1),
            }

    if best_weighted_mismatches > 3.0:
        f_gate = float(math.exp(-1.2 * (best_weighted_mismatches - 3.0)))
    else:
        f_gate = 1.0

    best_details["f_gate"] = round(f_gate, 6)
    best_details["gate_status"] = "applied" if f_gate < 0.99 else "passed"
    return f_gate, best_details

# Set of FDA/Clinical-de-risked Tier 0 modifications (Patisiran / Vutrisiran / Givosiran / Lumasiran / Inclisiran standard)
_TIER_0_FDA_CORE: FrozenSet[str] = frozenset("MFDS14acgtuACGTU.")

# Set of Tier 1 modifications with published preclinical in-vivo RISC activity (LNA, 2'-MOE, ENA)
_TIER_1_PRECLINICAL: FrozenSet[str] = frozenset("LEY")

def calculate_experimental_chemistry_penalty(sense: str, antisense: str) -> Tuple[float, Dict[str, float]]:
    """
    Calculates 3-Tier chemistry risk penalties and non-linear combinatorial stacking penalties
    for unvalidated, exotic novel chemical modifications (TNA, ANA, FANA, DihydroU, Abasic, etc.).
    
    Tier 0 (Penalty = 0): FDA-Approved Clinical Core (2'-OMe 'M', 2'-F 'F', 2'-deoxy 'D', PS 'S', GalNAc '4')
    Tier 1 (Penalty = 2.0): Preclinical in-vivo data (LNA 'L', 2'-MOE 'E', ENA 'Y')
    Tier 2 (Penalty = 6.0): Unvalidated/Exotic (TNA '9', ANA '7', FANA 'I', DihydroU 'O', Inosine 'J', Abasic 'Q', etc.)
    
    Combinatorial Stacking Penalty:
    If N >= 2 non-Tier-0 mods are stacked together, applies a non-linear penalty multiplier: 4.0 * (N - 1)^1.5
    """
    total_penalty = 0.0
    details = {}

    combined = sense + antisense
    t1_mods = [c for c in combined if c in _TIER_1_PRECLINICAL]
    t2_mods = [c for c in combined if c not in _TIER_0_FDA_CORE and c not in _TIER_1_PRECLINICAL]
    
    n_t1 = len(t1_mods)
    n_t2 = len(t2_mods)
    n_total_exotic = n_t1 + n_t2

    if n_t1 > 0:
        p_t1 = n_t1 * 2.0
        total_penalty += p_t1
        details[f"Tier 1 preclinical mod ({n_t1} mod{'s' if n_t1>1 else ''}: {set(t1_mods)})"] = p_t1

    if n_t2 > 0:
        p_t2 = n_t2 * 6.0
        total_penalty += p_t2
        details[f"Tier 2 unvalidated exotic mod ({n_t2} mod{'s' if n_t2>1 else ''}: {set(t2_mods)})"] = p_t2

    # Non-linear Combinatorial Stacking Penalty for multiple exotic modifications
    if n_total_exotic >= 2:
        stacking_penalty = round(4.0 * ((n_total_exotic - 1) ** 1.5), 1)
        total_penalty += stacking_penalty
        details[f"Combinatorial exotic stacking penalty ({n_total_exotic} stacked mods)"] = stacking_penalty

    return min(total_penalty, 40.0), details


# Default calibrated penalty adjustment factor for modified candidate ranking (12% scale)
_PENALTY_ADJUSTMENT_FACTOR = 0.12


def calculate_adjusted_efficacy(
    raw_ml_score: float,
    sense: str,
    antisense: str,
    base_sense: str,
    base_antisense: str,
    naked_baseline: Optional[float] = None,
    target_mrna_window: Optional[str] = None,
    mode: str = "mod_ranking",
    penalty_scale: float = 0.12,
) -> Tuple[float, Dict[str, Dict[str, any]], float]:
    """
    Applies all biophysical constraint penalties and target complementarity gating 
    to the raw Machine Learning efficacy score.

    Rules:
    - Naked candidates (0 modifications) & Targeted specific variant evaluation: scale = 0.0 (Zero deductions).
    - Modified ranked candidates (beam search & single-mod scan): scale = penalty_scale (Active biophysical filter).
    """
    pn, dn = calculate_nuclease_penalty(sense, antisense, base_sense, base_antisense)
    pi, di = calculate_immuno_penalty(sense, antisense, base_sense, base_antisense)
    pr, dr = calculate_risc_penalty(sense, antisense, base_sense, base_antisense)
    pt, dt = calculate_thermo_penalty(sense, antisense, base_sense, base_antisense)
    ps, ds = calculate_serum_penalty(sense, antisense, base_sense, base_antisense)
    psy, dsy = calculate_synthesis_penalty(sense, antisense, base_sense, base_antisense)
    pex, dex = calculate_experimental_chemistry_penalty(sense, antisense)
    f_gate, gate_details = calculate_target_complementarity_gate(base_antisense, target_mrna_window)

    # Automatic detection of naked baseline (0 modifications)
    is_naked = (sense == base_sense and antisense == base_antisense) or (mode == "naked")

    # Apply penalty deductions ONLY to modified ranked candidates
    if is_naked or mode == "targeted":
        scale = 0.0
    else:
        scale = penalty_scale

    penalties = {
        "nuclease": {"total": round(pn * scale, 1), "details": dn},
        "immuno": {"total": round(pi * scale, 1), "details": di},
        "risc": {"total": round((pr + pex) * scale, 1), "details": {**dr, **dex}},
        "thermo": {"total": round(pt * scale, 1), "details": dt},
        "serum": {"total": round(ps * scale, 1), "details": ds},
        "synthesis": {"total": round(psy * scale, 1), "details": dsy},
        "target_gate": {"total": round((1.0 - f_gate) * 100.0, 1), "details": gate_details},
    }
    
    absolute_penalty_sum = sum(v["total"] for k, v in penalties.items() if k != "target_gate")
    
    # Direct subtraction of scaled penalty sum from raw ML score
    adjusted_score = max(0.0, min(100.0, raw_ml_score - absolute_penalty_sum))
    
    # Target Complementarity Gate Multiplier
    adjusted_score = adjusted_score * f_gate

    return round(adjusted_score, 2), penalties, absolute_penalty_sum


# ─── Deep Module Seam ──────────────────────────────────────────────────────────

class BiophysicalGatingEngine:
    """
    Encapsulates biophysical penalty parameters and gating logic.
    Provides a single point of configuration and calibration for all
    thermodynamic, nuclease, immunogenicity, and serum stability penalties.
    """

    def __init__(
        self,
        max_penalty: float = 40.0,
        ps_min_count: int = 3,
        gc_min: float = 30.0,
        gc_max: float = 65.0,
    ) -> None:
        self.max_penalty: float = max_penalty
        self.ps_min_count: int = ps_min_count
        self.gc_min: float = gc_min
        self.gc_max: float = gc_max

    def evaluate(
        self,
        raw_score: float,
        sense: str,
        antisense: str,
        base_sense: Optional[str] = None,
        base_antisense: Optional[str] = None,
        penalty_scale: float = 1.0,
        mode: str = "ranked",
    ) -> Tuple[float, Dict[str, Any], float]:
        """
        Executes complete biophysical gating evaluation.
        
        Returns:
            Tuple[adjusted_score, penalties_dict, total_penalty_sum]
        """
        b_sense = base_sense or sense
        b_antisense = base_antisense or antisense
        return calculate_adjusted_efficacy(
            raw_ml_score=raw_score,
            sense=sense,
            antisense=antisense,
            base_sense=b_sense,
            base_antisense=b_antisense,
            penalty_scale=penalty_scale,
            mode=mode,
        )


_biophysical_gating_engine_instance: Optional[BiophysicalGatingEngine] = None


def get_biophysical_gating_engine() -> BiophysicalGatingEngine:
    """Returns the singleton BiophysicalGatingEngine instance."""
    global _biophysical_gating_engine_instance
    if _biophysical_gating_engine_instance is None:
        _biophysical_gating_engine_instance = BiophysicalGatingEngine()
    return _biophysical_gating_engine_instance

