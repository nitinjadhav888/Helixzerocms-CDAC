# HELIXZERO-CMS: AUTHORITATIVE ARCHITECTURE & SYSTEM DOCUMENTATION HUB
## The Definitive Documentation Center for Computational Biologists, AI Agents & Peer Reviewers
**Authoritative Single Source of Truth:** `final_benchmarks/`  
**Stack Status:** Production Engine (Single Unified Dose-Aware CatBoost Regressor)  
**Institution:** High Performance Computing — Medical & BioInformatics Group, Centre for Development of Advanced Computing (C-DAC, Pune)

---

### Welcome to the Authoritative HelixZero Documentation Hub

This directory (`d:\Helixx\docs/`) contains the single, unified, peer-review-grade documentation suite for the HelixZero oligonucleotide optimization platform. Every document in this folder is guaranteed to be 100% synchronized with the active production codebase and adheres strictly to the single source of truth in `final_benchmarks/`.

> [!IMPORTANT]
> **Zero Ambiguity Directive**:
> - The active production model for chemically modified siRNAs is the **Single Unified Dose-Aware CatBoost Regressor (517-D)**.
> - All legacy cascading architectures (IEEE v5 two-stage $pIC_{50} \rightarrow \text{Hill}$) and deep learning blends (85% GBDT / 15% GNN) have been **retired** and are not part of the active production inference pipeline.
> - All performance metrics are cited strictly from `final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md` and `final_benchmarks/master_benchmark_metrics.csv`.

---

### Navigation Index

| Document | Core Topic & Focus Areas |
| :--- | :--- |
| [**00_MASTER_SYSTEM_ARCHITECTURE.md**](00_MASTER_SYSTEM_ARCHITECTURE.md) | **System Topology & Data Pipeline**: The 4-step production workflow (Model A $\rightarrow$ Unified CatBoost $\rightarrow$ Biophysical Guardrails $\rightarrow$ 3D PDB Modeling) and forensic explanation of architectural consolidation. |
| [**01_UNIFIED_DOSE_AWARE_CATBOOST_ENGINE.md**](01_UNIFIED_DOSE_AWARE_CATBOOST_ENGINE.md) | **Core ML Model & Feature Space**: Deep dive into the 517-D vector space (444 chemical slots, 64 RNA-FM foundation embeddings, 5 ViennaRNA features, 4 dynamic dose covariates) and dynamic $pIC_{50}$ derivation. |
| [**02_MODEL_A_NAKED_SEQUENCE_SELECTOR.md**](02_MODEL_A_NAKED_SEQUENCE_SELECTOR.md) | **Upstream Transcript Scanner**: Model A LightGBM architecture, Reynolds/Ui-Tei rules, thermodynamic asymmetry ($\Delta\Delta G^\circ_{37}$), and the negative control chemistry blindness proof ($r = 0.1771$). |
| [**03_BIOPHYSICAL_GUARDRAILS_AND_SAFETY_FIREWALL.md**](03_BIOPHYSICAL_GUARDRAILS_AND_SAFETY_FIREWALL.md) | **Safety Engine & Penalties**: 4-domain biophysical penalties (thermodynamic unwinding barrier, tandem di-PS serum exonuclease kinetics, TLR7/8 immunostimulatory suppression, seed cytotoxicity) and 2-bit transcriptome firewall. |
| [**04_WORKSPACE_DIRECTORY_AND_FILE_STRUCTURE.md**](04_WORKSPACE_DIRECTORY_AND_FILE_STRUCTURE.md) | **Codebase Blueprint & Inventory**: Complete directory-by-directory inventory demarcating Active Production modules (`smepred/`, `final_benchmarks/`) from Historical Research Checkpoints (`helixzero_ieee_v5/`, `MEG-mod-main/`). |
| [**05_AUTHORITATIVE_BENCHMARKS_AND_CLINICAL_VALIDATION.md**](05_AUTHORITATIVE_BENCHMARKS_AND_CLINICAL_VALIDATION.md) | **Authoritative Empirical Metrics**: GroupKFold zero-leakage cross-validation ($N=17,761$), multi-dose held-out benchmarks ($r = 0.8359$), and blind validation on all 6 FDA commercial drugs (Inclisiran, Patisiran, etc.). |
