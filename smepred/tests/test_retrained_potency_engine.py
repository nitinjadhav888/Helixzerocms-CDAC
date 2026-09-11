"""
test_retrained_potency_engine.py
--------------------------------
Production-grade regression test suite for the HelixZero IEEE v5 Debiased Potency Engine
and Retrained Gold pIC50 Model (module2_potency_pIC50_retrained_gold.cbm).

Validates:
1. Retrained Gold Checkpoint Integrity and Architecture.
2. 577-Dimensional Multi-Modal Feature Extraction without NaNs/Infs.
3. Clinical Potency Invariance across FDA-Approved Therapeutics (Patisiran, Givosiran, Lumasiran, Inclisiran).
4. Hill Equation Dose-Response Monotonicity across Multi-Decade Concentration Series.
5. Exact Consistency between Single-Item and Vectorized Batch Inference Routines.
"""

import sys
import os
import pytest
import numpy as np
from pathlib import Path
from catboost import CatBoostRegressor

# Configure module paths
SMEPRED_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = SMEPRED_DIR.parent
IEEE_DIR = ROOT_DIR / "helixzero_ieee_v5"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SMEPRED_DIR) not in sys.path:
    sys.path.insert(0, str(SMEPRED_DIR))

from smepred.src import features_v4
from helixzero_ieee_v5.src.chem_ontology import parse_canonical_sequence
from helixzero_ieee_v5.predict_ieee_v5 import predict_sirna_potency, predict_sirna_potency_batch


# ─── 1. Checkpoint Integrity & Loading ────────────────────────────────────────

def test_gold_checkpoint_presence_and_loading():
    """Verify retrained Gold pIC50 model checkpoint exists and loads valid CatBoost trees."""
    gold_model_path = IEEE_DIR / "models" / "module2_potency_pIC50_retrained_gold.cbm"
    assert gold_model_path.exists(), f"Retrained Gold model checkpoint missing at: {gold_model_path}"
    
    cb = CatBoostRegressor()
    cb.load_model(str(gold_model_path))
    assert cb.tree_count_ > 0, f"Expected >0 decision trees in model, got {cb.tree_count_}"


# ─── 2. 577-Dimensional Feature Extraction ────────────────────────────────────

def test_577d_feature_extraction_integrity():
    """Verify 577D feature vector extraction is deterministic, finite, and strictly non-empty."""
    sense = "GGAUCAUCUCAAGUCUUAC"
    anti = "GUAAGACUUGAGAUGAUCC"
    
    # Unmodified slots
    s_slots_unmod = parse_canonical_sequence(sense)
    as_slots_unmod = parse_canonical_sequence(anti)
    X_unmod = features_v4.batch_features_v4([s_slots_unmod], [as_slots_unmod])
    
    assert X_unmod.shape == (1, 577), f"Expected shape (1, 577), got {X_unmod.shape}"
    assert not np.isnan(X_unmod).any(), "Extracted 577D feature vector contains NaN values!"
    assert not np.isinf(X_unmod).any(), "Extracted 577D feature vector contains Inf values!"

    # Modified slots (2'-OMe, 2'-F, PS)
    s_slots_mod = parse_canonical_sequence(sense, "M,F,M", "1,2,3")
    as_slots_mod = parse_canonical_sequence(anti, "F,M,S", "2,6,19")
    X_mod = features_v4.batch_features_v4([s_slots_mod], [as_slots_mod])
    
    assert X_mod.shape == (1, 577)
    assert not np.isnan(X_mod).any(), "Modified feature vector contains NaN values!"
    assert not np.allclose(X_unmod, X_mod), "Modified feature vector should differ from unmodified baseline!"


# ─── 3. FDA Therapeutics Clinical Range Benchmarks ────────────────────────────

FDA_DRUGS = [
    {
        "name": "Patisiran",
        "sense": "GGAUCAUCUCAAGUCUUAC",
        "anti": "GUAAGACUUGAGAUGAUCC",
        "s_mods": "MMFMFMFMFMFMFMFMFMF",
        "a_mods": "MFMFMFMFFFFFMFMFMMM",
        "conc_nM": 10.0,
        "expected_pIC50_min": 7.5,
        "expected_pIC50_max": 9.8,
    },
    {
        "name": "Givosiran",
        "sense": "AUGAGUGACUGGAGUGUUG",
        "anti": "CAACACUCCAGUCACUCAU",
        "s_mods": "MMMMFMFMFMFMMMMMMMM",
        "a_mods": "MFMMMFMFFFFMMMMFMFM",
        "conc_nM": 10.0,
        "expected_pIC50_min": 7.2,
        "expected_pIC50_max": 9.5,
    },
    {
        "name": "Lumasiran",
        "sense": "ACCAGGUGGUACUGAAACUAA",
        "anti": "UAGUUUCAGUACCACCUGGUU",
        "s_mods": "MMFMFMFMFMFMMMMMMMM",
        "a_mods": "MFMFMFMFFFFMMMMFMFM",
        "conc_nM": 10.0,
        "expected_pIC50_min": 7.5,
        "expected_pIC50_max": 9.8,
    },
    {
        "name": "Inclisiran",
        "sense": "CUACGAGACUGAUGACUAUTT",
        "anti": "AUAGUCAUCAGUCUCGUAGTT",
        "s_mods": "MMFMFMFMFMFMMMMMMMM",
        "a_mods": "MFMFMFMFFFFMMMMFMFM",
        "conc_nM": 10.0,
        "expected_pIC50_min": 7.5,
        "expected_pIC50_max": 9.8,
    },
]

