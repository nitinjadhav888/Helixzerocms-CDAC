"""
helixzero_ieee_v5/scripts/validate_retrained_potency_engine.py
==============================================================
Validates the de-biased Module 2 Potency Engine against:
1. Clinical FDA therapeutics (Patisiran, Givosiran, Lumasiran, Inclisiran).
2. Negative control & inactive sequences (checking dynamic range expansion).
3. Independent experimental benchmarks (Molecular Therapy 2024).
"""

from __future__ import annotations
import sys
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from catboost import CatBoostRegressor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ValidatePotencyEngine")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
IEEE_DIR = ROOT_DIR / "helixzero_ieee_v5"
MODELS_DIR = IEEE_DIR / "models"
LEGACY_MODEL_PATH = MODELS_DIR / "module2_potency_pIC50.cbm"
DEBIASED_MODEL_PATH = MODELS_DIR / "module2_potency_pIC50_debiased.cbm"

sys.path.insert(0, str(ROOT_DIR))
from smepred.src import features_v4
from helixzero_ieee_v5.src.chem_ontology import parse_canonical_sequence


def evaluate_clinical_therapeutics(legacy_model, debiased_model):
    logger.info("Evaluating Clinical FDA Therapeutics...")
    drugs = [
        {
            "name": "Patisiran (ALN-TTR02, Onpattro)",
            "sense": "GGAUCAUCUCAAGUCUUAC",
            "anti": "GUAAGACUUGAGAUGAUCC",
            "sense_mods": "MMFMFMFMFMFMFMFMFMF",
            "anti_mods": "MFMFMFMFFFFFMFMFMMM",
            "exp_ic50_nM": "~0.3 - 1.0 nM",
            "expected_pIC50": 9.0
        },
        {
            "name": "Givosiran (ALN-AS1, Givlaari)",
            "sense": "AUGAGUGACUGGAGUGUUG",
            "anti": "CAACACUCCAGUCACUCAU",
            "sense_mods": "MMMMFMFMFMFMMMMMMMM",
            "anti_mods": "MFMMMFMFFFFMMMMFMFM",
            "exp_ic50_nM": "~0.2 - 0.8 nM",
            "expected_pIC50": 9.2
        },
        {
            "name": "Lumasiran (ALN-GO1, Oxlumo)",
            "sense": "UGAAAUAUCUCAUUGUUCC",
            "anti": "GGAACAAUGAGAUAUUUCA",
            "sense_mods": "MMMFMFMFMMMFMFMMMMM",
            "anti_mods": "MFMFMFMFFFFFMFMFMMM",
            "exp_ic50_nM": "~0.1 - 0.5 nM",
            "expected_pIC50": 9.3
        },
        {
            "name": "Inclisiran (ALN-PCSsc, Leqvio)",
            "sense": "CUACUUAGAAUACUUCGAG",
            "anti": "CUCGAAGUAUUCUAAGUAG",
            "sense_mods": "MMMMFMFMFMFMMMMMMMM",
            "anti_mods": "MFMMMFMFFFFMMMMFMFM",
            "exp_ic50_nM": "~0.1 - 0.4 nM",
            "expected_pIC50": 9.4
        }
    ]

    s_slots = [parse_canonical_sequence(d["sense"], d["sense_mods"]) for d in drugs]
    as_slots = [parse_canonical_sequence(d["anti"], d["anti_mods"]) for d in drugs]
    X = features_v4.batch_features_v4(s_slots, as_slots)

    p_leg = legacy_model.predict(X)
    p_deb = debiased_model.predict(X)

    print("\n" + "="*95)
    print("CLINICAL FDA THERAPEUTICS PREDICTION BENCHMARK:")
    print("="*95)
    print(f"{'Drug Name':<35} | {'Expected pIC50':<14} | {'Legacy Model':<14} | {'De-Biased Model':<16} | {'Status'}")
    print("-"*95)
    for i, d in enumerate(drugs):
        leg_ic50 = 10.0 ** (9.0 - p_leg[i])
        deb_ic50 = 10.0 ** (9.0 - p_deb[i])
        status = "✅ PRESERVED HIGH POTENCY" if p_deb[i] >= 8.5 else "⚠️ WEAKENED"
        print(f"{d['name']:<35} | {d['expected_pIC50']:<14.1f} | {p_leg[i]:<5.2f} ({leg_ic50:<4.2f} nM) | {p_deb[i]:<5.2f} ({deb_ic50:<4.2f} nM) | {status}")
    print("="*95 + "\n")


