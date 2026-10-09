# AI AGENT PROJECT CONTEXT & OPERATIONAL BRIEFING
## Essential Onboarding Guide for Autonomous AI Coding Agents & LLM Pair-Programmers
**Document Status:** `AUTHORITATIVE — READ FIRST BEFORE MODIFYING CODEBASE`  
**Workspace Root:** `d:\Helixx`  
**Authoritative Benchmark Source:** `final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md`  

---

### 1. Project Purpose & Core Architecture

HelixZero-CMS is a production-grade machine learning platform for therapeutic siRNA efficacy prediction, chemical modification optimization, and whole-transcriptome safety verification.

The platform decouples oligonucleotide drug design into two distinct tiers:
1. **Tier 1 (Naked Transcript Scanner):** Ingests mRNA transcripts, evaluates overlapping 21-mers, filters palindromes, annotates transcript domains (5' UTR, CDS, 3' UTR), and scores naked sequences using **Model A** (LightGBM GBDT, 214-D baseline or 190-D context).
2. **Tier 2 (Chemical Modification Potency Engine):** Optimizes chemical configurations on lead duplexes using the **Single Unified Dose-Aware CatBoost Regressor** (517-D). Evaluates deterministic biophysical guardrails (4 domains) and queries a 2-bit packed human transcriptome index to eliminate off-target slicing.
3. **Delivery & UI:** Emits continuous 504-atom A-form PDB models with B-factor encoded modifications, served through a FastAPI backend (`smepred/api/main.py`) to a single-page laboratory workbench (`smepred/app.html`).

---

### 2. The Operational Boundary: Active Production vs. Historical Archives

> [!CRITICAL]
> **DO NOT CONFUSE ACTIVE PRODUCTION MODULES WITH HISTORICAL ABLATION CHECKPOINTS!**

| Subsystem / Directory | Role & Operational Status | Action Guidance for AI Agents |
| :--- | :--- | :--- |
| `smepred/` | **ACTIVE PRODUCTION ENGINE** | Contains all active runtime code: FastAPI API, feature extractors, predictors, biophysics engine, UI, and model checkpoints. **This is where production edits go.** |
| `final_benchmarks/` | **AUTHORITATIVE BENCHMARK SOURCE OF TRUTH** | Contains the certified benchmark report (`00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md`) and metrics CSV. **Never cite numbers from outside this directory.** |
| `helixzero/` | **CLEAN HIGH-LEVEL PACKAGE** | High-level client schemas and featurizers. |
| `helixzero_ieee_v5/` | **RETIRED / HISTORICAL ARCHIVE** | Preserved solely for historical two-stage ($pIC_{50} \to \text{Hill}$) ablation studies. **DO NOT call during active production serving.** |
| `MEG-mod-main/` | **RETIRED / HISTORICAL ARCHIVE** | Preserved solely for GNN TransformerConv ablation studies. **DO NOT call during active production serving.** |
| `docs/` | **MODULAR SYSTEM DOCUMENTATION** | Production-grade documentation system (26 modular files). |

---

### 3. Model Inventory & File Checkpoint Locations

| Model Key | Checkpoint Path | Feature Space | Operational Role |
| :--- | :--- | :---: | :--- |
| `normal` / `Model A` | `smepred/models/model_normal.txt` (`.pkl`) | 214-D | Active: Naked 21-mer transcript scanner ($r = 0.804 - 0.879$). |
| `normal_context` | `smepred/models/model_normal_context.txt` | 190-D | Active: Context-aware naked transcript scanner. |
| `Unified_v5` (Default) | `smepred/models/unified_dose_catboost.cbm` | 517-D | **Active Flagship:** Unified dose-aware chemical modification engine ($r = 0.8359$). |
| `B_v4` | `smepred/models/model_b_v4.cbm` | 517-D | Active Fallback: Alias pointing to the verified 517-D CatBoost checkpoint. |
| `IEEE_v5` | `helixzero_ieee_v5/` | Cascading | Retired: Two-stage cascading engine (ablation only). |
| `GNN_v2` | `MEG-mod-main/finetuned_v2.pt` | Graph | Retired: PyG GNN TransformerConv (ablation only). |

---

### 4. Critical Dependencies & Environment

- **Python Version:** 3.11 (Tested on 3.11.9 on Windows 11).
- **Core Packages:** `catboost>=1.2`, `lightgbm>=4.0`, `scikit-learn>=1.3`, `fastapi>=0.104`, `uvicorn>=0.24`, `numpy>=1.24`, `pandas>=2.0`, `biopython>=1.81`, `scipy>=1.11`.
- **ViennaRNA:** `import RNA` is wrapped in try/except with deterministic Turner nearest-neighbor fallbacks in `smepred/src/features_v4.py:215-226`. Do not break this fallback.

