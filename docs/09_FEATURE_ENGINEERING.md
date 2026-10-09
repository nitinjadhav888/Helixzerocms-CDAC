# 09. FEATURE ENGINEERING & VECTOR SPECIFICATIONS
## Comprehensive Feature-by-Feature Reference Manual
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  
**Total Feature Dimensionality:** **517 Continuous Features** (Unified CatBoost) | **214 Features** (Model A Baseline) | **190 Features** (Model A Context)  

---

### 1. Unified 517-D Feature Architecture Overview

The 517-dimensional vector space is decomposed into four orthogonal physical blocks:
$$\mathbf{x} = [\mathbf{s}_{\text{chem}} \in \mathbb{R}^{444}, \, \mathbf{z}_{\text{FM}} \in \mathbb{R}^{64}, \, \mathbf{t}_{\text{thermo}} \in \mathbb{R}^5, \, \mathbf{c}_{\text{dose}} \in \mathbb{R}^4].$$

```text
===================================================================================================
FEATURE BLOCK                 DIMENSIONS  ORIGIN / COMPUTATIONAL SOURCE           IMPLEMENTATION FILE
===================================================================================================
1. Positional Slot Flags             420  10 biological property flags x 42 slots smepred/src/features_v2.py
2. Global Engineered Chemistry        24  Literature-grounded biophysical ratios  smepred/src/features_v2.py
3. Evolutionary RNA-FM Embeddings     64  Dual PCA-32 projections (Sense + Anti)  smepred/src/features_v4.py
4. ViennaRNA Thermodynamics            5  MFE, duplex dG, ensemble diversity, GC  smepred/src/features_v4.py
5. Dynamic Pharmacokinetics            4  log10(Dose), relative dose, time, cell  smepred/src/features_v4.py
---------------------------------------------------------------------------------------------------
TOTAL UNIFIED VECTOR SPACE           517  Continuous Multi-Modal Representation   model_b_v4.py
===================================================================================================
```

---

### 2. Positional Chemistry Slot Features (420 Dimensions)

Each nucleotide slot $p \in [1, 21]$ on the sense strand (`ss`) and antisense strand (`as`) is mapped into 10 orthogonal binary property flags ($21 \times 2 \times 10 = 420$ features):

