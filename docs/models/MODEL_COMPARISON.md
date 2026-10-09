# MODEL COMPARISON & CROSS-ARCHITECTURE SYNTHESIS
## Comprehensive Comparative Matrix Across All Production and Historical Models
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  
**Authoritative Single Source of Truth:** `final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md`  

---

### 1. Master Cross-Model Performance Matrix

The following matrix synthesizes the empirical performance across all computational architectures evaluated in the HelixZero project:

| Evaluation Dimension | Model A (Naked LightGBM) | Unified CatBoost (Flagship) | IEEE v5 (Historical 2-Stage) | MEG-mod (Historical GNN) |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Operational Role** | Upstream Transcript Scanning | Chemical Modification Potency | Historical Potency Cascade | Graph Exploration Baseline |
| **Operational Status** | **Active Production** | **Active Production** | **Retired / Ablation** | **Retired / Ablation** |
| **Feature Dimensionality** | 214-D (or 190-D Context) | **517-D Continuous Vector** | 444-D + Hill Stage | Graph Nodes + 512-D UniMol |
| **Hardware Requirement** | CPU Only (Fast Histogram) | **CPU Only (Multi-threaded)** | CPU Only | GPU (CUDA / PyG Required) |
| **Inference Latency** | $< 0.05\text{ s}$ (3,000 sequences) | **$< 0.10\text{ s}$ (812 variants)** | $\sim 0.35\text{ s}$ | $> 12.0\text{ s}$ per duplex (CPU) |
| **Cold-Start Startup Time** | $< 0.1\text{ s}$ | **$< 0.4\text{ s}$** | $< 0.5\text{ s}$ | Up to 15 minutes |
| **Canonical Naked RNA ($r$)** | **0.8044 – 0.8788** | N/A (Designed for Chemistry)| N/A | N/A |
| **Chemically Modified RNA ($r$)**| 0.1771 (Negative Control) | **0.8359 (Held-Out)** | 0.8187 (Two-Stage) | 0.0631 (Held-Out) |
| **GroupKFold Zero-Leakage ($r$)**| N/A | **0.6776 ($N=17,761$)** | 0.6540 ($N=17,761$) | 0.0788 ($N=300$) |
| **ROC-AUC ($\ge 70\%$ Knockdown)**| 0.9099 – 0.9456 | **0.9312** | 0.9142 | 0.5210 |
| **Dose Titration Awareness** | None (Static) | **Continuous Dynamic Covariates** | Sigmoidal Fitting | None (Static) |
| **Potency Derivation** | None | **Closed-Form Analytical Hill** | Stage 1 GBDT Prediction | None |
| **FDA Commercial Drug Sensitivity**| N/A | **100% Sensitivity (65.04% Mean)**| 83.3% Sensitivity | Failed Generalization |

---

### 2. Architectural Trade-Off Analysis

#### 2.1 Tabular GBDT vs. Graph Neural Networks
- **Finding:** In small-molecule screening, graph representations capture arbitrary molecular topology. However, in siRNA therapeutics, duplexes adhere to an invariant, highly rigid A-form double-helical scaffold (21 base pairs).
- **Engineering Outcome:** Modeling structural positions via orthogonal tabular slots ($42 \times 10 = 420$ flags) combined with gradient boosted decision trees dramatically outperforms GNNs ($r = 0.8359$ vs $r = 0.0631$), eliminates GPU memory bottlenecks, and accelerates inference by $> 100\times$.

#### 2.2 Unified Single-Stage vs. Two-Stage Cascades
- **Finding:** Splitting pharmacokinetic modeling into $pIC_{50}$ prediction followed by assay curve fitting introduces compounding variance propagation ($\text{Var}(\text{Total}) = \text{Var}_1 + \text{Var}_2$).
- **Engineering Outcome:** A single unified CatBoost regressor conditioned directly on continuous $\log_{10}(\text{Dose\_nM})$ learns the joint multi-modal response surface in a single optimization step, yielding higher correlation ($r = 0.8359$ vs $0.8187$) and lower RMSE ($17.02\%$ vs $18.25\%$).
