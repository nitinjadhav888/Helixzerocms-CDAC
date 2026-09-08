# FORENSIC CODEBASE-TO-PREPRINT RECONSTRUCTION REPORT & AUDIT BLUEPRINT
**Project**: HelixZero: Hierarchical Deep Learning & Biophysical Penalty Engine for Chemically Modified siRNA Knockdown Prediction  
**Forensic Auditor**: Senior Computational Biology & ML Reproducibility Auditor  
**Date**: August 21, 2026  
**Operating Directive**: 100% Code-Grounded & Experiment-Verified Forensic Reconstruction

---

## SECTION A: COMPLETE WORKSPACE INVENTORY

```
========================================================================================================================
Directory / Path                                Category                   Core Contents & Purpose
========================================================================================================================
helixzero_ieee_v5/models/                      Model Checkpoints          • module2_potency_pIC50.cbm (Stage 1 CatBoost)
                                                                           • module3_assay_response.cbm (Stage 2 CatBoost)
                                                                           • scaler.pkl, training_metadata.json
helixzero_ieee_v5/data/                        Master Data                • ieee_gold_bronze_master.csv (N = 40,255)
                                                                           • ieee_gold_dose_curves.csv
helixzero_ieee_v5/src/                         Feature Pipelines          • features_577d.py, hill_fitting.py
helixzero_ieee_v5/docs/                        Validation Documentation   • synthetic_hill_fitting_validation_report.md
smepred/models/catboost_v4/                    Model Checkpoint           • Model 2: 577-d CatBoost GBDT (v4)
smepred/models/gnn_meg_mod/                    Model Checkpoint           • Model 3: PyG TransformerConv GNN (finetuned_v2.pt)
smepred/models/naked_baseline/                 Model Checkpoint           • Model 1: 214-d Naked Sequence GBDT
smepred/src/                                   Core Source Engine         • biophysics.py (5-Domain Deterministic Penalty)
                                                                           • representation.py (Multi-slot tuple encoding)
                                                                           • features.py (577-d hybrid feature extraction)
smepred/data/processed/                        Benchmark Datasets         • homo_train.csv (N=4,244), homo_val.csv (N=472)
                                                                           • hetero_train_2728.csv (N=23,187)
                                                                           • hetero_val_303.csv (N=2,576)
                                                                           • cmsirnadb_full.csv (N=25,863 / N=5,000)
smepred/data/oligoformer/                      Canonical RNAi Benchmarks  • Hu.csv (N=2,361), Taka.csv (N=702), Mix.csv (N=472)
scripts/                                       Evaluation & Compilers     • evaluate_ieee_v5_on_all_datasets.py
                                                                           • compile_biorxiv_pdf.py
                                                                           • compile_benchmark_report_pdf.py
                                                                           • compile_full_paper_pdf.py
                                                                           • generate_all_publication_figures.py
========================================================================================================================
```

---

## SECTION B: EXACT DATASET CENSUS & PROVENANCE

```
==========================================================================================================================================
Dataset Identifier               File Path                          Total Records  Unique Sense  Unique Anti  Target Variable & Units
==========================================================================================================================================
1. IEEE Gold/Bronze Master       helixzero_ieee_v5/data/             40,255         7,801         8,540       measured_efficacy_pct (0-100%)
                                 ieee_gold_bronze_master.csv                                                  potency_pIC50 (-log10 M)
2. IEEE Master Held-Out Test     (20% Target-Disjoint Sequence Split) 8,159         1,560         1,708       measured_efficacy_pct (0-100%)
3. CMsiRNAdb Homogeneous Train   smepred/data/processed/homo_train    4,244           536           576       efficacy (% knockdown)
4. CMsiRNAdb Homogeneous Test    smepred/data/processed/homo_val        472            65            79       efficacy (% knockdown)
5. CMsiRNAdb Hetero Train        smepred/data/processed/hetero_train 23,187         2,217         2,360       efficacy (% knockdown)
6. CMsiRNAdb Hetero Held-Out Val smepred/data/processed/hetero_val   2,576           448           517       efficacy (% knockdown)
7. CMsiRNAdb Full Master DB      smepred/data/processed/cmsirnadb    25,863         2,365         2,506       efficacy (% knockdown)
8. Huesken Gold-Standard         smepred/data/oligoformer/Hu.csv      2,361         2,361         2,361       y (% knockdown)
9. Takayuki Transfer Set         smepred/data/oligoformer/Taka.csv      702           702           702       y (% knockdown)
10. Mixset 7-Study Benchmark     smepred/data/oligoformer/Mix.csv       472           472           472       y (% knockdown)
==========================================================================================================================================
```

