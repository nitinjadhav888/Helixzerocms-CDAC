# 02. REPOSITORY & PROJECT STRUCTURE
## Codebase Topology, Directory Organization, and File Inventory
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. Workspace Structural Map

The HelixZero workspace (`d:\Helixx`) is partitioned into active production modules, authoritative benchmark stores, historical research archives, documentation suites, and automated deployment assets:

```text
d:\Helixx/
├── PROJECT_KNOWLEDGE_BASE.md    # Master single-file comprehensive system manual (63 sections)
├── AI_PROJECT_CONTEXT.md        # Dedicated briefing for AI coding agents & automated assistants
├── README.md                    # Root project entry point & navigational guide
├── requirements.txt             # Primary Python dependencies manifest
├── Dockerfile                   # Production container definition (Python 3.11-slim)
├── start_system.bat             # One-click Windows development & production server launch script
│
├── smepred/                     # 🚀 ACTIVE PRODUCTION APPLICATION & INFERENCE ENGINE
│   ├── api/                     # FastAPI microservice layer
│   │   ├── __init__.py
│   │   └── main.py              # Production REST endpoints (/rank, /single-mod, /multi-mod, /offtarget)
│   ├── app.html                 # Production Single-Page Application (SPA) laboratory workbench
│   ├── src/                     # Core computational biology & ML feature extractors
│   │   ├── parser.py            # Ingests mRNA FASTA/GenBank sequence files
│   │   ├── sirna_generator.py   # Sliding 21-mer candidate duplex generator with 3'-dTdT overhangs
│   │   ├── filters.py           # 15-mer slicer pre-filter & Janas seed cytotoxicity estimator
│   │   ├── offtarget.py         # 2-bit SIMD whole-transcriptome off-target safety engine
│   │   ├── offtarget_store.py   # Transcriptome database indexing & cache loader
│   │   ├── chem_schema.py       # Positional NucSlot orthogonal data structure
│   │   ├── chem_alphabet.py     # 30-modification chemical ontology & thermodynamic delta tables
│   │   ├── features.py          # Model A baseline 214-D thermodynamic feature extractor
│   │   ├── features_v2.py       # 444-D multi-slot literature-grounded chemical feature extractor
│   │   ├── features_v4.py       # 517-D joint multi-modal feature vectorizer (V2 + RNA-FM + Vienna + Dose)
│   │   ├── context_feature_extractor.py # 190-D context-aware transcript secondary structure extractor
│   │   ├── model_b_v4.py        # Active production serving wrapper for Unified CatBoost (517-D)
│   │   ├── predictor.py         # Primary orchestration gateway & multi-model dispatcher
│   │   ├── biophysics.py        # Deterministic 4-domain biophysical penalty engine
│   │   ├── modification_engine.py # Single-mod scanner & combinatorial beam search optimizer
│   │   ├── multislot_designer.py  # Alnylam ESC / ESC+ clinical multi-slot template generator
│   │   ├── pdb_generator.py     # Continuous A-form 3D PDB atomic coordinate model generator (504 atoms)
│   │   ├── calibrator.py        # Isotonic probability monotonic calibrator
│   │   ├── assistant_service.py # LLM-assisted scientific co-pilot service
│   │   ├── assistant_prompts.py # System prompts for scientific reasoning & dossier generation
│   │   └── utils.py             # Shared string manipulation & GC content calculators
│   ├── models/                  # Serialized ML weights & persistent feature caches
│   │   ├── unified_dose_catboost.cbm # Production Unified CatBoost Checkpoint (517-D, 1.70 MB)
│   │   ├── model_b_v4.cbm       # Production fallback alias (1.70 MB)
│   │   ├── model_normal.txt     # Model A Naked LightGBM booster text format
│   │   ├── model_normal.pkl     # Model A Naked LightGBM booster joblib pickle
│   │   ├── model_normal_context.txt # Model A Context-Aware 190-D LightGBM booster
│   │   ├── calibrator_naked.pkl # Isotonic calibrator for Model A
│   │   ├── calibrator_context.pkl # Isotonic calibrator for context model
│   │   ├── rnafm_embeddings.pkl # Pre-computed RNA-FM 640-D embeddings cache (56.4 MB)
│   │   ├── rnafm_pca_32.pkl     # Fitted PCA transformer (640-D -> 32-D)
│   │   ├── vienna_features_cache.pkl # Persistent disk cache for ViennaRNA duplex calculations (3.67 MB)
│   │   └── unimol_1b_emb_dict.pkl   # Uni-Mol 3D conformation embeddings cache
│   └── data/                    # Transcriptome databases & processed data lakes
│       ├── human_transcriptome.idx.pkl # 2-bit packed binary transcriptome index (863.8 MB)
│       ├── human_transcriptome.fasta   # Human RefSeq cDNA transcriptome source (449.5 MB)
│       ├── modification_codes.json     # Standardized JSON taxonomy for 30 chemical modifications
│       └── processed/           # Curated ML matrices & training CSVs (see docs/06_DATASETS.md)
│
├── final_benchmarks/            # 🏆 AUTHORITATIVE SINGLE SOURCE OF TRUTH FOR BENCHMARKS
│   ├── 00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md # Certified master evaluation dossier
│   ├── master_benchmark_metrics.csv           # Complete numerical metric ledger
│   ├── 01_MODEL_A_NAKED_LIGHTGBM_BENCHMARK.md  # Detailed Model A empirical report
│   ├── 02_UNIFIED_DOSE_AWARE_CATBOOST_BENCHMARK.md # Unified CatBoost empirical report
│   ├── ai_vs_human_chemist_5cases.csv          # AI vs human medicinal chemist benchmark
│   └── siRNAmod_50_benchmark_results.csv       # External benchmark validation report
│
├── helixzero/                   # Clean Python Client & Schema Package
│   ├── api/                     # High-level API schemas and client library
│   ├── featurizers/             # Modular biophysical & multi-slot featurizers
│   ├── models/                  # Abstract model engines & CatBoost wrappers
│   └── ontology/                # Chemical alphabet & tokenization routines
│
├── helixzero_ieee_v5/           # 📦 HISTORICAL / ABLATION ARCHIVE: IEEE v5 Two-Stage Engine
│   ├── data/                    # Gold/Bronze master datasets
│   ├── scripts/                 # Two-stage training and validation scripts
│   └── src/                     # Chemical ontology and cascading predictor
│
├── MEG-mod-main/                # 📦 HISTORICAL / ABLATION ARCHIVE: PyTorch GNN Engine
│   ├── model.py                 # PyTorch Geometric TransformerConv network
│   └── dataset_pre.py           # Graph dataset construction routines
│
├── scripts/                     # Production Training, Evaluation & Monograph Scripts
│   ├── train_unified_dose_aware_catboost.py # Master training script (GroupKFold + FDA blind)
│   ├── run_all_model_benchmarks_live.py     # Live empirical benchmark runner
│   ├── test_pipeline_integrity.py          # End-to-end integration and smoke test
│   └── optimize_unified_catboost_loop.py   # Hyperparameter tuning sweep script
│
├── docs/                        # 📚 COMPREHENSIVE MODULAR DOCUMENTATION SUITE
│   ├── 01_PROJECT_OVERVIEW.md
│   ├── 02_PROJECT_STRUCTURE.md
│   ├── ... (Modular documentation files 01 to 26)
│   └── models/                  # Granular per-model technical architecture manuals
│
├── Paper/                       # Academic Publications & Submission Manifests
│   ├── manuscript_NAR.md        # Full research article manuscript (NAR format)
│   └── manuscript_NAR.tex       # LaTeX submission source
│
├── Outputs/                     # Visual Evidence & UI Screenshots
└── paper_figures/               # High-Resolution Publication Vector Figures
```

---

### 2. Operational Separation of Production vs. Historical Code

To prevent confusion during codebase maintenance and AI agent pair-programming:
- **Active Runtime Path:** All production API calls and user interactions route strictly through `smepred/api/main.py` $\to$ `smepred/src/predictor.py` $\to$ `smepred/src/model_b_v4.py` $\to$ `smepred/models/unified_dose_catboost.cbm`.
- **Historical Checkpoints:** `helixzero_ieee_v5/` and `MEG-mod-main/` are strictly archived. They are not called during active inference and exist purely to support ablation studies in peer review.
- **Authoritative Benchmark Rule:** Any benchmark cited must exist in `final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md` or `final_benchmarks/master_benchmark_metrics.csv`.