---

### 5. Critical Data Locations

- **Clean Feature Matrix:** `smepred/data/processed/cmsirnadb_clean_features_X_517.npy` ($17,761 \times 517$ float32).
- **Clean Targets:** `smepred/data/processed/cmsirnadb_clean_targets_Y.npy` ($17,761$ float32).
- **Clean Metadata:** `smepred/data/processed/cmsirnadb_clean_meta.csv` (contains `target_gene` groupings).
- **Human Transcriptome Binary Index:** `smepred/data/human_transcriptome.idx.pkl` (863.8 MB packed 2-bit hash).
- **Modification Taxonomy:** `smepred/data/modification_codes.json` (30 standardized chemistries).

---

### 6. Do-Not-Break Components (Protected Seams)

1. **517-D Feature Ordering (`smepred/src/features_v4.py`):**
   - Indices 0–443: Positional and engineered chemistry (420 slot flags + 24 global features).
   - Indices 444–507: RNA-FM embeddings (32 PCA sense + 32 PCA antisense).
   - Indices 508–512: ViennaRNA thermodynamics (5 features).
   - Indices 513–516: Dynamic exposure covariates ($\log_{10}(C)$, $\log_{10}(C) - 1$, $t_{\text{norm}}$, $\text{is\_hepatic}$).
   *NEVER reorder or truncate these feature columns; doing so invalidates the trained CatBoost checkpoint.*
2. **2-Bit Packed Binary Hashing (`smepred/src/offtarget.py`):**
   - The packing scheme maps nucleotides: $\text{A}=0, \text{C}=1, \text{G}=2, \text{U}/\text{T}=3$.
   - Packing a 15-mer requires bitwise shift `(val << 2) | nuc` into a 30-bit integer.
3. **PDB Coordinate B-Factor Mapping (`smepred/src/pdb_generator.py`):**
   - 3Dmol.js in `app.html` relies on exact B-factors ($90.0=2'\text{-F}, 80.0=2'\text{-OMe}, 70.0=\text{PS}$, etc.) for color styling. Do not change these numeric identifiers.
4. **Closed-Form Hill Inversion (`smepred/src/predictor.py:808-811`):**
   - $\text{IC}_{50} = C \cdot (100 - y) / y$, with bounds $y \in [1.0, 99.0]$. Do not reintroduce slow numerical optimization routines.

---

### 7. Common Development Commands

```bash
# 1. Start development server:
start_system.bat
# Or:
cd smepred && uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Run end-to-end integration test:
python scripts/test_pipeline_integrity.py

# 3. Retrain unified CatBoost model (GroupKFold + FDA blind check):
python scripts/train_unified_dose_aware_catboost.py

# 4. Run live benchmark suite:
python scripts/run_all_model_benchmarks_live.py
```

---

### 8. AI AGENT RULES

Before modifying any file in this repository, all AI agents **MUST ALWAYS FOLLOW THESE DIRECTIVES WITHOUT EXCEPTION**:

1. **Read-Before-Writing Directive:** Always inspect active implementations before modifying code or asserting facts.
2. **Absolute Source-of-Truth Directive:** All benchmark numbers, correlation values, and error metrics cited must originate strictly from `final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md` and `final_benchmarks/master_benchmark_metrics.csv`. Never hallucinate benchmark figures.
3. **Git Safety Directive:** **DO NOT** execute `git add`, `git commit`, or `git push` automatically. Only execute git commands when the user gives explicit instructions.
4. **Historical Isolation Directive:** Do not resurrect retired models (`MEG-mod-main/`, `helixzero_ieee_v5/`) into the active runtime path. The active production model is strictly the **Single Unified Dose-Aware CatBoost Regressor** (517-D).
5. **Zero Data Leakage Directive:** Any training or evaluation script created must enforce sequence-disjoint `GroupKFold` clustering on the 19-nt core antisense sequence. Random $K$-fold splits are strictly prohibited.
6. **Scientific Rigor & Uncertainty Protocol:** When confidence is below 95% or evidence is missing, do not guess or infer. Explicitly classify statements as `VERIFIED — CURRENT IMPLEMENTATION`, `VERIFIED — HISTORICAL IMPLEMENTATION`, `PLANNED — NOT IMPLEMENTED`, `EXPERIMENTAL`, or `UNVERIFIED — REQUIRES CONFIRMATION`.