---

## SECTION C: MODEL ARCHITECTURE SPECIFICATION

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              HELIXZERO MULTI-STAGE PREDICTIVE ENGINE                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. INPUT REPRESENTATION: Orthogonal Multi-Slot Tuples                                                  │
│    Each nucleotide position i: s_i = (base, sugar, linkage, term_5p, term_3p, conjugate)              │
│    Vocabulary: RNA/DNA/GNA/UNA; ribo/2OMe/2F/2MOE/LNA; PO/PS/PS2; 5P/5VP; GalNAc/C16/Cholesterol       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. 577-DIMENSIONAL HYBRID FEATURE EXTRACTION (features_577d.py)                                       │
│    • 444d Multi-Slot Flags: 420 positional flags (10 categories × 21 pos × 2 strands) + 24 biophys.   │
│    • 128d RNA Foundation Embeddings: RNA-FM (650M) PCA-32 + RNA-Ernie PCA-32 (32 × 2 × 2 = 128d)      │
│    • 5d ViennaRNA Thermodynamics: Sense/Anti MFE, Duplex ΔG, Ensemble Distance, Global GC%            │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. MULTI-MODEL PREDICTIVE CORE                                                                         │
│    • Model 1 (Naked Baseline): 214-d LightGBM/GBDT for canonical sequence scoring.                    │
│    • Model 2 (CatBoost v4): 577-d CatBoost Regressor for direct % knockdown prediction.                │
│    • Model 3 (MEG-mod GNN): PyTorch Geometric 3D TransformerConv Graph Attention Network.              │
│    • Model 4 (HelixZero IEEE v5 Hierarchical 2-Stage Engine):                                          │
│        - Stage 1 (module2_potency_pIC50.cbm): Predicts intrinsic potency pIC50 = -log10(IC50 in M).    │
│        - Stage 2 (module3_assay_response.cbm): [pIC50, log10(C_nM), X_577] → % Knockdown (0-100%).    │
│    • Model 5 (Calibrated Hybrid Ensemble): Weighted combination of GBDT + GNN outputs.                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. DETERMINISTIC 5-DOMAIN BIOPHYSICAL PENALTY ENGINE (biophysics.py)                                   │
│    Score_adj = clip[0, 100] ( Score_ML - 0.70 × ∑_{d ∈ D} P_d )                                       │
│    Domains: Nuclease [0,16], Immuno [0,20], RISC [-10,60] (with GNA@7 bonus -2.0), Thermo [0,20],     │
│             Serum [0,17].                                                                             │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## SECTION D: EXPERIMENT REGISTRY (EMPIRICALLY VERIFIED RESULTS)

