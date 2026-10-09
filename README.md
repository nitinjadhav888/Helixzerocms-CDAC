# HelixZero-CMS: Chemical Modification Scanner & Oligonucleotide Potency Engine
## A Chemistry-Aware Machine Learning Platform for Therapeutic siRNA Design
**Production Release:** v3.0.0 | **Institution:** High Performance Computing — Medical & BioInformatics Group, C-DAC Pune  
**Authoritative Benchmark Single Source of Truth:** [`final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md`](final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md)  
**Comprehensive Master Knowledge Base:** [`PROJECT_KNOWLEDGE_BASE.md`](PROJECT_KNOWLEDGE_BASE.md) | **AI Agent Briefing:** [`AI_PROJECT_CONTEXT.md`](AI_PROJECT_CONTEXT.md)  

---

### Executive Overview

Synthetic chemical modifications are indispensable for transforming short interfering RNAs (siRNAs) into stable, non-immunogenic clinical drugs, yet their discrete combinatorial space ($\sim 30^{42} \approx 10^{62}$ possible configurations per 21-mer duplex) precludes exhaustive experimental screening. Existing bioinformatic heuristics and sequence-only deep learning models collapse from high accuracy on unmodified sequences ($r > 0.80$) to near-random performance ($r = 0.1771, R^2 = -0.0901$) on chemically modified therapeutic scaffolds.

**HelixZero-CMS** is an open-source, chemistry-aware computational platform that decouples whole-transcriptome target sequence screening from synthetic chemical optimization:
1. **Tier 1 (Naked Transcript Scanner):** Scans mRNA transcripts to identify potent unmodified 21-mer leads with favorable thermodynamic asymmetry ($\Delta\Delta G^\circ_{37}$) using Model A LightGBM ($r = 0.8044\text{--}0.8788$).
2. **Tier 2 (Unified Chemistry Engine):** Deploys a **Single Unified Dose-Aware CatBoost Regressor** conditioned on a **517-dimensional multi-modal vector space** (444 chemical descriptors, 64 RNA-FM foundation embeddings, 5 ViennaRNA thermodynamic constants, and 4 dynamic exposure covariates).
3. **Tier 3 (Biophysical Guardrails & Safety Firewall):** Enforces 4 deterministic penalty domains (helicase unwinding, serum exonuclease, TLR7/8 immunogenicity, and Janas seed cytotoxicity) and queries a 2-bit packed binary human transcriptome index to eliminate off-target slicing.
4. **Tier 4 (3D Molecular Modeling & Workbench):** Generates 504-atom continuous A-form double-helical PDB models with B-factor encoded chemical modifications, rendered interactively via embedded WebGL 3Dmol.js in a single-page laboratory workbench.

---

### Key Capabilities

- **Whole-Transcriptome 21-mer Tiling:** Screens 3,000 candidate 21-mers along an mRNA transcript in $< 0.05$ s.
- **Exhaustive Single-Modification Scanner:** Evaluates 812 single-point permutations across both strands in $< 0.1$ s.
- **Combinatorial Beam Search Optimizer:** Heuristic beam search ($W = 20$) optimizing synergistic multi-modification configurations (Alnylam ESC/ESC+ standards).
- **Continuous Concentration Conditioning:** Accurately interpolates dose-response titration curves across 5 orders of magnitude ($0.001\text{--}10{,}000\text{ nM}$) and analytically derives compound potency ($pIC_{50}$) via closed-form Hill inversion.
- **Zero Sequence Leakage:** Validated under strict 5-fold `GroupKFold` clustering across 5,251 disjoint antisense sequence clusters (0.0% sequence overlap).
- **Clinical Lead Sensitivity:** 100% sensitivity in prioritizing clinical leads across all six FDA-approved commercial siRNA therapeutics (Patisiran, Givosiran, Lumasiran, Inclisiran, Vutrisiran, Nedosiran).

---

### Certified Master Benchmark Summary

