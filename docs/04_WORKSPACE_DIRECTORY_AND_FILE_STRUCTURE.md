# HELIXZERO-CMS: COMPLETE WORKSPACE DIRECTORY & FILE STRUCTURE
## Authoritative Architecture Blueprint, Codebase Inventory & Component Demarcation
**Authoritative Source Alignment:** `final_benchmarks/`  
**Classification:** System Architecture, Codebase Inventory & AI Navigation Map  
**Workspace Root:** `d:\Helixx`  
**Institution:** High Performance Computing — Medical & BioInformatics Group, C-DAC, Pune

---

### 1. High-Level Workspace Architecture

The HelixZero repository is structured to maintain strict separation between the **Active Production Engine**, **Authoritative Benchmarks**, **Scientific Presentation Assets**, and **Historical Research Checkpoints**:

```
d:\Helixx/
│
├── smepred/                    # [ACTIVE PRODUCTION ENGINE] Core ML, Biophysics, Engine & API
│   ├── api/                    # FastAPI REST application exposing production endpoints
│   ├── src/                    # Model orchestration, biophysics, beam search, PDB generation
│   ├── models/                 # Pre-trained CatBoost v4 (517-D) & LightGBM production weights
│   ├── data/                   # Chemical modification ontologies & human reference sequences
│   └── tests/                  # Comprehensive pytest suite (74 tests, 100% passing)
│
├── final_benchmarks/           # [SINGLE SOURCE OF TRUTH] Authoritative empirical metrics
│   ├── 00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md
│   ├── 01_MODEL_A_NAKED_LIGHTGBM_BENCHMARK.md
│   ├── 02_UNIFIED_DOSE_AWARE_CATBOOST_BENCHMARK.md
│   └── master_benchmark_metrics.csv
│
├── docs/                       # [AUTHORITATIVE DOCUMENTATION] Clean, consolidated system specs
│   ├── 00_MASTER_SYSTEM_ARCHITECTURE.md
│   ├── 01_UNIFIED_DOSE_AWARE_CATBOOST_ENGINE.md
│   ├── 02_MODEL_A_NAKED_SEQUENCE_SELECTOR.md
│   ├── 03_BIOPHYSICAL_GUARDRAILS_AND_SAFETY_FIREWALL.md
│   ├── 04_WORKSPACE_DIRECTORY_AND_FILE_STRUCTURE.md
│   └── 05_AUTHORITATIVE_BENCHMARKS_AND_CLINICAL_VALIDATION.md
│
├── Paper/                      # [SCIENTIFIC PRESENTATION & PUBLICATION] Presentation decks & manuscripts
│   ├── HELIXZERO_SOFTWARE_ARCHITECTURE_PRESENTATION.md
│   ├── HelixZero_Software_Presentation.html
│   ├── PRESENTATION_TALK_TRACKS_AND_MENTOR_SCRIPTS.md
│   └── MENTOR_PROFILES_AND_PROJECT_ALIGNMENT_ANALYSIS.md
│
├── helixzero_ieee_v5/          # [HISTORICAL / ABLATION REPRODUCIBILITY] Two-Stage Engine Archive
│   ├── models/                 # Legacy module2/module3 checkpoints (kept for benchmark comparison)
│   ├── src/                    # Legacy 577-D feature extractor & Hill calibration routines
│   └── scripts/                # Historical evaluation and ablation scripts
│
├── MEG-mod-main/               # [HISTORICAL / ABLATION REPRODUCIBILITY] PyG GNN Archive
│   └── BAN_graph.py            # Graph Attention Network evaluated during ablation studies
│
├── scripts/                    # Platform utilities, PDF report compilers, batch evaluators
├── data_pre/                   # Raw dataset cleaning, deduplication, and extraction scripts
├── scratch/                    # Temporary scratch scripts, evaluation runs, and debug files
├── app.html                    # Single-Page Application (SPA) production frontend interface
├── Dockerfile                  # Production containerization specification
├── start_system.bat            # Automated local launch script
└── README.md                   # Repository overview and setup guide
```

---

