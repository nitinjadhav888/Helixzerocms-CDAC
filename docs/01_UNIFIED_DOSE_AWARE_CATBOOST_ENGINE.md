# HELIXZERO-CMS: UNIFIED DOSE-AWARE CATBOOST ENGINE SPECIFICATION
## The Flagship 517-Dimensional Potency Architecture & Dynamic Dose-Response Engine
**Authoritative Source Alignment:** `final_benchmarks/`  
**Classification:** Core Machine Learning Architecture & Feature Engineering Specification  
**Model Artifact:** `smepred/models/model_b_v4.cbm` (Retrained Dose-Aware CatBoost Regressor)  
**Institution:** High Performance Computing — Medical & BioInformatics Group, C-DAC, Pune

---

### 1. Executive Summary & Design Rationale

The **HelixZero Single Unified Dose-Aware CatBoost Regressor** is the core predictive machine learning engine of the HelixZero platform. It directly predicts in vitro and in vivo mRNA knockdown percentage ($0.0\%$ to $100.0\%$) for chemically modified siRNAs across continuous transfection concentrations ($0.001\,\text{nM}$ to $10,000\,\text{nM}$).

#### Why the Unified Architecture Replaced Previous Pipelines:
1. **Elimination of Compounding Variance**:
   The previous two-stage cascading architecture (predicting $pIC_{50}$ in Stage 1 and subsequently predicting knockdown via Hill regression in Stage 2) suffered from compound variance propagation:
   $$\sigma^2_{\text{total}} = \left(\frac{\partial Y}{\partial pIC_{50}}\right)^2 \sigma^2_{pIC_{50}} + \sigma^2_{\text{Hill}}$$
   In extreme dosage regimes, small errors in the initial $pIC_{50}$ estimate caused massive swings in observed knockdown predictions. By training a single gradient-boosted decision tree directly on the concatenated feature vector $[\mathbf{x}_{\text{chem}}, \mathbf{x}_{\text{FM}}, \mathbf{x}_{\text{thermo}}, \mathbf{x}_{\text{dose}}]$, the model learns the joint interaction between chemical architecture and concentration natively across its tree split nodes.
2. **Elimination of Unstable Deep Learning Components**:
   Deep Graph Neural Networks (MEG-mod PyG GATv2) proved empirically brittle during extensive cross-dataset validation:
   - On out-of-distribution multi-dose screens, MEG-mod achieved a near-zero correlation ($r = 0.0631$).
   - PyG graphs required heavy CUDA/PyTorch overhead, leading to 15-minute cold starts and GPU memory fragmentation.
   - The previously proposed 85% GBDT / 15% GNN blend degraded overall precision compared to a pure CatBoost regressor.
   Consequently, **the GNN was completely retired from the production inference path**.
3. **Preservation of Thermodynamic and Physical Interpretability**:
   Tree splits on discrete chemical modification categories preserve sharp, non-linear biological thresholds (e.g. RISC seed rigidity, cleavage site steric clearance) that neural continuous relaxations fail to resolve.

---

### 2. The 517-Dimensional Feature Vector Architecture

Every siRNA candidate is vectorized into a continuous and categorical feature space of exactly **517 dimensions**:

```
+---------------------------------------------------------------------------------------------------------+
|                                517-DIMENSIONAL MULTI-MODAL FEATURE VECTOR                               |
+-----------------------------+-----------------------------+-----------------------+---------------------+
| 444-D Positional Chemistry  | 64-D RNA Foundation Model   | 5-D ViennaRNA Duplex  | 4-D Dynamic Assay   |
| (Sense & Antisense Slots)   | (Live rna_fm_t12 Embedding) | (Thermodynamics & MFE)| Covariates (Dose)   |
| Indices: 0 – 443            | Indices: 444 – 507          | Indices: 508 – 512    | Indices: 513 – 516  |
+-----------------------------+-----------------------------+-----------------------+---------------------+
```