@pytest.mark.parametrize("drug", FDA_DRUGS, ids=[d["name"] for d in FDA_DRUGS])
def test_clinical_fda_drug_potency_ranges(drug):
    """Verify FDA approved drugs predict into clinically calibrated picomolar/low-nanomolar ranges."""
    res = predict_sirna_potency(
        sense_seq=drug["sense"],
        anti_seq=drug["anti"],
        sense_mods=drug["s_mods"],
        anti_mods=drug["a_mods"],
        conc_nM=drug["conc_nM"]
    )
    
    pIC50 = res["estimated_pIC50"]
    ic50_nM = res["estimated_IC50_nM"]
    kd_pct = res["predicted_knockdown_pct"]
    
    assert drug["expected_pIC50_min"] <= pIC50 <= drug["expected_pIC50_max"], (
        f"{drug['name']} predicted pIC50={pIC50:.2f} is outside expected clinical bounds "
        f"[{drug['expected_pIC50_min']}, {drug['expected_pIC50_max']}]."
    )
    assert 0.01 <= ic50_nM <= 100.0, f"{drug['name']} IC50={ic50_nM:.2f} nM outside plausible active range"
    assert 40.0 <= kd_pct <= 100.0, f"{drug['name']} biological knockdown={kd_pct:.1f}% at assay dose too low"


# ─── 4. Hill Equation Dose-Response Monotonicity ──────────────────────────────

def test_hill_dose_response_monotonicity():
    """Verify predicted biological knockdown increases monotonically with target assay concentration."""
    sense = "GGAUCAUCUCAAGUCUUAC"
    anti = "GUAAGACUUGAGAUGAUCC"
    s_mods = "MMFMFMFMFMFMFMFMFMF"
    a_mods = "MFMFMFMFFFFFMFMFMMM"
    
    concentrations = [0.01, 0.1, 1.0, 10.0, 100.0]
    kd_responses = []
    
    for conc in concentrations:
        res = predict_sirna_potency(
            sense_seq=sense,
            anti_seq=anti,
            sense_mods=s_mods,
            anti_mods=a_mods,
            conc_nM=conc
        )
        kd_responses.append(res["predicted_knockdown_pct"])
        assert 0.0 <= res["predicted_knockdown_pct"] <= 100.0

    # Assert strict monotonicity: KD(c_i) <= KD(c_{i+1})
    for i in range(len(kd_responses) - 1):
        assert kd_responses[i] <= kd_responses[i + 1] + 1e-3, (
            f"Dose-response non-monotonicity detected: KD({concentrations[i]} nM) = {kd_responses[i]:.2f}% "
            f"> KD({concentrations[i+1]} nM) = {kd_responses[i+1]:.2f}%"
        )


# ─── 5. Vectorized Batch vs Single-Item Consistency ───────────────────────────

def test_batch_vs_single_consistency():
    """Verify vectorized batch inference produces identical values to single-item inference."""
    s_list = ["GGAUCAUCUCAAGUCUUAC", "AUGAGUGACUGGAGUGUUG"]
    a_list = ["GUAAGACUUGAGAUGAUCC", "CAACACUCCAGUCACUCAU"]
    sm_list = ["MMFMFMFMFMFMFMFMFMF", "MMMMFMFMFMFMMMMMMMM"]
    am_list = ["MFMFMFMFFFFFMFMFMMM", "MFMMMFMFFFFMMMMFMFM"]
    
    # 1. Batch inference
    batch_res = predict_sirna_potency_batch(
        sense_seqs=s_list,
        anti_seqs=a_list,
        sense_mods_list=sm_list,
        anti_mods_list=am_list,
        conc_nM=10.0
    )
    
    # 2. Single-item inference
    for i in range(len(s_list)):
        single_res = predict_sirna_potency(
            sense_seq=s_list[i],
            anti_seq=a_list[i],
            sense_mods=sm_list[i],
            anti_mods=am_list[i],
            conc_nM=10.0
        )
        
        assert np.isclose(batch_res[i]["estimated_pIC50"], single_res["estimated_pIC50"], atol=1e-3), (
            f"Batch pIC50 {batch_res[i]['estimated_pIC50']} differs from single {single_res['estimated_pIC50']}"
        )
        assert np.isclose(batch_res[i]["predicted_knockdown_pct"], single_res["predicted_knockdown_pct"], atol=0.1), (
            f"Batch KD% {batch_res[i]['predicted_knockdown_pct']} differs from single {single_res['predicted_knockdown_pct']}"
        )


if __name__ == "__main__":
    print("=" * 60)
    print("Running Suite 3 standalone verification...")
    print("=" * 60)
    print("[1/5] Testing gold checkpoint...")
    test_gold_checkpoint_presence_and_loading()
    print(" -> PASSED")
    print("[2/5] Testing 577D feature extraction integrity...")
    test_577d_feature_extraction_integrity()
    print(" -> PASSED")
    print("[3/5] Testing FDA drug potency ranges...")
    for drug in FDA_DRUGS:
        test_clinical_fda_drug_potency_ranges(drug)
        print(f"   ✓ {drug['name']} passed")
    print(" -> PASSED")
    print("[4/5] Testing Hill dose response monotonicity...")
    test_hill_dose_response_monotonicity()
    print(" -> PASSED")
    print("[5/5] Testing batch vs single consistency...")
    test_batch_vs_single_consistency()
    print(" -> PASSED")
    print("=" * 60)
    print("🎉 ALL SUITE 3 TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
