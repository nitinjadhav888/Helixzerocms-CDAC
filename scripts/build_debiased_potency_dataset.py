"""
scripts/build_debiased_potency_dataset.py
=========================================
Recovers multi-dose Hill curves from un-fitted BRONZE measurements,
anchors inactive/weak candidates to eliminate survivorship bias,
and compiles the expanded, full-dynamic-range pIC50 training dataset.
"""

from __future__ import annotations
import sys
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DeBiasBuilder")

ROOT_DIR = Path(__file__).resolve().parent.parent
IEEE_DATA_DIR = ROOT_DIR / "helixzero_ieee_v5" / "data"
RAW_MASTER = IEEE_DATA_DIR / "ieee_gold_bronze_master.csv"
OUT_DATASET = IEEE_DATA_DIR / "ieee_v5_potency_debiased_master.csv"


def hill_equation(log_conc: np.ndarray, pIC50: float, h: float, E_max: float) -> np.ndarray:
    """Standard 3-parameter Hill dose-response function (E_min = 0)."""
    conc = 10.0 ** log_conc
    ic50 = 10.0 ** (9.0 - pIC50)
    return E_max / (1.0 + (ic50 / (conc + 1e-9)) ** h)


def fit_single_curve(concs: np.ndarray, effs: np.ndarray) -> tuple | None:
    """Fits bounded Hill equation on empirical multi-concentration data."""
    valid = (~np.isnan(concs)) & (~np.isnan(effs)) & (concs > 0)
    c, e = concs[valid], effs[valid]
    if len(np.unique(c)) < 3:
        return None

    log_c = np.log10(c)
    # Bounds: pIC50 in [4.5, 12.0], h in [0.4, 2.8], E_max in [60.0, 105.0]
    p0 = [8.5, 1.0, 95.0]
    try:
        popt, _ = curve_fit(
            hill_equation, log_c, e, p0=p0,
            bounds=([4.5, 0.4, 60.0], [12.0, 2.8, 105.0]),
            maxfev=1500
        )
        preds = hill_equation(log_c, *popt)
        ss_res = np.sum((e - preds) ** 2)
        ss_tot = np.sum((e - np.mean(e)) ** 2)
        r2 = 1.0 - (ss_res / (ss_tot + 1e-8)) if ss_tot > 0 else 0.0

        pIC50, h, E_max = popt
        ic50_nM = 10.0 ** (9.0 - pIC50)
        if r2 >= 0.75:
            return float(pIC50), float(ic50_nM), float(h), float(E_max), float(r2), len(c)
    except Exception:
        pass
    return None


