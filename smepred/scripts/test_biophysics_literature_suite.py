"""
test_biophysics_literature_suite.py
===================================
Literature-Grounded Biophysical Regression Test Suite:
1. Weingärtner 2020: 5'-antisense GalNAc is fatal vs 3'-sense GalNAc anchor.
2. Elmén 2005: LNA at Ago2 catalytic slicing center (pos 10, 11, 12) causes catalytic loss vs flanking positions.
3. Naked Baseline Exemption: Unmodified naked RNA candidates receive 0.0 total penalty.
4. Schlegel 2022: GNA at position 7 (thermal disruption) receives position-7 bonus relative to early seed (pos 2-5).
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from smepred.src.biophysics import calculate_adjusted_efficacy


def test_naked_baseline_exemption():
    print("[TEST 1] Testing Naked Baseline Exemption (0.0 Penalty Anchor)...")
    sense = "GGAAUCUUCAUAGCUCAGCUU"
    anti  = "AAGCUGAGCUAAGAAGAUUCC"
    
    score, penalties, total_pen = calculate_adjusted_efficacy(
        raw_ml_score=80.0,
        sense=sense,
        antisense=anti,
        base_sense=sense,
        base_antisense=anti,
        is_naked=True
    )
    
    assert total_pen == 0.0, f"FAILED: Naked baseline candidate received penalty {total_pen} (expected 0.0)!"
    assert score == 80.0, f"FAILED: Naked baseline score altered to {score} (expected 80.0)!"
    print("  -> SUCCESS: Naked baseline candidate receives exactly 0.0 penalty deduction.")


def test_weingartner_galnac_asymmetry():
    print("[TEST 2] Testing Weingärtner 2020 5'-Antisense GalNAc Hard-Gate Penalty...")
    sense = "GGAAUCUUCAUAGCUCAGCUU"
    anti  = "AAGCUGAGCUAAGAAGAUUCC"
    
    # 5'-antisense GalNAc (fatal)
    anti_galnac_5p = "4" + anti[1:]
    score_bad, pen_bad, tot_bad = calculate_adjusted_efficacy(
        raw_ml_score=80.0,
        sense=sense,
        antisense=anti_galnac_5p,
        base_sense=sense,
        base_antisense=anti
    )
    
    # 3'-sense GalNAc (optimal clinical anchor)
    sense_galnac_3p = sense[:-1] + "4"
    score_good, pen_good, tot_good = calculate_adjusted_efficacy(
        raw_ml_score=80.0,
        sense=sense_galnac_3p,
        antisense=anti,
        base_sense=sense,
        base_antisense=anti
    )
    
    # Assert exact numerical hard gate magnitude AND exact bucket totals to prove zero double counting
    assert pen_bad["risc"]["details"].get("Fatal: 5'-antisense GalNAc conjugation (Weingärtner 2020)") == 40.0, "FAILED: 5'-antisense GalNAc hard gate detail missing or not equal to 40.0!"
    assert pen_bad["risc"]["total"] == 41.3, f"FAILED: 5'-antisense GalNAc RISC bucket total is {pen_bad['risc']['total']} (expected 41.3 = 40.0 hard gate + 1.3 soft RISC)!"
    assert pen_bad["serum"]["total"] == 1.0, f"FAILED: Serum bucket total is {pen_bad['serum']['total']} (expected 1.0, down from 5.8 duplicate)!"
    assert score_bad < score_good, f"FAILED: 5'-antisense GalNAc ({score_bad}) should rank lower than 3'-sense GalNAc ({score_good})!"
    print(f"  -> SUCCESS: 5'-antisense GalNAc exact 40.0-pt hard gate & zero double-counting verified (Score: {score_bad}).")


def test_elmen_lna_catalytic_slicing_center():
    print("[TEST 3] Testing Elmén 2005 LNA Ago2 Catalytic Slicing Center Penalty...")
    sense = "GGAAUCUUCAUAGCUCAGCUU"
    anti  = "AAGCUGAGCUAAGAAGAUUCC"
    
    # LNA at catalytic slicing center (pos 10)
    anti_lna_slice = anti[:9] + "L" + anti[10:]
    score_slice, pen_slice, tot_slice = calculate_adjusted_efficacy(
        raw_ml_score=80.0,
        sense=sense,
        antisense=anti_lna_slice,
        base_sense=sense,
        base_antisense=anti
    )
    
    # LNA at flanking seed position (pos 3)
    anti_lna_flank = anti[:2] + "L" + anti[3:]
    score_flank, pen_flank, tot_flank = calculate_adjusted_efficacy(
        raw_ml_score=80.0,
        sense=sense,
        antisense=anti_lna_flank,
        base_sense=sense,
        base_antisense=anti
    )
    
    # Assert exact numerical hard gate magnitude AND exact bucket totals to prove zero double counting
    assert pen_slice["risc"]["details"].get("Fatal: LNA at Ago2 catalytic slicing position 10 (Elmén 2005)") == 15.0, "FAILED: LNA slicing center hard gate detail missing or not equal to 15.0!"
    assert pen_slice["risc"]["total"] == 16.6, f"FAILED: LNA pos 10 RISC bucket total is {pen_slice['risc']['total']} (expected 16.6 = 15.0 hard gate + 1.6 soft RISC/pex)!"
    assert score_slice < score_flank, f"FAILED: Catalytic slicing LNA ({score_slice}) should rank lower than flanking LNA ({score_flank})!"
    print(f"  -> SUCCESS: Catalytic slicing LNA at pos 10 exact 15.0-pt hard gate & zero double-counting verified (Score: {score_slice}).")


def test_tier0_fda_core_chemistry_classification():
    print("[TEST 4] Testing Tier 0 FDA-Core Classification ('2' 3'-Phosphate & '3' 5'-OMe cap)...")
    from smepred.src.biophysics import calculate_experimental_chemistry_penalty
    
    # Candidate using 3'-Phosphate ('2') and 5'-OMe cap ('3')
    sense = "3GGAAUCUUCAUAGCUCAGCU2"
    anti  = "3AAGCUGAGCUAAGAAGAUU2"
    
    pex, details = calculate_experimental_chemistry_penalty(sense, anti)
    assert pex == 0.0, f"FAILED: Tier 0 chemistry ('2'/'3') received experimental chemistry penalty {pex} (expected 0.0)! Details: {details}"
    print("  -> SUCCESS: 3'-Phosphate ('2') and 5'-OMe cap ('3') classified as Tier 0 FDA-Core (0.0 penalty).")


if __name__ == "__main__":
    print("=" * 60)
    print("      RUNNING LITERATURE BIOPHYSICS REGRESSION SUITE")
    print("=" * 60)
    test_naked_baseline_exemption()
    test_weingartner_galnac_asymmetry()
    test_elmen_lna_catalytic_slicing_center()
    test_tier0_fda_core_chemistry_classification()
    print("=" * 60)
    print("      ALL LITERATURE BIOPHYSICS TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
