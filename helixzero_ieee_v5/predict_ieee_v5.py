"""
predict_ieee_v5.py
===================
HelixZero IEEE v5 Multi-Module Inference Engine.

Takes any siRNA molecule (Sense + Antisense + Chemical Modifications) and target Dose (nM)
and returns:
1. Estimated Intrinsic Potency (pIC50 log units and IC50 in nM).
2. Predicted Biological mRNA Knockdown Percentage (%) at the target dose.

Usage via CLI:
  python helixzero_ieee_v5/predict_ieee_v5.py --sense "GGAUCAUCUCAAGUCUUAC" --anti "GUAAGACUUGAGAUGAUCC" --conc 10.0
"""

import sys
import argparse
import numpy as np
from pathlib import Path
from catboost import CatBoostRegressor

THIS_FILE = Path(__file__).resolve()
IEEE_DIR = THIS_FILE.parent
ROOT_DIR = IEEE_DIR.parent
MODELS_DIR = IEEE_DIR / "models"

sys.path.insert(0, str(ROOT_DIR))

from smepred.src import features_v4
from helixzero_ieee_v5.src.chem_ontology import parse_canonical_sequence

# Load pre-trained IEEE v5 model checkpoints
print("Loading HelixZero IEEE v5 Model Checkpoints...")
mod2_path = MODELS_DIR / "module2_potency_pIC50.cbm"
mod3_path = MODELS_DIR / "module3_assay_response.cbm"

if not mod2_path.exists() or not mod3_path.exists():
    raise FileNotFoundError(f"Model checkpoints missing in {MODELS_DIR}")

mod2_engine = CatBoostRegressor()
mod2_engine.load_model(mod2_path)

mod3_engine = CatBoostRegressor()
mod3_engine.load_model(mod3_path)

print("✅ HelixZero IEEE v5 Inference Engine Ready!\n")

def predict_sirna_potency(sense_seq: str, anti_seq: str, 
                          sense_mods: str = "", anti_mods: str = "", 
                          sense_positions: str = "", anti_positions: str = "",
                          conc_nM: float = 10.0) -> dict:
    """
    Runs end-to-end 2-stage prediction for a chemically modified siRNA candidate.
    """
    # 1. Parse Canonical NucSlot Chemical Ontology
    s_slots = parse_canonical_sequence(sense_seq, sense_mods, sense_positions)
    as_slots = parse_canonical_sequence(anti_seq, anti_mods, anti_positions)
    
    # 2. Extract 577-dimensional Multi-Modal Feature Vector
    X_base = features_v4.batch_features_v4([s_slots], [as_slots])
    
    # 3. Stage 1: Predict Intrinsic Potency (pIC50 Engine)
    pred_pIC50 = float(mod2_engine.predict(X_base)[0])
    ic50_nM = float(10**(-pred_pIC50) * 1e9)
    
    # 4. Stage 2: Predict Dose-Aware Assay Knockdown Percentage
    log_conc = np.log10(conc_nM + 1e-6).reshape(-1, 1)
    X_mod3 = np.hstack([np.array([[pred_pIC50]]), log_conc, X_base])
    
    pred_knockdown = float(np.clip(mod3_engine.predict(X_mod3)[0], 0.0, 100.0))
    
    return {
        "sense_sequence": sense_seq,
        "antisense_sequence": anti_seq,
        "target_dose_nM": conc_nM,
        "estimated_pIC50": round(pred_pIC50, 4),
        "estimated_IC50_nM": round(ic50_nM, 4),
        "predicted_knockdown_pct": round(pred_knockdown, 2)
    }


def predict_sirna_potency_batch(
    sense_seqs: list, anti_seqs: list,
    sense_mods_list: list = None, anti_mods_list: list = None,
    sense_pos_list: list = None, anti_pos_list: list = None,
    conc_nM: float = 10.0
) -> list:
    """
    Vectorized batch inference for IEEE v5 engine (6000x faster than single-item loops).
    """
    N = len(sense_seqs)
    if N == 0:
        return []
    if sense_mods_list is None: sense_mods_list = [""] * N
    if anti_mods_list is None: anti_mods_list = [""] * N
    if sense_pos_list is None: sense_pos_list = [""] * N
    if anti_pos_list is None: anti_pos_list = [""] * N

    s_slots_list = [parse_canonical_sequence(s, sm, sp) for s, sm, sp in zip(sense_seqs, sense_mods_list, sense_pos_list)]
    as_slots_list = [parse_canonical_sequence(a, am, ap) for a, am, ap in zip(anti_seqs, anti_mods_list, anti_pos_list)]

    X_base = features_v4.batch_features_v4(s_slots_list, as_slots_list)

    preds_pIC50 = mod2_engine.predict(X_base)
    ic50s_nM = (10.0 ** (-preds_pIC50)) * 1e9

    log_conc = np.full((N, 1), np.log10(conc_nM + 1e-6))
    X_mod3 = np.hstack([preds_pIC50.reshape(-1, 1), log_conc, X_base])

    preds_knockdown = np.clip(mod3_engine.predict(X_mod3), 0.0, 100.0)

    results = []
    for i in range(N):
        results.append({
            "sense_sequence": sense_seqs[i],
            "antisense_sequence": anti_seqs[i],
            "target_dose_nM": conc_nM,
            "estimated_pIC50": round(float(preds_pIC50[i]), 4),
            "estimated_IC50_nM": round(float(ic50s_nM[i]), 4),
            "predicted_knockdown_pct": round(float(preds_knockdown[i]), 2)
        })
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HelixZero IEEE v5 siRNA Potency & Knockdown Predictor")
    parser.add_argument("--sense", type=str, required=True, help="Sense sequence (5' to 3')")
    parser.add_argument("--anti", type=str, required=True, help="Antisense sequence (5' to 3')")
    parser.add_argument("--smods", type=str, default="", help="Sense modification mask string")
    parser.add_argument("--amods", type=str, default="", help="Antisense modification mask string")
    parser.add_argument("--conc", type=float, default=10.0, help="Assay concentration in nM (default: 10.0)")
    
    args = parser.parse_args()
    
    res = predict_sirna_potency(args.sense, args.anti, args.smods, args.amods, args.conc)
    
    print("=" * 65)
    print("🧬 HELIXZERO IEEE v5 PREDICTION RESULT")
    print("=" * 65)
    print(f"  Sense Sequence           : {res['sense_sequence']}")
    print(f"  Antisense Sequence       : {res['antisense_sequence']}")
    print(f"  Assay Concentration      : {res['target_dose_nM']} nM")
    print("  ---------------------------------------------------------------")
    print(f"  Estimated Intrinsic pIC50: {res['estimated_pIC50']} log10(M)")
    print(f"  Estimated Intrinsic IC50 : {res['estimated_IC50_nM']} nM")
    print(f"  Predicted Target Knockdown: {res['predicted_knockdown_pct']}% ⭐")
    print("=" * 65)