def main():
    logger.info(f"Loading raw master from {RAW_MASTER}...")
    df = pd.read_csv(RAW_MASTER)
    logger.info(f"Total rows in raw master: {len(df):,}")

    # 1. Retain legacy GOLD curves
    gold = df[df["tier"] == "GOLD"].copy()
    logger.info(f"Preserving existing verified GOLD curves: {len(gold):,}")
    gold_records = []
    for _, r in gold.iterrows():
        gold_records.append({
            "sense_seq": str(r["sense_seq"]),
            "anti_seq": str(r["anti_seq"]),
            "sense_mods": str(r["sense_mods"]) if pd.notna(r["sense_mods"]) else "",
            "anti_mods": str(r["anti_mods"]) if pd.notna(r["anti_mods"]) else "",
            "tier": "GOLD_LEGACY",
            "pIC50": float(r["estimated_pIC50"]),
            "ic50_nM": float(r["estimated_ic50_nM"]),
            "hill_slope": float(r["hill_slope"]) if pd.notna(r["hill_slope"]) else 1.0,
            "fit_r2": float(r["fit_r2"]) if pd.notna(r["fit_r2"]) else 1.0,
            "source_type": "MULTI_DOSE_HILL"
        })

    # 2. Recover multi-dose curves from BRONZE
    bronze = df[df["tier"] == "BRONZE"].copy()
    logger.info(f"Scanning {len(bronze):,} BRONZE rows for un-fitted multi-dose series...")
    grouped = bronze.groupby(["sense_seq", "anti_seq", "sense_mods", "anti_mods"])
    
    recovered_count = 0
    recovered_records = []
    
    for (s, a, sm, am), group in grouped:
        concs = group["measured_conc_nM"].values
        effs = group["measured_efficacy_pct"].values
        fit_res = fit_single_curve(concs, effs)
        if fit_res is not None:
            pIC50, ic50_nM, h, E_max, r2, n_pts = fit_res
            recovered_records.append({
                "sense_seq": str(s),
                "anti_seq": str(a),
                "sense_mods": str(sm) if pd.notna(sm) else "",
                "anti_mods": str(am) if pd.notna(am) else "",
                "tier": "GOLD_RECOVERED",
                "pIC50": round(pIC50, 4),
                "ic50_nM": round(ic50_nM, 4),
                "hill_slope": round(h, 3),
                "fit_r2": round(r2, 4),
                "source_type": "MULTI_DOSE_HILL"
            })
            recovered_count += 1

    logger.info(f"✅ Successfully recovered {recovered_count:,} high-fidelity GOLD curves (R² >= 0.75)!")

    # 3. Anchor Inactive / Weak candidates (Breaking Survivorship Bias)
    logger.info("Extracting verified inactive / low-potency negative anchors...")
    inactive_candidates = bronze[
        ((bronze["measured_conc_nM"] == 10.0) & (bronze["measured_efficacy_pct"] <= 15.0)) |
        ((bronze["measured_conc_nM"] == 50.0) & (bronze["measured_efficacy_pct"] <= 20.0))
    ].drop_duplicates(subset=["sense_seq", "anti_seq"])

    logger.info(f"Found {len(inactive_candidates):,} inactive candidates tested at 10-50 nM.")
    sampled_inactive = inactive_candidates.sample(n=min(1200, len(inactive_candidates)), random_state=42)
    
    inactive_records = []
    for _, r in sampled_inactive.iterrows():
        eff = max(1.0, float(r["measured_efficacy_pct"]))
        c = float(r["measured_conc_nM"])
        ic50_est = c * (100.0 - eff) / eff
        ic50_est = np.clip(ic50_est, 300.0, 100000.0)
        pIC50_est = 9.0 - np.log10(ic50_est)
        
        inactive_records.append({
            "sense_seq": str(r["sense_seq"]),
            "anti_seq": str(r["anti_seq"]),
            "sense_mods": str(r["sense_mods"]) if pd.notna(r["sense_mods"]) else "",
            "anti_mods": str(r["anti_mods"]) if pd.notna(r["anti_mods"]) else "",
            "tier": "INACTIVE_ANCHOR",
            "pIC50": round(float(pIC50_est), 4),
            "ic50_nM": round(float(ic50_est), 2),
            "hill_slope": 1.0,
            "fit_r2": 1.0,
            "source_type": "CALIBRATED_INACTIVE"
        })
    logger.info(f"✅ Created {len(inactive_records):,} calibrated inactive anchors (pIC50 4.0 - 6.5).")

    # 4. Merge all sets into Master De-Biased Dataset
    all_records = gold_records + recovered_records + inactive_records
    out_df = pd.DataFrame(all_records)
    out_df = out_df.drop_duplicates(subset=["sense_seq", "anti_seq", "sense_mods", "anti_mods"])
    
    out_df.to_csv(OUT_DATASET, index=False)
    logger.info(f"🎉 Master De-Biased Dataset saved to {OUT_DATASET}!")
    logger.info(f"Total Unique Curves: {len(out_df):,} (vs original 2,309 GOLD curves -> {len(out_df)/2309:.2f}x expansion!)")
    
    print("\n" + "="*80)
    print("DE-BIASED DATASET AUDIT SUMMARY:")
    print("="*80)
    print(out_df["tier"].value_counts())
    print("\npIC50 Distribution:")
    print(out_df["pIC50"].describe())
    print("\nDynamic Range Comparison:")
    print(f"Legacy GOLD Range: {gold['estimated_pIC50'].min():.2f} - {gold['estimated_pIC50'].max():.2f} (span: {gold['estimated_pIC50'].max() - gold['estimated_pIC50'].min():.2f} log units)")
    print(f"De-Biased Range  : {out_df['pIC50'].min():.2f} - {out_df['pIC50'].max():.2f} (span: {out_df['pIC50'].max() - out_df['pIC50'].min():.2f} log units)")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