#### 2.1 Positional Chemistry Slots (444 Dimensions, Indices 0 – 443)
- **Strand Coverage**: 21 nucleotide positions on the passenger (sense) strand + 21 nucleotide positions on the guide (antisense) strand = 42 total nucleotide slots.
- **Slot Encoding**: Each slot is featurized into orthogonal molecular properties:
  - Canonical Base Identity (One-hot A, C, G, U).
  - 2'-Ribose Modification Class (Unmodified 2'-OH, 2'-O-methyl, 2'-Fluoro, 2'-Deoxy, LNA, MOE, 2'-F-ANA, etc.).
  - Internucleotide Linkage Chemistry (Phosphodiester `PO`, Phosphorothioate `PS`, Phosphorodithioate `PS2`).
  - Terminal Capping & Conjugates (5'-Vinylphosphonate `5'-VP`, 5'-Phosphate, 3'-GalNAc conjugate, inverted abasic caps).
- **Supported Chemical Palette**: Encodes all 30 clinically validated and emerging chemical moieties defined in [`smepred/data/modification_codes.json`](file:///d:/Helixx/smepred/data/modification_codes.json).

#### 2.2 Evolutionary Foundation Model Embeddings (64 Dimensions, Indices 444 – 507)
- **Model**: Extracted using the 12-layer 100M-parameter RNA Foundation Model (`rna_fm_t12`).
- **Input**: Concatenated duplex sequence passed through transformer self-attention blocks.
- **Latent Dimension**: 64 continuous mean-pooled representations capturing evolutionary conservation across homologous RNA transcripts, base-pairing propensities, and structural flexibility.

#### 2.3 ViennaRNA Duplex Thermodynamics (5 Dimensions, Indices 508 – 512)
Computed dynamically using ViennaRNA package algorithms at $37^\circ\text{C}$:
1. **Duplex Minimum Free Energy ($\Delta G_{\text{duplex}}$)**: Overall thermodynamic stability of the 21-mer duplex ($\text{kcal/mol}$).
2. **Ensemble Free Energy ($\Delta G_{\text{ensemble}}$)**: Boltzmann partition function free energy.
3. **Frequency of MFE Structure**: Thermodynamic probability of the minimum free energy conformer.
4. **5' Antisense Terminal End-Opening Energy**: $\Delta G^\circ_{37}$ of terminal positions 1–4 of the guide strand.
5. **5' Sense Terminal End-Opening Energy**: $\Delta G^\circ_{37}$ of terminal positions 1–4 of the passenger strand.

#### 2.4 Dynamic Assay Covariates (4 Dimensions, Indices 513 – 516)
These 4 features condition the prediction on the experimental testing environment, enabling the model to serve as a universal multi-dose predictor:
1. **Feature 513: $\log_{10}(\text{Dose\_nM})$**: Base-10 logarithm of the assay concentration (e.g. $-1.0$ for $0.1\,\text{nM}$, $1.0$ for $10.0\,\text{nM}$, $2.0$ for $100.0\,\text{nM}$). Feature importance ranking = **Top 3 feature in the entire ensemble**.
2. **Feature 514: Relative Dose Metric**: Normalized ratio of assay dose relative to screening median.
3. **Feature 515: Incubation Duration**: Transfection duration in hours (typically 24h or 48h).
4. **Feature 516: Hepatic Cell Lineage Flag**: Binary indicator for hepatic lines (HepG2, Huh7, Primary Human Hepatocytes) versus non-hepatic screens (HeLa, HEK293).

---

### 3. Training Protocol & Zero Data Leakage Guarantee

To withstand rigorous peer review (IEEE TNNLS / Nature Biotechnology standards), the model was trained under strict sequence-level segregation:

- **Total Training Dataset**: $N = 17,761$ experimentally measured, chemically modified siRNA assays across multiple concentration titrations.
- **Partitioning Algorithm**: 5-Fold `GroupKFold` grouped strictly by **unique core antisense sequence** (`anti_seq`).
  - **Unique Sequence Groups**: 5,251 independent sequence clusters.
  - **Zero Leakage**: No two folds share the same core sequence. All modification patterns, dosage titrations, and replicates of a sequence reside exclusively within a single fold.
- **Model Parameters**:
  - Objective: `RMSE`
  - Maximum Depth: 6
  - Learning Rate: 0.05
  - L2 Leaf Regularization: 3.0
  - Early Stopping: 100 iterations on validation RMSE.

---

### 4. Empirical Performance Benchmarks

All metrics are extracted strictly from [`final_benchmarks/master_benchmark_metrics.csv`](file:///d:/Helixx/final_benchmarks/master_benchmark_metrics.csv):

| Metric | 5-Fold GroupKFold CV ($N=17,761$) | Held-Out Homogeneous Multi-Dose ($N=472$) | Held-Out Heterogeneous Multi-Dose ($N=1,796$) |
| :--- | :---: | :---: | :---: |
| **Pearson Correlation ($r$)** | **0.6776** | **0.8359** | **0.8334** |
| **Spearman Rank Correlation ($\rho$)** | **0.6752** | **0.8558** | **0.8383** |
| **ROC-AUC (High Efficacy $\ge 70\%$)** | **0.8524** | **0.9312** | **0.9291** |
| **Mean Absolute Error (MAE)** | **17.19%** | **12.90%** | **13.20%** |
| **Root Mean Squared Error (RMSE)** | **21.57%** | **17.02%** | **17.44%** |
| **Coefficient of Determination ($R^2$)** | **0.4497** | **0.6231** | **0.6185** |

---

### 5. Dynamic Pharmacokinetic & Intrinsic Affinity Derivations

In clinical siRNA drug development, researchers require both concentration-dependent phenotypic efficacy (% Knockdown at dose $C$) and concentration-independent thermodynamic potency ($IC_{50}$ and $pIC_{50}$).

From the predicted knockdown percentage $\text{KD}_{\text{pred}} \in [1.0, 99.0]$ at concentration $C$ ($\text{nM}$), the engine analytically derives the Hill-equivalent parameters:

$$\text{Estimated } IC_{50} = C \times \left(\frac{100.0 - \text{KD}_{\text{pred}}}{\text{KD}_{\text{pred}}}\right)$$

$$\text{Estimated } pIC_{50} = 9.0 - \log_{10}\left(\max\left(10^{-4}, \text{Estimated } IC_{50}\right)\right)$$

This direct derivation provides continuous, physically sound $pIC_{50}$ estimates without requiring fragile numerical optimization or suffering from compounding two-stage variance.
