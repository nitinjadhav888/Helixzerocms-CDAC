"""
benchmark_helixzero_full_suite.py
==================================
Comprehensive 100% Real Empirical Validation Suite across ALL workspace datasets:
1. Standard Reference Benchmarks:
   - Huesken Gold-Standard Screen (Hu.csv, N=2,361)
   - Takayuki Independent Transfer (Taka.csv, N=702)
   - Mixset 7-Study Generalization (Mix.csv, N=472)
2. Chemically Modified Benchmarks:
   - CMsiRNAdb Heterogeneous Held-Out Test Set (hetero_val_303.csv, N=2,576)
   - CMsiRNAdb Homogeneous Test Set (homo_val.csv, N=472)
   - CMsiRNAdb Full Curated Database (cmsirnadb_full.csv, N=25,863)
   - HelixZero Unified Master IEEE Dataset (helixzero_unified_master_ieee_dataset.csv, N=47,407)
"""

import sys
import traceback
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "smepred"))

import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import roc_auc_score, mean_squared_error, mean_absolute_error, r2_score

from smepred.src import model_b_v4, features_v4, biophysics, predictor
from smepred.src.chem_schema import promote_legacy_string
from helixzero_ieee_v5.predict_ieee_v5 import mod2_engine, mod3_engine

COMP_MAP = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C', 'T': 'A'}

def get_21mer_duplex(guide19: str):
    guide19 = guide19.upper().replace('T', 'U')
    sense19 = "".join(COMP_MAP.get(b, 'A') for b in guide19[::-1])
    sense21 = sense19 + "TT"
    anti21 = guide19 + "TT"
    return sense21, anti21

def calc_metrics(y_true, y_pred, thresh=70.0):
    mask = ~np.isnan(y_true) & ~np.isnan(y_pred)
    yt = np.array(y_true)[mask]
    yp = np.array(y_pred)[mask]
    if len(yt) < 5:
        return {"PCC": 0.0, "SPCC": 0.0, "AUC": 0.0, "RMSE": 0.0, "MAE": 0.0, "R2": 0.0}
    try:
        r, _ = pearsonr(yt, yp)
    except:
        r = 0.0
    try:
        rho, _ = spearmanr(yt, yp)
    except:
        rho = 0.0
    try:
        bin_y = (yt >= thresh).astype(int)
        if len(np.unique(bin_y)) > 1:
            auc = roc_auc_score(bin_y, yp)
        else:
            auc = 0.5
    except:
        auc = 0.5
    rmse = np.sqrt(mean_squared_error(yt, yp))
    mae = mean_absolute_error(yt, yp)
    r2 = r2_score(yt, yp)
    return {
        "PCC": round(float(r), 4),
        "SPCC": round(float(rho), 4),
        "AUC": round(float(auc), 4),
        "RMSE": round(float(rmse), 2),
        "MAE": round(float(mae), 2),
        "R2": round(float(r2), 4)
    }

def evaluate_naked_dataset(filepath: Path, dataset_name: str):
    print(f"Benchmarking: {dataset_name} ({filepath.name})...", flush=True)
    df = pd.read_csv(filepath).dropna(subset=["label"])
    y_true = df["label"].values * 100.0 if df["label"].max() <= 1.0 else df["label"].values
    
    senses, antis = [], []
    for s in df["siRNA"]:
        s21, a21 = get_21mer_duplex(str(s))
        senses.append(s21)
        antis.append(a21)

    # 1. Model 1: Baseline Naked LightGBM
    feat_naked = predictor.extract_batch_v4(senses, antis)
    preds_m1 = np.clip(predictor._predict_naked(feat_naked), 0.0, 100.0)

    # 2. Model 4: IEEE v5 Potency Engine
    s_slots = [promote_legacy_string(s, s) for s in senses]
    a_slots = [promote_legacy_string(a, a) for a in antis]
    X2_feats = features_v4.batch_features_v4(s_slots, a_slots)
    pIC50_pred = mod2_engine.predict(X2_feats)
    log_conc = np.log10(np.array([10.0] * len(df), dtype=np.float32) + 1e-6).reshape(-1, 1)
    X3_feats = np.hstack([pIC50_pred.reshape(-1, 1), log_conc, X2_feats])
    preds_m4 = np.clip(mod3_engine.predict(X3_feats), 0.0, 100.0)

    m1 = calc_metrics(y_true, preds_m1)
    m4 = calc_metrics(y_true, preds_m4)

    return [
        {"Dataset": dataset_name, "N": len(y_true), "Model": "Model 1 (Baseline Naked GBDT)", **m1},
        {"Dataset": dataset_name, "N": len(y_true), "Model": "Model 4 (HelixZero IEEE v5 Hierarchical)", **m4},
    ]

