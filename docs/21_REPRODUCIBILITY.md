# 21. REPRODUCIBILITY & VERIFICATION GUIDE
## Step-by-Step Instructions to Recreate All Models, Benchmarks, and Audits
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. Prerequisites and Environment Setup

Executed on Microsoft Windows 11 or Linux (Ubuntu 22.04 LTS):

```bash
# 1. Clone the repository
git clone https://github.com/nitinjadhav888/Helixzerocms-CDAC.git
cd Helixzerocms-CDAC

# 2. Initialize Python 3.11 Virtual Environment
python -m venv .venv

# 3. Activate Virtual Environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# 4. Install Verified Python Dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 2. Dataset Preparation & Feature Matrix Verification

Verify that all required pre-processed matrices exist in `smepred/data/processed/`:

```bash
# Verify feature matrix and target shapes
python -c "import numpy as np; X = np.load('smepred/data/processed/cmsirnadb_clean_features_X_517.npy'); Y = np.load('smepred/data/processed/cmsirnadb_clean_targets_Y.npy'); print(f'Feature Matrix X: {X.shape}, Target Y: {Y.shape}')"
# Expected Output: Feature Matrix X: (17761, 517), Target Y: (17761,)
```

---

### 3. Model Training & Zero-Leakage Cross-Validation

To retrain the flagship Unified Dose-Aware CatBoost Regressor from scratch and execute the 5-fold `GroupKFold` cross-validation:

```bash
python scripts/train_unified_dose_aware_catboost.py
```

**Expected Console Output:**
- 5-Fold GroupKFold Cross-Validation: Mean Pearson $r = 0.6776 \pm 0.028$, Mean Spearman $\rho = 0.6752 \pm 0.026$.
- Training duration: $\sim 35\text{--}45$ seconds on CPU.
- Production checkpoint exported to: `smepred/models/unified_dose_catboost.cbm` (1.70 MB).
- Live FDA Blind Benchmark: 100% Sensitivity, Cohort Mean Knockdown: **65.04%** at 10.0 nM.

---

### 4. Running the Full Empirical Benchmark Suite

To execute the 100% live, non-hardcoded benchmark suite across all models and test partitions:

```bash
python scripts/run_all_model_benchmarks_live.py
```

This updates all tables and validates metrics against `final_benchmarks/master_benchmark_metrics.csv`.

---

### 5. Running the Pipeline Integrity Test

To run the end-to-end integration and smoke test:

```bash
python scripts/test_pipeline_integrity.py
```

**Expected Verifications:**
- [PASS] Sequence Parser & 21-mer Generation
- [PASS] Model A Naked Scorer & Isotonic Calibration
- [PASS] Curated Lead Selection & Domain Partitioning
- [PASS] Single-Modification Permutation Scanner
- [PASS] Combinatorial Multi-Mod Beam Search Optimizer
- [PASS] 4-Domain Biophysical Penalty Engine
- [PASS] 2-Bit Whole-Transcriptome Off-Target Slicing Search
- [PASS] Continuous A-Form 3D PDB Structural Generator

---

### 6. Starting the Production Application

```bash
# Launch server via Windows batch script:
start_system.bat

# Or launch directly via CLI:
cd smepred
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Open a web browser and navigate to `http://localhost:8000` to interact with the laboratory workbench.
