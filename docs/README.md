# HELIXZERO-CMS: AUTHORITATIVE DOCUMENTATION HUB
## The Definitive Documentation Center for Computational Biologists, AI Agents & Peer Reviewers
**Authoritative Single Source of Truth for Benchmarks:** `final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md`  
**Production Flagship Engine:** Single Unified Dose-Aware CatBoost Regressor (517-D)  
**Institution:** High Performance Computing — Medical & BioInformatics Group, Centre for Development of Advanced Computing (C-DAC, Pune)  

---

### Welcome to the Authoritative HelixZero Documentation Hub

This directory (`docs/`) contains the complete, production-grade documentation system for the HelixZero oligonucleotide optimization platform. Every document in this directory is guaranteed to be 100% synchronized with the active production codebase and adheres strictly to the single source of truth in `final_benchmarks/`.

> [!IMPORTANT]
> **Zero Ambiguity Directive**:
> - The active production model for chemically modified siRNAs is the **Single Unified Dose-Aware CatBoost Regressor (517-D)**.
> - All legacy cascading architectures (IEEE v5 two-stage $pIC_{50} \rightarrow \text{Hill}$) and deep learning blends (MEG-mod GNN) have been **retired** from the runtime path and preserved solely for ablation reproducibility.
> - All performance metrics are cited strictly from `final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md` and `final_benchmarks/master_benchmark_metrics.csv`.

---

### Master Navigation Index

| Document | Primary Focus & Core Topics Covered |
| :--- | :--- |
| [**01_PROJECT_OVERVIEW.md**](01_PROJECT_OVERVIEW.md) | Executive vision, problem statement, biological RNAi mechanisms, and key performance highlights. |
| [**02_PROJECT_STRUCTURE.md**](02_PROJECT_STRUCTURE.md) | Codebase topology, directory organization, and separation of active vs. historical archives. |
| [**03_TECH_STACK.md**](03_TECH_STACK.md) | Software, language, ML library, and infrastructure inventory with code-level evidence. |
| [**04_SYSTEM_ARCHITECTURE.md**](04_SYSTEM_ARCHITECTURE.md) | Decoupled dual-stage pipeline design, component topology, and Mermaid data flows. |
| [**05_DATA_ARCHITECTURE.md**](05_DATA_ARCHITECTURE.md) | End-to-end data lifecycle, binary storage formats (`.npy`, `.idx.pkl`), and zero-leakage splits. |
| [**06_DATASETS.md**](06_DATASETS.md) | Inventory of canonical naked, chemically modified, multi-dose, and transcriptome datasets. |
| [**07_DATA_COLLECTION.md**](07_DATA_COLLECTION.md) | Provenance and assembly protocols for CMsiRNAdb, Novartis, Takayuki, Davis, and RefSeq. |
| [**08_DATA_CLEANING_PREPROCESSING.md**](08_DATA_CLEANING_PREPROCESSING.md) | Cleaning accounting, outlier bounds clamping, deduplication, and chemical normalization. |
| [**09_FEATURE_ENGINEERING.md**](09_FEATURE_ENGINEERING.md) | Exhaustive feature-by-feature manual for all 517 dimensions (444 chem, 64 RNA-FM, 5 Vienna, 4 dose). |
| [**10_MODEL_CATALOG.md**](10_MODEL_CATALOG.md) | Catalog of production, baseline, and historical models with checkpoints and dimensions. |
| [**11_MODEL_ARCHITECTURE.md**](11_MODEL_ARCHITECTURE.md) | Mathematical formulations, oblivious tree algorithms, and analytical closed-form Hill inversion. |
| [**12_TRAINING_PIPELINE.md**](12_TRAINING_PIPELINE.md) | End-to-end training execution, 5-fold sequence GroupKFold cross-validation, and model export. |
| [**13_HYPERPARAMETER_TUNING.md**](13_HYPERPARAMETER_TUNING.md) | Grid search optimization schedules, tuning curves, L2 regularization, and early stopping. |
| [**14_EVALUATION.md**](14_EVALUATION.md) | Multi-tiered evaluation protocols, mathematical metric formulas, and statistical audit rules. |
| [**15_BENCHMARKS.md**](15_BENCHMARKS.md) | Certified empirical benchmark ledger, FDA clinical blind validation, and batch noise analysis. |
| [**16_INFERENCE_PIPELINE.md**](16_INFERENCE_PIPELINE.md) | Step-by-step inference flow, latency benchmarks, sequence diagrams, and error boundaries. |
| [**17_OUTPUTS.md**](17_OUTPUTS.md) | Input $\to$ Processing $\to$ Model $\to$ Output mapping, persistent file ledger, and UI screens. |
| [**18_API_BACKEND.md**](18_API_BACKEND.md) | FastAPI microservice specification, Pydantic schemas, and complete endpoint reference. |
| [**19_FRONTEND.md**](19_FRONTEND.md) | Single-page laboratory application, design system tokens, and 3Dmol.js WebGL viewer. |
| [**20_DEPLOYMENT.md**](20_DEPLOYMENT.md) | Containerized Docker deployment, environment variables, healthchecks, and HPC scaling. |
| [**21_REPRODUCIBILITY.md**](21_REPRODUCIBILITY.md) | Exact verified terminal commands to reproduce environment, training, benchmarking, and tests. |
| [**22_RESEARCH_REFERENCES.md**](22_RESEARCH_REFERENCES.md) | Scientific literature foundations and granular code-to-paper implementation mappings. |
| [**23_RESEARCH_GAPS.md**](23_RESEARCH_GAPS.md) | Prior art limitations, HelixZero engineering solutions, and claims requiring confirmation. |
| [**24_LIMITATIONS.md**](24_LIMITATIONS.md) | Real-world biological, algorithmic, and computational constraints and edge cases. |
| [**25_FUTURE_WORK.md**](25_FUTURE_WORK.md) | Planned research roadmap: stereopure chiral modeling, extrahepatic delivery, workcells. |
| [**26_CHANGELOG.md**](26_CHANGELOG.md) | Complete version history, architectural consolidation milestones, and deprecation accounting. |
| [**DATASETS_AND_ASSAYS.md**](DATASETS_AND_ASSAYS.md) | Granular technical guide to RT-qPCR, Dual-Luciferase, Multi-Dose, and CellTiter-Glo assays. |
| [**IMPLEMENTATION_PLAN.md**](IMPLEMENTATION_PLAN.md) | Status classification of implemented, partially implemented, experimental, and planned features. |

---

### Granular Per-Model Documentation

Detailed architectural deep-dives for each computational model:

- [**docs/models/MODEL_A_LIGHTGBM.md**](models/MODEL_A_LIGHTGBM.md): Upstream mRNA transcript scanner and thermodynamic asymmetry scorer ($r = 0.8044\text{--}0.8788$).
- [**docs/models/MODEL_B_CATBOOST_UNIFIED.md**](models/MODEL_B_CATBOOST_UNIFIED.md): Flagship 517-D Unified Dose-Aware CatBoost Regressor ($r = 0.8359$).
- [**docs/models/MODEL_HISTORICAL_GNN_MEGMOD.md**](models/MODEL_HISTORICAL_GNN_MEGMOD.md): PyTorch Geometric TransformerConv exploration and deprecation audit.
- [**docs/models/MODEL_HISTORICAL_IEEE_V5.md**](models/MODEL_HISTORICAL_IEEE_V5.md): Cascading two-stage potency pipeline and compounded error analysis.
- [**docs/models/MODEL_COMPARISON.md**](models/MODEL_COMPARISON.md): Exhaustive cross-architecture comparative matrix and trade-off analysis.