def evaluate_cm_dataset(filepath: Path, dataset_name: str, sample_limit: int = None):
    print(f"Benchmarking: {dataset_name} ({filepath.name})...", flush=True)
    df = pd.read_csv(filepath, low_memory=False)
    eff_col = "efficacy" if "efficacy" in df.columns else ("knockdown_percent" if "knockdown_percent" in df.columns else "label")
    df = df.dropna(subset=[eff_col])
    if sample_limit and len(df) > sample_limit:
        df = df.sample(n=sample_limit, random_state=42).reset_index(drop=True)
        
    y_true = df[eff_col].values.astype(float)
    if y_true.max() <= 1.0: y_true = y_true * 100.0
    
    if "base_sense" in df.columns:
        s_mod_list = [str(r["sense"]) if pd.notnull(r.get("sense")) else "" for _, r in df.iterrows()]
        a_mod_list = [str(r["antisense"]) if pd.notnull(r.get("antisense")) else "" for _, r in df.iterrows()]
        s_base_list = [str(r["base_sense"]) if pd.notnull(r.get("base_sense")) else s_mod_list[i] for i, (_, r) in enumerate(df.iterrows())]
        a_base_list = [str(r["base_antisense"]) if pd.notnull(r.get("base_antisense")) else a_mod_list[i] for i, (_, r) in enumerate(df.iterrows())]
        conc_list = [float(r["concentration_nM"]) if pd.notnull(r.get("concentration_nM")) and float(r["concentration_nM"]) > 0 else 10.0 for _, r in df.iterrows()]
    elif "sense_mods" in df.columns:
        s_mod_list = [str(r["sense_mods"]) if pd.notnull(r.get("sense_mods")) else str(r.get("sense", "")) for _, r in df.iterrows()]
        a_mod_list = [str(r["anti_mods"]) if pd.notnull(r.get("anti_mods")) else str(r.get("antisense", "")) for _, r in df.iterrows()]
        s_base_list = [str(r.get("sense", s_mod_list[i])) for i, (_, r) in enumerate(df.iterrows())]
        a_base_list = [str(r.get("antisense", a_mod_list[i])) for i, (_, r) in enumerate(df.iterrows())]
        conc_list = [10.0] * len(df)
    else:
        s_mod_list = [str(r.get("modified_sense_sequence", r.get("sense", ""))) for _, r in df.iterrows()]
        a_mod_list = [str(r.get("modified_antisense_sequence", r.get("antisense", ""))) for _, r in df.iterrows()]
        s_base_list = [str(r.get("canonical_sense_sequence", s_mod_list[i])) for i, (_, r) in enumerate(df.iterrows())]
        a_base_list = [str(r.get("canonical_antisense_sequence", a_mod_list[i])) for i, (_, r) in enumerate(df.iterrows())]
        conc_list = [10.0] * len(df)

    # 1. Model 1: Baseline Naked GBDT
    feat_naked = predictor.extract_batch_v4(s_base_list, a_base_list)
    preds_m1 = np.clip(predictor._predict_naked(feat_naked), 0.0, 100.0)

    # 2. Model 2: Model B v4 CatBoost GBDT Potency Engine
    preds_m2 = np.clip(model_b_v4.predict(s_mod_list, a_mod_list, s_base_list, a_base_list), 0.0, 100.0)

    # 3. Model 4: HelixZero IEEE v5 Hierarchical Potency Engine
    s_slots = [promote_legacy_string(sm, sb) for sm, sb in zip(s_mod_list, s_base_list)]
    a_slots = [promote_legacy_string(am, ab) for am, ab in zip(a_mod_list, a_base_list)]
    X2_feats = features_v4.batch_features_v4(s_slots, a_slots)
    pIC50_pred = mod2_engine.predict(X2_feats)
    log_conc = np.log10(np.array(conc_list, dtype=np.float32) + 1e-6).reshape(-1, 1)
    X3_feats = np.hstack([pIC50_pred.reshape(-1, 1), log_conc, X2_feats])
    preds_m4 = np.clip(mod3_engine.predict(X3_feats), 0.0, 100.0)

    # 4. Model 5: Biophysics Calibrated Layer
    preds_m5 = []
    for raw_s, sm, am, sb, ab in zip(preds_m2, s_mod_list, a_mod_list, s_base_list, a_base_list):
        adj, _, _ = biophysics.calculate_adjusted_efficacy(raw_s, sm, am, sb, ab)
        preds_m5.append(adj)
    preds_m5 = np.array(preds_m5, dtype=np.float32)

    m1 = calc_metrics(y_true, preds_m1)
    m2 = calc_metrics(y_true, preds_m2)
    m4 = calc_metrics(y_true, preds_m4)
    m5 = calc_metrics(y_true, preds_m5)

    return [
        {"Dataset": dataset_name, "N": len(y_true), "Model": "Model 1 (Baseline Naked GBDT)", **m1},
        {"Dataset": dataset_name, "N": len(y_true), "Model": "Model 2 (Model B v4 CatBoost)", **m2},
        {"Dataset": dataset_name, "N": len(y_true), "Model": "Model 4 (HelixZero IEEE v5 Hierarchical)", **m4},
        {"Dataset": dataset_name, "N": len(y_true), "Model": "Model 5 (HelixZero Calibrated Ensemble)", **m5},
    ]

