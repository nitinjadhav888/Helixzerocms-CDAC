# 26. SYSTEM CHANGELOG & ARCHITECTURAL EVOLUTION
## Version History, Refactoring Milestones, and Deprecation Accounting
**Status:** `VERIFIED — HISTORICAL & CURRENT IMPLEMENTATION`  

---

### Version 3.0.0 — Production Release (October 2026)
`VERIFIED — CURRENT IMPLEMENTATION`
- **Architectural Consolidation:** Fully consolidated the production serving path into the **Single Unified Dose-Aware CatBoost Regressor** (517-D).
- **Zero Sequence Leakage Certification:** Implemented strict 5-fold `GroupKFold` partitioning across 5,251 disjoint antisense sequence clusters ($N = 17,761$), certifying Pearson $r = 0.6776$ on novel genes and $r = 0.8359$ on held-out multi-dose screens.
- **Closed-Form Hill Inversion:** Implemented microsecond-scale analytical $pIC_{50}$ derivation ($pIC_{50} = 9 - \log_{10}[IC_{50}]$), eliminating cascading two-stage error.
- **Authoritative Benchmark Single Source of Truth:** Established `final_benchmarks/` as the immutable master repository for all benchmark numbers and deleted redundant historical draft markdown files.
- **Continuous 3D Structural Modeling:** Engineered `pdb_generator.py` emitting 504-atom continuous A-form double-helices with B-factor encoded chemical modifications.
- **Whole-Transcriptome 2-Bit SIMD Firewall:** Compiled the 863.8 MB binary packed index (`human_transcriptome.idx.pkl`) enabling sub-microsecond 15-mer slicer queries.

---

### Version 2.2.0 — IEEE v5 Two-Stage Archive (August 2026)
`VERIFIED — HISTORICAL IMPLEMENTATION`
- **Two-Stage Cascading Engine:** Implemented `module2_potency_pIC50.cbm` (predicting intermediate potency) and `module3_assay_response.cbm` (predicting assay response via sigmoidal fitting).
- **Compounded Variance Audit:** Identified that two-stage prediction compounded intermediate errors ($r = 0.8187$ vs unified $0.8359$). Checkpoint archived in `helixzero_ieee_v5/` for ablation comparison.

---

### Version 2.0.0 — Deep Learning Hybrid & MEG-mod Exploration (May 2026)
`VERIFIED — HISTORICAL IMPLEMENTATION`
- **MEG-mod GNN Integration:** Explored PyTorch Geometric `TransformerConv` bi-directional graph attention network with Uni-Mol 3D conformation embeddings.
- **Retirement Decision:** Identified poor out-of-distribution transfer ($r = 0.0631$), CUDA memory crashes, and 15-minute cold starts. Retired from active runtime and isolated in `MEG-mod-main/`.

---

### Version 1.0.0 — Baseline Inception (January 2026)
`VERIFIED — HISTORICAL IMPLEMENTATION`
- Initial implementation of Model A (LightGBM) trained on Huesken and Novartis high-throughput screens ($r = 0.8044$).
- Initial single-character chemical modification parser.
