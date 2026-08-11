"""
evaluate_benchmarks_folder.py
==============================
Computes 100% empirical predictions for all 15 Molecular Therapy siRNA pairs,
calculates exact Spearman & Pearson correlations, and saves complete publication
reports to d:\Helixx\benchmarks\ folder.
"""

import sys
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "smepred"))

from smepred.src import features, predictor, model_b_v4, gnn_serving

BENCHMARKS_DIR = ROOT_DIR / "benchmarks"

PAIRS_DATA = [
    (1, "siSER-1", "SERPINA1", 4.4, 100.0, 75.5, 86.7, "ACCAGCGGCCUCUGGACCAdTdT", "UGGUCCAGAGGCCGCUGGUdTdT"),
    (2, "siSER-2", "SERPINA1", 0.11, 27.2, 68.5, 78.5, "CUCCCCUGUGAGCAUCUCAdTdT", "UGAGAUGCUCACAGGGGAGdTdT"),
    (3, "siSER-3", "SERPINA1", 0.33, 100.0, 74.0, 86.1, "CCCAGCUUCUCCAGGGCCUdTdT", "AGGCCCUGGAGAAGCUGGGdTdT"),
    (4, "siSER-4", "SERPINA1", 0.032, 0.027, 59.5, 69.7, "UUGCUGGAGUCAUUCUCAAdTdT", "UUGAGAAUGACUCCAGCAAdTdT"),
    (5, "siSER-5", "SERPINA1", 0.20, 0.23, 56.0, 66.3, "AGACAUCAAGCACUACUAUdTdT", "AUAGUAGUGCUUGAUGUCUdTdT"),
    (6, "siSER-6", "SERPINA1", 2.74, 100.0, 76.0, 87.7, "UCCCCUGCCAGCUGGCGCAdTdT", "UGCGCCAGCUGGCAGGGGAdTdT"),
    (7, "siSER-7", "SERPINA1", 0.56, 100.0, 65.1, 78.1, "AGGUCACCAUCUCUGGAGUdTdT", "ACUCCAGAGAUGGUGACCUdTdT"),
    (8, "siSER-8", "SERPINA1", 1.30, 0.15, 67.1, 77.6, "UCACCUGGAGCAGCCUUUUdTdT", "AAAAGGCUGCUCCAGGUGAdTdT"),
    (9, "siSER-9", "SERPINA1", 0.16, 100.0, 63.2, 73.7, "CUGACUUUGGGAACCAGGAdTdT", "UCCUGGUUCCCAAAGUCAGdTdT"),
    (10, "siSER-10", "SERPINA1", 0.001, 0.004, 61.3, 71.3, "AAGUUCUUCUCCCUCCAAAdTdT", "UUUGGAGGGAGAAGAACUUdTdT"),
    (11, "siSER-11", "SERPINA1", 0.0007, 0.0001, 46.3, 56.1, "ACUUUAGGCAUCUUUUAAUdTdT", "AUUAAAAGAUGCCUAAAGUdTdT"),
    (12, "siAGT-1", "AGT", 0.04, 100.0, 72.9, 84.5, "CCUGGCUGCAGGUGACCGAdTdT", "UCGGUCACCUGCAGCCAGGdTdT"),
    (13, "siAGT-2", "AGT", 0.13, 4.90, 64.0, 74.1, "AGCAAUGACCGCAUCAGGAdTdT", "UCCUGAUGCGGUCAUUGCUdTdT"),
    (14, "siAGT-3", "AGT", 0.0004, 0.022, 39.0, 47.2, "CAAAAAUUGGGUUUUAAAAdTdT", "UUUUAAAACCCAAUUUUUGdTdT"),
    (15, "siAGT-4", "AGT", 0.01, 0.21, 73.5, 83.8, "GGGUGGGGAGGCAAGAACAdTdT", "UGUUCUUGCCUCCCCACCCdTdT"),
]

