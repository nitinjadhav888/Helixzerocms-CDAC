# 06. DATASET CATALOG & SPECIFICATIONS
## Authoritative Inventory of Curated Datasets and Feature Stores
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  
**Cross-Reference Audit:** `datasets_audit.md`  

---

### 1. Canonical Naked siRNA Datasets

Used for training and benchmarking Model A (Naked Transcript Scanner):

| Dataset Name | File Path | Records ($N$) | Target Output | Source Reference | Role & Context |
| :--- | :--- | ---: | :--- | :--- | :--- |
| **Takayuki Screen** | `smepred/data/oligoformer/Taka.csv` | 702 | Biological Knockdown % | Takayuki et al., 2008 | Dual-luciferase reporter screens across 70 genes under uniform assay conditions. |
| **Mixset 7-Studies** | `smepred/data/oligoformer/Mix.csv` | 472 | Biological Knockdown % | Aggregated multi-lab screens | Cross-laboratory benchmark evaluating generalizability across distinct protocols. |
| **Huesken Gold-Standard** | `smepred/data/oligoformer/Hu.csv` | 2,361 | Quantitative mRNA KD % | Huesken et al., 2005 (Novartis) | High-throughput qPCR screen across 34 human transcripts. |
| **Normal siRNA Baseline** | `smepred/data/raw/normal_siRNA.csv` | 661 | Relative Potency Margin | Curated literature screen | Baseline training screen for early LightGBM prototypes. |
| **Extended Normal siRNA** | `smepred/data/raw/normal_siRNA_extended.csv` | 4,060 | Relative Potency Margin | Curated public repositories | Extended training set for Model A baseline models. |

---

### 2. Chemically Modified siRNA Datasets

Used for training and validating the Unified Dose-Aware CatBoost Potency Engine:

| Dataset Name | File Path | Records ($N$) | Input Dim | Target Output | Source Reference |
| :--- | :--- | ---: | :---: | :--- | :--- |
| **CMsiRNAdb Clean Features Matrix** | `smepred/data/processed/cmsirnadb_clean_features_X_517.npy` | 17,761 | 517 | Continuous KD % | CMsiRNAdb (PMC12870949) / Davis et al., 2025 |
| **CMsiRNAdb Clean Targets** | `smepred/data/processed/cmsirnadb_clean_targets_Y.npy` | 17,761 | 1 | Observed Knockdown % | Derived from standardized assays |
| **CMsiRNAdb Clean Metadata** | `smepred/data/processed/cmsirnadb_clean_meta.csv` | 17,761 | 10 | Target Gene, Dose, Time | Metadata tracking for zero-leakage GroupKFold |
| **CMsiRNAdb Full Archive** | `smepred/data/processed/cmsirnadb_full.csv` | 25,863 | — | Raw Assay Knockdown % | Raw consolidated CMsiRNAdb table |
| **Multi-Slot Chemical Feature Store** | `smepred/data/processed/v2_multislot_dataset.csv` | 42,638 | 444 | Continuous KD % | Internal multi-slot chemical parser pipeline |
| **CMsiRNA Master TSV** | `smepred/data/processed/CMsiRNA_data_update.tsv` | 43,153 | — | Raw Chemical Readouts | Expanded public release of CMsiRNAdb |

---

### 3. Held-Out Multi-Dose Validation Partitions

Used for rigorous evaluation of concentration titration curves without sequence overlap:

| Dataset Name | File Path | Records ($N$) | Dose Range | Source Reference | Benchmark Role |
| :--- | :--- | ---: | :--- | :--- | :--- |
| **Homogeneous Multi-Dose Held-Out** | `smepred/data/processed/homo_val.csv` | 472 | 0.01 nM – 100 nM | Davis et al., 2025 | Standardized robotic transfection screens with zero sequence overlap ($r = 0.8359$). |
| **Heterogeneous Multi-Dose Held-Out** | `smepred/data/processed/hetero_val_303.csv` | 1,796 | 0.001 nM – 10,000 nM | Multi-lab screens | Heterogeneous assay screens evaluated across diverse cell lines ($r = 0.8334$). |
| **Homogeneous Train Split** | `smepred/data/processed/homo_train.csv` | 4,244 | 0.01 nM – 100 nM | Davis et al., 2025 | Training split for homogeneous experiments. |
| **Heterogeneous Train Split** | `smepred/data/processed/hetero_train_2728.csv` | 23,187 | 0.001 nM – 10,000 nM | Multi-lab screens | Training split for heterogeneous experiments. |

---

### 4. Safety & Transcriptome Datasets

| Dataset Name | File Path | Records / Size | Purpose |
| :--- | :--- | ---: | :--- |
| **Human Transcriptome 2-Bit Index** | `smepred/data/human_transcriptome.idx.pkl` | 863.8 MB (94M 15-mers) | Real-time whole-transcriptome off-target slicing and seed frequency query engine. |
| **Human Transcriptome Raw cDNA FASTA** | `smepred/data/human_transcriptome.fasta` | 449.5 MB | NCBI RefSeq GRCh38 / Ensembl cDNA source file. |
| **HeLa Cell Viability Seed Screen** | `smepred/data/oligoformer/cell_viability.tsv` | 4,096 hexamers | High-throughput empirical seed cytotoxicity table from Janas et al. (Nat Commun 2018). |
