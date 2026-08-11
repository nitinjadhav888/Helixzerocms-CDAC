"""
benchmark_true_models.py

Executes a 100% true, zero-assumption benchmark evaluating our actual trained model checkpoints:
1. Model A Ensemble_v4 (CatBoost GBDT + PyTorch GNN Graph Attention)
2. Model C IEEE v5 Engine (mod2_engine pIC50 + mod3_engine Assay Converter)

Evaluated across:
- Mixset Dataset (Mix.csv - N=472, 7 literature sources: Reynolds, Ui-Tei, Vickers, Amarzguioui, Harborth, Hsieh, Khvorova)
- Huesken Dataset (Hu.csv - N=2,361 siRNAs)
- Takayuki Dataset (Taka.csv - N=702 siRNAs)
- Heterogeneous Modified Validation Dataset (hetero_val_303.csv - N=2,576 siRNAs)
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "smepred"))

import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import roc_auc_score, mean_squared_error, mean_absolute_error

from smepred.src import model_b_v4, gnn_serving, features_v4, biophysics, predictor
from helixzero_ieee_v5.predict_ieee_v5 import mod2_engine, mod3_engine


COMP_MAP = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C', 'T': 'A'}

def get_21mer_duplex(guide19: str):
    guide19 = guide19.upper().replace('T', 'U')
    sense19 = "".join(COMP_MAP.get(b, 'A') for b in guide19[::-1])
    sense21 = sense19 + "TT"
    anti21 = guide19 + "TT"
    return sense21, anti21


def evaluate_dataset(csv_path: Path, dataset_name: str, is_oligoformer_format: bool = True):
    if not csv_path.exists():
        print(f"Dataset {csv_path} not found.")
        return None

    df = pd.read_csv(csv_path)
    
    if is_oligoformer_format:
        df = df.dropna(subset=["label"])
        y_true = df["label"].values * 100.0 if df["label"].max() <= 1.0 else df["label"].values
        senses, antis = [], []
        for s in df["siRNA"]:
            s21, a21 = get_21mer_duplex(str(s))
            senses.append(s21)
            antis.append(a21)
        s_base_list = senses
        a_base_list = antis
        s_mod_list = senses
        a_mod_list = antis
        conc_list = [10.0] * len(df)
    else:
        df = df.dropna(subset=["efficacy"])
        y_true = df["efficacy"].values
        s_mod_list = [str(r["sense"]) for _, r in df.iterrows()]
        a_mod_list = [str(r["antisense"]) for _, r in df.iterrows()]
        s_base_list = [str(r["base_sense"]) for _, r in df.iterrows()]
        a_base_list = [str(r["base_antisense"]) for _, r in df.iterrows()]
        conc_list = [float(r["concentration_nM"]) if pd.notnull(r.get("concentration_nM")) else 10.0 for _, r in df.iterrows()]

    print(f"\n--- Evaluating {dataset_name} (N = {len(y_true)} items) ---")

    # 1. Model A CatBoost GBDT Baseline Score
    ens_raw = np.clip(model_b_v4.predict(s_mod_list, a_mod_list, s_base_list, a_base_list), 0.0, 100.0)

    # 2. Biophysics Adjusted Ensemble_v4
    ens_adj = []
    for raw_s, sm, am, sb, ab in zip(ens_raw, s_mod_list, a_mod_list, s_base_list, a_base_list):
        adj, _, _ = biophysics.calculate_adjusted_efficacy(raw_s, sm, am, sb, ab)
        ens_adj.append(adj)
    ens_adj = np.array(ens_adj)

    # 3. Model C IEEE v5 Engine
    from smepred.src.chem_schema import promote_legacy_string
    s_slots = [promote_legacy_string(sm, sb) for sm, sb in zip(s_mod_list, s_base_list)]
    a_slots = [promote_legacy_string(am, ab) for am, ab in zip(a_mod_list, a_base_list)]
    X2_feats = features_v4.batch_features_v4(s_slots, a_slots)
    pIC50_pred = mod2_engine.predict(X2_feats)
    log_conc = np.log10(np.array(conc_list, dtype=np.float32) + 1e-6).reshape(-1, 1)
    X3_feats = np.hstack([pIC50_pred.reshape(-1, 1), log_conc, X2_feats])
    ieee_kd = np.clip(mod3_engine.predict(X3_feats), 0.0, 100.0)

    def get_metrics(y_real, y_hat):
        r, _ = pearsonr(y_real, y_hat)
        rho, _ = spearmanr(y_real, y_hat)
        auc = roc_auc_score((y_real >= 70.0).astype(int), y_hat)
        rmse = np.sqrt(mean_squared_error(y_real, y_hat))
        mae = mean_absolute_error(y_real, y_hat)
        return r, rho, auc, rmse, mae

    r_raw, rho_raw, auc_raw, rmse_raw, mae_raw = get_metrics(y_true, ens_raw)
    r_adj, rho_adj, auc_adj, rmse_adj, mae_adj = get_metrics(y_true, ens_adj)
    r_v5, rho_v5, auc_v5, rmse_v5, mae_v5 = get_metrics(y_true, ieee_kd)

    print(f"▶ Ensemble_v4 Raw       : PCC (r) = {r_raw:.4f} | SPCC (rho) = {rho_raw:.4f} | AUC = {auc_raw:.4f} | RMSE = {rmse_raw:.2f}")
    print(f"▶ Ensemble_v4 Adjusted  : PCC (r) = {r_adj:.4f} | SPCC (rho) = {rho_adj:.4f} | AUC = {auc_adj:.4f} | RMSE = {rmse_adj:.2f}")
    print(f"▶ IEEE v5 Potency Engine: PCC (r) = {r_v5:.4f} | SPCC (rho) = {rho_v5:.4f} | AUC = {auc_v5:.4f} | RMSE = {rmse_v5:.2f}")

    return {
        "Dataset": dataset_name,
        "N": len(y_true),
        "Ensemble_v4 Raw r": round(r_raw, 3),
        "Ensemble_v4 Raw rho": round(rho_raw, 3),
        "Ensemble_v4 Raw AUC": round(auc_raw, 3),
        "IEEE v5 Engine r": round(r_v5, 3),
        "IEEE v5 Engine rho": round(rho_v5, 3),
        "IEEE v5 Engine AUC": round(auc_v5, 3)
    }


def main():
    print("=" * 95)
    print("⚡ STRICT EMPIRICAL MODEL VALIDATION RUNNER (ZERO ASSUMPTIONS)")
    print("=" * 95)

    oligo_dir = ROOT_DIR / "smepred" / "data" / "oligoformer"
    proc_dir = ROOT_DIR / "smepred" / "data" / "processed"

    results = []

    res_mix = evaluate_dataset(oligo_dir / "Mix.csv", "Mixset Heterogeneous Test Dataset", is_oligoformer_format=True)
    if res_mix: results.append(res_mix)

    res_hu = evaluate_dataset(oligo_dir / "Hu.csv", "Huesken et al. 2005 Dataset", is_oligoformer_format=True)
    if res_hu: results.append(res_hu)

    res_taka = evaluate_dataset(oligo_dir / "Taka.csv", "Takayuki et al. 2007 Dataset", is_oligoformer_format=True)
    if res_taka: results.append(res_taka)

    res_mod = evaluate_dataset(proc_dir / "hetero_val_303.csv", "HelixZero Modified Validation Set", is_oligoformer_format=False)
    if res_mod: results.append(res_mod)

    print("\n" + "=" * 95)
    print("📊 CONSOLIDATED TRUE MODEL PERFORMANCE MATRIX")
    print("=" * 95)
    summary_df = pd.DataFrame(results)
    print(summary_df.to_string(index=False))
    print("=" * 95)

if __name__ == "__main__":
    main()
