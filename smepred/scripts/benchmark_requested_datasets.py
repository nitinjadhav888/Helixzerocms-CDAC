"""
benchmark_requested_datasets.py
================================
Comprehensive, strict empirical benchmark evaluation of all multi-mod models, ensembles, 
and embedding ablation variations across the THREE primary target datasets:

1. v2_multislot_dataset.csv  (N=42,638 master dataset)
2. cmsirnadb_full.csv        (N=25,863 cmSiRNADB dataset)
3. siRNAmod.xls              (N=5,329 siRNAmod literature dataset)

Metrics calculated for each configuration:
- Spearman rank correlation (rho)
- Pearson correlation (r)
- Mean Absolute Error (MAE %)
- Root Mean Squared Error (RMSE %)
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

# Add paths
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "smepred"))
sys.path.insert(0, str(ROOT_DIR / "MEG-mod-main"))

from smepred.src import model_b_v4, gnn_serving, features_v4, chem_schema

# File paths
V2_FULL_CSV = ROOT_DIR / "smepred" / "data" / "processed" / "v2_multislot_dataset.csv"
CMS_FULL_CSV = ROOT_DIR / "smepred" / "data" / "processed" / "cmsirnadb_full.csv"
SIRNAMOD_XLS = ROOT_DIR / "smepred" / "data" / "processed" / "siRNAmod.xls"

def eval_metrics(y_true, y_pred):
    sp, sp_p = spearmanr(y_true, y_pred)
    pe, pe_p = pearsonr(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    return float(sp), float(pe), float(mae), float(rmse)

def extract_slot_from_row(row, strand, pos):
    b = str(row.get(f"{strand}_pos{pos}_base", "A")).upper()
    if b == "NAN" or not b or len(b) > 1: b = "A"
    s = str(row.get(f"{strand}_pos{pos}_sugar", "ribo"))
    if s == "NAN" or not s or s == "none": s = "ribo"
    l = str(row.get(f"{strand}_pos{pos}_linkage3p", "PO"))
    if l == "NAN" or not l or l == "none": l = "PO"
    bm = row.get(f"{strand}_pos{pos}_basemod")
    if pd.isna(bm) or bm == "none": bm = None
    t5 = row.get(f"{strand}_pos{pos}_term5p")
    if pd.isna(t5) or t5 == "none": t5 = None
    return chem_schema.NucSlot(base=b, sugar=s, linkage_3p=l, base_mod=bm, terminal_5p=t5)

fm_start = features_v4._N_V2
fm_end = fm_start + features_v4.N_FM
ernie_start = fm_end
ernie_end = ernie_start + features_v4.N_ERNIE

# -----------------------------------------------------------------------------
# 1. EVALUATION ON v2_multislot_dataset.csv (N=42,638)
# -----------------------------------------------------------------------------
print("=" * 90)
print("1. LOADING v2_multislot_dataset.csv (N=42,638 master dataset)...")
df_v2 = pd.read_csv(V2_FULL_CSV, low_memory=False)
df_v2 = df_v2.dropna(subset=["sense_seq", "anti_seq", "efficacy"]).reset_index(drop=True)
print(f"  Valid master rows: {len(df_v2):,}")

v2_s_slots, v2_a_slots = [], []
for _, r in df_v2.iterrows():
    s_s = [extract_slot_from_row(r, "sense", i) for i in range(1, len(str(r["sense_seq"])) + 1)]
    a_s = [extract_slot_from_row(r, "anti", i) for i in range(1, len(str(r["anti_seq"])) + 1)]
    v2_s_slots.append(s_s)
    v2_a_slots.append(a_s)

print("  Extracting 522-dim features for v2_multislot_dataset.csv...")
X_v2_full = features_v4.batch_features_v4(v2_s_slots, v2_a_slots)
y_v2_true = df_v2["efficacy"].to_numpy(dtype=np.float32)

print("  Predicting CatBoost v4 (full features)...")
cb_v4_v2_pred = np.clip(model_b_v4._load().predict(X_v2_full), 0.0, 100.0)

print("  Predicting Fine-Tuned MEG-mod GNN (finetuned_v2.pt)...")
s_base_v2 = df_v2["sense_seq"].str.upper().tolist()
a_base_v2 = df_v2["anti_seq"].str.upper().tolist()
gnn_v2_ft_pred = gnn_serving.predict_gnn(s_base_v2, a_base_v2, s_base_v2, a_base_v2, ckpt_key="finetuned_v2")

print("  Predicting Original MEG-mod GNN (best_model.pt)...")
gnn_v2_orig_pred = gnn_serving.predict_gnn(s_base_v2, a_base_v2, s_base_v2, a_base_v2, ckpt_key="best_model")

# Ablations for v2_multislot_dataset
X_v2_no_fm = X_v2_full.copy()
X_v2_no_fm[:, fm_start:fm_end] = 0.0
cb_v2_no_fm_pred = np.clip(model_b_v4._load().predict(X_v2_no_fm), 0.0, 100.0)

X_v2_no_ernie = X_v2_full.copy()
X_v2_no_ernie[:, ernie_start:ernie_end] = 0.0
cb_v2_no_ernie_pred = np.clip(model_b_v4._load().predict(X_v2_no_ernie), 0.0, 100.0)

X_v2_no_emb = X_v2_full.copy()
X_v2_no_emb[:, fm_start:ernie_end] = 0.0
cb_v2_no_emb_pred = np.clip(model_b_v4._load().predict(X_v2_no_emb), 0.0, 100.0)


# -----------------------------------------------------------------------------
# 2. EVALUATION ON cmsirnadb_full.csv (N=25,863)
# -----------------------------------------------------------------------------
print("\n" + "=" * 90)
print("2. LOADING cmsirnadb_full.csv (N=25,863 cmSiRNADB dataset)...")
df_cms = pd.read_csv(CMS_FULL_CSV, low_memory=False)
df_cms = df_cms.dropna(subset=["sense", "antisense", "base_sense", "base_antisense", "efficacy"]).reset_index(drop=True)
print(f"  Valid cmSiRNADB rows: {len(df_cms):,}")

cms_s_slots, cms_a_slots = [], []
for _, r in df_cms.iterrows():
    s_s = [chem_schema.NucSlot(base=b.upper(), sugar="2OMe" if m.islower() else "ribo") for b, m in zip(r["base_sense"], r["sense"])]
    a_s = [chem_schema.NucSlot(base=b.upper(), sugar="2OMe" if m.islower() else "ribo") for b, m in zip(r["base_antisense"], r["antisense"])]
    cms_s_slots.append(s_s)
    cms_a_slots.append(a_s)

print("  Extracting 522-dim features for cmsirnadb_full.csv...")
X_cms_full = features_v4.batch_features_v4(cms_s_slots, cms_a_slots)
y_cms_true = df_cms["efficacy"].to_numpy(dtype=np.float32)

print("  Predicting CatBoost v4 (full features)...")
cb_v4_cms_pred = np.clip(model_b_v4._load().predict(X_cms_full), 0.0, 100.0)

print("  Predicting Fine-Tuned MEG-mod GNN (finetuned_v2.pt)...")
s_base_cms = df_cms["base_sense"].str.upper().tolist()
a_base_cms = df_cms["base_antisense"].str.upper().tolist()
s_mod_cms = df_cms["sense"].tolist()
a_mod_cms = df_cms["antisense"].tolist()
gnn_cms_ft_pred = gnn_serving.predict_gnn(s_base_cms, a_base_cms, s_mod_cms, a_mod_cms, ckpt_key="finetuned_v2")

print("  Predicting Original MEG-mod GNN (best_model.pt)...")
gnn_cms_orig_pred = gnn_serving.predict_gnn(s_base_cms, a_base_cms, s_mod_cms, a_mod_cms, ckpt_key="best_model")

# Ablations for cmSiRNADB
X_cms_no_fm = X_cms_full.copy()
X_cms_no_fm[:, fm_start:fm_end] = 0.0
cb_cms_no_fm_pred = np.clip(model_b_v4._load().predict(X_cms_no_fm), 0.0, 100.0)

X_cms_no_ernie = X_cms_full.copy()
X_cms_no_ernie[:, ernie_start:ernie_end] = 0.0
cb_cms_no_ernie_pred = np.clip(model_b_v4._load().predict(X_cms_no_ernie), 0.0, 100.0)

X_cms_no_emb = X_cms_full.copy()
X_cms_no_emb[:, fm_start:ernie_end] = 0.0
cb_cms_no_emb_pred = np.clip(model_b_v4._load().predict(X_cms_no_emb), 0.0, 100.0)


# -----------------------------------------------------------------------------
# 3. EVALUATION ON siRNAmod.xls (N=5,329)
# -----------------------------------------------------------------------------
print("\n" + "=" * 90)
print("3. LOADING siRNAmod.xls (N=5,329 literature dataset)...")
df_mod = pd.read_excel(SIRNAMOD_XLS)
df_mod = df_mod.dropna(subset=["Sequence of sense strand", "Sequence of antisense strand", "Biological inhibition percentage"]).reset_index(drop=True)
print(f"  Valid siRNAmod rows: {len(df_mod):,}")

mod_s_slots, mod_a_slots = [], []
for _, r in df_mod.iterrows():
    ss = str(r["Sequence of sense strand"])
    as_ = str(r["Sequence of antisense strand"])
    sm = str(r["Modifications (sense strand)"]) if pd.notna(r["Modifications (sense strand)"]) else ""
    am = str(r["Modifications  (antisense strand)"]) if pd.notna(r["Modifications  (antisense strand)"]) else ""
    
    s_s = chem_schema.parse_position_string(sm, ss) or [chem_schema.NucSlot(base=b.upper()) for b in ss]
    a_s = chem_schema.parse_position_string(am, as_) or [chem_schema.NucSlot(base=b.upper()) for b in as_]
    mod_s_slots.append(s_s)
    mod_a_slots.append(a_s)

print("  Extracting 522-dim features for siRNAmod.xls...")
X_mod_full = features_v4.batch_features_v4(mod_s_slots, mod_a_slots)
y_mod_true = df_mod["Biological inhibition percentage"].to_numpy(dtype=np.float32)

print("  Predicting CatBoost v4 (full features)...")
cb_v4_mod_pred = np.clip(model_b_v4._load().predict(X_mod_full), 0.0, 100.0)

print("  Predicting Fine-Tuned MEG-mod GNN (finetuned_v2.pt)...")
s_base_mod = df_mod["Sequence of sense strand"].str.upper().tolist()
a_base_mod = df_mod["Sequence of antisense strand"].str.upper().tolist()
gnn_mod_ft_pred = gnn_serving.predict_gnn(s_base_mod, a_base_mod, s_base_mod, a_base_mod, ckpt_key="finetuned_v2")

print("  Predicting Original MEG-mod GNN (best_model.pt)...")
gnn_mod_orig_pred = gnn_serving.predict_gnn(s_base_mod, a_base_mod, s_base_mod, a_base_mod, ckpt_key="best_model")

# Ablations for siRNAmod
X_mod_no_fm = X_mod_full.copy()
X_mod_no_fm[:, fm_start:fm_end] = 0.0
cb_mod_no_fm_pred = np.clip(model_b_v4._load().predict(X_mod_no_fm), 0.0, 100.0)

X_mod_no_ernie = X_mod_full.copy()
X_mod_no_ernie[:, ernie_start:ernie_end] = 0.0
cb_mod_no_ernie_pred = np.clip(model_b_v4._load().predict(X_mod_no_ernie), 0.0, 100.0)

X_mod_no_emb = X_mod_full.copy()
X_mod_no_emb[:, fm_start:ernie_end] = 0.0
cb_mod_no_emb_pred = np.clip(model_b_v4._load().predict(X_mod_no_emb), 0.0, 100.0)


# -----------------------------------------------------------------------------
# PRINT RESULTS SUMMARY TABLES FOR ALL THREE DATASETS
# -----------------------------------------------------------------------------

def print_dataset_report(ds_name, y_true, cb_pred, gnn_ft_pred, gnn_orig_pred, cb_no_fm, cb_no_ernie, cb_no_emb):
    print("\n" + "=" * 95)
    print(f"BENCHMARK REPORT: {ds_name} (N={len(y_true):,})")
    print("=" * 95)
    print(f"{'Model / Ensemble / Feature Configuration':<45} | {'Spearman rho':<12} | {'Pearson r':<10} | {'MAE (%)':<8} | {'RMSE (%)':<8}")
    print("-" * 95)

    configs = {
        "CatBoost v4 (100% GBDT)": cb_pred,
        "Fine-Tuned MEG-mod GNN (100% GNN)": gnn_ft_pred,
        "Original MEG-mod GNN (best_model.pt)": gnn_orig_pred,
        "Ensemble 95% GBDT / 5% GNN": 0.95 * cb_pred + 0.05 * gnn_ft_pred,
        "Ensemble 90% GBDT / 10% GNN": 0.90 * cb_pred + 0.10 * gnn_ft_pred,
        "Ensemble 85% GBDT / 15% GNN (Prod Ensemble_v4)": 0.85 * cb_pred + 0.15 * gnn_ft_pred,
        "Ensemble 80% GBDT / 20% GNN": 0.80 * cb_pred + 0.20 * gnn_ft_pred,
        "Ensemble 75% GBDT / 25% GNN": 0.75 * cb_pred + 0.25 * gnn_ft_pred,
        "Ensemble 70% GBDT / 30% GNN": 0.70 * cb_pred + 0.30 * gnn_ft_pred,
        "Ensemble 50% GBDT / 50% GNN": 0.50 * cb_pred + 0.50 * gnn_ft_pred,
        "--- FEATURE ABLATION (CatBoost v4) ---": None,
        "Full 522-dim Features (v2 + FM + ERNIE + Vienna)": cb_pred,
        "Ablated RNA-FM (-32 dim)": cb_no_fm,
        "Ablated RNA-Ernie (-32 dim)": cb_no_ernie,
        "Ablated BOTH Embeddings (v2 + Vienna only)": cb_no_emb,
    }

    for name, preds in configs.items():
        if preds is None:
            print("-" * 95)
            continue
        sp, pe, mae, rmse = eval_metrics(y_true, preds)
        print(f"{name:<45} | {sp:<12.4f} | {pe:<10.4f} | {mae:<8.2f} | {rmse:<8.2f}")


print_dataset_report("v2_multislot_dataset.csv (Master Dataset)", y_v2_true, cb_v4_v2_pred, gnn_v2_ft_pred, gnn_v2_orig_pred, cb_v2_no_fm_pred, cb_v2_no_ernie_pred, cb_v2_no_emb_pred)

print_dataset_report("cmsirnadb_full.csv (cmSiRNADB Dataset)", y_cms_true, cb_v4_cms_pred, gnn_cms_ft_pred, gnn_cms_orig_pred, cb_cms_no_fm_pred, cb_cms_no_ernie_pred, cb_cms_no_emb_pred)

print_dataset_report("siRNAmod.xls (siRNAmod Literature Dataset)", y_mod_true, cb_v4_mod_pred, gnn_mod_ft_pred, gnn_mod_orig_pred, cb_mod_no_fm_pred, cb_mod_no_ernie_pred, cb_mod_no_emb_pred)

print("=" * 95)
