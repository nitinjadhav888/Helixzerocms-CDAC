"""
train_rnafm_zero_leakage_benchmark.py
======================================
Strict Zero-Leakage RNA Foundation Model (RNA-FM) Benchmark:
- Training: Hu.csv ONLY (N=2,361)
- Testing:  Mix.csv 100% Unseen (N=472, across 7 independent studies)
- Features:
  1. Live 640-dim RNA-FM Transformer Layer-12 Embeddings (Sense & Antisense)
  2. 24-dim Thermodynamic Vectors (td: terminal dG, seed stability, dG_open)
  3. 214-dim Positional Sequence Motifs & Thermodynamic Profiles
- Models:
  1. Regularized LightGBM
  2. Oblivious CatBoost
  3. Foundation-Biophysics Blend Ensemble
"""

import sys
import torch
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "smepred"))

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score, mean_squared_error, r2_score
from scipy.stats import pearsonr, spearmanr
import lightgbm as lgb
from catboost import CatBoostRegressor
from sklearn.linear_model import RidgeCV

from smepred.src import predictor
import fm

COMP_MAP = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C', 'T': 'A'}

def get_21mer_duplex(guide19: str):
    guide19 = guide19.upper().replace('T', 'U')
    sense19 = "".join(COMP_MAP.get(b, 'A') for b in guide19[::-1])
    sense21 = sense19 + "UU"
    anti21 = guide19 + "UU"
    return sense21, anti21

