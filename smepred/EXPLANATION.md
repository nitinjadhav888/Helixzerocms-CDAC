# HelixZero-CMS: End-to-End Computational siRNA Engineering Platform
## Production Architecture, Feature Schemas, and Verification

---

## 1. Unified End-to-End Workflow Architecture

```
User Input (Target mRNA Sequence, Gene Symbol, or Pre-designed siRNA Duplex)
     │
     ▼
Dual-Track Parsing Pipeline
  ├─ Track A: Unmodified Candidate Generator (parser.py & sirna_generator.py)
  │    └─ 214-d Naked Sequence Features → Model A LightGBM (Pearson r = 0.804 - 0.879)
  │    └─ Curated Lead Selection (ORF Partitioning: 5' UTR, CDS, 3' UTR, Spatial Non-Redundancy)
  │
  └─ Track B: Clinical Chemical Modification Engine (chem_schema.py & modification_engine.py)
       └─ Multi-Slot NucSlot Representation (Independent 2'-Sugar + Internucleotide PS + 5'-Cap + 3'-Conjugate)
     │
     ▼
517-Dimensional Multi-Modal Feature Extractor (features_v4.py)
  ├─ 444-d Multi-Slot Chemical Category Matrix (features_v2.py)
  ├─ 64-d PCA-32 RNA-FM Foundation Embeddings (640-d raw via rna_fm_t12)
  ├─ 5-d ViennaRNA Thermodynamics (Duplex dG, Sense/Anti MFE, GC%, Ensemble Diversity)
  └─ 4-d Dose & Lineage Covariates (log10(conc_nM), Relative Dose, Assay Time, Hepatic Lineage)
     │
     ▼
Single Unified Dose-Aware & Cell-Aware CatBoost Regressor (unified_dose_catboost.cbm)
  ├─ Evaluates complete 5-log dose range (0.001 nM - 100 nM) in <0.5 ms
  ├─ Directly predicts biological % mRNA knockdown
  └─ Derives intrinsic affinity parameters (IC50 in nM, pIC50)
     │
     ▼
6-Domain Biophysical Constraint & Guardrail Penalty Engine (biophysics.py)
  ├─ 1. Nuclease Degradation Resistance (PS terminal protection, 2'-mod density)
  ├─ 2. Toll-Like Receptor (TLR7/8) Immunogenicity Avoidance (unmodified U-motifs)
  ├─ 3. RISC Ago2 Loading Asymmetry & Seed Rigidity (5'-VP anchor, 2'-F pyrimidines)
  ├─ 4. Thermal Stability & Duplex Hybridization MFE
  ├─ 5. Serum Half-Life & Plasma Clearance (GalNAc clustering)
  └─ 6. Chemical Synthesis Complexity & Yield Burden
     │
     ▼
Calibrated % Knockdown, pIC50, IC50 (nM), and 3D PDB Double-Helix Structure (pdb_generator.py)
```

---

## 2. The 517-Dimensional Feature Pipeline (`features_v4.py`)

HelixZero extracts a high-signal **517-dimensional numerical feature space** grounded in published chemical biology:

| Feature Sub-Vector | Dimensions | Primary Biophysical Source & Description |
|:---|:---:|:---|
| **Positional Chemical Ontology Flags** | **420** | 10 flags per position ($8\text{ sugar groups} + 1\text{ PS linkage} + 1\text{ base mod}$) $\times 21\text{ slots} \times 2\text{ strands}$. |
| **Engineered Biophysical Features** | **24** | Seed rigidity (*Bramsen et al. 2009*), 2'-mod density (*Allerson et al. 2005*), 5'-VP phosphate mimic status (*Parmar et al. 2016*), terminal PS protection (*Behlke 2008*), GalNAc conjugate identity (*Nair et al. 2014*), 5'-asymmetry (*Khvorova 2003*). |
| **RNA-FM PCA Embeddings** | **64** | PCA-reduced 32-d sense + 32-d antisense vectors from the 640-d RNA-FM foundation model (`rna_fm_t12`). |
| **ViennaRNA Thermodynamics** | **5** | $\Delta G_{\text{duplex}}$, $\text{MFE}_{\text{sense}}$, $\text{MFE}_{\text{anti}}$, $\text{GC\%}$, ensemble diversity computed via Turner/Xia thermodynamic nearest-neighbor models. |
| **Dose & Lineage Covariates** | **4** | $\log_{10}(\text{conc\_nM})$, relative concentration $(\log_{10}(\text{conc\_nM}) - 1.0)$, normalized assay time $(\text{time\_h} / 24.0)$, and binary hepatic lineage indicator ($\text{is\_hepatic}$). |
| **Total Feature Vector Dimension** | **517** | **Complete unified multi-modal feature vector fed to CatBoost.** |

