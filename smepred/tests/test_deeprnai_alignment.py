"""
test_deeprnai_alignment.py — Verification of DeepRNAi & Janas Preclinical Hepatotoxicity Index

Validates:
1. Chemical seed rescue monomers (GNA '8' and UNA '6' inclusion).
2. DeepRNAi / Janas et al. (2018) Preclinical Hepatotoxicity Burden Index.
3. Inclisiran (PCSK9) benchmark classification into 'FDA Good Actor Profile'.
4. Toxic seed identification as 'Janas Bad Actor Risk' and rescue with pos 7 GNA.
5. Non-Perfect Match (NPM / G:U wobble) liability quantification.
6. Serialization invariance in RankedSiRNA and RankedCmSiRNA DTOs.
"""

import pytest
from src.filters import (
    _SEED_RESCUING_MODS,
    _MOD_NOMENCLATURE,
    check_seed_rescue,
    calculate_preclinical_hepatotoxicity_index,
    toxicity_for_modified,
)
from src.offtarget import get_offtarget_engine
from src.predictor import RankedSiRNA, RankedCmSiRNA


def test_seed_rescuing_mods_include_gna_and_una():
    """Verify GNA ('8') and UNA ('6') are registered in seed rescue monomer catalog."""
    assert "8" in _SEED_RESCUING_MODS
    assert "6" in _SEED_RESCUING_MODS
    assert _MOD_NOMENCLATURE["8"] == "GNA"
    assert _MOD_NOMENCLATURE["6"] == "UNA"


def test_pos7_gna_rescue_potency():
    """Verify pos 7 GNA (Alnylam ESC+ benchmark) is recognized with therapeutic weight."""
    mock_anti_gna = "......8.............."
    mods, note, strength = check_seed_rescue(mock_anti_gna)
    assert len(mods) == 1
    assert mods[0] == (7, "8")
    assert "GNA @ pos 7" in note
    assert strength > 0.25


def test_inclisiran_fda_good_actor_profile():
    """
    Verify Inclisiran (PCSK9) cm-siRNA achieves 'FDA Good Actor Profile' 
    under Janas et al. / DeepRNAi criteria.
    """
    inclisiran_anti = "AUAGUCAUCAGUCUCGUAGTT"
    inclisiran_anti_mods = "MFMFMFMFFFFMMMMFMFM"
    
    hep_idx = calculate_preclinical_hepatotoxicity_index(
        antisense=inclisiran_anti,
        modified_antisense=inclisiran_anti_mods,
        slicer_matches=1
    )
    
    assert hep_idx["hepato_profile"] == "FDA Good Actor Profile"
    assert hep_idx["hepato_status"] == "Safe"
    assert hep_idx["hepato_score"] >= 80.0
    assert hep_idx["rescue_strength"] >= 0.90
    assert "2'-Fluoro @ pos 2" in hep_idx["mitigation_details"]


def test_janas_bad_actor_detection_and_rescue():
    """
    Verify an unmitigated high-affinity/toxic seed is classified as 'Janas Bad Actor Risk',
    and that introducing pos 7 GNA rescues it.
    """
    toxic_anti = "ACCCCCCGUCUCGUAGTTTTT"
    
    # 1. Unmodified -> Janas Bad Actor Risk
    bad_actor_idx = calculate_preclinical_hepatotoxicity_index(toxic_anti)
    assert bad_actor_idx["hepato_profile"] == "Janas Bad Actor Risk"
    assert bad_actor_idx["hepato_status"] == "High Risk"
    assert bad_actor_idx["hepato_score"] < 50.0
    
    # 2. Rescued with pos 7 GNA
    rescued_idx = calculate_preclinical_hepatotoxicity_index(
        toxic_anti,
        modified_antisense="......8.............."
    )
    assert rescued_idx["rescue_strength"] > 0.0
    assert rescued_idx["hepato_score"] > bad_actor_idx["hepato_score"]


def test_npm_wobble_burden_quantification():
    """Verify Non-Perfect Match (NPM) G:U wobble burden score calculation."""
    # Gu-rich seed (high wobble capacity)
    gu_rich_anti = "AGUGUGUGUCUCGUAGTTTTT"
    idx_gu = calculate_preclinical_hepatotoxicity_index(gu_rich_anti)
    assert idx_gu["npm_burden"] >= 0.70

    # AC-rich seed (low wobble capacity)
    ac_rich_anti = "ACACACACUCUCGUAGTTTTT"
    idx_ac = calculate_preclinical_hepatotoxicity_index(ac_rich_anti)
    assert idx_ac["npm_burden"] <= 0.30


def test_dto_serialization_invariance():
    """Verify RankedSiRNA and RankedCmSiRNA serialize new preclinical hepatotoxicity fields."""
    sirna = RankedSiRNA(
        rank=1,
        position=100,
        sense="AAGUUCUAGAUGCUGUCCGAG",
        antisense="CGGACAGCAUCUAGAACUUUG",
        efficacy_score=85.0,
        efficacy_label="High",
        hepato_score=88.5,
        hepato_profile="FDA Good Actor Profile",
        hepato_status="Safe",
        npm_burden=0.43,
    )
    d = sirna.to_dict()
    assert d["hepato_score"] == 88.5
    assert d["hepato_profile"] == "FDA Good Actor Profile"
    assert d["hepato_status"] == "Safe"
    assert d["npm_burden"] == 0.43

    cmsirna = RankedCmSiRNA(
        rank=1,
        sense="CUACGAGACUGAUGACUAUTT",
        antisense="AUAGUCAUCAGUCUCGUAGTT",
        mod_symbol="8",
        mod_position=7,
        mod_strand="antisense",
        efficacy_score=82.0,
        delta_score=4.5,
        efficacy_label="High",
        hepato_score=84.0,
        hepato_profile="FDA Good Actor Profile",
        hepato_status="Safe",
    )
    cd = cmsirna.to_dict()
    assert cd["hepato_score"] == 84.0
    assert cd["hepato_profile"] == "FDA Good Actor Profile"
    assert cd["hepato_status"] == "Safe"