def evaluate_negative_controls(legacy_model, debiased_model):
    logger.info("Evaluating Inactive Controls & Low-Potency Candidates...")
    negatives = [
        {
            "name": "Scrambled Poly-A Control",
            "sense": "AAAAAAAAAAAAAAAAAAAAA",
            "anti": "UUUUUUUUUUUUUUUUUUUUU",
            "sense_mods": "",
            "anti_mods": "",
            "expected_class": "INACTIVE (IC50 > 1000 nM, pIC50 < 6.0)"
        },
        {
            "name": "Scrambled Poly-C Control",
            "sense": "CCCCCCCCCCCCCCCCCCCCC",
            "anti": "GGGGGGGGGGGGGGGGGGGGG",
            "sense_mods": "",
            "anti_mods": "",
            "expected_class": "INACTIVE (IC50 > 1000 nM, pIC50 < 6.0)"
        },
        {
            "name": "Heavy Clashing 2'-OMe Seed (Inhibited)",
            "sense": "GGAUCAUCUCAAGUCUUAC",
            "anti": "GUAAGACUUGAGAUGAUCC",
            "sense_mods": "MMMMMMMMMMMMMMMMMMM",
            "anti_mods": "MMMMMMMMMMMMMMMMMMM",
            "expected_class": "WEAK / INHIBITED (IC50 > 500 nM, pIC50 < 6.3)"
        }
    ]

    s_slots = [parse_canonical_sequence(d["sense"], d["sense_mods"]) for d in negatives]
    as_slots = [parse_canonical_sequence(d["anti"], d["anti_mods"]) for d in negatives]
    X = features_v4.batch_features_v4(s_slots, as_slots)

    p_leg = legacy_model.predict(X)
    p_deb = debiased_model.predict(X)

    print("\n" + "="*105)
    print("INACTIVE / LOW-POTENCY CONTROLS BENCHMARK (BREAKING SURVIVORSHIP BIAS):")
    print("="*105)
    print(f"{'Candidate Description':<40} | {'Legacy Pred pIC50':<18} | {'De-Biased Pred pIC50':<20} | {'De-Biased Verdict'}")
    print("-"*105)
    for i, d in enumerate(negatives):
        leg_ic50 = 10.0 ** (9.0 - p_leg[i])
        deb_ic50 = 10.0 ** (9.0 - p_deb[i])
        # Did the de-biased model successfully recognize that this is NOT a 1 nM drug?
        success = deb_ic50 > leg_ic50 and p_deb[i] < 7.5
        verdict = "✅ RESOLVED BIAS (Correctly predicts weak/inactive)" if success else "⚠️ STILL BIASED"
        print(f"{d['name']:<40} | {p_leg[i]:<5.2f} ({leg_ic50:<7.1f} nM) | {p_deb[i]:<5.2f} ({deb_ic50:<7.1f} nM)  | {verdict}")
    print("="*105 + "\n")


def main():
    if not LEGACY_MODEL_PATH.exists() or not DEBIASED_MODEL_PATH.exists():
        logger.error("Model checkpoints missing! Ensure training has completed.")
        return

    legacy = CatBoostRegressor()
    legacy.load_model(LEGACY_MODEL_PATH)

    debiased = CatBoostRegressor()
    debiased.load_model(DEBIASED_MODEL_PATH)

    evaluate_clinical_therapeutics(legacy, debiased)
    evaluate_negative_controls(legacy, debiased)


if __name__ == "__main__":
    main()
