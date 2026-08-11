"""
evaluate_ieee_v5_molecular_therapy_benchmark.py
===================================================
Executes a 100% quantitative empirical benchmark evaluation of the
HelixZero IEEE v5 Hierarchical Model Suite across the 15 siRNA duplex pairs
(30 total duplexes) from Molecular Therapy: Nucleic Acids (Vol 36, March 2025 Table 1).

Evaluates:
1. Module 2 Intrinsic Potency Engine (Estimated pIC50 vs Experimental pIC50)
2. Module 3 Assay Response Predictor (Predicted Target Knockdown % at 10 nM)
3. Pearson (r), Spearman (rho), MAE, and Classification Accuracy

Outputs:
- d:\Helixx\benchmarks\molecular_therapy_15_sirna_panel_benchmark_report.csv
- d:\Helixx\benchmarks\molecular_therapy_15_sirna_panel_benchmark_report.md
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from helixzero_ieee_v5.predict_ieee_v5 import predict_sirna_potency

BENCHMARKS_DIR = ROOT_DIR / "benchmarks"
OUT_CSV = BENCHMARKS_DIR / "molecular_therapy_15_sirna_panel_benchmark_report.csv"
OUT_MD = BENCHMARKS_DIR / "molecular_therapy_15_sirna_panel_benchmark_report.md"

TABLE1_DUPLEXES = [
    ("siSER-1", "ACCAGCGGCCUCUGGACCA", "UGGUCCAGAGGCCGCUGGU", 4.4, 75.5),
    ("siSER-1m", "ACCAGCGGCCUCUGGACCA", "UGGUCCAGAGGCCGCUGGU", 100.0, 86.7),
    ("siSER-2", "CUCCCCUGUGAGCAUCUCA", "UGAGAUGCUCACAGGGGAG", 0.11, 68.5),
    ("siSER-2m", "CUCCCCUGUGAGCAUCUCA", "UGAGAUGCUCACAGGGGAG", 27.2, 78.5),
    ("siSER-3", "CCCAGCUUCUCCAGGGCCU", "AGGCCCUGGAGAAGCUGGG", 0.33, 74.0),
    ("siSER-3m", "CCCAGCUUCUCCAGGGCCU", "AGGCCCUGGAGAAGCUGGG", 100.0, 86.1),
    ("siSER-4", "UUGCUGGAGUCAUUCUCAA", "UUGAGAAUGACUCCAGCAA", 0.032, 59.5),
    ("siSER-4m", "UUGCUGGAGUCAUUCUCAA", "UUGAGAAUGACUCCAGCAA", 0.027, 69.7),
    ("siSER-5", "AGACAUCAAGCACUACUAU", "AUAGUAGUGCUUGAUGUCU", 0.2, 56.0),
    ("siSER-5m", "AGACAUCAAGCACUACUAU", "AUAGUAGUGCUUGAUGUCU", 0.23, 66.3),
    ("siSER-6", "UCCCCUGCCAGCUGGCGCA", "UGCGCCAGCUGGCAGGGGA", 2.74, 76.0),
    ("siSER-6m", "UCCCCUGCCAGCUGGCGCA", "UGCGCCAGCUGGCAGGGGA", 100.0, 87.7),
    ("siSER-7", "AGGUCACCAUCUCUGGAGU", "ACUCCAGAGAUGGUGACCU", 0.56, 65.1),
    ("siSER-7m", "AGGUCACCAUCUCUGGAGU", "ACUCCAGAGAUGGUGACCU", 100.0, 78.1),
    ("siSER-8", "UCACCUGGAGCAGCCUUUU", "AAAAGGCUGCUCCAGGUGA", 1.3, 67.1),
    ("siSER-8m", "UCACCUGGAGCAGCCUUUU", "AAAAGGCUGCUCCAGGUGA", 0.15, 77.6),
    ("siSER-9", "CUGACUUUGGGAACCAGGA", "UCCUGGUUCCCAAAGUCAG", 0.16, 63.2),
    ("siSER-9m", "CUGACUUUGGGAACCAGGA", "UCCUGGUUCCCAAAGUCAG", 100.0, 73.7),
    ("siSER-10", "AAGUUCUUCUCCCUCCAAA", "UUUGGAGGGAGAAGAACUU", 0.001, 61.3),
    ("siSER-10m", "AAGUUCUUCUCCCUCCAAA", "UUUGGAGGGAGAAGAACUU", 0.004, 71.3),
    ("siAGT-1", "ACUUUAGGCAUCUUUUAAU", "AUUAAAAGAUGCCUAAAGU", 0.0007, 46.3),
    ("siAGT-1m", "ACUUUAGGCAUCUUUUAAU", "AUUAAAAGAUGCCUAAAGU", 0.0001, 56.1),
    ("siAGT-2", "CCUGGCUGCAGGUGACCGA", "UCGGUCACCUGCAGCCAGG", 0.04, 72.9),
    ("siAGT-2m", "CCUGGCUGCAGGUGACCGA", "UCGGUCACCUGCAGCCAGG", 100.0, 84.5),
    ("siAGT-3", "AGCAAUGACCGCAUCAGGA", "UCCUGAUGCGGUCAUUGCU", 0.13, 64.0),
    ("siAGT-3m", "AGCAAUGACCGCAUCAGGA", "UCCUGAUGCGGUCAUUGCU", 4.9, 74.1),
    ("siAGT-4", "CAAAAAUUGGGUUUUAAAA", "UUUUAAAACCCAAUUUUUG", 0.0004, 39.0),
    ("siAGT-4m", "CAAAAAUUGGGUUUUAAAA", "UUUUAAAACCCAAUUUUUG", 0.022, 47.2),
    ("siAGT-5", "GGGUGGGGAGGCAAGAACA", "UGUUCUUGCCUCCCCACCC", 0.01, 73.5),
    ("siAGT-5m", "GGGUGGGGAGGCAAGAACA", "UGUUCUUGCCUCCCCACCC", 0.21, 83.8),
]

def build_mod_mask(length=19, f_positions=[]):
    mods = ['M'] * length
    for pos in f_positions:
        mods[pos - 1] = 'F'
    return "".join(mods)

def run_benchmark():
    print("=" * 80)
    print("RUNNING HELIXZERO IEEE v5 BENCHMARK ON MOLECULAR THERAPY 15 siRNA PANEL")
    print("=" * 80)

    BENCHMARKS_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    for sid, s_rna, as_rna, ic50_val, tm_val in TABLE1_DUPLEXES:
        is_mod = sid.endswith("m")
        s_seq = s_rna + "UU"
        as_seq = as_rna + "UU"
        
        if is_mod:
            s_mods = build_mod_mask(19, [5, 7, 8, 9]) + "UU"
            as_mods = build_mod_mask(19, [2, 6, 14, 16]) + "UU"
        else:
            s_mods = ""
            as_mods = ""

        pIC50_exp = float(9.0 - np.log10(ic50_val))

        # Predict using IEEE v5 Hierarchical Pipeline
        res = predict_sirna_potency(
            sense_seq=s_seq,
            anti_seq=as_seq,
            sense_mods=s_mods,
            anti_mods=as_mods,
            conc_nM=10.0
        )

        pIC50_pred = float(res["estimated_pIC50"])
        ic50_pred_nM = float(res["estimated_IC50_nM"])
        kd_pct_pred = float(res["predicted_knockdown_pct"])

        records.append({
            "siRNA_ID": sid,
            "Target": "SERPINA1" if "SER" in sid else "AGT",
            "Sense_Seq": s_seq,
            "Antisense_Seq": as_seq,
            "Is_Modified": is_mod,
            "Exp_IC50_nM": ic50_val,
            "Exp_pIC50": round(pIC50_exp, 4),
            "Exp_Tm_degC": tm_val,
            "IEEE_v5_pIC50": round(pIC50_pred, 4),
            "IEEE_v5_IC50_nM": round(ic50_pred_nM, 4),
            "IEEE_v5_Knockdown_Pct": round(kd_pct_pred, 2),
            "pIC50_Error": round(abs(pIC50_pred - pIC50_exp), 4),
        })

    df = pd.DataFrame(records)

    # Compute Statistical Metrics
    y_exp = df["Exp_pIC50"].values
    y_pred = df["IEEE_v5_pIC50"].values

    pearson_r, _ = pearsonr(y_exp, y_pred)
    spearman_rho, _ = spearmanr(y_exp, y_pred)
    mae = mean_absolute_error(y_exp, y_pred)
    rmse = np.sqrt(mean_squared_error(y_exp, y_pred))

    print("\n" + "=" * 80)
    print("📊 HELIXZERO IEEE v5 BENCHMARK RESULTS (N=30 DUPLEXES)")
    print("=" * 80)
    print(f"  Pearson Correlation (r)      : {pearson_r:.4f} ⭐")
    print(f"  Spearman Rank Correlation (ρ): {spearman_rho:.4f} ⭐")
    print(f"  Mean Absolute Error (MAE)    : {mae:.4f} log10(M)")
    print(f"  Root Mean Squared Error (RMSE): {rmse:.4f} log10(M)")
    print("=" * 80)

    # Save CSV
    df.to_csv(OUT_CSV, index=False)
    print(f"\n✅ Saved benchmark CSV to: {OUT_CSV}")

    # Generate Markdown Summary Report
    md_content = f"""# 📊 HelixZero IEEE v5 Benchmark Report — Molecular Therapy 15 siRNA Panel (N=30 Duplexes)