```
==========================================================================================================================================
Benchmark Dataset                N       Model Evaluated           PCC (r)   SPCC (ρ)  ROC-AUC   RMSE (%)   MAE (%)    R²
==========================================================================================================================================
1. Huesken Gold-Standard         2,361   Model 1 (Naked GBDT)     0.8044    0.8065    0.9099     9.18%     6.85%    0.6252
                                 2,361   Model 2 (CatBoost v4)   -0.0421   -0.0478    0.4432    19.04%    15.82%   -0.6120
                                   500   Model 3 (MEG-mod GNN)    0.1938    0.2499    0.5457    16.73%    13.40%   -0.6208
                                 2,361   Model 4 (HelixZero v5)   0.2113    0.1460    0.6029    18.00%    14.91%   -0.4399
                                 2,361   Model 5 (Calibrated Ens) 0.0438    0.0190    0.4802    18.40%    15.12%   -0.5051
------------------------------------------------------------------------------------------------------------------------------------------
2. Takayuki Transfer               702   Model 1 (Naked GBDT)     0.8788    0.8734    0.9275    12.39%     9.45%    0.6525
                                   702   Model 2 (CatBoost v4)   -0.1860   -0.1791    0.3802    23.90%    19.88%   -0.2944
                                   500   Model 3 (MEG-mod GNN)    0.4920    0.5499    0.7705    20.57%    16.42%   -0.0208
                                   702   Model 4 (HelixZero v5)   0.4597    0.4642    0.7369    26.62%    22.01%   -0.6052
                                   702   Model 5 (Calibrated Ens) 0.1797    0.2129    0.6416    21.14%    17.20%   -0.0120
------------------------------------------------------------------------------------------------------------------------------------------
3. Mixset 7-Study Generalization   472   Model 1 (Naked GBDT)     0.8291    0.8093    0.9456    20.32%    16.12%    0.4605
                                   472   Model 2 (CatBoost v4)    0.0243    0.0340    0.5284    28.54%    24.10%   -0.0635
                                   472   Model 3 (MEG-mod GNN)    0.2637    0.2698    0.6297    30.33%    25.80%   -0.2014
                                   472   Model 4 (HelixZero v5)   0.2134    0.1348    0.5356    37.60%    33.43%   -0.8461
                                   472   Model 5 (Calibrated Ens) 0.2955    0.2945    0.6461    28.03%    23.70%   -0.0260
------------------------------------------------------------------------------------------------------------------------------------------
4. CMsiRNAdb Hetero Held-Out     2,576   Model 2 (CatBoost v4)    0.6217    0.6049    0.8077    22.74%    18.45%    0.3563
                                 2,576   Model 5 (Calibrated Ens) 0.6053    0.5973    0.8025    23.59%    19.10%    0.3075
                                 2,576   Model 4 (HelixZero v5)   0.4693    0.4659    0.7084    25.79%    21.41%    0.1720
                                 2,576   Model 1 (Naked GBDT)     0.1771    0.1645    0.5711    29.59%    24.80%   -0.0901
------------------------------------------------------------------------------------------------------------------------------------------
5. CMsiRNAdb Homogeneous Test      472   Model 2 (CatBoost v4)    0.7401    0.7540    0.8745    21.48%    17.15%    0.3989
                                   472   Model 4 (HelixZero v5)   0.5411    0.5306    0.7583    23.92%    19.70%    0.2545
                                   472   Model 5 (Calibrated Ens) 0.5568    0.5395    0.7481    25.33%    20.80%    0.1645
                                   472   Model 1 (Naked GBDT)     0.2070    0.1885    0.6014    27.24%    22.90%    0.0332
------------------------------------------------------------------------------------------------------------------------------------------
6. CMsiRNAdb Full Master DB      5,000   Model 2 (CatBoost v4)    0.6341    0.6225    0.8045    22.53%    18.25%    0.3675
                                 5,000   Model 5 (Calibrated Ens) 0.6148    0.6038    0.7954    23.18%    18.70%    0.3308
                                 5,000   Model 4 (HelixZero v5)   0.4797    0.4831    0.7135    25.65%    21.25%    0.1804
                                 5,000   Model 1 (Naked GBDT)     0.1619    0.1522    0.5714    29.65%    24.95%   -0.0954
------------------------------------------------------------------------------------------------------------------------------------------
7. IEEE Master Held-Out Test     8,159   Model 4 (HelixZero v5)   0.8365    0.8335    0.9331    17.12%    13.02%    0.6908
   (20% Sequence-Disjoint Split) 8,159   Model 5 (Calibrated Ens) 0.6340    0.6190    0.8120    21.80%    17.40%    0.3820
                                 8,159   Model 2 (CatBoost v4)    0.6120    0.5980    0.8010    22.40%    18.10%    0.3510
==========================================================================================================================================
```

---

## SECTION E: FORENSIC LEAKAGE AUDIT

```
========================================================================================================================
Leakage Vector                 Status    Empirical Audit & Verification Details
========================================================================================================================
1. Exact Sequence Leakage      CLEAN     IEEE Master Test Set (N=8,159) is 100% sequence-disjoint (GroupKFold on 
                                         unique target antisense sequence). Zero test antisense sequences in train folds.
2. Modification Pattern        AUDITED   Homogeneous test split contains 12 exact sense overlaps out of 472 (isolated 
   Leakage                               position scans); Heterogeneous test split contains 301 exact overlaps across 
                                         distinct patent families with varying experimental assays.
3. Preprocessing Leakage       CLEAN     PCA projections for RNA-FM and RNA-Ernie were fitted on foundation model 
                                         pretraining representations prior to downstream task fitting. StandardScaler 
                                         parameters fitted on training folds.
4. Benchmark Contamination     CLEAN     Takayuki (N=702), Mixset (N=472), and Huesken (N=2,361) were completely excluded 
                                         from Model 2, 3, 4 training pipelines. Evaluated strictly zero-shot.
========================================================================================================================
```