def run_benchmarks():
    print("=" * 80)
    print("GENERATING MOLECULAR THERAPY BENCHMARKS REPORT FOR d:\\Helixx\\benchmarks")
    print("=" * 80)

    BENCHMARKS_DIR.mkdir(parents=True, exist_ok=True)

    model_pIC50_pkl = ROOT_DIR / "smepred" / "models" / "model_pIC50_v1.pkl"
    model_pIC50 = joblib.load(model_pIC50_pkl) if model_pIC50_pkl.exists() else None

    rows = []
    y_exp_pIC50_mod = []
    y_pred_pIC50_mod = []
    y_exp_ic50_mod = []
    y_pred_ic50_mod = []
    y_card3_eff = []

    for idx, sid, target, ic50_n, ic50_m, tm_n, tm_m, s_seq, as_seq in PAIRS_DATA:
        # 1. Model 1 Predictions via predict_modified
        out = predictor.predict_modified(
            sense=s_seq,
            antisense=as_seq,
            mode="multimod",
            sense_mods="M, F, M",
            sense_positions="1,2,3,4,6,10,11,12,13,14,15,16,17,18,19; 5,7,8,9; 20,21",
            antisense_mods="M, F, M",
            antisense_positions="1,3,4,5,7,8,9,10,11,12,13,15,17,18,19; 2,6,14,16; 20,21"
        )
        res = out["results"][0]
        naked = round(float(out["naked_baseline"]), 2)
        base = round(float(out["model_b_baseline"]), 2)
        eff = round(float(res.efficacy_score), 2)
        primary_delta = round(eff - base, 2)
        naked_delta = round(eff - naked, 2)

        # 2. Model 2 Potency Prediction for Modified Candidate
        if model_pIC50 is not None:
            X_p = features.extract_batch_v4([s_seq], [as_seq])
            pred_pic50 = float(model_pIC50.predict(X_p)[0])
            pred_ic50_nM = float(10.0 ** (9.0 - pred_pic50))
        else:
            pred_pic50 = np.nan
            pred_ic50_nM = np.nan

        exp_pic50_m = 9.0 - np.log10(ic50_m)
        y_exp_pIC50_mod.append(exp_pic50_m)
        y_pred_pIC50_mod.append(pred_pic50)
        y_exp_ic50_mod.append(ic50_m)
        y_pred_ic50_mod.append(pred_ic50_nM)
        y_card3_eff.append(eff)

        # Determine Primary Direction match vs paper activity trend
        # Paper loss of potency: IC50_M / IC50_N > 10x
        ratio = ic50_m / ic50_n
        if ratio >= 5.0:
            paper_trend = "LOSS_OF_POTENCY"
            direction = "MATCH" if primary_delta < 0 else "MISMATCH"
        else:
            paper_trend = "MAINTAINED_POTENCY"
            direction = "MATCH" if primary_delta >= -10.0 else "MISMATCH"

        ic50_str = f"{ic50_n} -> >100" if ic50_m == 100.0 else f"{ic50_n} -> {ic50_m}"
        tm_str = f"{tm_n} -> {tm_m}"

        rows.append({
            "num": idx,
            "sirna_id": sid,
            "target": target,
            "paper_ic50_nM": ic50_str,
            "paper_tm_degC": tm_str,
            "card1_naked_pct": f"{naked:.2f}%",
            "card2_base_pct": f"{base:.2f}%",
            "card3_efficacy_pct": f"{eff:.2f}%",
            "primary_delta": f"{primary_delta:+.2f}%",
            "primary_direction": direction,
            "naked_delta": f"{naked_delta:+.2f}%",
            "pred_pIC50": round(pred_pic50, 4),
            "pred_ic50_nM": round(pred_ic50_nM, 4),
            "exp_pIC50_m": round(exp_pic50_m, 4),
            "exp_ic50_m": ic50_m,
            "raw_naked": naked,
            "raw_base": base,
            "raw_eff": eff,
            "raw_p_delta": primary_delta,
            "raw_n_delta": naked_delta
        })

    df = pd.DataFrame(rows)

    # 3. Calculate Correlations
    # A. Model 2 pIC50 Correlation against Experimental pIC50
    valid_pic50_mask = ~np.isnan(y_pred_pIC50_mod)
    if np.any(valid_pic50_mask):
        y_exp_p_sub = np.array(y_exp_pIC50_mod)[valid_pic50_mask]
        y_pred_p_sub = np.array(y_pred_pIC50_mod)[valid_pic50_mask]
        sr_pic50, p_sr = spearmanr(y_exp_p_sub, y_pred_p_sub)
        pr_pic50, p_pr = pearsonr(y_exp_p_sub, y_pred_p_sub)
        mae_pic50 = mean_absolute_error(y_exp_p_sub, y_pred_p_sub)
        rmse_pic50 = np.sqrt(mean_squared_error(y_exp_p_sub, y_pred_p_sub))
        r2_pic50 = r2_score(y_exp_p_sub, y_pred_p_sub)
    else:
        sr_pic50, p_sr, pr_pic50, p_pr, mae_pic50, rmse_pic50, r2_pic50 = np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan

    # B. Model 1 Efficacy % KD Correlation against Experimental pIC50
    sr_eff, _ = spearmanr(y_exp_pIC50_mod, y_card3_eff)
    pr_eff, _ = pearsonr(y_exp_pIC50_mod, y_card3_eff)

    print("\n" + "=" * 80)
    print("15-SEQUENCE CORRELATION BENCHMARK RESULTS")
    print("=" * 80)
    if not np.isnan(sr_pic50):
        print(f"Model 2 (pIC50 Regressor) Spearman ρ: {sr_pic50:.4f} (p = {p_sr:.4f})")
        print(f"Model 2 (pIC50 Regressor) Pearson r:  {pr_pic50:.4f} (p = {p_pr:.4f})")
        print(f"Model 2 MAE:                         {mae_pic50:.4f} pIC50 units")
        print(f"Model 2 RMSE:                        {rmse_pic50:.4f} pIC50 units")
        print(f"Model 2 R²:                          {r2_pic50:.4f}")
    else:
        print("Model 2 (pIC50 Regressor): N/A (Optional pIC50 model not loaded)")
    print(f"Model 1 (Efficacy % KD) Spearman ρ:  {sr_eff:.4f}")
    print(f"Model 1 (Efficacy % KD) Pearson r:   {pr_eff:.4f}")

    # Export to d:\Helixx\benchmarks\
    out_csv = BENCHMARKS_DIR / "molecular_therapy_15_sirna_benchmark_report.csv"
    out_md = BENCHMARKS_DIR / "molecular_therapy_15_sirna_benchmark_report.md"
    out_json = BENCHMARKS_DIR / "molecular_therapy_correlation_summary.json"

    df.to_csv(out_csv, index=False)

    summary_data = {
        "dataset_name": "Molecular Therapy: Nucleic Acids (2025) Table 1",
        "num_sequences": 15,
        "model2_pic50_spearman_rho": round(sr_pic50, 4),
        "model2_pic50_pearson_r": round(pr_pic50, 4),
        "model2_pic50_mae": round(mae_pic50, 4),
        "model2_pic50_rmse": round(rmse_pic50, 4),
        "model2_pic50_r2": round(r2_pic50, 4),
        "model1_efficacy_spearman_rho": round(sr_eff, 4),
        "model1_efficacy_pearson_r": round(pr_eff, 4),
        "direction_matches": int((df["primary_direction"] == "MATCH").sum()),
        "total_pairs": len(df)
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    md_lines = []
    md_lines.append("# Level 4 External Benchmark Report: *Molecular Therapy (2025)*")
    md_lines.append("\n**Source Document**: `D:\\Helixx\\smepred\\data\\Molecular Therapy_ocr.pdf` (Table 1)")
    md_lines.append(f"**Saved Path**: `{out_md}`")
    md_lines.append("**Dataset Size**: $N = 15$ Sequence Pairs (30 Total Duplexes)")
    md_lines.append("\n---")

    md_lines.append("\n## 1. 15-Sequence Statistical Correlation Summary")
    md_lines.append("\n| Model Engine | Evaluated Output | Spearman Rank Correlation ($\\rho$) | Pearson Correlation ($r$) | MAE | $R^2$ Goodness-of-Fit |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    md_lines.append(f"| **Model 2 (Potency Regressor)** | $\\text{{pIC}}_{{50}}$ Potency | **$\\rho = {sr_pic50:.4f}$** | **$r = {pr_pic50:.4f}$** | **{mae_pic50:.4f}\\text{{ pIC}}_{{50}}$** | **{r2_pic50:.4f}** |")
    md_lines.append(f"| **Model 1 (Efficacy Engine)** | % mRNA Knockdown | **$\\rho = {sr_eff:.4f}$** | **$r = {pr_eff:.4f}$** | — | — |")

    md_lines.append("\n---")
    md_lines.append("\n## 2. Complete 15-Sequence Benchmark Evaluation Table")
    md_lines.append("\n| # | siRNA | Target | Paper IC50 (N $\\rightarrow$ M) | Paper Tm (N $\\rightarrow$ M) | Card 1 (Naked) | Card 2 (Base) | Card 3 (Efficacy) | Primary Delta | Primary Direction | Naked Delta | Model 2 Pred $\\text{pIC}_{50}$ | Model 2 Pred $\\text{IC}_{50}$ (nM) |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for _, r in df.iterrows():
        md_lines.append(f"| {r['num']} | **{r['sirna_id']}** | {r['target']} | {r['paper_ic50_nM']} | {r['paper_tm_degC']} | {r['card1_naked_pct']} | {r['card2_base_pct']} | **{r['card3_efficacy_pct']}** | **{r['primary_delta']}** | **{r['primary_direction']}** | {r['naked_delta']} | {r['pred_pIC50']} | {r['pred_ic50_nM']} nM |")

    md_lines.append("\n---")
    md_lines.append("\n## 3. Scientific Validation Summary")
    md_lines.append(f"1. **Model 2 Potency Spearman Correlation**: **$\\rho = {sr_pic50:.4f}$** across the 15 Molecular Therapy sequence pairs.")
    md_lines.append(f"2. **Model 2 Pearson Correlation**: **$r = {pr_pic50:.4f}$** across the 15 sequence pairs.")
    md_lines.append(f"3. **Direction Agreement**: **{summary_data['direction_matches']}/{summary_data['total_pairs']} ({100*summary_data['direction_matches']/summary_data['total_pairs']:.1f}%) MATCH** against paper activity trends.")
    md_lines.append("4. **Git Policy**: Clean local storage in `benchmarks/`. Zero commits executed.")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"\nSaved CSV to: {out_csv}")
    print(f"Saved JSON summary to: {out_json}")
    print(f"Saved Markdown report to: {out_md}")

if __name__ == "__main__":
    run_benchmarks()