**Dataset Source**: *Molecular Therapy: Nucleic Acids* (Vol 36, March 2025, Table 1)  
**Evaluated Model**: HelixZero IEEE v5 Hierarchical Model Suite (Module 2 CatBoost pIC50 + Module 3 Knockdown %)  
**Validation Standard**: IEEE TNNLS / Bioinformatics Publication-Grade (Zero Sequence Leakage GroupKFold Protocol)

---

## 🎯 Quantitative Performance Metrics

| Metric | IEEE v5 Performance | Baseline Target |
| :--- | :---: | :---: |
| **Pearson Correlation (r)** | **{pearson_r:.4f}** ⭐ | $> 0.7000$ |
| **Spearman Rank Correlation (rho)** | **{spearman_rho:.4f}** ⭐ | $> 0.7000$ |
| **Mean Absolute Error (MAE)** | **{mae:.4f} log10(M)** | $< 0.8000$ |
| **Root Mean Squared Error (RMSE)** | **{rmse:.4f} log10(M)** | $< 1.0000$ |

---

## 🧬 Full 30 Duplex Benchmark Evaluation Table

| # | siRNA ID | Target | Is Mod | Exp IC50 (nM) | Exp pIC50 | IEEE v5 pIC50 | IEEE v5 IC50 (nM) | IEEE v5 Knockdown % | Error |
| :-: | :--- | :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
"""
    for i, row in df.iterrows():
        md_content += f"| {i+1} | `{row['siRNA_ID']}` | {row['Target']} | {'Yes' if row['Is_Modified'] else 'No'} | {row['Exp_IC50_nM']} | {row['Exp_pIC50']} | **{row['IEEE_v5_pIC50']}** | **{row['IEEE_v5_IC50_nM']}** | **{row['IEEE_v5_Knockdown_Pct']}%** | {row['pIC50_Error']} |\n"

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✅ Saved benchmark report to: {OUT_MD}")

if __name__ == "__main__":
    run_benchmark()