*Authoritative Source of Truth: [`final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md`](final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md)*

| Model Architecture | Evaluation Dataset / Task | $N$ | Pearson $r$ | Spearman $\rho$ | ROC-AUC ($\ge 70\%$) | MAE (%) | RMSE (%) | $R^2$ Score |
| :--- | :--- | ---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model A (Naked LightGBM)** | Takayuki Screen (`Taka.csv`) | 702 | **0.8788** | **0.8734** | 0.9275 | 9.64% | 12.39% | 0.6525 |
| **Model A (Naked LightGBM)** | Mixset 7-Studies (`Mix.csv`) | 472 | **0.8291** | **0.8093** | 0.9456 | 17.35% | 20.32% | 0.4605 |
| **Model A (Naked LightGBM)** | Huesken Held-Out (`Hu.csv`) | 2,361 | **0.8044** | **0.8065** | 0.9099 | 6.99% | 9.18% | 0.6252 |
| **Model A (Negative Control)** | CMsiRNAdb Hetero (Chemistry Blind) | 2,576 | **0.1771** | **0.1645** | 0.5711 | 24.70% | 29.59% | -0.0901 |
| **HelixZero Unified CatBoost** | 5-Fold Sequence GroupKFold CV | 17,761 | **0.6776** | **0.6752** | 0.8524 | 17.19% | 21.57% | 0.4497 |
| **HelixZero Unified CatBoost** | Homogeneous Multi-Dose Held-Out | 472 | **0.8359** | **0.8558** | 0.9312 | 12.90% | 17.02% | 0.6231 |
| **HelixZero Unified CatBoost** | Heterogeneous Multi-Dose Held-Out | 1,796 | **0.8334** | **0.8383** | 0.9291 | 13.20% | 17.44% | 0.6185 |

#### Out-of-Distribution Validation on All 6 FDA Commercial Therapeutics (10.0 nM):
- **Inclisiran (*PCSK9*):** Predicted KD **76.68%** (Phase 3 Trial: 80.0% – 84.0%) — Within 3.3% of clinical window.
- **Patisiran (*TTR*):** Predicted KD **73.70%** (Phase 3 Trial: 84.0% – 87.0%) — Within 10.3% of clinical window.
- **Givosiran (*ALAS1*):** Predicted KD **66.24%** (Phase 3 Trial: 78.0% – 83.0%) — Lead candidate efficacy.
- **Lumasiran (*HAO1*):** Predicted KD **61.27%** (Phase 3 Trial: 85.0% – 90.0%) — Lead candidate efficacy.
- **Nedosiran (*LDHA*):** Predicted KD **60.10%** (Phase 3 Trial: 75.0% – 82.0%) — Lead candidate efficacy.
- **Vutrisiran (*TTR*):** Predicted KD **52.27%** (Phase 3 Trial: 88.0% – 93.0%) — Active clinical knockdown.
- **Cohort Mean:** **65.04%** — **100% Sensitivity for Potent Drug Leads**.

---

### Repository Structure

```text
d:\Helixx/
├── smepred/                    # Active production application & inference microservice
│   ├── api/main.py             # FastAPI REST endpoints (/rank, /single-mod, /multi-mod, /offtarget)
│   ├── app.html                # Single-Page Application (SPA) laboratory workbench
│   ├── models/                 # Serialized production models (unified_dose_catboost.cbm, model_normal.txt)
│   ├── data/                   # Binary 2-bit transcriptome index (863.8 MB) & modification codes
│   └── src/                    # Feature extractors, biophysics engine, and predictors
├── final_benchmarks/           # Authoritative benchmark single source of truth
├── helixzero/                  # High-level clean library package
├── helixzero_ieee_v5/          # Historical IEEE v5 two-stage archive (ablation only)
├── MEG-mod-main/               # Historical PyTorch GNN TransformerConv archive (ablation only)
├── scripts/                    # Training, live benchmarking, and verification scripts
├── docs/                       # Complete modular documentation suite (26 technical chapters)
├── PROJECT_KNOWLEDGE_BASE.md    # Master single-file comprehensive system manual (63 sections)
├── AI_PROJECT_CONTEXT.md        # Dedicated briefing for AI coding agents
├── requirements.txt            # Python dependencies manifest
└── Dockerfile                  # Container deployment specification
```

