"""
benchmark_multimod_comprehensive.py
====================================
Comprehensive, empirical benchmark evaluation of all multi-mod models, ensembles, 
and feature ablation variations across test datasets:

1. Models:
   - CatBoost v4 (model_b_v4.cbm)
   - Fine-tuned MEG-mod PyTorch GNN (finetuned_v2.pt)
   - Original MEG-mod PyTorch GNN (best_model.pt)
   - Ensemble weight grid: 100/0, 95/5, 90/10, 85/15, 80/20, 75/25, 70/30, 50/50, 0/100

2. Feature Ablations on CatBoost v4:
   - Full 522-dim feature space (444 v2 + RNA-FM + RNA-Ernie + ViennaRNA)
   - Without RNA-FM embeddings (-32 dim)
   - Without RNA-Ernie embeddings (-32 dim)
   - Without BOTH RNA-FM and RNA-Ernie (-64 dim embeddings)

3. Datasets:
   - v2_test.csv (N=4,769 locked test split)
   - cleaned_patent_set.csv (N=435 real-world patent dataset)
   - alnylam_140_duplex_benchmark_results.csv (N=32 IC50 holdout)
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

# Add parent directory of smepred to sys.path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "smepred"))
sys.path.insert(0, str(ROOT_DIR / "MEG-mod-main"))

from smepred.src import model_b_v4, gnn_serving, features_v4, chem_schema
from smepred.scripts.data.patent_sources import parse_alnylam_compact, parse_position_string

# Paths
V2_TEST_CSV = ROOT_DIR / "MEG-mod-main" / "data_split" / "v2_test.csv"
PATENT_CSV = ROOT_DIR / "smepred" / "data" / "patent_data" / "cleaned_patent_set.csv"
ALNYLAM_CSV = ROOT_DIR / "smepred" / "data" / "alnylam_140_duplex_benchmark_results.csv"

def eval_metrics(y_true, y_pred):
    sp, sp_p = spearmanr(y_true, y_pred)
    pe, pe_p = pearsonr(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    return float(sp), float(pe), float(mae), float(rmse)

# -----------------------------------------------------------------------------
# 1. EVALUATION ON v2_test.csv (N=4,769)
# -----------------------------------------------------------------------------
print("=" * 80)
print("1. LOADING v2_test.csv (N=4,769 locked test duplexes)...")
df_v2 = pd.read_csv(V2_TEST_CSV)
df_v2 = df_v2.dropna(subset=["sense", "antisense", "knockdown"]).reset_index(drop=True)
print(f"  Valid test rows: {len(df_v2):,}")

# Build multi-slot representations for features_v4
def parse_v2_row_slots(row):
    ss = str(row["sense"])
    as_ = str(row["antisense"])
    s_mods = str(row["modification_sense"]) if pd.notna(row["modification_sense"]) else ""
    a_mods = str(row["modification_antisense"]) if pd.notna(row["modification_antisense"]) else ""
    
    s_slots = parse_position_string(s_mods, ss) or [chem_schema.NucSlot(base=b.upper()) for b in ss]
    a_slots = parse_position_string(a_mods, as_) or [chem_schema.NucSlot(base=b.upper()) for b in as_]
    return s_slots, a_slots

print("  Extracting 522-dim features for v2_test.csv...")
v2_s_slots, v2_a_slots = [], []
for _, r in df_v2.iterrows():
    s_s, a_s = parse_v2_row_slots(r)
    v2_s_slots.append(s_s)
    v2_a_slots.append(a_s)

X_v2_full = features_v4.batch_features_v4(v2_s_slots, v2_a_slots)
y_v2_true = df_v2["knockdown"].to_numpy(dtype=np.float32)

print("  Predicting CatBoost v4 (full features)...")
cb_v4_v2_pred = np.clip(model_b_v4._load().predict(X_v2_full), 0.0, 100.0)

print("  Predicting Fine-Tuned MEG-mod GNN (finetuned_v2.pt)...")
s_base_v2 = df_v2["sense"].str.upper().tolist()
a_base_v2 = df_v2["antisense"].str.upper().tolist()
gnn_v2_ft_pred = gnn_serving.predict_gnn(s_base_v2, a_base_v2, s_base_v2, a_base_v2, ckpt_key="finetuned_v2")

print("  Predicting Original MEG-mod GNN (best_model.pt)...")
gnn_v2_orig_pred = gnn_serving.predict_gnn(s_base_v2, a_base_v2, s_base_v2, a_base_v2, ckpt_key="best_model")

# Ablation feature matrices for CatBoost v4
fm_start = features_v4._N_V2
fm_end = fm_start + features_v4.N_FM
ernie_start = fm_end
ernie_end = ernie_start + features_v4.N_ERNIE

# Ablate RNA-FM
X_v2_no_fm = X_v2_full.copy()
X_v2_no_fm[:, fm_start:fm_end] = 0.0
cb_v4_no_fm_pred = np.clip(model_b_v4._load().predict(X_v2_no_fm), 0.0, 100.0)

# Ablate RNA-Ernie
X_v2_no_ernie = X_v2_full.copy()
X_v2_no_ernie[:, ernie_start:ernie_end] = 0.0
cb_v4_no_ernie_pred = np.clip(model_b_v4._load().predict(X_v2_no_ernie), 0.0, 100.0)

# Ablate BOTH embeddings
X_v2_no_emb = X_v2_full.copy()
X_v2_no_emb[:, fm_start:ernie_end] = 0.0
cb_v4_no_emb_pred = np.clip(model_b_v4._load().predict(X_v2_no_emb), 0.0, 100.0)


# -----------------------------------------------------------------------------
# 2. EVALUATION ON cleaned_patent_set.csv (N=435)
# -----------------------------------------------------------------------------
print("\n2. LOADING cleaned_patent_set.csv (N=435 real patent duplexes)...")
df_pat = pd.read_csv(PATENT_CSV)
df_pat = df_pat.dropna(subset=["sense_seq", "anti_seq", "knockdown"]).reset_index(drop=True)
print(f"  Valid patent rows: {len(df_pat):,}")

pat_s_slots, pat_a_slots = [], []
for _, r in df_pat.iterrows():
    s_s = parse_position_string(r.get("sense_mod"), r["sense_seq"]) or [chem_schema.NucSlot(base=b.upper()) for b in r["sense_seq"]]
    a_s = parse_position_string(r.get("anti_mod"), r["anti_seq"]) or [chem_schema.NucSlot(base=b.upper()) for b in r["anti_seq"]]
    pat_s_slots.append(s_s)
    pat_a_slots.append(a_s)

X_pat_full = features_v4.batch_features_v4(pat_s_slots, pat_a_slots)
y_pat_true = df_pat["knockdown"].to_numpy(dtype=np.float32)

cb_v4_pat_pred = np.clip(model_b_v4._load().predict(X_pat_full), 0.0, 100.0)

s_base_pat = df_pat["sense_seq"].str.upper().tolist()
a_base_pat = df_pat["anti_seq"].str.upper().tolist()
gnn_pat_ft_pred = gnn_serving.predict_gnn(s_base_pat, a_base_pat, s_base_pat, a_base_pat, ckpt_key="finetuned_v2")
gnn_pat_orig_pred = gnn_serving.predict_gnn(s_base_pat, a_base_pat, s_base_pat, a_base_pat, ckpt_key="best_model")

# Ablations for Patent dataset
X_pat_no_fm = X_pat_full.copy()
X_pat_no_fm[:, fm_start:fm_end] = 0.0
cb_pat_no_fm_pred = np.clip(model_b_v4._load().predict(X_pat_no_fm), 0.0, 100.0)

X_pat_no_ernie = X_pat_full.copy()
X_pat_no_ernie[:, ernie_start:ernie_end] = 0.0
cb_pat_no_ernie_pred = np.clip(model_b_v4._load().predict(X_pat_no_ernie), 0.0, 100.0)

X_pat_no_emb = X_pat_full.copy()
X_pat_no_emb[:, fm_start:ernie_end] = 0.0
cb_pat_no_emb_pred = np.clip(model_b_v4._load().predict(X_pat_no_emb), 0.0, 100.0)


# -----------------------------------------------------------------------------
# 3. EVALUATION ON alnylam_140_duplex_benchmark_results.csv (N=32 IC50 Holdout)
# -----------------------------------------------------------------------------
print("\n3. LOADING alnylam_140_duplex_benchmark_results.csv (N=32 IC50 holdout)...")
from smepred.scripts.data.patent_sources import load_external_ic50_holdout
df_aln = load_external_ic50_holdout()
print(f"  Valid Alnylam IC50 holdout duplexes: {len(df_aln):,}")

aln_s_slots = [parse_alnylam_compact(m) for m in df_aln["sense_compact"]]
aln_a_slots = [parse_alnylam_compact(m) for m in df_aln["anti_compact"]]

X_aln_full = features_v4.batch_features_v4(aln_s_slots, aln_a_slots)
y_aln_potency = -np.log10(df_aln["ic50_nM"].to_numpy() + 1e-10)

cb_v4_aln_pred = model_b_v4._load().predict(X_aln_full)

s_base_aln = [s[0].base for s in aln_s_slots] # extract sequence string
s_base_aln_seqs = ["".join([slot.base for slot in s]) for s in aln_s_slots]
a_base_aln_seqs = ["".join([slot.base for slot in a]) for a in aln_a_slots]

gnn_aln_ft_pred = gnn_serving.predict_gnn(s_base_aln_seqs, a_base_aln_seqs, s_base_aln_seqs, a_base_aln_seqs, ckpt_key="finetuned_v2")

X_aln_no_fm = X_aln_full.copy()
X_aln_no_fm[:, fm_start:fm_end] = 0.0
cb_aln_no_fm_pred = model_b_v4._load().predict(X_aln_no_fm)

X_aln_no_ernie = X_aln_full.copy()
X_aln_no_ernie[:, ernie_start:ernie_end] = 0.0
cb_aln_no_ernie_pred = model_b_v4._load().predict(X_aln_no_ernie)

X_aln_no_emb = X_aln_full.copy()
X_aln_no_emb[:, fm_start:ernie_end] = 0.0
cb_aln_no_emb_pred = model_b_v4._load().predict(X_aln_no_emb)


# -----------------------------------------------------------------------------
# PRINT RESULTS & SUMMARY TABLES
# -----------------------------------------------------------------------------

print("\n" + "=" * 90)
print("A. MODEL EVALUATION RESULTS ON v2_test.csv (N=4,769)")
print("=" * 90)
print(f"{'Model / Ensemble Configuration':<40} | {'Spearman rho':<12} | {'Pearson r':<10} | {'MAE (%)':<8} | {'RMSE (%)':<8}")
print("-" * 90)

models_v2 = {
    "CatBoost v4 (GBDT 100%)": cb_v4_v2_pred,
    "Fine-Tuned MEG-mod GNN (GNN 100%)": gnn_v2_ft_pred,
    "Original MEG-mod GNN (ECUST)": gnn_v2_orig_pred,
    "Ensemble 95% GBDT / 5% GNN": 0.95 * cb_v4_v2_pred + 0.05 * gnn_v2_ft_pred,
    "Ensemble 90% GBDT / 10% GNN": 0.90 * cb_v4_v2_pred + 0.10 * gnn_v2_ft_pred,
    "Ensemble 85% GBDT / 15% GNN (Prod Ensemble_v4)": 0.85 * cb_v4_v2_pred + 0.15 * gnn_v2_ft_pred,
    "Ensemble 80% GBDT / 20% GNN": 0.80 * cb_v4_v2_pred + 0.20 * gnn_v2_ft_pred,
    "Ensemble 75% GBDT / 25% GNN": 0.75 * cb_v4_v2_pred + 0.25 * gnn_v2_ft_pred,
    "Ensemble 70% GBDT / 30% GNN": 0.70 * cb_v4_v2_pred + 0.30 * gnn_v2_ft_pred,
    "Ensemble 50% GBDT / 50% GNN": 0.50 * cb_v4_v2_pred + 0.50 * gnn_v2_ft_pred,
}

for name, preds in models_v2.items():
    sp, pe, mae, rmse = eval_metrics(y_v2_true, preds)
    print(f"{name:<40} | {sp:<12.4f} | {pe:<10.4f} | {mae:<8.2f} | {rmse:<8.2f}")


print("\n" + "=" * 90)
print("B. FEATURE ABLATION STUDY ON CatBoost v4 (v2_test.csv N=4,769)")
print("=" * 90)
print(f"{'Feature Set Configuration':<40} | {'Spearman rho':<12} | {'Pearson r':<10} | {'MAE (%)':<8} | {'RMSE (%)':<8}")
print("-" * 90)

ablations_v2 = {
    "Full 522-dim Features (v2 + FM + ERNIE + Vienna)": cb_v4_v2_pred,
    "Ablated RNA-FM (-32 dim)": cb_v4_no_fm_pred,
    "Ablated RNA-Ernie (-32 dim)": cb_v4_no_ernie_pred,
    "Ablated BOTH Embeddings (v2 + Vienna only)": cb_v4_no_emb_pred,
}

for name, preds in ablations_v2.items():
    sp, pe, mae, rmse = eval_metrics(y_v2_true, preds)
    print(f"{name:<40} | {sp:<12.4f} | {pe:<10.4f} | {mae:<8.2f} | {rmse:<8.2f}")


print("\n" + "=" * 90)
print("C. REAL-WORLD PATENT DATASET EVALUATION (cleaned_patent_set.csv N=435)")
print("=" * 90)
print(f"{'Model / Configuration':<40} | {'Spearman rho':<12} | {'Pearson r':<10} | {'MAE (%)':<8} | {'RMSE (%)':<8}")
print("-" * 90)

models_pat = {
    "CatBoost v4 (GBDT 100%)": cb_v4_pat_pred,
    "Fine-Tuned MEG-mod GNN (GNN 100%)": gnn_pat_ft_pred,
    "Original MEG-mod GNN (ECUST)": gnn_pat_orig_pred,
    "Ensemble 85% GBDT / 15% GNN (Prod)": 0.85 * cb_v4_pat_pred + 0.15 * gnn_pat_ft_pred,
    "Ensemble 50% GBDT / 50% GNN": 0.50 * cb_v4_pat_pred + 0.50 * gnn_pat_ft_pred,
    "Ablated RNA-FM (CatBoost v4)": cb_pat_no_fm_pred,
    "Ablated RNA-Ernie (CatBoost v4)": cb_pat_no_ernie_pred,
    "Ablated BOTH Embeddings (CatBoost v4)": cb_pat_no_emb_pred,
}

for name, preds in models_pat.items():
    sp, pe, mae, rmse = eval_metrics(y_pat_true, preds)
    print(f"{name:<40} | {sp:<12.4f} | {pe:<10.4f} | {mae:<8.2f} | {rmse:<8.2f}")


print("\n" + "=" * 90)
print("D. ALNYLAM IC50 HOLDOUT BENCHMARK (N=32 Duplexes)")
print("=" * 90)
print(f"{'Model / Configuration':<40} | {'Spearman rho vs IC50':<22} | {'Pearson r vs IC50':<20}")
print("-" * 90)

models_aln = {
    "CatBoost v4 (GBDT 100%)": cb_v4_aln_pred,
    "Fine-Tuned MEG-mod GNN (GNN 100%)": gnn_aln_ft_pred,
    "Ensemble 85% GBDT / 15% GNN (Prod)": 0.85 * cb_v4_aln_pred + 0.15 * gnn_aln_ft_pred,
    "Ensemble 50% GBDT / 50% GNN": 0.50 * cb_v4_aln_pred + 0.50 * gnn_aln_ft_pred,
    "Ablated RNA-FM (CatBoost v4)": cb_aln_no_fm_pred,
    "Ablated RNA-Ernie (CatBoost v4)": cb_aln_no_ernie_pred,
    "Ablated BOTH Embeddings (CatBoost v4)": cb_aln_no_emb_pred,
}

for name, preds in models_aln.items():
    sp, _ = spearmanr(preds, y_aln_potency)
    pe, _ = pearsonr(preds, y_aln_potency)
    print(f"{name:<40} | {sp:<22.4f} | {pe:<20.4f}")

print("=" * 90)
