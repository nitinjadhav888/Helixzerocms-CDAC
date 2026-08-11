"""
run_patisiran_ieee_v5.py
========================
Executes exact evaluation of FDA-Approved Patisiran (AD-18328 / ALN-TTR02 Lead) across:
1. Legacy Model B v4 & Ensemble v4 (~71% Modified Efficacy Score)
2. New IEEE v5 Module 2 Intrinsic Potency Engine (Estimated pIC50)
3. New IEEE v5 Module 3 Assay Response Predictor (Target Knockdown % at 10 nM)
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

ROOT_DIR = Path("d:/Helixx")
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "smepred") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "smepred"))

from smepred.src import model_b_v4, gnn_serving, predictor
from helixzero_ieee_v5.predict_ieee_v5 import predict_sirna_potency

# Exact FDA-Approved Patisiran Specification (ALN-TTR02 / AD-18328)
SENSE_SEQ = "GUAACCAAGAGUAUUCCAUTT"
ANTI_SEQ  = "AUGGAAUACUCUUGGUUACTT"

# 2'-O-Methyl (M) positions
SENSE_POSITIONS = "2,5,6,12,14,15,16,17,19"
SENSE_MODS      = "M,M,M,M,M,M,M,M,M"

ANTI_POSITIONS  = "7,17"
ANTI_MODS       = "M,M"

def build_modified_sequence(seq_21, mod_sym_str, pos_str):
    chars = list(seq_21)
    if mod_sym_str and pos_str:
        syms = [s.strip() for s in mod_sym_str.split(",") if s.strip()]
        poss = [int(p.strip()) for p in pos_str.split(",") if p.strip()]
        for s, p in zip(syms, poss):
            if 1 <= p <= len(chars):
                chars[p - 1] = s
    return "".join(chars)

SENSE_MODIFIED_STR = build_modified_sequence(SENSE_SEQ, SENSE_MODS, SENSE_POSITIONS)
ANTI_MODIFIED_STR  = build_modified_sequence(ANTI_SEQ, ANTI_MODS, ANTI_POSITIONS)

print("=" * 85)
print("🧬 FDA-APPROVED PATISIRAN (AD-18328 / ALN-TTR02) CANDIDATE SPECIFICATION")
print("=" * 85)
print(f"  Sense Strand (21-nt)       : {SENSE_SEQ}")
print(f"  Antisense Strand (21-nt)   : {ANTI_SEQ}")
print(f"  Sense Modifications        : {SENSE_MODS} at positions [{SENSE_POSITIONS}]")
print(f"  Antisense Modifications    : {ANTI_MODS} at positions [{ANTI_POSITIONS}]")
print(f"  Modified Sense String      : {SENSE_MODIFIED_STR}")
print(f"  Modified Antisense String  : {ANTI_MODIFIED_STR}")
print("=" * 85)

# 1. Legacy Model Evaluation
print("\n[1] EXECUTING LEGACY MODEL ENGINES...")
raw_naked_score = float(predictor._normalize_scores(predictor._predict_naked(predictor.extract_batch_v4([SENSE_SEQ], [ANTI_SEQ])), calibrator_key="normal")[0])

gbdt_v4 = float(model_b_v4.predict([SENSE_MODIFIED_STR], [ANTI_MODIFIED_STR], [SENSE_SEQ], [ANTI_SEQ])[0])
gnn_v2  = float(gnn_serving.predict_gnn([SENSE_SEQ], [ANTI_SEQ], [SENSE_MODIFIED_STR], [ANTI_MODIFIED_STR])[0])
ensemble_v4_score = float(np.clip(0.85 * gbdt_v4 + 0.15 * gnn_v2, 0.0, 100.0))

print(f"  - Legacy Naked Baseline    : {raw_naked_score:.2f}%")
print(f"  - Legacy CatBoost v4 Score : {gbdt_v4:.2f}%")
print(f"  - Legacy GNN v2 Score      : {gnn_v2:.2f}%")
print(f"  - Legacy Ensemble v4 Score : {ensemble_v4_score:.2f}% ⭐ (~71%)")

# 2. New IEEE v5 Evaluation
print("\n[2] EXECUTING NEW HELIXZERO IEEE v5 HIERARCHICAL FRAMEWORK...")
v5_res = predict_sirna_potency(
    sense_seq=SENSE_SEQ,
    anti_seq=ANTI_SEQ,
    sense_mods=SENSE_MODIFIED_STR,
    anti_mods=ANTI_MODIFIED_STR,
    conc_nM=10.0
)

v5_pIC50 = v5_res["estimated_pIC50"]
v5_IC50_nM = v5_res["estimated_IC50_nM"]
v5_kd_pct = v5_res["predicted_knockdown_pct"]

print("=" * 85)
print("🎯 HELIXZERO IEEE v5 PATISIRAN EVALUATION RESULT")
print("=" * 85)
print(f"  Estimated Intrinsic pIC50 : {v5_pIC50:.4f} log10(M)")
print(f"  Estimated Intrinsic IC50  : {v5_IC50_nM:.4f} nM ({v5_IC50_nM * 1000.0:.1f} pM)")
print(f"  Predicted Target Knockdown: {v5_kd_pct:.2f}% ⭐ (at 10.0 nM)")
print("=" * 85)
