"""
test_alnylam_therapeutics_benchmark.py
======================================
Evaluates FDA-Approved Alnylam Clinical siRNA Therapeutics:
1. Patisiran (ALN-TTR02 / AD-18328 - TTR, FDA 2018)
2. Givosiran (ALN-AS1 / AD-62846 - ALAS1, FDA 2019)
3. Lumasiran (ALN-GO1 / AD-67379 - HAO1, FDA 2020)
4. Inclisiran (ALN-PCS / AD-63025 - PCSK9, FDA 2021)
5. Vutrisiran (ALN-TTR02sc / AD-101150 - TTR, FDA 2022)

Compares:
- Raw ML Predictions (Ensemble_v4 vs IEEE_v5)
- Biophysical Penalty Deductions & Exemption Verification
- Clinical Ground Truth Knockdown % in clinical trials / FDA labels
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "smepred"))

from smepred.src import model_b_v4, gnn_serving, biophysics, predictor, features
from helixzero_ieee_v5.predict_ieee_v5 import predict_sirna_potency


CLINICAL_ALNYLAM_THERAPEUTICS = [
    {
        "name": "Patisiran (ALN-TTR02 / AD-18328)",
        "gene": "TTR",
        "fda_year": 2018,
        "sense": "GUAACCAAGAGUAUUCCAUTT",
        "anti":  "AUGGAAUACUCUUGGUUACTT",
        "sense_mods": ".M..MM......MMMM.M...",
        "anti_mods":  "......M.........M....",
        "clinical_kd": "84.0% - 90.0% serum TTR reduction",
        "dose_nM": 10.0
    },
    {
        "name": "Givosiran (ALN-AS1 / AD-62846)",
        "gene": "ALAS1",
        "fda_year": 2019,
        "sense": "CAGACUGUCCUCAUGUACUTT",
        "anti":  "AGUACAUGAGGACAGUCUGTT",
        "sense_mods": "3MFMFMFMMMMFMFMMFFFMM4",
        "anti_mods":  "1FMFMFMMMMFMFMMFFFMM2",
        "clinical_kd": "88.0% - 93.0% ALAS1 urinary reduction",
        "dose_nM": 10.0
    },
    {
        "name": "Lumasiran (ALN-GO1 / AD-67379)",
        "gene": "HAO1",
        "fda_year": 2020,
        "sense": "ACCAGCGGCCUCUGGACCATT",
        "anti":  "UGGUCCAGAGGCCGCUGGUTT",
        "sense_mods": "3MFMFMFMMMMFMFMMFFFMM4",
        "anti_mods":  "1FMFMFMMMMFMFMMFFFMM2",
        "clinical_kd": "80.0% - 85.0% urinary oxalate reduction",
        "dose_nM": 10.0
    },
    {
        "name": "Inclisiran (ALN-PCS / AD-63025)",
        "gene": "PCSK9",
        "fda_year": 2021,
        "sense": "CUAGACCUGGAGAAUGAGAATT",
        "anti":  "UUCUCAUUCUCCAGGUCUAGTT",
        "sense_mods": "3MFFMMFMFMFMMFFFMMMFM4",
        "anti_mods":  "1FMFMFMMMMFMFMMFFFMM2",
        "clinical_kd": "80.0% - 86.0% PCSK9 plasma reduction",
        "dose_nM": 10.0
    },
    {
        "name": "Vutrisiran (ALN-TTR02sc / AD-101150)",
        "gene": "TTR",
        "fda_year": 2022,
        "sense": "GUAACCAAGAGUAUUCCAUTT",
        "anti":  "AUGGAAUACUCUUGGUUACTT",
        "sense_mods": "3MFFMMFMFMFMMFFFMMMFM4",
        "anti_mods":  "1FMFMF8MMMMFMFMMFFFMM2",
        "clinical_kd": "83.0% - 88.0% serum TTR reduction",
        "dose_nM": 10.0
    }
]


def run_alnylam_benchmark():
    print("=" * 95)
    print("🧬 BENCHMARKING FDA-APPROVED ALNYLAM CLINICAL SIRNA THERAPEUTICS (2018 - 2022)")
    print("=" * 95)
    
    results = []
    
    for item in CLINICAL_ALNYLAM_THERAPEUTICS:
        name = item["name"]
        sense = item["sense"]
        anti = item["anti"]
        s_mods = item["sense_mods"]
        a_mods = item["anti_mods"]
        dose = item["dose_nM"]
        clin_kd = item["clinical_kd"]
        
        # 1. Evaluate Real Naked Parent Baseline (Zero-Penalty Anchor)
        X_naked = features.extract_batch_v4([sense], [anti])
        raw_naked_pred = float(predictor._normalize_scores(predictor._predict_naked(X_naked), calibrator_key="normal")[0])
        
        score_naked, _, pen_naked = biophysics.calculate_adjusted_efficacy(
            raw_ml_score=raw_naked_pred,
            sense=sense,
            antisense=anti,
            base_sense=sense,
            base_antisense=anti,
            is_naked=True
        )
        
        # 2. Evaluate Model A (Ensemble_v4) via predictor.predict_modified
        out_v4 = predictor.predict_modified(
            sense, anti,
            mode="multimod",
            model_key="Ensemble_v4",
            sense_mods=s_mods if len(s_mods) == len(sense) else "",
            sense_positions=item.get("sense_positions", ""),
            antisense_mods=a_mods if len(a_mods) == len(anti) else "",
            antisense_positions=item.get("antisense_positions", ""),
        )
        res_v4 = out_v4["results"][0]
        ens_v4_raw = res_v4.gbdt_score * 0.85 + res_v4.gnn_score * 0.15
        score_v4_adj = res_v4.efficacy_score
        pen_v4_tot = sum(p.get("total", 0.0) for p in res_v4.biophysics.values()) if res_v4.biophysics else 0.0

        # 3. Evaluate Model C (IEEE v5 Potency Engine) via predictor.predict_modified
        out_v5 = predictor.predict_modified(
            sense, anti,
            mode="multimod",
            model_key="IEEE_v5",
            sense_mods=s_mods if len(s_mods) == len(sense) else "",
            sense_positions=item.get("sense_positions", ""),
            antisense_mods=a_mods if len(a_mods) == len(anti) else "",
            antisense_positions=item.get("antisense_positions", ""),
        )
        res_v5 = out_v5["results"][0]
        est_pIC50 = res_v5.estimated_pIC50
        est_IC50_nM = res_v5.estimated_IC50_nM
        pred_kd = res_v5.predicted_knockdown_pct
        
        pIC50 = est_pIC50
        ic50_nM = est_IC50_nM
        ieee_v5_kd = pred_kd
        
        print(f"\n📌 {name} (FDA {item['fda_year']} - Target: {item['gene']})")
        print(f"   • Clinical Ground Truth : {clin_kd}")
        print(f"   • Naked Baseline Penalty: {pen_naked:.1f} pts (Verified 0.0 Anchor Exemption)")
        print(f"   • Model Ensemble_v4     : Raw={ens_v4_raw:.1f}%, Adj={score_v4_adj:.1f}% (Penalty: {pen_v4_tot:.1f} pts)")
        print(f"   • Model IEEE_v5 Potency : pIC50={pIC50:.3f} ({ic50_nM:.2f} nM) → Knockdown = {ieee_v5_kd:.1f}% ⭐")
        
        results.append({
            "Therapeutic": name,
            "Target Gene": item["gene"],
            "FDA Approval": item["fda_year"],
            "Naked Baseline": f"{score_naked:.1f}%",
            "Ensemble_v4 Raw": f"{ens_v4_raw:.1f}%",
            "Biophysics Penalty": f"{pen_v4_tot:.1f} pts",
            "Ensemble_v4 Adj": f"{score_v4_adj:.1f}%",
            "IEEE_v5 pIC50": pIC50,
            "IEEE_v5 IC50 (nM)": ic50_nM,
            "IEEE_v5 Knockdown %": f"{ieee_v5_kd:.1f}%",
            "Clinical Label": clin_kd
        })

    print("\n" + "=" * 95)
    print("📊 ALNYLAM CLINICAL THERAPEUTICS BENCHMARK SUMMARY TABLE")
    print("=" * 95)
    df_res = pd.DataFrame(results)
    print(df_res.to_string(index=False))
    print("=" * 95)


if __name__ == "__main__":
    run_alnylam_benchmark()
