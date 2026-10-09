# 03. TECHNICAL STACK & DEPENDENCY PROVENANCE
## Exact Software, Algorithmic, and Infrastructure Stack
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. Technology Inventory Matrix

Every technology documented below is verified by direct evidence in the codebase. No libraries or frameworks are assumed.

| Category | Technology | Verified Version | Where Used | Why Used | Codebase Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Language Runtime** | **Python** | `3.11.9` / `3.10+` | Root, `smepred/`, `scripts/` | Core programming language for scientific computing, ML, and API microservice. | Verified in `Dockerfile:1` (`FROM python:3.11-slim`) and runtime `sys.version`. |
| **ML Framework** | **CatBoost** | `>=1.2.0` | `smepred/src/model_b_v4.py`, `scripts/train_unified_dose_aware_catboost.py` | Trains and serves the 517-D Unified Dose-Aware Regressor using oblivious decision trees. | Imported in `smepred/src/model_b_v4.py:10` (`from catboost import CatBoostRegressor`). |
| **ML Framework** | **LightGBM** | `>=4.0.0` | `smepred/src/predictor.py`, `smepred/models/model_normal.txt` | Rapid upstream scanning of mRNA transcripts (Model A 214-D baseline and 190-D context). | Imported in `smepred/src/predictor.py:92` (`import lightgbm as lgb`). |
| **ML Framework** | **scikit-learn** | `>=1.3.0` | `smepred/src/calibrator.py`, `scripts/train_unified_dose_aware_catboost.py` | Provides `GroupKFold`, PCA dimensionality reduction, and isotonic regression calibration. | Imported in `scripts/train_unified_dose_aware_catboost.py:19` (`from sklearn.model_selection import GroupKFold`). |
| **Scientific Computing** | **NumPy** | `>=1.24.0` | Omnipresent in `smepred/src/`, `scripts/` | High-performance multi-dimensional array operations and feature vector concatenation. | Imported in `smepred/src/features_v4.py:12` (`import numpy as np`). |
| **Data Processing** | **Pandas** | `>=2.0.0` | Data ingestion, benchmark tabulation, feature extraction | Ingests, parses, cleans, and groups multi-assay chemical modification datasets. | Imported in `scripts/train_unified_dose_aware_catboost.py:17` (`import pandas as pd`). |
| **Statistical Physics** | **SciPy** | `>=1.11.0` | `scripts/run_all_model_benchmarks_live.py`, `smepred/src/` | Calculates Pearson $r$, Spearman $\rho$, and non-linear curve fitting metrics. | Imported in `scripts/run_all_model_benchmarks_live.py:24` (`from scipy.stats import pearsonr, spearmanr`). |
| **Bioinformatics** | **Biopython** | `>=1.81` | `smepred/src/parser.py`, `smepred/src/sirna_generator.py` | Ingests and parses standard FASTA and GenBank nucleotide records. | In `requirements.txt:2` (`biopython>=1.81`) and `smepred/src/parser.py`. |
| **Bioinformatics** | **ViennaRNA** | `2.6.4` (C-extension or fallback) | `smepred/src/features_v4.py:177`, `smepred/src/predictor.py:574` | Computes Minimum Free Energy (MFE) folding, duplex binding $\Delta G$, and partition functions. | Handled in `smepred/src/features_v4.py:177` (`import RNA`) with deterministic Turner fallback. |
| **Deep Learning** | **PyTorch & PyG** | `>=2.4.0` | `MEG-mod-main/`, `helixzero/models/` | Historical Graph Neural Network (TransformerConv) exploration and graph attention weights. | In `requirements.txt:8` (`torch-geometric>=2.4.0`) and `MEG-mod-main/model.py`. |
| **Web Framework** | **FastAPI** | `>=0.104.0` | `smepred/api/main.py` | Production asynchronous REST API gateway serving prediction endpoints. | Imported in `smepred/api/main.py:41` (`from fastapi import FastAPI`). |
| **ASGI Server** | **Uvicorn** | `>=0.24.0` | Server startup, `start_system.bat` | Production ASGI web server hosting the FastAPI application on port 8000. | In `requirements.txt:11` (`uvicorn[standard]>=0.24`) and `start_system.bat`. |
| **Frontend Runtime** | **Vanilla HTML5 / CSS3 / ES2022** | Modern Standard | `smepred/app.html` | Zero-dependency, high-performance laboratory workbench SPA. | Located at `smepred/app.html` (4,670 lines, 239 KB single-file SPA). |
| **3D Rendering** | **3Dmol.js** | `2.0.4` | `smepred/app.html:8` | Real-time WebGL rendering of A-form siRNA double helices with B-factor color mapping. | Script inclusion in `smepred/app.html:8` (`3Dmol-min.js`). |
| **Model Persistence** | **Joblib** | `>=1.3.0` | `smepred/src/features_v4.py`, `smepred/models/` | Serializes and loads fitted PCA models, isotonic calibrators, and legacy LightGBM boosters. | Imported in `smepred/src/features_v4.py:13` (`import joblib`). |
| **Containerization** | **Docker** | Engine `20.10+` | `Dockerfile` | Containerized deployment for CDAC HPC and cloud infrastructures. | Configured in `Dockerfile` with multi-stage caching and healthcheck probes. |
| **LLM Integration** | **Google GenAI** | `>=0.1.0` | `smepred/src/assistant_service.py` | Powers the conversational scientific co-pilot grounded in biophysical guardrails. | In `requirements.txt:18` (`google-genai>=0.1.0`). |

---

### 2. Hardware and Compute Specifications

- **Development OS:** Microsoft Windows 11 Enterprise (Tested with PowerShell 5.1 / PowerShell 7).
- **Target Deployment OS:** Linux (Ubuntu 22.04 LTS / Debian Bookworm container).
- **CPU Architecture:** x86_64 (AVX2 instructions utilized for NumPy vectorization).
- **RAM Footprint:**
  - Active ML Inference: $< 500\text{ MB}$.
  - Whole-Transcriptome Off-Target Slicing: $\sim 1.4\text{ GB}$ (when `human_transcriptome.idx.pkl` is loaded into memory).
- **GPU Requirements:** None for active production runtime. Both LightGBM and CatBoost run natively on CPU multi-threading.