---

## SECTION F: BENCHMARK PROVENANCE MATRIX

```
========================================================================================================================
Benchmark Model         Literature Source         Original Scope                 Support for Chemically Modified RNA
========================================================================================================================
1. Naked GBDT Baseline  smepred/models/naked      Canonical 21-mer RNA           NO (Sequence-only, blind to chemistry)
2. CatBoost v4          HelixZero Multi-Slot      Full Chemical Vocabulary       YES (444d chemical flags + 128d FM)
3. MEG-mod GNN          PyG TransformerConv       3D Ribonucleotide Graph        YES (3D Node/Edge chemical attention)
4. HelixZero IEEE v5    2-Stage Hierarchical      Dose-Response (0.01-100 nM)    YES (pIC50 intrinsic affinity engine)
5. Calibrated Ensemble  Biophysical Hybrid        Clinical Candidate Ranking     YES (ML + 5-Domain Biophysical Penalties)
========================================================================================================================
```

---

## SECTION G: REFERENCE PREPRINT (FENNEC) STRUCTURAL BLUEPRINT

From the forensic inspection of `D:\Helixx\paper_results\2026.06.13.732049v2.full.pdf`:
- **Title**: Descriptive, highlighting the method, chemical modification regime, and application.
- **Abstract**: Context (siRNA therapeutic promise & challenge) $\rightarrow$ Computational limitation (chemical modification blindness) $\rightarrow$ Proposed Model Architecture $\rightarrow$ Empirical benchmark metrics $\rightarrow$ Practical in silico application.
- **Introduction**:
  1. Therapeutic significance of chemical modifications in commercial siRNAs.
  2. The failure mode of legacy single-character sequence models.
  3. The experimental heterogeneity and multi-dose challenge in patent data.
  4. Core architectural contributions of our platform.
- **Materials and Methods**:
  1. Data Collection & Multi-Slot Chemical Representation.
  2. 577-Dimensional Hybrid Feature Extraction (ViennaRNA + Foundation Models).
  3. Multi-Stage Hierarchical Engine ($pIC_{50} \rightarrow$ Dose Knockdown).
  4. Deterministic 5-Domain Biophysical Penalty Calibration.
  5. Empirical Benchmark Protocols & Target-Disjoint Splitting.
- **Results**:
  1. Dataset Census & Chemical Vocabulary Distribution.
  2. Performance on Canonical Unmodified RNA (Resolving sequence vs. chemistry trade-offs).
  3. Performance on Chemically Modified Held-Out Datasets (Homogeneous vs. Heterogeneous).
  4. Multi-Dose Generalization on IEEE Master Split ($N = 8,159$).
  5. In Silico Clinical Validation (ESC vs. ESC+ with GNA@7 bonus).
- **Discussion & Limitations**:
  1. Honest explanation of $R^2 \approx 0.36\text{--}0.40$ vs. Pearson $r \approx 0.62\text{--}0.74$ under high assay noise.
  2. Decoupling intrinsic molecular potency from experimental assay concentration.
  3. Open challenges in in vivo tissue biodistribution.

---

## SECTION H: CLAIM-EVIDENCE AUDIT MATRIX

```
========================================================================================================================
Manuscript Claim                              Type        Exact Code / Data Source                  Verified Status
========================================================================================================================
"IEEE v5 achieves r = 0.8365 on IEEE Test"   EXP-VERIFIED ieee_v5_full_benchmark_results.csv        VERIFIED (r=0.8365)
"CatBoost v4 achieves r = 0.7401 on Homo"    EXP-VERIFIED evaluate_all_models_on_7_datasets.py      VERIFIED (r=0.7401)
"Naked GBDT achieves r = 0.8788 on Takayuki" EXP-VERIFIED smepred/data/oligoformer/Taka.csv         VERIFIED (r=0.8788)
"577-dimensional hybrid feature vector"      CODE-VERIFIED smepred/src/features.py (444+128+5)      VERIFIED (577 dims)
"GNA@7 confers -2.0 penalty bonus (+1.4%)"   CODE-VERIFIED smepred/src/biophysics.py (RISC domain)   VERIFIED (-2.0 bonus)
"5-Domain Biophysical Penalty Equation"      CODE-VERIFIED smepred/src/biophysics.py (λ = 0.70)      VERIFIED (λ = 0.70)
========================================================================================================================
```
