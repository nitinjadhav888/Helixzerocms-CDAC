import sys
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, roc_auc_score
from catboost import CatBoostRegressor

ROOT_DIR = Path(__file__).resolve().parent.parent
IEEE_DIR = ROOT_DIR / "helixzero_ieee_v5"
MODELS_DIR = IEEE_DIR / "models"

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "smepred"))

from smepred.src import features_v4
from smepred.src.chem_schema import promote_legacy_string
from helixzero_ieee_v5.src.chem_ontology import parse_canonical_sequence

# Load IEEE v5 models
print("Loading IEEE v5 production models...")
mod2_engine = CatBoostRegressor()
mod2_engine.load_model(MODELS_DIR / "module2_potency_pIC50.cbm")

mod3_engine = CatBoostRegressor()
mod3_engine.load_model(MODELS_DIR / "module3_assay_response.cbm")

def get_21mer_duplex(seq):
    s = str(seq).strip().upper().replace("T", "U")
    if len(s) < 21:
        s = (s + "N" * 21)[:21]
    elif len(s) > 21:
        s = s[:21]
    comp = {'A':'U', 'U':'A', 'G':'C', 'C':'G', 'N':'N'}
    as_seq = "".join([comp.get(base, 'N') for base in reversed(s)])
    return s, as_seq

def evaluate_slots_and_concs(s_slots, a_slots, concs, y_true, name):
    X_base = features_v4.batch_features_v4(s_slots, a_slots)
    pred_pIC50 = mod2_engine.predict(X_base).reshape(-1, 1)
    log_conc = np.log10(np.array(concs, dtype=np.float32) + 1e-6).reshape(-1, 1)
    X_mod3 = np.hstack([pred_pIC50, log_conc, X_base])
    
    preds_val = np.clip(mod3_engine.predict(X_mod3), 0.0, 100.0)
    
    r_val, _ = pearsonr(y_true, preds_val)
    rho_val, _ = spearmanr(y_true, preds_val)
    mae_val = mean_absolute_error(y_true, preds_val)
    rmse_val = np.sqrt(mean_squared_error(y_true, preds_val))
    r2_val = r2_score(y_true, preds_val)
    
    y_true_bin = (y_true >= 70.0).astype(int)
    if len(np.unique(y_true_bin)) > 1:
        auroc = roc_auc_score(y_true_bin, preds_val / 100.0)
    else:
        auroc = float("nan")
        
    print(f"[{name}] N={len(y_true):,} | PCC(r)={r_val:.4f} | SPCC(rho)={rho_val:.4f} | AUC={auroc:.4f} | RMSE={rmse_val:.2f}% | MAE={mae_val:.2f}% | R2={r2_val:.4f}")
    return {
        "Dataset": name,
        "N": len(y_true),
        "PCC": round(r_val, 4),
        "SPCC": round(rho_val, 4),
        "ROC_AUC": round(auroc, 4),
        "RMSE": round(rmse_val, 2),
        "MAE": round(mae_val, 2),
        "R2": round(r2_val, 4)
    }

results = []

# -------------------------------------------------------------
# 1. IEEE Master Test Split (20% Target-Disjoint Sequence Split)
# -------------------------------------------------------------
df_ieee_master = pd.read_csv(IEEE_DIR / "data" / "ieee_gold_bronze_master.csv")
df_ieee_master = df_ieee_master.dropna(subset=["sense_seq", "anti_seq", "measured_efficacy_pct"]).copy()
unique_seqs = df_ieee_master["anti_seq"].dropna().unique()
np.random.seed(42)
test_seqs = set(np.random.choice(unique_seqs, size=int(len(unique_seqs)*0.2), replace=False))
df_ieee_test = df_ieee_master[df_ieee_master["anti_seq"].isin(test_seqs)].copy()

s_mods = df_ieee_test["sense_mods"].fillna("").astype(str).tolist()
a_mods = df_ieee_test["anti_mods"].fillna("").astype(str).tolist()
s_slots_ieee = [parse_canonical_sequence(s, sm) for s, sm in zip(df_ieee_test["sense_seq"], s_mods)]
a_slots_ieee = [parse_canonical_sequence(a, am) for a, am in zip(df_ieee_test["anti_seq"], a_mods)]
concs_ieee = df_ieee_test["measured_conc_nM"].fillna(10.0).to_numpy(dtype=np.float32)
y_ieee = df_ieee_test["measured_efficacy_pct"].to_numpy(dtype=np.float32)

results.append(evaluate_slots_and_concs(s_slots_ieee, a_slots_ieee, concs_ieee, y_ieee, "IEEE Master Test Set (20% Target-Disjoint)"))

# -------------------------------------------------------------
# 2. CMsiRNAdb Homogeneous Test Set (homo_val.csv, N=472)
# -------------------------------------------------------------
df_homo = pd.read_csv(ROOT_DIR / "smepred" / "data" / "processed" / "homo_val.csv")
df_homo = df_homo.dropna(subset=["sense", "antisense", "base_sense", "base_antisense", "efficacy"]).copy()
s_slots_homo = [promote_legacy_string(sm, sb) for sm, sb in zip(df_homo["sense"], df_homo["base_sense"])]
a_slots_homo = [promote_legacy_string(am, ab) for am, ab in zip(df_homo["antisense"], df_homo["base_antisense"])]
concs_homo = [10.0] * len(df_homo)
y_homo = df_homo["efficacy"].to_numpy(dtype=np.float32)

results.append(evaluate_slots_and_concs(s_slots_homo, a_slots_homo, concs_homo, y_homo, "CMsiRNAdb Homogeneous Test Set"))

