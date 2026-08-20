# HelixZero-CMS — Full Technical Architecture & Parameter Specification (Release 5.3.0)

> **Official Technical Specification Document**  
> **Platform**: HelixZero-CMS (Centre for Development of Advanced Computing, C-DAC, Pune)  
> **Release Version**: 5.3.0 (IEEE v5 + CatBoost GBDT + PyTorch GNN Production Stack)  

---

## 1. Efficacy Score & Potency Prediction Engine

### What It Is
The **Efficacy Score** ($0\text{–}100\%$) represents the predicted **% target-gene mRNA knockdown (silencing)** for a chemically modified siRNA candidate at a given assay concentration (default 10 nM). A score of $85.0$ indicates that the model predicts an $85\%$ reduction in target mRNA expression relative to an untreated negative control.

In addition to percentage knockdown, the platform computes the **Intrinsic Chemical Affinity ($pIC_{50}$)**:
$$pIC_{50} = -\log_{10}(IC_{50} \text{ in M})$$
where $IC_{50}$ is the half-maximal inhibitory concentration in nanomolar (nM).

---

### End-to-End Prediction Pipeline

```
Target mRNA Sequence / FASTA Input
    │
    ▼
21-mer siRNA Candidate Generation (Sliding Window Engine)
    │
    ▼
Canonical Chemical Ontology Parsing (chem_schema.NucSlot)
  → Sugar conformation (2'-F, 2'-OMe, LNA, MOE, ENA, UNA, FANA, DNA)
  → Base modification (5-mC, Pseudouridine, Inosine, 2-thioU)
  → 3'-Internucleotide linkage (Phosphodiester PO vs. Phosphorothioate PS)
  → 5'-Terminal cap / Phosphate mimics (5'-VP, 5'-P)
  → Conjugate identity (GalNAc, PEG, Cholesterol)
    │
    ▼
577-Dimensional Multi-Modal Feature Extractor (features_v4.py)
  ├─ 444-d Multi-Slot Chemical Category Matrix (features_v2.py)
  ├─ 64-d PCA-32 RNA-FM Foundation Embeddings (640-d raw)
  ├─ 64-d PCA-32 RNA-Ernie Foundation Embeddings (768-d raw)
  └─ 5-d ViennaRNA Thermodynamics (Duplex dG, Sense/Anti MFE, GC%, Seed dG)
    │
    ▼
Hierarchical Dual-Engine Inference Pipeline
  ├─ Stage 1: Intrinsic Potency Engine (module2_potency_pIC50.cbm → pIC50)
  ├─ Stage 2: Dose-Aware Response Engine (module3_assay_response.cbm → % Knockdown)
  └─ Stage 3: PyTorch MEG-mod GNN Engine (finetuned_v2.pt → Structural Graph Efficacy)
    │
    ▼
Hybrid Production Ensemble V4 (85% GBDT + 15% GNN)
    │
    ▼
6-Domain Biophysical Constraint & Off-Target Penalty Engine
  ├─ 1. Nuclease Degradation Resistance
  ├─ 2. Toll-Like Receptor (TLR7/8) Immunogenicity Avoidance
  ├─ 3. RISC Ago2 Loading Asymmetry & Seed Rigidity
  ├─ 4. Thermal Stability & Internal Ribosome Entry
  ├─ 5. Serum Half-Life & Plasma Clearance
  └─ 6. Chemical Synthesis Complexity & Yield Burden
    │
    ▼
Calibrated % Knockdown, pIC50, IC50 (nM), and Optimized siRNA Ranking
```

---

## 2. The 577-Dimensional Multi-Modal Feature Pipeline (`features_v4.py`)

Rather than viewing sequences as plain text, HelixZero extracts a dense **577-dimensional numerical feature space** grounded in published biophysical literature:

| Feature Sub-Vector | Dimensions | Primary Biophysical Source & Description |
|:---|:---:|:---|
| **Positional Chemical Ontology Flags** | **420** | 10 flags per position ($8\text{ sugar groups} + 1\text{ PS linkage} + 1\text{ base mod}$) $\times 21\text{ slots} \times 2\text{ strands}$. |
| **Engineered Biophysical Features** | **24** | Seed rigidity (*Bramsen et al. 2009*), 2'-mod density (*Allerson et al. 2005*), 5'-VP phosphate mimic status (*Parmar et al. 2016*), terminal PS protection (*Behlke 2008*), GalNAc conjugate identity (*Nair et al. 2014*), 5'-asymmetry (*Khvorova 2003*). |
| **RNA-FM PCA Embeddings** | **64** | PCA-reduced 32-d sense + 32-d antisense vectors from the 640-d RNA-FM foundation model. |
| **RNA-Ernie PCA Embeddings** | **64** | PCA-reduced 32-d sense + 32-d antisense vectors from the 768-d RNA-Ernie foundation model. |
| **ViennaRNA Thermodynamics** | **5** | $\Delta G_{\text{duplex}}$, $\text{MFE}_{\text{sense}}$, $\text{MFE}_{\text{anti}}$, $\text{GC\%}$, $\Delta G_{\text{seed}}$ computed via ViennaRNA 2.7 C-bindings. |
| **Total Feature Vector Dimension** | **577** | **Complete multi-modal input vector fed to GBDT and GNN models.** |