def extract_rnafm_embeddings_batch(sequences, model, batch_converter, batch_size=64):
    embeddings = []
    print(f"Extracting RNA-FM embeddings for {len(sequences)} sequences (batch_size={batch_size})...", flush=True)
    
    with torch.no_grad():
        for i in range(0, len(sequences), batch_size):
            batch_seqs = sequences[i : i + batch_size]
            data = [(f"seq_{j}", s) for j, s in enumerate(batch_seqs)]
            _, _, batch_tokens = batch_converter(data)
            results = model(batch_tokens, repr_layers=[12])
            token_reps = results["representations"][12]
            
            for j, s in enumerate(batch_seqs):
                # Mean pool excluding <cls> and <eos>
                seq_rep = token_reps[j, 1 : len(s) + 1].mean(0).cpu().numpy()
                embeddings.append(seq_rep)
                
            if (i // batch_size) % 10 == 0:
                print(f"  Processed {min(i + batch_size, len(sequences))} / {len(sequences)} sequences", flush=True)
                
    return np.array(embeddings, dtype=np.float32)

def main():
    print("=" * 80)
    print("🧬 RNA-FM FOUNDATION-AUGMENTED ZERO-LEAKAGE BENCHMARK")
    print("=" * 80)
    
    # 1. Load Datasets
    hu_path = ROOT_DIR / "smepred" / "data" / "oligoformer" / "Hu.csv"
    mix_path = ROOT_DIR / "smepred" / "data" / "oligoformer" / "Mix.csv"
    
    df_hu = pd.read_csv(hu_path)
    df_mix = pd.read_csv(mix_path)
    
    # Ground truth labels
    y_train = df_hu["label"].values * 100.0 if df_hu["label"].max() <= 1.0 else df_hu["label"].values
    y_test = df_mix["label"].values * 100.0 if df_mix["label"].max() <= 1.0 else df_mix["label"].values
    
    # Prepare 21-mer sequences
    senses_hu, antis_hu = [], []
    for s in df_hu["siRNA"]:
        s21, a21 = get_21mer_duplex(str(s))
        senses_hu.append(s21)
        antis_hu.append(a21)
        
    senses_mix, antis_mix = [], []
    for s in df_mix["siRNA"]:
        s21, a21 = get_21mer_duplex(str(s))
        senses_mix.append(s21)
        antis_mix.append(a21)

    # 2. Extract Classical Positional & Biophysical Features (214-dim)
    print("\n--- 1. Extracting 214-d Positional Sequence Features ---", flush=True)
    X_pos_train = predictor.extract_batch_v4(senses_hu, antis_hu)
    X_pos_test = predictor.extract_batch_v4(senses_mix, antis_mix)
    
    # 3. Extract 24-dim Thermodynamic Vectors (td)
    td_train = np.array([list(map(float, row.split(","))) for row in df_hu["td"]], dtype=np.float32)
    td_test = np.array([list(map(float, row.split(","))) for row in df_mix["td"]], dtype=np.float32)
    
    # Terminal asymmetry delta: (5' AS - 5' Sense)
    asym_train = (td_train[:, 0] - td_train[:, 1]).reshape(-1, 1)
    asym_test = (td_test[:, 0] - td_test[:, 1]).reshape(-1, 1)
    
    # 4. Extract Live 640-dim RNA-FM Foundation Embeddings
    print("\n--- 2. Extracting Live 640-d RNA-FM Foundation Model Embeddings ---", flush=True)
    fm_model, fm_alphabet = fm.pretrained.rna_fm_t12()
    fm_model.eval()
    batch_converter = fm_alphabet.get_batch_converter()
    
    # Antisense & Sense embeddings
    fm_as_train = extract_rnafm_embeddings_batch(antis_hu, fm_model, batch_converter)
    fm_ss_train = extract_rnafm_embeddings_batch(senses_hu, fm_model, batch_converter)
    
    fm_as_test = extract_rnafm_embeddings_batch(antis_mix, fm_model, batch_converter)
    fm_ss_test = extract_rnafm_embeddings_batch(senses_mix, fm_model, batch_converter)
    
    # Concatenate Sense + Antisense FM embeddings (1280-dim)
    fm_comb_train = np.hstack([fm_ss_train, fm_as_train])
    fm_comb_test = np.hstack([fm_ss_test, fm_as_test])
    
    # Fit PCA ONLY on Training Data (Zero Leakage Protocol)
    print("\n--- 3. Fitting PCA (64-dim) on Training Data ONLY ---", flush=True)
    pca = PCA(n_components=64, random_state=42)
    fm_pca_train = pca.fit_transform(fm_comb_train)
    fm_pca_test = pca.transform(fm_comb_test)
    print(f"  PCA Explained Variance Ratio (64 components): {pca.explained_variance_ratio_.sum():.4f}", flush=True)
    
    # Combine All Feature Modalities
    X_train = np.hstack([X_pos_train, td_train, asym_train, fm_pca_train])
    X_test = np.hstack([X_pos_test, td_test, asym_test, fm_pca_test])
    print(f"\nFinal Master Feature Space Shape: Train={X_train.shape}, Test={X_test.shape}", flush=True)

    # 5. Train Zero-Leakage Model Stack
    print("\n--- 4. Training Foundation-Augmented Zero-Leakage Models ---", flush=True)
    
    # Model 1: Regularized LightGBM
    lgb_model = lgb.LGBMRegressor(
        n_estimators=500,
        learning_rate=0.018,
        num_leaves=31,
        colsample_bytree=0.70,
        subsample=0.80,
        reg_alpha=2.0,
        reg_lambda=4.0,
        min_child_samples=25,
        random_state=42,
        verbose=-1
    )
    lgb_model.fit(X_train, y_train)
    p_lgb = np.clip(lgb_model.predict(X_test), 0.0, 100.0)
    
    # Model 2: Oblivious Tree CatBoost
    cb_model = CatBoostRegressor(
        iterations=650,
        learning_rate=0.025,
        depth=6,
        l2_leaf_reg=5.0,
        random_seed=42,
        verbose=0
    )
    cb_model.fit(X_train, y_train)
    p_cb = np.clip(cb_model.predict(X_test), 0.0, 100.0)
    
    # Model 3: Regularized Ridge Regression
    ridge = RidgeCV(alphas=np.logspace(-2, 4, 30))
    ridge.fit(X_train, y_train)
    p_ridge = np.clip(ridge.predict(X_test), 0.0, 100.0)
    
    # Model 4: Foundation-Biophysics Ensemble Blend
    p_blend = 0.45 * p_lgb + 0.45 * p_cb + 0.10 * p_ridge
    
    # 6. Evaluation & Reporting
    def score_model(name, preds):
        r, _ = pearsonr(y_test, preds)
        rho, _ = spearmanr(y_test, preds)
        auc = roc_auc_score((y_test >= 70.0).astype(int), preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        print(f"▶ {name:<36} | PCC (r) = {r:.4f} | SPCC (rho) = {rho:.4f} | AUC = {auc:.4f} | RMSE = {rmse:.2f}% | R² = {r2:.4f}", flush=True)
        return {"Model": name, "PCC": r, "SPCC": rho, "AUC": auc, "RMSE": rmse, "R2": r2}

    print("\n" + "=" * 90)
    print("📊 ZERO-LEAKAGE BENCHMARK ON MIXSET (TRAINED ON HU ONLY, N=472 UNSEEN)")
    print("=" * 90)
    res_lgb = score_model("LightGBM + RNA-FM + Biophysics", p_lgb)
    res_cb = score_model("CatBoost + RNA-FM + Biophysics", p_cb)
    res_ridge = score_model("Ridge + RNA-FM + Biophysics", p_ridge)
    res_ens = score_model("RNA-FM Foundation Ensemble (Blend)", p_blend)
    print("=" * 90)

    # Save Results
    out_df = pd.DataFrame([res_lgb, res_cb, res_ridge, res_ens])
    out_file = ROOT_DIR / "rnafm_pure_zeroleakage_benchmark_results.csv"
    out_df.to_csv(out_file, index=False)
    print(f"\n✅ All results saved to: {out_file}", flush=True)

if __name__ == "__main__":
    main()
