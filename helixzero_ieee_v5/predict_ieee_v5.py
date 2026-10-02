"""
predict_ieee_v5.py
===================
HelixZero IEEE v5 Single Unified Dose-Aware & Cell-Aware Inference Engine.

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

THIS_FILE = Path(__file__).resolve()
IEEE_DIR = THIS_FILE.parent
ROOT_DIR = IEEE_DIR.parent

sys.path.insert(0, str(ROOT_DIR))

from smepred.src import model_b_v4
from helixzero_ieee_v5.src.chem_ontology import parse_canonical_sequence

print("Loading HelixZero Unified Dose-Aware Model Checkpoint...")
_ = model_b_v4._load()
print("✅ HelixZero Unified Dose-Aware CatBoost Engine Ready!\n")


def predict_sirna_potency(sense_seq: str, anti_seq: str, 
                          sense_mods: str = "", anti_mods: str = "", 
                          sense_positions: str = "", anti_positions: str = "",
                          parent_sense: str = None, parent_anti: str = None,
                          conc_nM: float = 10.0) -> dict:
    """
    Runs end-to-end unified dose-aware prediction for a chemically modified siRNA candidate.
    """
    s_slots = parse_canonical_sequence(sense_seq, sense_mods, sense_positions, parent_sense)
    as_slots = parse_canonical_sequence(anti_seq, anti_mods, anti_positions, parent_anti)
    
    pred_knockdown = float(model_b_v4.predict_from_slots([s_slots], [as_slots], conc_nM=conc_nM)[0])
    
    # Intrinsic potency directly derived from concentration-response relationship
    safe_kd = max(1.0, min(99.0, pred_knockdown))
    ic50_nM = float(conc_nM * (100.0 - safe_kd) / safe_kd)
    pred_pIC50 = float(9.0 - np.log10(max(1e-4, ic50_nM)))
    
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
    parent_sense_seqs: list = None, parent_anti_seqs: list = None,
    conc_nM: float = 10.0
) -> list:
    """
    Vectorized batch inference for unified dose-aware engine.
    """
    N = len(sense_seqs)
    if N == 0:
        return []
    if sense_mods_list is None: sense_mods_list = [""] * N
    if anti_mods_list is None: anti_mods_list = [""] * N
    if sense_pos_list is None: sense_pos_list = [""] * N
    if anti_pos_list is None: anti_pos_list = [""] * N
    if parent_sense_seqs is None: parent_sense_seqs = [None] * N
    if parent_anti_seqs is None: parent_anti_seqs = [None] * N

    s_slots_list = [parse_canonical_sequence(s, sm, sp, ps) for s, sm, sp, ps in zip(sense_seqs, sense_mods_list, sense_pos_list, parent_sense_seqs)]
    as_slots_list = [parse_canonical_sequence(a, am, ap, pa) for a, am, ap, pa in zip(anti_seqs, anti_mods_list, anti_pos_list, parent_anti_seqs)]

    preds_kd = model_b_v4.predict_from_slots(s_slots_list, as_slots_list, conc_nM=conc_nM)

    results = []
    for i in range(N):
        pred_kd = float(preds_kd[i])
        safe_kd = max(1.0, min(99.0, pred_kd))
        ic50_nM = float(conc_nM * (100.0 - safe_kd) / safe_kd)
        pred_pIC50 = float(9.0 - np.log10(max(1e-4, ic50_nM)))
        results.append({
            "sense_sequence": sense_seqs[i],
            "antisense_sequence": anti_seqs[i],
            "target_dose_nM": conc_nM,
            "estimated_pIC50": round(pred_pIC50, 4),
            "estimated_IC50_nM": round(ic50_nM, 4),
            "predicted_knockdown_pct": round(pred_kd, 2)
        })
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HelixZero Unified siRNA Potency & Knockdown Predictor")
    parser.add_argument("--sense", type=str, required=True, help="Sense sequence (5' to 3')")
    parser.add_argument("--anti", type=str, required=True, help="Antisense sequence (5' to 3')")
    parser.add_argument("--smods", type=str, default="", help="Sense modification mask string")
    parser.add_argument("--amods", type=str, default="", help="Antisense modification mask string")
    parser.add_argument("--conc", type=float, default=10.0, help="Assay concentration in nM (default: 10.0)")
    
    args = parser.parse_args()
    
    res = predict_sirna_potency(args.sense, args.anti, args.smods, args.amods, conc_nM=args.conc)
    
    print("=" * 65)
    print("🧬 HELIXZERO UNIFIED DOSE-AWARE PREDICTION RESULT")
    print("=" * 65)
    print(f"  Sense Sequence           : {res['sense_sequence']}")
    print(f"  Antisense Sequence       : {res['antisense_sequence']}")
    print(f"  Assay Concentration      : {res['target_dose_nM']} nM")
    print("  ---------------------------------------------------------------")
    print(f"  Estimated Intrinsic pIC50: {res['estimated_pIC50']} log10(M)")
    print(f"  Estimated Intrinsic IC50 : {res['estimated_IC50_nM']} nM")
    print(f"  Predicted Target Knockdown: {res['predicted_knockdown_pct']}% ⭐")
    print("=" * 65)