---

## 3. Deep Learning & Hybrid Ensemble Architecture

### 1. CatBoost GBDT Engines
- **Model B v4 (`model_b_v4.cbm`)**: Gradient boosted decision tree regressor trained on 42,638 CMsiRNAdb master rows.
- **IEEE v5 Potency Engine (`module2_potency_pIC50.cbm`)**: Predicts intrinsic $pIC_{50}$ affinity.
- **IEEE v5 Assay Response Engine (`module3_assay_response.cbm`)**: Predicts dose-aware % knockdown using $[pIC_{50}, \log_{10}(\text{dose}), X_{\text{base}}(577\text{-d})] = 579\text{-d}$ input.

### 2. PyTorch MEG-mod GNN Graph Attention Engine (`finetuned_v2.pt`)
- **Architecture**: Bimodal Graph Attention Network (BAN_graph / GATv2) with 512 hidden channels.
- **Per-Nucleotide Node Inputs**: 768-d RNA-Ernie embedding + 10-d physicochemical property vector = **778-d per node** across 54 nodes (27 sense + 27 antisense).
- **Edge Connections**: Primary backbone phosphodiester bonds + ViennaRNA `RNAcofold` base-pairing hydrogen bonds.

### 3. Production Ensemble V4
$$\text{Efficacy}_{\text{final}} = 0.85 \times \text{Efficacy}_{\text{CatBoost\_v4}} + 0.15 \times \text{Efficacy}_{\text{MEG-mod\_GNN}}$$

---

## 4. Master Training Datasets & Empirical Performance

### Primary Datasets
1. **`ieee_gold_bronze_master.csv`** ($N = 37,946$ multi-dose items): Primary multi-concentration master dataset.
2. **`v2_multislot_dataset.csv`** ($N = 42,638$ CMsiRNAdb items): Master chemical modification database.
3. **`cmsirnadb_full.csv`** ($N = 25,863$ items): Curated cmSiRNADB dataset.

---

### Empirical Validation Performance (Zero-Sequence-Leakage GroupKFold CV)

| Model Architecture | Test Pearson ($r$) | Test Spearman ($\rho$) | MAE (% Knockdown) | RMSE (% Knockdown) |
|:---|:---:|:---:|:---:|:---:|
| **Hybrid Ensemble V4 (85% GBDT / 15% GNN)** | **0.7366 ±0.058** | **0.7463 ±0.064** | **17.86 ±0.95%** | **21.11 ±0.84%** |
| **CatBoost Model B v4 (577-d)** | **0.7314 ±0.063** | **0.7379 ±0.071** | **18.05 ±0.91%** | **21.46 ±0.85%** |
| **IEEE v5 Hierarchical 2-Stage Engine** | **0.6120 ±0.051** | **0.6087 ±0.056** | **21.41 ±0.49%** | **25.32 ±0.55%** |

---

## 5. Summary of Core File Dependencies for Submission

- **System Architecture**: [HELIXZERO_COMPLETE_ECOSYSTEM_BUNDLE.md](file:///d:/Helixx/HELIXZERO_COMPLETE_ECOSYSTEM_BUNDLE.md)
- **Technical Specification**: [EXPLANATION.md](file:///d:/Helixx/smepred/EXPLANATION.md)
- **Hierarchical Predictor**: [predict_ieee_v5.py](file:///d:/Helixx/helixzero_ieee_v5/predict_ieee_v5.py)
- **Chemical Ontology**: [chem_ontology.py](file:///d:/Helixx/helixzero_ieee_v5/src/chem_ontology.py), [chem_schema.py](file:///d:/Helixx/smepred/src/chem_schema.py)
- **Feature Extractor**: [features_v4.py](file:///d:/Helixx/smepred/src/features_v4.py)
- **PyTorch GNN Serving**: [gnn_serving.py](file:///d:/Helixx/smepred/src/gnn_serving.py)
- **Master Dataset**: [ieee_gold_bronze_master.csv](file:///d:/Helixx/helixzero_ieee_v5/data/ieee_gold_bronze_master.csv)
