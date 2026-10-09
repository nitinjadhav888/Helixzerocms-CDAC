# 01. HELIXZERO PROJECT OVERVIEW
## Executive Vision, Scientific Scope, and Operational Mandate
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  
**Authoritative Single Source of Truth for Benchmarks:** `final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md`  

---

### 1. Executive Summary

**HelixZero-CMS** is an open-source, chemistry-aware oligonucleotide potency prediction and structural optimization platform developed at the **Centre for Development of Advanced Computing (C-DAC), Pune**. The system addresses the central translational bottleneck in RNA interference (RNAi) therapeutics: while naked small interfering RNAs (siRNAs) are rapidly cleaved by nucleases and provoke dangerous innate immune responses, chemical modifications rewiring the oligonucleotide architecture introduce a combinatorial explosion of approximately $30^{42} \approx 1.09 \times 10^{62}$ possible configurations per 21-mer duplex.

HelixZero establishes a dual-stage computational engine that decouples whole-transcriptome target sequence screening from synthetic chemical optimization:
1. **Upstream Transcript Scanner (Model A):** Evaluates thousands of candidate 21-mers along an mRNA transcript, scoring thermodynamic asymmetry, Reynolds/Ui-Tei rule compliance, and target site accessibility in $< 0.05$ s ($r = 0.8044\text{--}0.8788$).
2. **Unified Dose-Aware Chemistry Engine (Model B):** Deploys a 517-dimensional multi-modal gradient boosted decision tree (CatBoost) trained on 17,761 multi-dose experimental assays with zero sequence identity leakage (`GroupKFold` on 5,251 disjoint antisense sequence clusters), achieving $r = 0.8359$ on held-out multi-dose validation sets and 100% sensitivity across all six commercial FDA-approved siRNA therapeutics.

---

### 2. Scientific & Biological Context

In human cells, RNA interference is catalyzed by Argonaute-2 (Ago2), the central slicer endonuclease within the multiprotein RNA-Induced Silencing Complex (RISC). The guide (antisense) strand of an siRNA duplex is anchored into the Ago2 MID domain by its $5'$-phosphate, while the $3'$ end is held by the PAZ domain. Target mRNA complementary to the guide strand is positioned across the catalytic PIWI domain, where an Asp-Glu-Asp-His tetrad cleaves the mRNA backbone opposite guide nucleotides 10 and 11.

Clinical siRNAs (such as Patisiran, Inclisiran, and Vutrisiran) cannot be administered as naked canonical RNA. They require:
- **$2'$-Ribose Modifications ($2'$-OMe, $2'$-F, $2'$-MOE):** Conformationally constrain the ribose ring into $C3'$-endo (A-form RNA geometry) and eliminate the reactive $2'$-OH group attacked by nucleases.
- **Phosphorothioate (PS) Internucleotide Linkages:** Replace a non-bridging oxygen atom with sulfur to resist serum exonucleases.
- **$5'$-Phosphate Mimics ($5'$-(E)-vinylphosphonate [$5'$-VP]):** Protect the $5'$ terminus from intracellular phosphatases and lock the guide strand into the Ago2 MID pocket.
- **Targeting Conjugates (Trivalent GalNAc):** Direct high-affinity delivery to asialoglycoprotein receptors (ASGPR) on hepatocytes.

However, synthetic modifications interact non-linearly with Ago2. For example, introducing a bulky $2'$-MOE modification at guide position 10 physically clashes with the catalytic cleft, abolishing mRNA cleavage despite high binding affinity. HelixZero accurately predicts these non-linear chemical epistatic phenomena.

---

### 3. Computational Strategy

HelixZero solves the representation challenge without sparse one-hot explosion:
- **Positional Chemistry Grouping:** 31 supported modifications mapped into 10 biologically grounded physical property flags across 42 nucleotide slots ($42 \times 10 = 420$ features) + 24 global architecture descriptors $= 444$ dimensions.
- **Evolutionary Context:** 64 dimensions derived from dual PCA-32 projections of the RNA-FM 100M-parameter foundation model.
- **Thermodynamic Constants:** 5 ViennaRNA physical parameters ($\Delta G_{\text{MFE}}$, $\Delta G_{\text{duplex}}$, ensemble diversity, GC ratio).
- **Dynamic Pharmacokinetics:** 4 continuous covariates including $\log_{10}(\text{Dose\_nM})$, enabling direct dose-response curve generation and closed-form analytical Hill inversion ($pIC_{50} = 9 - \log_{10}[IC_{50}]$).

---

### 4. Key Performance Highlights

Certified by `final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md`:
- **Model A (Naked LightGBM):**
  - Takayuki Screen ($N = 702$): Pearson $r = 0.8788$, Spearman $\rho = 0.8734$, ROC-AUC $= 0.9275$.
  - Mixset 7-Studies ($N = 472$): Pearson $r = 0.8291$, Spearman $\rho = 0.8093$, ROC-AUC $= 0.9456$.
  - Huesken Gold-Standard ($N = 2,361$): Pearson $r = 0.8044$, Spearman $\rho = 0.8065$, ROC-AUC $= 0.9099$.
  - Negative Control on Modified RNA ($N = 2,576$): Pearson $r = 0.1771$, $R^2 = -0.0901$ (Proof of sequence blindness).
- **Unified CatBoost Engine (517-D):**
  - 5-Fold Sequence `GroupKFold` CV ($N = 17,761$): Pearson $r = 0.6776$, Spearman $\rho = 0.6752$, $R^2 = 0.4497$.
  - Homogeneous Multi-Dose Held-Out ($N = 472$): Pearson $r = 0.8359$, Spearman $\rho = 0.8558$, ROC-AUC $= 0.9312$.
  - Heterogeneous Multi-Dose Held-Out ($N = 1,796$): Pearson $r = 0.8334$, Spearman $\rho = 0.8383$, ROC-AUC $= 0.9291$.
- **Clinical Blind Validation (10 nM):**
  - Cohort Mean Predicted Knockdown: **65.04%** across all 6 FDA-approved drugs (Inclisiran: 76.68%, Patisiran: 73.70%).
  - **100% Sensitivity** for clinical leads.

---

### 5. Architectural Consolidation Overview

To ensure production stability, high throughput, and minimal operational footprint, the platform was consolidated from legacy fragmented prototypes into a single unified engine:
- **Retired:** MEG-mod GNN TransformerConv ($r = 0.0631$ on held-out sets, 15-minute cold starts, CUDA memory spikes).
- **Retired:** IEEE v5 Two-Stage cascading pipeline ($pIC_{50} \to \text{Hill}$ regression, which compounded intermediate prediction variance).
- **Active:** Single Unified Dose-Aware CatBoost Regressor conditioned directly on $[ \mathbf{x}_{513}, \log_{10}(C), \text{covars} ]$, executing on standard CPU architectures in sub-second latency.
