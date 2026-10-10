# 26. SYSTEM CHANGELOG & ARCHITECTURAL EVOLUTION
## Version History, Refactoring Milestones, and Deprecation Accounting
**Status:** `VERIFIED — HISTORICAL & CURRENT IMPLEMENTATION`  

---

### Version 3.1.1 — GNA Antisense Position 7 Guardrail, Novel Pareto Beam Search & Isotonic Calibration (October 2026)
`VERIFIED — CURRENT IMPLEMENTATION`
- **Strict (S)-GNA Antisense Position 7 Guardrail:** Enforced strict clinical prior constraints across `smepred/src/modification_engine.py` (`_is_positionally_valid`, `_is_chemically_viable`, `single_mod_scan`) and `smepred/src/biophysics.py`. (S)-GNA (`8`) is strictly pinned to **antisense position 7** (the Alnylam AMVUTTRA® / ESC+ standard). GNA is strictly rejected on the sense strand and at any antisense position other than 7 (eliminating anomalous selection at antisense position 6).
- **Multi-Objective Pareto Beam Search for Novel Chemistries:** Fixed candidate beam collapse where zero-penalty FDA Core duplexes purged innovative monomers. When `fda_core_only=False` (Novel Mode), a 40% innovative candidate quota preserves preclinical chemistries (LNA `L`, 2'-MOE `E`, ENA `Y`, UNA `6`, TNA `9`) across expansion rounds. Endpoints `/multi-mod-scan` and `/multi-mod-from-single` Pareto-interleave core anchors and innovative candidates in the top rankings.
- **Empirical Isotonic Calibration Restoration:** Restored scikit-learn's empirical `IsotonicRegression` checkpoint for `calibrator_naked.pkl`. Replaces the aggressive linear stretching ($\hat{y} = 1.5165 \cdot x - 25.892$) that artificially saturated top naked mRNA leads at 100.00%, returning realistic, smooth monotonic scores ($87.85\%$ on Lead #1, $78.13\%$ on Lead #2). Added runtime module namespace aliases (`smepred.src.calibrator` and `src.calibrator`) in `predictor.py`, eliminating unpickle errors across Docker containers.
- **Synthesis Budget Tag Realignment for (S)-GNA:** Corrected `MOD_EVIDENCE_MAP['8']` in `smepred/app.html` to `Specialty ($$)` (`costIndex: "$$"`), ensuring duplexes containing FDA Core monomers and position-7 GNA accurately display `Tier 0: FDA Core` and `Specialty ($$)` rather than contradictory `Exotic Custom ($$$)`.

---

### Version 3.1.0 — Positional Coverage Beam Search, Chemical Tiers & Monotonic Clamping (October 2026)
`VERIFIED — PRIOR RELEASE`
- **Full-Duplex Combinatorial Beam Search Expansion:** Eliminated premature beam search stagnation at ~16–20 modifications by replacing naive global score slicing with 42-position positional coverage in `pairing_pool`. Enables combinatorial chemical design across all 42 sense and antisense positions.
- **Automated (S)-GNA Seeding for ESC+ Design:** Ensured (S)-GNA (`8`) at antisense position 7 is automatically seeded into the initial beam and pairing pool, preserving its critical biological role as an off-target seed destabilizer regardless of single-point on-target delta scores.
- **Pharmacological Evidence Tier Realignment:** Reclassified 2'-MOE (`E`) and ENA (`Y`) to **Tier 1: Innovative/Preclinical** (reflecting their single-stranded ASO clinical status and steric bulk in duplex siRNA), reserving **Tier 0: FDA Core** strictly for clinical siRNA drugs (`M`, `F`, `D`, `S`, `1`, `2`, `3`, `4`, and position-7 `8`).
- **Monotonic Calibration Clamping:** Integrated and bound the out-of-fold `StrictlyMonotonicCalibrator` ($\hat{y} = 1.5165 \cdot x - 25.892$) with deterministic $[0.00\%, 100.00\%]$ clamping across `predictor.py` and UI components (`scoreBar`, `scoreBarSmall`), preventing mathematical overshoots.
- **Frontend Evidence Limit Badging:** Updated `getEvidenceLimitSummary` and `confidenceBadge` to aggregate all strand modifications while ignoring canonical ribonucleotides (`AUCG`), ensuring accurate synthesis budget and clinical prior tier display.

---

### Version 3.0.0 — Production Release (October 2026)
`VERIFIED — PRIOR RELEASE`
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
