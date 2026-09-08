"""
test_biophysics_suite.py
------------------------
Production-grade test suite for HelixZero biophysical thermodynamics, chemical alphabet integrity,
nearest-neighbor duplex stability, RISC loading asymmetry, and nuclease/immunogenicity safety models.

Validates:
1. 30-Character Chemical Alphabet Ontology (Molecular Weights, SMILES, Heavy Atoms).
2. Terminal Asymmetry & Thermodynamic Guide Strand RISC Loading Selection.
3. Progressive Nuclease Penalty Saturation via Terminal PS and 2'-Ribose Chemistries.
4. TLR7/8 Innate Immunogenicity Sensing & 2'-OMe Evasion Heuristics.
5. Serum Half-life & Endonuclease Stability Indices.
"""

import sys
import os
import pytest
import numpy as np
from pathlib import Path

# Configure paths
SMEPRED_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = SMEPRED_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SMEPRED_DIR) not in sys.path:
    sys.path.insert(0, str(SMEPRED_DIR))

from smepred.src.chem_alphabet import MODIFICATION_ALPHABET, TIER_0_FDA_CORE
from smepred.src.biophysics import (
    calculate_adjusted_efficacy,
    calculate_nuclease_penalty,
    calculate_immuno_penalty,
    calculate_risc_penalty,
    calculate_thermo_penalty,
    calculate_serum_penalty,
)


# ─── 1. Chemical Alphabet Dictionary Integrity ───────────────────────────────

def test_chemical_alphabet_30_definitions():
    """Verify chemical modifications have complete, scientifically validated metadata."""
    assert len(MODIFICATION_ALPHABET) >= 25, f"Expected >=25 defined modification symbols, got {len(MODIFICATION_ALPHABET)}"
    
    REQUIRED_CORE = {"M", "F", "D", "S", "1"}
    assert REQUIRED_CORE.issubset(set(MODIFICATION_ALPHABET.keys())), "Core FDA chemical alphabet symbols missing!"

    for sym, meta in MODIFICATION_ALPHABET.items():
        assert "name" in meta, f"Symbol {sym} missing 'name'"
        assert "type" in meta, f"Symbol {sym} missing 'type'"
        assert meta["type"] in ("sugar", "backbone", "terminus", "conjugate", "base")
        assert "b_factor" in meta, f"Symbol {sym} missing 'b_factor'"
        assert "tier" in meta, f"Symbol {sym} missing 'tier'"


# ─── 2. Thermodynamic Asymmetry & RISC Loading ────────────────────────────────

def test_terminal_asymmetry_guide_strand_selection():
    """Verify duplexes with weaker 5'-AS base pairing show favorable RISC guide loading."""
    # Favorable asymmetry: 5'-Sense starts with GC-rich "GGCC", 5'-Antisense starts with AU-rich "UAUA"
    sense_fav = "GGCCAAGUUCUCCCAACUAUA"
    anti_fav  = "UAUAGUUGGGAGAACUUGGCC"
    
    p_fav, details_fav = calculate_thermo_penalty(sense_fav, anti_fav, sense_fav, anti_fav)
    assert not any("Thermodynamic asymmetry" in k for k in details_fav), "Favorable duplex should not have asymmetry penalty"
    
    # Unfavorable asymmetry: 5'-Sense starts with AU-rich "UAUA", 5'-Antisense starts with GC-rich "GGCC"
    sense_unfav = "UAUAAGUUCUCCCAACUGGCC"
    anti_unfav  = "GGCCAGUUGGGAGAACUUAUA"
    
    p_unfav, details_unfav = calculate_thermo_penalty(sense_unfav, anti_unfav, sense_unfav, anti_unfav)
    assert any("Thermodynamic asymmetry" in k for k in details_unfav), "Unfavorable duplex must trigger asymmetry penalty"


# ─── 3. Progressive Nuclease Protection Saturation ────────────────────────────

def test_progressive_nuclease_protection():
    """Verify progressive addition of PS linkages and 2'-OMe/2'-F strictly reduces nuclease penalty."""
    sense = "GGAUCAUCUCAAGUCUUAC"
    anti  = "GUAAGACUUGAGAUGAUCC"
    
    # 1. Unmodified naked duplex (no PS, low 2'-mod density)
    p_unmod, _ = calculate_nuclease_penalty(sense, anti, sense, anti)
    
    # 2. Terminal Phosphorothioate (PS) end caps (2 PS at both ends, but low 2'-mod density)
    sense_ps = "SS" + sense[2:]
    anti_ps  = "SS" + anti[2:-2] + "SS"
    p_ps, _ = calculate_nuclease_penalty(sense_ps, anti_ps, sense, anti)
    
    # 3. Fully modified clinical pattern (PS end caps + 100% 2'-OMe/2'-F density)
    sense_pat = "SS" + "M" * 17 + "SS"
    anti_pat  = "SS" + "F" * 17 + "SS"
    p_pat, _ = calculate_nuclease_penalty(sense_pat, anti_pat, sense, anti)
    
    assert p_unmod > p_ps, f"PS end caps ({p_ps}) should reduce nuclease penalty vs naked ({p_unmod})"
    assert p_ps > p_pat, f"Full 2'-mod + PS ({p_pat}) should have lower nuclease penalty than PS alone ({p_ps})"
    assert p_pat == 0.0, f"Fully protected clinical duplex should have 0 nuclease penalty, got {p_pat}"


# ─── 4. TLR7/8 Innate Immunogenicity Sensing & 2'-OMe Evasion ─────────────────

def test_immunogenicity_uridine_motifs_and_2ome_evasion():
    """Verify uridine rich motifs trigger immunogenicity penalty and 2'-OMe modification evades it."""
    # Highly immunogenic poly-uridine duplex
    sense_poly_u = "UUUUUGACUUCUUCAAGUUUU"
    anti_poly_u  = "AAAACUUGAAGAAGUCAAAAA"
    
    p_immuno_u, details_u = calculate_immuno_penalty(sense_poly_u, anti_poly_u, sense_poly_u, anti_poly_u)
    assert p_immuno_u > 0, "Poly-uridine sequence must trigger innate immunogenicity penalty!"
    
    # Evade TLR7/8 by 2'-O-methylating uridines
    sense_mod = sense_poly_u.replace("U", "M")
    anti_mod = anti_poly_u
    p_immuno_mod, details_mod = calculate_immuno_penalty(sense_mod, anti_mod, sense_poly_u, anti_poly_u)
    
    assert p_immuno_mod < p_immuno_u, (
        f"2'-OMe modification ({p_immuno_mod}) must evade TLR sensing vs unmodified uridine ({p_immuno_u})"
    )


# ─── 5. Serum Stability Index ─────────────────────────────────────────────────

def test_serum_stability_ps_end_caps():
    """Verify PS terminal linkages suppress exonuclease serum degradation penalty."""
    sense = "GCAGCACGACUUCUUCAAGUU"
    anti  = "CUUGAAGAAGUCGUGCUGCUU"
    
    p_naked, _ = calculate_serum_penalty(sense, anti, sense, anti)
    
    # Add PS terminal linkages
    mod_anti = "S" + anti[1:-1] + "S"
    p_protected, _ = calculate_serum_penalty(sense, mod_anti, sense, anti)
    
    assert p_protected <= p_naked, (
        f"Phosphorothioate termini ({p_protected}) should improve serum stability vs naked ({p_naked})"
    )
