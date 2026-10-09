# 24. SYSTEM LIMITATIONS & KNOWN TECHNICAL RISKS
## Critical Constraints, Edge Cases, and Boundary Conditions
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. Dataset & Biological Training Constraints

1. **Multi-Laboratory Batch Variance:**
   The primary training corpus ($N = 17,761$) consolidates assays from academic literature published over 15 years. Variations in transfection reagents (Lipofectamine 2000 vs. RNAiMAX), cell seeding densities, and reporter systems introduce inter-laboratory batch noise that establishes an empirical correlation ceiling of $r \approx 0.68$ on novel genes.
2. **Stereorandom Phosphorothioate Representation:**
   Synthesis of standard clinical siRNAs yields diastereomeric mixtures ($2^k$ isomers for $k$ phosphorothioate linkages). CMsiRNAdb does not report stereochemical purity. HelixZero models the stereorandom ensemble average; stereopure $R_p$ vs. $S_p$ differences are not resolved.
3. **Hepatic Lineage Preponderance:**
   The training data heavily reflects the historical dominance of liver-targeted GalNAc therapeutics (such as Inclisiran and Patisiran). Cell-type covariates for extrahepatic tissues (neurons, cardiomyocytes, podocytes) have limited sample density.

---

### 2. Algorithmic & Modeling Constraints

1. **Fixed Hill Cooperativity Assumption ($h = 1.0$):**
   The closed-form analytical Hill inversion assumes ideal non-cooperative single-site binding ($h = 1.0$). While accurate for standard catalytic Ago2 cleavage, complex cooperative silencing kinetics or multi-target sequestering are not explicitly modeled.
2. **Sequence Length Boundaries:**
   The positional feature extractor is engineered for canonical 19-mer to 23-mer duplexes with canonical $3'$ overhangs. Non-canonical long duplexes ($> 27$ nt, Dicer substrates) are summarized via aggregate lengths rather than per-position feature slots.

---

### 3. Infrastructure & Runtime Constraints

1. **Memory Footprint of Binary Transcriptome Index:**
   The pre-indexed human transcriptome (`human_transcriptome.idx.pkl`) is 863.8 MB on disk and expands to $\sim 1.4\text{ GB}$ of system RAM when loaded. While lazy-loading protects startup latency, memory-constrained containers ($< 2\text{ GB}$ RAM) may encounter out-of-memory errors during whole-transcriptome scans.
2. **ViennaRNA Native C-Extension on Windows:**
   Pre-compiled ViennaRNA Python wheels are occasionally unavailable on native Windows environments. HelixZero provides a deterministic nearest-neighbor Turner fallback, but full secondary structure ensemble diversity requires the native C-extension.
