# DATASETS & EXPERIMENTAL ASSAYS REFERENCE
## Comprehensive Technical Guide to Biological Assays, Readouts, and Representations
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. Catalog of Biological Assays Used in HelixZero

The training, evaluation, and safety components of HelixZero ingest and model data from four distinct classes of biological assays:

```text
===================================================================================================
ASSAY CLASSIFICATION           EXPERIMENTAL METHOD              PRIMARY READOUT / MEASUREMENT
===================================================================================================
1. Quantitative mRNA RT-qPCR   Real-Time Quantitative PCR       Relative target mRNA expression
2. Dual-Luciferase Reporter    Dual-Luciferase Chemiluminescence Renilla / Firefly luminescence ratio
3. Multi-Dose Titrations       High-Throughput Robotic Dilution Concentration-response curves (IC50)
4. Cellular Viability Screens  CellTiter-Glo / AlamarBlue       ATP luminescence (% cell viability)
===================================================================================================
```

---

### 2. Granular Assay Profiles & Computational Mapping

#### 2.1 Quantitative mRNA RT-qPCR Assays
- **Biological Target:** Measures direct intracellular transcript degradation of endogenous human mRNAs.
- **Experimental Protocol:** Cells (e.g. HeLa, HepG2) are transfected with candidate siRNAs using lipid nanoparticles (LNPs) or cationic lipids (Lipofectamine RNAiMAX). Total RNA is harvested 24 hours post-transfection, reverse-transcribed into cDNA, and amplified using target-specific and housekeeping (e.g. *GAPDH*, *ACTB*) TaqMan primers.
- **Computational Representation:** 
  $$\text{Knockdown \%} = 100.0 - \left( 2^{-\Delta\Delta C_t} \times 100.0 \right).$$
  Represented as a continuous float $[0.0, 100.0]$ in `cmsirnadb_clean_targets_Y.npy`.
- **Pipeline Entry:** Serves as the primary ground-truth target variable for Model A (Huesken et al. 2005) and the Unified CatBoost Regressor.

#### 2.2 Dual-Luciferase Chemiluminescence Reporter Assays
- **Biological Target:** Evaluates target sequence cleavage in synthetic reporter constructs.
- **Experimental Protocol:** Target mRNA target sites are cloned into the $3'$ UTR of a *Renilla* luciferase gene. A constitutive *Firefly* luciferase vector acts as an internal transfection control. Ratios of *Renilla* to *Firefly* luminescence reflect target cleavage.
- **Computational Representation:**
  $$\text{Knockdown \%} = 100.0 - \left(\frac{\text{Luminescence}_{\text{Renilla}} / \text{Luminescence}_{\text{Firefly}}}{\text{Control Ratio}} \times 100.0\right).$$
- **Pipeline Entry:** Used in the Takayuki et al. (2008) canonical screening dataset (`Taka.csv`, $N = 702$).

#### 2.3 Multi-Concentration Pharmacodynamic Titrations
- **Biological Target:** Determines intrinsic potency ($IC_{50}$) and cooperativity ($h$) by testing siRNAs across systematic dilution series.
- **Experimental Protocol:** siRNAs are titrated across 5 to 8 serial dilution steps spanning five orders of magnitude ($0.001\text{ nM}$, $0.01\text{ nM}$, $0.1\text{ nM}$, $1.0\text{ nM}$, $10\text{ nM}$, $100\text{ nM}$, $1{,}000\text{ nM}$, $10{,}000\text{ nM}$).
- **Computational Representation:**
  Represented as paired inputs $[\mathbf{x}_{513}, \log_{10}(C)]$, where $C = \text{conc\_nM}$, mapped directly to observed knockdown.
- **Pipeline Entry:** Drives the dynamic exposure covariates in `smepred/src/features_v4.py:build_unified_features()` and validates closed-form Hill inversion.

#### 2.4 High-Throughput Cellular Viability Assays (Janas Seed Toxicity)
- **Biological Target:** Measures phenotypic cell death triggered by microRNA-like off-target seed down-regulation of essential housekeeping genes.
- **Experimental Protocol:** HeLa cells are transfected with 4,096 distinct hexamer seed duplexes in 384-well plates. Cell viability is quantified 72 hours post-transfection using CellTiter-Glo ATP luminescent cell viability assays.
- **Computational Representation:**
  Tabulated as a 4,096-row empirical lookup table (`smepred/data/oligoformer/cell_viability.tsv`). Each hexamer maps to percentage cell viability relative to mock-transfected controls.
- **Pipeline Entry:** Ingested via `smepred/src/filters.py:get_toxicity_score()`. Guides with seeds $< 50\%$ viability receive the `Toxic` label and are filtered from curated lead selections.