| Feature Pattern | Physical / Biological Definition | Data Type | Dim | Why Used & Biological Meaning | Code Evidence |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `{strand}_pos{p}_is_2F` | $2'$-deoxy-$2'$-fluoro ribose modification at position $p$. | `float32` (0/1) | 42 | Enforces $C3'$-endo A-form RNA helical geometry; accelerates Ago2 catalytic cleavage. | `features_v2.py:48-63` |
| `{strand}_pos{p}_is_2OMe` | $2'$-O-methyl ribose modification at position $p$. | `float32` (0/1) | 42 | Eliminates $2'$-OH nucleophile; protects against endonucleases and suppresses TLR7/8 recognition. | `features_v2.py:48-63` |
| `{strand}_pos{p}_is_bulky_rigid` | Locked or bulky sugar (LNA, MOE, ENA) at position $p$. | `float32` (0/1) | 42 | Extreme $C3'$-endo rigidity; stabilizes duplex melting but clashes sterically in catalytic cleft. | `features_v2.py:36,48` |
| `{strand}_pos{p}_is_flexible_exotic` | Flexible acyclic or exotic sugar (UNA, GNA, TNA, FANA). | `float32` (0/1) | 42 | Locally destabilizes seed region to ablate off-target microRNA-like binding (e.g. GNA at pos 7). | `features_v2.py:37,48` |
| `{strand}_pos{p}_is_unmod_ribo` | Natural, unmodified canonical ribose sugar at position $p$. | `float32` (0/1) | 42 | Baseline natural RNA backbone; vulnerable to degradation and immunogenic detection. | `features_v2.py:57` |
| `{strand}_pos{p}_is_dna` | $2'$-deoxyribose (DNA monomer) at position $p$. | `float32` (0/1) | 42 | Confers B-form conformational flexibility; commonly used in $3'\text{-dTdT}$ overhangs. | `features_v2.py:59` |
| `{strand}_pos{p}_is_abasic_cap` | Abasic ribose, inverted abasic, or THF cap at position $p$. | `float32` (0/1) | 42 | Terminal cap blocking exonucleases without Watson-Crick base-pairing capability. | `features_v2.py:61` |
| `{strand}_pos{p}_is_other_sugar` | Unclassified non-standard ribose modification at position $p$. | `float32` (0/1) | 42 | Captures novel chemical exploration outside primary categories. | `features_v2.py:63` |
| `{strand}_pos{p}_is_PS` | Phosphorothioate ($3'$ internucleotide linkage) at position $p$. | `float32` (0/1) | 42 | Replaces non-bridging oxygen with sulfur; confers serum exonuclease resistance. | `features_v2.py:72` |
| `{strand}_pos{p}_is_base_mod` | Modified nucleobase (e.g. 5-methyl-C, pseudouridine) at $p$. | `float32` (0/1) | 42 | Alters hydrogen-bonding and base-stacking thermodynamics without ribose changes. | `features_v2.py:73` |

---

### 3. Global Engineered Features (24 Dimensions)

Grounded in published biochemical literature and cited inline in `smepred/src/features_v2.py:85-148`:

| Feature Name | Definition & Formulation | Biological Rationale | Literature Reference |
| :--- | :--- | :--- | :--- |
| `seed_bulky_rigid_frac` | Fraction of bulky-rigid sugars in guide seed (AS pos 2–8). | Rigid seed locks non-target binding, increasing off-target liability. | Bramsen et al., 2009 (NAR) |
| `seed_flexible_exotic_frac`| Fraction of flexible sugars in guide seed (AS pos 2–8). | Flexible sugars relax seed duplex, suppressing off-target binding. | Schlegel et al., 2022 (Nat Biotech) |
| `ss_mod_density` | Overall $2'$-modification density on sense strand. | High density required to protect passenger strand in circulation. | Allerson et al., 2005 (J Med Chem) |
| `as_mod_density` | Overall $2'$-modification density on antisense strand. | High density required for stability while avoiding Ago2 inhibition. | Allerson et al., 2005 (J Med Chem) |
| `as_pos1_bulky_rigid` | Binary flag for LNA/MOE at antisense position 1. | LNA at AS pos 1 abolishes RNAi activity (fatal rigidity). | Elmén et al., 2005 (PMC546170) |
| `as_pos1_2F` | Binary flag for $2'$-F at antisense position 1. | Evaluates compatibility with Ago2 MID domain binding. | Schirle & MacRae, 2012 (Science) |
| `as_pos1_2OMe` | Binary flag for $2'$-OMe at antisense position 1. | Evaluates exonuclease protection at guide $5'$ terminus. | Hoerter & Walter, 2007 (RNA) |
| `as_pos1_5p_phosphate_mimic` | Flag for $5'\text{-P}$, $5'\text{-VP}$, or phosphate mimic at AS pos 1. | Mandatory anchor required for Ago2 MID pocket recognition. | Parmar et al., 2016 (ChemBioChem) |
| `as_5p_terminal_PS_frac` | Fraction of PS linkages at AS positions 1–2. | Critical clinical protection against $5'\to 3'$ exonucleases. | Sakamuri et al., 2020 (ChemBioChem) |
| `as_3p_terminal_PS_frac` | Fraction of PS linkages at AS positions 20–21. | Critical clinical protection against $3'\to 5'$ exonucleases. | Behlke, 2008 (Oligonucleotides) |
| `as_internal_PS_frac` | Fraction of PS linkages in AS central body (pos 3–19). | Dense internal PS impairs RISC loading and causes cytotoxicity. | Sakamuri et al., 2020 (ChemBioChem) |
| `ss_5p_terminal_PS_frac` | Fraction of PS linkages at SS positions 1–2. | Nuclease shield at sense $5'$ terminus. | Sakamuri et al., 2020 (ChemBioChem) |
| `ss_3p_terminal_PS_frac` | Fraction of PS linkages at SS positions 20–21. | Nuclease shield at sense $3'$ terminus. | Sakamuri et al., 2020 (ChemBioChem) |
| `sense_has_conjugate` | Binary flag for targeting conjugate on sense strand. | Required for targeted in vivo delivery (e.g. GalNAc, lipid). | Nair et al., 2014 (JACS) |
| `antisense_has_conjugate_FATAL_FLAG` | Flag for targeting conjugate on antisense strand. | Bulky conjugate on guide strand physically blocks RISC entry (fatal).| Weingaertner et al., 2020 |
| `sense_3p_galnac` | Flag for trivalent GalNAc at canonical sense $3'$ end. | Golden standard for targeted clinical liver delivery. | Nair et al., 2014 (JACS) |
| `sense_gc` | GC fraction of sense strand. | Governs duplex thermal stability ($T_m$). | Reynolds et al., 2004 (Nat Biotech) |
| `antisense_gc` | GC fraction of antisense strand. | Governs target binding kinetics. | Reynolds et al., 2004 (Nat Biotech) |
| `gc_asymmetry` | Absolute difference $|\text{GC}_{\text{ss}} - \text{GC}_{\text{as}}|$. | Thermodynamic imbalance indicator. | Khvorova et al., 2003 (Cell) |
| `as_5p_weak_end_AU` | Binary flag for A or U at antisense position 1. | Fosters preferential RISC loading of guide strand. | Khvorova / Schwarz, 2003 (Cell) |
| `ss_5p_strong_end_GC` | Binary flag for G or C at sense position 1. | Fosters rapid passenger strand unwinding. | Khvorova / Schwarz, 2003 (Cell) |
| `as_3p_gc_clamp` | GC fraction of antisense terminal dinucleotide. | Enforces thermodynamic stability clamp at guide $3'$ end. | Reynolds et al., 2004 (Nat Biotech) |
| `sense_len_norm` | Sense length divided by 27. | Normalizes length variation (19-mer, 21-mer, 23-mer). | `features_v2.py:145` |
| `anti_len_norm` | Antisense length divided by 27. | Normalizes guide length variation across designs. | `features_v2.py:146` |

---

### 4. Evolutionary Foundation Model Embeddings (64 Dimensions)

- **Source:** Pre-trained RNA-FM transformer (12 layers, 100M parameters, pre-trained on 23 million non-coding RNA sequences).
- **Extraction:** Generates 640-D representations for sense and antisense sequences.
- **Dimensionality Reduction:** Pre-fitted Principal Component Analysis (`rnafm_pca_32.pkl`) projects each sequence into 32 orthogonal components capturing $> 95\%$ of contextual sequence variance:
  $$\mathbf{z}_{\text{FM}} = [\text{PCA}_{32}(\text{RNA-FM}(\text{sense})), \, \text{PCA}_{32}(\text{RNA-FM}(\text{antisense}))] \in \mathbb{R}^{64}.$$

---

### 5. ViennaRNA Biophysical Thermodynamics (5 Dimensions)

Computed via ViennaRNA Package 2.6 (`smepred/src/features_v4.py:164-240`) with deterministic Turner fallback:
1. `mfe_s_norm`: Minimum free energy of sense folding normalized by $-50.0\text{ kcal/mol}$.
2. `mfe_a_norm`: Minimum free energy of antisense folding normalized by $-50.0\text{ kcal/mol}$.
3. `duplex_dG_norm`: Intermolecular duplex binding free energy normalized by $-70.0\text{ kcal/mol}$.
4. `ensemble_diversity`: Mean base-pair distance derived from partition function $Q$ normalized by $21.0$.
5. `duplex_gc_ratio`: Aggregate GC ratio across duplex base pairs.

---

### 6. Dynamic Exposure & Context Covariates (4 Dimensions)

Conditioned directly into CatBoost tree splits (`smepred/src/features_v4.py:257-268`):
1. `log_c`: $\log_{10}(\max(10^{-4}, \text{conc\_nM}))$.
2. `log_c_rel`: $\log_{10}(\text{conc\_nM}) - 1.0$ (Relative to standard 10 nM clinical screen).
3. `t_norm`: Assay duration normalized by standard 24 hours ($\text{time\_h} / 24.0$).
4. `is_hepatic`: Binary cellular lineage indicator ($1.0$ for hepatocyte models, $0.0$ otherwise).
