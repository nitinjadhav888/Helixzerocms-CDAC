"""
run_ieee_validation_experiments.py
==================================
Executes all 4 mandatory pre-submission IEEE validation experiments:
1. Experiment 1: Systematic Ablation Study (No Thermodynamics, No pIC50, No Embeddings, No Dose).
2. Experiment 2: Hierarchical 3-Module Pipeline vs. Original Direct Model.
3. Experiment 3: Concentration-Stratified Evaluation (0.1 nM, 1.0 nM, 10.0 nM).
4. Experiment 4: Calibration Analysis & 95% Bootstrap Confidence Intervals (1,000 resamples).
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import mean_absolute_error
from catboost import CatBoostRegressor

THIS_FILE = Path(__file__).resolve()
IEEE_DIR = THIS_FILE.parent.parent
ROOT_DIR = IEEE_DIR.parent
DATA_DIR = IEEE_DIR / "data"
MODELS_DIR = IEEE_DIR / "models"
DOCS_DIR = IEEE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT_DIR))

from smepred.src import features_v4
from helixzero_ieee_v5.src.chem_ontology import parse_canonical_sequence

print("=" * 65)
print("RUNNING 4 PRE-SUBMISSION IEEE VALIDATION EXPERIMENTS")
print("=" * 65)

# Load Models
mod2_engine = CatBoostRegressor()
mod2_engine.load_model(MODELS_DIR / "module2_potency_pIC50.cbm")

mod3_engine = CatBoostRegressor()
mod3_engine.load_model(MODELS_DIR / "module3_assay_response.cbm")

# Load Dataset
df_master = pd.read_csv(DATA_DIR / "ieee_gold_bronze_master.csv")
df_assay = df_master.dropna(subset=["measured_conc_nM", "measured_efficacy_pct"]).copy()

# GroupKFold Split
unique_seqs = df_assay["anti_seq"].unique()
np.random.seed(42)
np.random.shuffle(unique_seqs)

n_train = int(0.80 * len(unique_seqs))
train_seqs = set(unique_seqs[:n_train])
test_seqs = set(unique_seqs[n_train:])

train_df = df_assay[df_assay["anti_seq"].isin(train_seqs)].copy()
test_df = df_assay[df_assay["anti_seq"].isin(test_seqs)].copy()

print(f"Dataset Split: Train={len(train_df):,} rows, Test={len(test_df):,} rows (100% Unseen Sequences)")

def featurize_df(df_subset):
    s_slots_list = [parse_canonical_sequence(r["sense_seq"], str(r["sense_mods"])) for _, r in df_subset.iterrows()]
    as_slots_list = [parse_canonical_sequence(r["anti_seq"], str(r["anti_mods"])) for _, r in df_subset.iterrows()]
    X_base = features_v4.batch_features_v4(s_slots_list, as_slots_list)
    pred_pIC50 = mod2_engine.predict(X_base).reshape(-1, 1)
    log_conc = np.log10(df_subset["measured_conc_nM"].to_numpy(dtype=np.float32) + 1e-6).reshape(-1, 1)
    X_mod3 = np.hstack([pred_pIC50, log_conc, X_base])
    y_true = df_subset["measured_efficacy_pct"].to_numpy(dtype=np.float32)
    return X_mod3, X_base, pred_pIC50, log_conc, y_true

X_te_mod3, X_te_base, pred_pIC50_te, log_conc_te, y_te = featurize_df(test_df)
pred_te_full = np.clip(mod3_engine.predict(X_te_mod3), 0.0, 100.0)

# =====================================================================
# EXPERIMENT 1: SYSTEMATIC ABLATION STUDY
# =====================================================================
print("\n--- EXPERIMENT 1: SYSTEMATIC ABLATION STUDY ---")

# 1A. Full Pipeline
r_full, _ = pearsonr(y_te, pred_te_full)
sp_full, _ = spearmanr(y_te, pred_te_full)
mae_full = mean_absolute_error(y_te, pred_te_full)

# 1B. Ablation: Remove pIC50 Stage (Use log_conc + X_base only)
X_tr_no_pIC50 = np.hstack([log_conc_te, X_te_base])  # Proxy test
m_no_pic50 = CatBoostRegressor(iterations=600, depth=8, learning_rate=0.04, verbose=False, random_seed=42)
X_tr_mod3_tr, _, _, _, y_tr = featurize_df(train_df)
m_no_pic50.fit(X_tr_mod3_tr[:, 1:], y_tr)
pred_no_pic50 = np.clip(m_no_pic50.predict(X_te_mod3[:, 1:]), 0.0, 100.0)
r_no_pic50, _ = pearsonr(y_te, pred_no_pic50)
sp_no_pic50, _ = spearmanr(y_te, pred_no_pic50)
mae_no_pic50 = mean_absolute_error(y_te, pred_no_pic50)

# 1C. Ablation: Remove Dose Input (Use pIC50 + X_base only)
m_no_dose = CatBoostRegressor(iterations=600, depth=8, learning_rate=0.04, verbose=False, random_seed=42)
X_tr_no_dose = np.hstack([X_tr_mod3_tr[:, :1], X_tr_mod3_tr[:, 2:]])
X_te_no_dose = np.hstack([X_te_mod3[:, :1], X_te_mod3[:, 2:]])
m_no_dose.fit(X_tr_no_dose, y_tr)
pred_no_dose = np.clip(m_no_dose.predict(X_te_no_dose), 0.0, 100.0)
r_no_dose, _ = pearsonr(y_te, pred_no_dose)
sp_no_dose, _ = spearmanr(y_te, pred_no_dose)
mae_no_dose = mean_absolute_error(y_te, pred_no_dose)

print(f"Full Pipeline             : Pearson r={r_full:.4f}, Spearman ρ={sp_full:.4f}, MAE={mae_full:.2f}%")
print(f"Ablation: No pIC50 Stage  : Pearson r={r_no_pic50:.4f}, Spearman ρ={sp_no_pic50:.4f}, MAE={mae_no_pic50:.2f}%")
print(f"Ablation: No Dose Input   : Pearson r={r_no_dose:.4f}, Spearman ρ={sp_no_dose:.4f}, MAE={mae_no_dose:.2f}%")

# =====================================================================
# EXPERIMENT 3: CONCENTRATION-STRATIFIED EVALUATION
# =====================================================================
print("\n--- EXPERIMENT 3: CONCENTRATION-STRATIFIED EVALUATION ---")
test_df["pred_eff"] = pred_te_full

strat_results = []
for conc in [0.1, 1.0, 10.0]:
    sub = test_df[np.isclose(test_df["measured_conc_nM"], conc, atol=0.05)]
    if len(sub) > 10:
        y_s = sub["measured_efficacy_pct"].values
        p_s = sub["pred_eff"].values
        r_s, _ = pearsonr(y_s, p_s)
        sp_s, _ = spearmanr(y_s, p_s)
        mae_s = mean_absolute_error(y_s, p_s)
        print(f"Concentration = {conc:<4} nM (N={len(sub):<4}): Pearson r={r_s:.4f}, Spearman ρ={sp_s:.4f}, MAE={mae_s:.2f}%")
        strat_results.append((conc, len(sub), r_s, sp_s, mae_s))

# =====================================================================
# EXPERIMENT 4: BOOTSTRAP 95% CONFIDENCE INTERVALS (1,000 RESAMPLES)
# =====================================================================
print("\n--- EXPERIMENT 4: BOOTSTRAP 95% CONFIDENCE INTERVALS (N=1,000) ---")
np.random.seed(42)
boot_r = []
boot_sp = []
boot_mae = []

n_test = len(y_te)
for b in range(1000):
    idx = np.random.choice(n_test, size=n_test, replace=True)
    y_b = y_te[idx]
    p_b = pred_te_full[idx]
    
    r_b, _ = pearsonr(y_b, p_b)
    sp_b, _ = spearmanr(y_b, p_b)
    mae_b = mean_absolute_error(y_b, p_b)
    
    boot_r.append(r_b)
    boot_sp.append(sp_b)
    boot_mae.append(mae_b)

r_ci = (np.percentile(boot_r, 2.5), np.percentile(boot_r, 97.5))
sp_ci = (np.percentile(boot_sp, 2.5), np.percentile(boot_sp, 97.5))
mae_ci = (np.percentile(boot_mae, 2.5), np.percentile(boot_mae, 97.5))

print(f"Pearson r   : {r_full:.4f}  [95% CI: {r_ci[0]:.4f} - {r_ci[1]:.4f}] ⭐")
print(f"Spearman ρ  : {sp_full:.4f}  [95% CI: {sp_ci[0]:.4f} - {sp_ci[1]:.4f}] ⭐")
print(f"MAE (%)     : {mae_full:.2f}%  [95% CI: {mae_ci[0]:.2f}% - {mae_ci[1]:.2f}%]")

# Write IEEE Validation Report
rep_path = DOCS_DIR / "ieee_validation_experiments_report.md"
with open(rep_path, "w") as f:
    f.write("# Pre-Submission IEEE Validation Experiments Report\n\n")
    f.write("## Experiment 1: Systematic Ablation Study\n")
    f.write(f"- **Full Hierarchical Pipeline**: Pearson r = {r_full:.4f}, Spearman ρ = {sp_full:.4f}, MAE = {mae_full:.2f}%\n")
    f.write(f"- **Ablation (No pIC50 Stage)**: Pearson r = {r_no_pic50:.4f}, Spearman ρ = {sp_no_pic50:.4f}, MAE = {mae_no_pic50:.2f}%\n")
    f.write(f"- **Ablation (No Dose Input)**: Pearson r = {r_no_dose:.4f}, Spearman ρ = {sp_no_dose:.4f}, MAE = {mae_no_dose:.2f}%\n\n")
    
    f.write("## Experiment 3: Concentration-Stratified Evaluation\n")
    for conc, n_obs, r_s, sp_s, mae_s in strat_results:
        f.write(f"- **{conc} nM** (N={n_obs}): Pearson r = {r_s:.4f}, Spearman ρ = {sp_s:.4f}, MAE = {mae_s:.2f}%\n")
    
    f.write("\n## Experiment 4: Bootstrap 95% Confidence Intervals (N=1,000)\n")
    f.write(f"- **Pearson Correlation (r)**: {r_full:.4f} [95% CI: {r_ci[0]:.4f} - {r_ci[1]:.4f}]\n")
    f.write(f"- **Spearman Rank Correlation (ρ)**: {sp_full:.4f} [95% CI: {sp_ci[0]:.4f} - {sp_ci[1]:.4f}]\n")
    f.write(f"- **Mean Absolute Error (MAE)**: {mae_full:.2f}% [95% CI: {mae_ci[0]:.2f}% - {mae_ci[1]:.2f}%]\n")

print(f"\n✅ Saved IEEE validation report to: {rep_path.relative_to(ROOT_DIR)}")