def main():
    oligo_dir = ROOT_DIR / "smepred" / "data" / "oligoformer"
    proc_dir = ROOT_DIR / "smepred" / "data" / "processed"

    results = []

    print("\n--- 1. Evaluating Standard Reference Datasets ---", flush=True)
    try:
        results.extend(evaluate_naked_dataset(oligo_dir / "Hu.csv", "Huesken Dataset (Internal Gold-Standard)"))
    except Exception as e:
        print(f"Error Hu: {e}")
    try:
        results.extend(evaluate_naked_dataset(oligo_dir / "Taka.csv", "Takayuki Dataset (Independent Transfer)"))
    except Exception as e:
        print(f"Error Taka: {e}")
    try:
        results.extend(evaluate_naked_dataset(oligo_dir / "Mix.csv", "Mixset Dataset (7 Studies Generalization)"))
    except Exception as e:
        print(f"Error Mix: {e}")

    print("\n--- 2. Evaluating Chemically Modified Datasets ---", flush=True)
    try:
        results.extend(evaluate_cm_dataset(proc_dir / "hetero_val_303.csv", "CMsiRNAdb Heterogeneous Held-Out Set"))
    except Exception as e:
        print(f"Error hetero_val: {e}")
    try:
        results.extend(evaluate_cm_dataset(proc_dir / "homo_val.csv", "CMsiRNAdb Homogeneous Test Set"))
    except Exception as e:
        print(f"Error homo_val: {e}")
    try:
        results.extend(evaluate_cm_dataset(proc_dir / "cmsirnadb_full.csv", "CMsiRNAdb Full Curated Master Database", sample_limit=5000))
    except Exception as e:
        print(f"Error cmsirnadb_full: {e}")
    try:
        results.extend(evaluate_cm_dataset(proc_dir / "helixzero_unified_master_ieee_dataset.csv", "HelixZero Unified Master IEEE Dataset", sample_limit=5000))
    except Exception as e:
        print(f"Error unified_ieee: {e}")

    df_res = pd.DataFrame(results)
    out_csv = ROOT_DIR / "helixzero_full_suite_benchmark_report.csv"
    df_res.to_csv(out_csv, index=False)

    print("\n" + "=" * 105, flush=True)
    print("📊 100% REAL EMPIRICAL BENCHMARK PERFORMANCE MATRIX (ALL MODELS & DATASETS)", flush=True)
    print("=" * 105, flush=True)
    print(df_res.to_string(index=False), flush=True)
    print("=" * 105, flush=True)

if __name__ == "__main__":
    main()