# -------------------------------------------------------------
# 3. CMsiRNAdb Heterogeneous Held-Out Set (hetero_val_303.csv, N=2,576)
# -------------------------------------------------------------
df_hetero = pd.read_csv(ROOT_DIR / "smepred" / "data" / "processed" / "hetero_val_303.csv")
df_hetero = df_hetero.dropna(subset=["sense", "antisense", "base_sense", "base_antisense", "efficacy"]).copy()
s_slots_hetero = [promote_legacy_string(sm, sb) for sm, sb in zip(df_hetero["sense"], df_hetero["base_sense"])]
a_slots_hetero = [promote_legacy_string(am, ab) for am, ab in zip(df_hetero["antisense"], df_hetero["base_antisense"])]
concs_hetero = df_hetero["concentration_nM"].fillna(10.0).to_numpy(dtype=np.float32)
y_hetero = df_hetero["efficacy"].to_numpy(dtype=np.float32)

results.append(evaluate_slots_and_concs(s_slots_hetero, a_slots_hetero, concs_hetero, y_hetero, "CMsiRNAdb Heterogeneous Held-Out Set"))

# -------------------------------------------------------------
# 4. CMsiRNAdb Full Master Database (cmsirnadb_full.csv, N=5,000 slice)
# -------------------------------------------------------------
df_full = pd.read_csv(ROOT_DIR / "smepred" / "data" / "processed" / "cmsirnadb_full.csv")
df_full = df_full.dropna(subset=["sense", "antisense", "base_sense", "base_antisense", "efficacy"]).copy()
if len(df_full) > 5000:
    df_full_slice = df_full.sample(n=5000, random_state=42).reset_index(drop=True)
else:
    df_full_slice = df_full
s_slots_full = [promote_legacy_string(sm, sb) for sm, sb in zip(df_full_slice["sense"], df_full_slice["base_sense"])]
a_slots_full = [promote_legacy_string(am, ab) for am, ab in zip(df_full_slice["antisense"], df_full_slice["base_antisense"])]
concs_full = df_full_slice["concentration_nM"].fillna(10.0).to_numpy(dtype=np.float32)
y_full = df_full_slice["efficacy"].to_numpy(dtype=np.float32)

results.append(evaluate_slots_and_concs(s_slots_full, a_slots_full, concs_full, y_full, "CMsiRNAdb Full Master Database (N=5,000)"))

# -------------------------------------------------------------
# 5. Huesken Gold-Standard (Hu.csv, N=2,361)
# -------------------------------------------------------------
df_hu = pd.read_csv(ROOT_DIR / "smepred" / "data" / "oligoformer" / "Hu.csv")
df_hu = df_hu.dropna(subset=["siRNA", "label"]).copy()
y_hu = (df_hu["label"].values * 100.0 if df_hu["label"].max() <= 1.0 else df_hu["label"].values).astype(np.float32)
s_slots_hu, a_slots_hu = [], []
for s in df_hu["siRNA"]:
    s21, a21 = get_21mer_duplex(str(s))
    s_slots_hu.append(promote_legacy_string(s21, s21))
    a_slots_hu.append(promote_legacy_string(a21, a21))
concs_hu = [10.0] * len(df_hu)

results.append(evaluate_slots_and_concs(s_slots_hu, a_slots_hu, concs_hu, y_hu, "Huesken Gold-Standard (Unmodified RNA)"))

# -------------------------------------------------------------
# 6. Takayuki Transfer Set (Taka.csv, N=702)
# -------------------------------------------------------------
df_taka = pd.read_csv(ROOT_DIR / "smepred" / "data" / "oligoformer" / "Taka.csv")
df_taka = df_taka.dropna(subset=["siRNA", "label"]).copy()
y_taka = (df_taka["label"].values * 100.0 if df_taka["label"].max() <= 1.0 else df_taka["label"].values).astype(np.float32)
s_slots_taka, a_slots_taka = [], []
for s in df_taka["siRNA"]:
    s21, a21 = get_21mer_duplex(str(s))
    s_slots_taka.append(promote_legacy_string(s21, s21))
    a_slots_taka.append(promote_legacy_string(a21, a21))
concs_taka = [10.0] * len(df_taka)

results.append(evaluate_slots_and_concs(s_slots_taka, a_slots_taka, concs_taka, y_taka, "Takayuki Transfer Set (Unmodified RNA)"))

# -------------------------------------------------------------
# 7. Mixset 7-Study Generalization (Mix.csv, N=472)
# -------------------------------------------------------------
df_mix = pd.read_csv(ROOT_DIR / "smepred" / "data" / "oligoformer" / "Mix.csv")
df_mix = df_mix.dropna(subset=["siRNA", "label"]).copy()
y_mix = (df_mix["label"].values * 100.0 if df_mix["label"].max() <= 1.0 else df_mix["label"].values).astype(np.float32)
s_slots_mix, a_slots_mix = [], []
for s in df_mix["siRNA"]:
    s21, a21 = get_21mer_duplex(str(s))
    s_slots_mix.append(promote_legacy_string(s21, s21))
    a_slots_mix.append(promote_legacy_string(a21, a21))
concs_mix = [10.0] * len(df_mix)

results.append(evaluate_slots_and_concs(s_slots_mix, a_slots_mix, concs_mix, y_mix, "Mixset 7-Study Generalization (Unmodified RNA)"))

df_res = pd.DataFrame(results)
print("\n" + "=" * 95)
print("FINAL CONSOLIDATED HELIXZERO IEEE V5 EMPIRICAL BENCHMARK RESULTS ACROSS ALL DATASETS:")
print("=" * 95)
print(df_res.to_string(index=False))

df_res.to_csv(ROOT_DIR / "ieee_v5_full_benchmark_results.csv", index=False)
print(f"\nSaved to {ROOT_DIR / 'ieee_v5_full_benchmark_results.csv'}")
