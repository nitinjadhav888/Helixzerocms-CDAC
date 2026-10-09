# 10. MODEL CATALOG & INVENTORY
## Complete Inventory of Production, Baseline, and Historical Models
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. Model Inventory Matrix

| Model Identifier | Architecture | Checkpoint Location | Feature Space | Operational Status | Verified Pearson $r$ |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **Model A Baseline** | LightGBM GBDT | `smepred/models/model_normal.txt` | 214-D | **Active Production** | $0.8044\text{--}0.8788$ |
| **Model A Context** | LightGBM GBDT | `smepred/models/model_normal_context.txt` | 190-D | **Active Production** | $0.8210$ (Context) |
| **Unified Dose CatBoost** | CatBoost Regressor | `smepred/models/unified_dose_catboost.cbm` | 517-D | **Active Flagship** | $0.8359$ (Held-Out) |
| **Model B v4 Legacy** | CatBoost Regressor | `smepred/models/model_b_v4.cbm` | 517-D | **Production Fallback** | $0.8334$ (Hetero) |
| **MEG-mod GNN (v2)** | PyG TransformerConv | `MEG-mod-main/finetuned_v2.pt` | Graph + UniMol | **Retired / Ablation** | $0.0631$ (Poor Gen) |
| **IEEE v5 Cascading Engine** | 2-Stage GBDT ($pIC_{50} \to \text{Hill}$) | `helixzero_ieee_v5/` | 444-D + Hill | **Retired / Ablation** | $0.8187$ (Compounded Error) |

---

### 2. Detailed Model Profiles

#### 2.1 Model A: Naked Transcript Scanner
- **Purpose:** Ingests raw mRNA transcripts and scans all candidate 21-mers to identify potent unmodified siRNA leads.
- **Inputs:** 21-nt guide strand, 21-nt passenger strand, target transcript sequence.
- **Outputs:** Predicted naked silencing efficacy $[0.0, 100.0]\%$, calibrated via isotonic regression.
- **Architecture:** Gradient Boosted Decision Tree (LightGBM) using Huber loss ($\alpha = 0.9$), 31 leaves, max depth 6.
- **Feature Space (214-D):** 42-nt sequence composition, dinucleotide frequencies, terminal thermodynamic asymmetry ($\Delta\Delta G^\circ_{37}$), Reynolds rule matrix, and Ui-Tei criteria.
- **Performance:** Pearson $r = 0.8788$ on Takayuki ($N = 702$), $r = 0.8291$ on Mixset ($N = 472$), $r = 0.8044$ on Huesken ($N = 2,361$).
- **Negative Control Blindness:** Evaluated on chemically modified CMsiRNAdb ($N = 2,576$), performance collapses to $r = 0.1771$ ($R^2 = -0.0901$).

#### 2.2 HelixZero Unified Dose-Aware CatBoost Regressor (Active Flagship)
- **Purpose:** Predicts biological knockdown of chemically modified siRNAs across any concentration titration ($0.001\text{--}10,000\text{ nM}$) and analytically derives compound potency ($pIC_{50}$).
- **Inputs:** Sense `NucSlot` list (21 nt), antisense `NucSlot` list (21 nt), assay concentration `conc_nM`, incubation time `time_h`, cell lineage `is_hepatic`.
- **Outputs:** Biological knockdown percentage $[0.0, 100.0]\%$, $\text{IC}_{50}$ (nM), $p\text{IC}_{50}$.
- **Architecture:** Symmetric oblivious decision tree gradient booster (CatBoost) trained on RMSE loss, 1,500 trees, depth 6, $L_2$ leaf regularization 3.0.
- **Feature Space (517-D):** 444 chemical descriptors, 64 RNA-FM foundation embeddings, 5 ViennaRNA parameters, 4 dose covariates.
- **Performance:** Pearson $r = 0.6776$ on 5-fold sequence `GroupKFold` ($N = 17,761$, 5,251 disjoint sequence groups), $r = 0.8359$ on homogeneous multi-dose held-out ($N = 472$), 100% sensitivity on all 6 FDA commercial therapeutics.

#### 2.3 MEG-mod GNN Baseline (Historical / Ablation)
- **Purpose:** Explored graph neural network representation of secondary structure base-pairing and Uni-Mol 3D molecular conformations.
- **Why Retired:** Produced poor out-of-distribution transfer ($r = 0.0631$), caused CUDA out-of-memory crashes, and required 15-minute cold starts due to heavy PyG model loading.

#### 2.4 IEEE v5 Cascading Engine (Historical / Ablation)
- **Purpose:** Two-stage model predicting intermediate potency $pIC_{50}$ in Module 2, followed by sigmoidal response prediction in Module 3.
- **Why Retired:** Splitting into two stages introduced compounding variance propagation ($r = 0.8187$). Training a single unified CatBoost regressor directly on continuous concentration eliminated this error and improved accuracy to $r = 0.8359$.