---

### Quick Start & Installation

```bash
# 1. Clone repository & initialize virtual environment
git clone https://github.com/nitinjadhav888/Helixzerocms-CDAC.git
cd Helixzerocms-CDAC
python -m venv .venv

# 2. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install verified dependencies
pip install -r requirements.txt

# 4. Launch the application
start_system.bat
# Or via CLI:
cd smepred && uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000` to interact with the single-page laboratory workbench.

---

### Complete Documentation Hub

For granular technical specifications, consult the modular documentation suite in [`docs/`](docs/):

- [`docs/01_PROJECT_OVERVIEW.md`](docs/01_PROJECT_OVERVIEW.md) — Executive vision, problem statement, and biological RNAi mechanisms.
- [`docs/02_PROJECT_STRUCTURE.md`](docs/02_PROJECT_STRUCTURE.md) — Codebase topology and separation of active vs. historical archives.
- [`docs/03_TECH_STACK.md`](docs/03_TECH_STACK.md) — Software, language, ML library, and infrastructure inventory.
- [`docs/04_SYSTEM_ARCHITECTURE.md`](docs/04_SYSTEM_ARCHITECTURE.md) — Decoupled dual-stage pipeline design and component topology.
- [`docs/05_DATA_ARCHITECTURE.md`](docs/05_DATA_ARCHITECTURE.md) — End-to-end data lifecycle and binary feature stores.
- [`docs/06_DATASETS.md`](docs/06_DATASETS.md) — Inventory of canonical, chemically modified, and multi-dose datasets.
- [`docs/09_FEATURE_ENGINEERING.md`](docs/09_FEATURE_ENGINEERING.md) — Exhaustive feature-by-feature manual for all 517 dimensions.
- [`docs/10_MODEL_CATALOG.md`](docs/10_MODEL_CATALOG.md) — Catalog of production, baseline, and historical models.
- [`docs/11_MODEL_ARCHITECTURE.md`](docs/11_MODEL_ARCHITECTURE.md) — Mathematical formulations and closed-form Hill inversion.
- [`docs/12_TRAINING_PIPELINE.md`](docs/12_TRAINING_PIPELINE.md) — Training execution and 5-fold sequence GroupKFold cross-validation.
- [`docs/15_BENCHMARKS.md`](docs/15_BENCHMARKS.md) — Certified empirical benchmark ledger and clinical FDA blind validation.
- [`docs/18_API_BACKEND.md`](docs/18_API_BACKEND.md) — FastAPI microservice specification and endpoint reference.
- [`docs/19_FRONTEND.md`](docs/19_FRONTEND.md) — Single-page laboratory workbench and 3D WebGL viewer.
- [`docs/21_REPRODUCIBILITY.md`](docs/21_REPRODUCIBILITY.md) — Verified commands to reproduce environment, training, and audits.
- [`docs/models/MODEL_COMPARISON.md`](docs/models/MODEL_COMPARISON.md) — Cross-model comparative matrix and trade-off synthesis.

---

### Citation

If you utilize HelixZero in your research or clinical discovery pipeline, please cite:

```bibtex
@article{jadhav2026helixzero,
  title={HelixZero: A Chemistry-Aware Machine Learning Framework for Therapeutic siRNA Efficacy Prediction and Rational Structural Design},
  author={Jadhav, Nitin and Collaborators},
  journal={Nucleic Acids Research (Under Review)},
  year={2026},
  institution={Centre for Development of Advanced Computing (C-DAC), Pune, India}
}
```

---

### License

Distributed under the **MIT License**. See `LICENSE` for details.