---

## 3. Production Model Architecture

### Single Unified Dose-Aware CatBoost Regressor (`unified_dose_catboost.cbm` / `model_b_v4.cbm`)
- **Algorithm**: Symmetric Oblivious Decision Trees (CatBoost) trained on $N = 17,761$ clean, non-null dose rows from `cmsirnadb_full.csv`.
- **Latency**: Under 0.5 ms per candidate; evaluates 1,260 chemical variants in < 0.1s.
- **Dose Conditioning**: Continuous concentration response covering 0.001 nM to 100 nM with zero compounding multi-stage error.
- **Potency Derivation**: Intrinsic $IC_{50}$ and $pIC_{50}$ are directly calculated from the concentration-dependent knockdown output:
  $$IC_{50} = \text{conc\_nM} \times \frac{100 - KD\%}{KD\%}, \quad pIC_{50} = 9.0 - \log_{10}(\max(10^{-4}, IC_{50}))$$

---

## 4. Master Datasets & Empirical Performance

### Empirical Validation Performance (Zero-Sequence-Leakage GroupKFold CV)

| Model Architecture | Evaluation Set | Sample Count ($N$) | Pearson ($r$) | Spearman ($\rho$) | MAE (% Knockdown) | RMSE (% Knockdown) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Model A (Naked LightGBM)** | Takayuki Screen | 702 | **0.8788** | **0.8734** | 9.64% | 12.39% |
| **Model A (Naked LightGBM)** | Huesken Screen | 2,361 | **0.8044** | **0.8065** | 6.99% | 9.18% |
| **Unified Dose-Aware CatBoost** | 5-Fold GroupKFold CV | 17,761 | **0.6776** | **0.6752** | 17.19% | 21.57% |
| **Unified Dose-Aware CatBoost** | Homogeneous Multi-Dose (`homo_val.csv`) | 472 | **0.8359** | **0.8558** | 12.90% | 17.02% |
| **Unified Dose-Aware CatBoost** | Heterogeneous Multi-Dose (`hetero_val_303.csv`) | 1,796 | **0.8334** | **0.8383** | 13.20% | 17.44% |
| **Unified Dose-Aware CatBoost** | FDA Commercial Drugs Holdout (10 nM) | 6 | — *(N=6 Clinical Case Study)* | — | 18.82% *(vs trial mid)* | — |

---

## 5. Summary of Core File Dependencies

- **Authoritative Benchmark Directory**: [final_benchmarks/](file:///d:/Helixx/final_benchmarks/)
- **Unified CatBoost Checkpoint**: [unified_dose_catboost.cbm](file:///d:/Helixx/smepred/models/unified_dose_catboost.cbm)
- **Serving Wrapper**: [model_b_v4.py](file:///d:/Helixx/smepred/src/model_b_v4.py)
- **Inference Orchestrator**: [predictor.py](file:///d:/Helixx/smepred/src/predictor.py)
- **517-D Feature Extractor**: [features_v4.py](file:///d:/Helixx/smepred/src/features_v4.py)
- **Chemical Schema & Slots**: [chem_schema.py](file:///d:/Helixx/smepred/src/chem_schema.py)
- **Biophysical Constraint Engine**: [biophysics.py](file:///d:/Helixx/smepred/src/biophysics.py)
- **3D PDB Structure Generator**: [pdb_generator.py](file:///d:/Helixx/smepred/src/pdb_generator.py)