### 2. Detailed Component Inventory: Active vs. Historical

To prevent any confusion when reading or extracting workflows for research papers or presentations:

#### 2.1 The Active Production Stack (Always Cite This Architecture)
| Directory / File | Status | Technical Role |
| :--- | :---: | :--- |
| [`smepred/api/main.py`](file:///d:/Helixx/smepred/api/main.py) | **Active** | Production FastAPI REST server exposing `/rank`, `/single-mod`, `/multi-mod`, `/multi-mod-scan`, `/multi-mod-from-single`, `/offtarget-scan`, `/generate-pdb`, and `/assistant/chat`. |
| [`smepred/src/model_b_v4.py`](file:///d:/Helixx/smepred/src/model_b_v4.py) | **Active** | Production wrapper for the Single Unified Dose-Aware CatBoost Regressor. Handles 517-D vectorization, concentration conditioning, and batch inference. |
| [`smepred/models/model_b_v4.cbm`](file:///d:/Helixx/smepred/models/model_b_v4.cbm) | **Active** | Trained CatBoost model binary (517-D, 17,761 multi-dose rows, zero sequence leakage). |
| [`smepred/models/lgb_naked_model.txt`](file:///d:/Helixx/smepred/models/lgb_naked_model.txt) | **Active** | Model A LightGBM binary for naked mRNA transcript scanning. |
| [`smepred/src/modification_engine.py`](file:///d:/Helixx/smepred/src/modification_engine.py) | **Active** | Heuristic beam-search multi-modification design engine and single-modification scanner. |
| [`smepred/src/biophysics.py`](file:///d:/Helixx/smepred/src/biophysics.py) | **Active** | Deterministic 4-domain biophysical penalty calculator with empirical $\Delta\Delta G^\circ_{37}$ thermodynamics. |
| [`smepred/src/offtarget.py`](file:///d:/Helixx/smepred/src/offtarget.py) | **Active** | 2-bit binary encoded whole-transcriptome off-target safety firewall. |
| [`smepred/src/pdb_generator.py`](file:///d:/Helixx/smepred/src/pdb_generator.py) | **Active** | Atomic coordinate PDB builder (504 atoms) mapping chemical modifications to crystallographic $B$-factors. |
| [`final_benchmarks/`](file:///d:/Helixx/final_benchmarks/) | **Active** | **The ONLY authoritative source of truth for benchmark metrics.** |

#### 2.2 Historical / Ablation Archives (Do NOT Cite as Current Architecture)
| Directory / File | Status | Historical Purpose & Why It Is Retained |
| :--- | :---: | :--- |
| [`helixzero_ieee_v5/`](file:///d:/Helixx/helixzero_ieee_v5/) | **Archived** | Retained strictly to reproduce historical ablation studies comparing the old two-stage cascading architecture against the modern Single Unified Engine. **Not in the active production runtime path.** |
| [`MEG-mod-main/`](file:///d:/Helixx/MEG-mod-main/) | **Archived** | Retained strictly to document the empirical failure of Graph Attention Networks on out-of-distribution siRNA screens ($r = 0.0631$). **Not in the active production runtime path.** |

---

### 3. Source Code Integrity & Production Testing

The active production engine is systematically tested across 7 pytest suites:
- `smepred/tests/test_api.py`: REST endpoint contracts, Pydantic schemas, dynamic dose-conditioning, and tie-breaking.
- `smepred/tests/test_biophysics_suite.py`: Thermodynamic asymmetry, serum exonuclease kinetics, and penalty bounds.
- `smepred/tests/test_pipeline.py`: End-to-end RNA transcript scanning and candidate filtering.
- `smepred/tests/test_3d_inspector.py`: Continuous PDB generation and B-factor mapping.
- `smepred/tests/test_multimod_regression.py`: Multi-modification beam search determinism.
- `smepred/tests/test_retrained_potency_engine.py`: Single Unified CatBoost inference verification.
- `smepred/tests/test_megmod_paper.py`: Ablation benchmarks.
- **Pass Rate**: **74 / 74 tests passing (100%)**.
