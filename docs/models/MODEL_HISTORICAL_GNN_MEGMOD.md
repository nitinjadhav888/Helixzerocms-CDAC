# HISTORICAL MODEL: MEG-MOD GRAPH NEURAL NETWORK
## PyG TransformerConv Exploration, Graph Attention, and Deprecation Audit
**Status:** `VERIFIED — HISTORICAL / ABLATION ARCHIVE`  
**Archive Location:** `MEG-mod-main/`  
**Checkpoint Path:** `MEG-mod-main/finetuned_v2.pt` (268 MB)  

---

### 1. Model Profile & Architecture

- **Model Identifier:** MEG-mod GNN Baseline (`GNN_v2`)
- **Exploratory Objective:** Evaluate graph neural network representation of nucleic acid secondary structure base-pairing and Uni-Mol 3D molecular conformations.
- **Neural Architecture:** Bi-directional Attention Network (BAN) with PyTorch Geometric `TransformerConv` graph layers across 4 attention heads.
- **Node Inputs:**
  - Uni-Mol 1B 3D conformation embeddings (512-D per chemical modification).
  - ViennaRNA `RNAcofold` base-pairing probabilities ($N = 49,715$ pre-computed duplexes in `data_pre/cofold_results.pkl`).
  - RNA-Ernie sequence embeddings (fallback to zero tensor in `smepred/src/gnn_serving.py`).

---

### 2. Empirical Benchmark & Generalization Failure

Evaluated against held-out test partitions:

| Benchmark Task | Sample Count ($N$) | Pearson $r$ | Spearman $\rho$ | MAE (%) | Failure Mode |
| :--- | ---: | :---: | :---: | :---: | :--- |
| **In-Distribution Training Split** | 23,187 | 0.8124 | 0.8015 | 11.20% | High training capacity |
| **Held-Out Generalization Set** | 300 | **0.0631** | **0.0788** | 35.95% | Catastrophic Generalization Collapse |

---

### 3. Engineering Justification for Retirement

The MEG-mod GNN architecture was retired from the production inference pipeline due to four critical bottlenecks:
1. **Severe Out-of-Distribution Generalization Failure:** While the model achieved high training fit on seen duplexes, performance collapsed to near-zero ($r = 0.0631$) on novel sequences, proving that the dense graph attention heads over-fit dataset-specific topology.
2. **Excessive Cold-Start Latency:** Loading the 268 MB PyTorch checkpoint and initializing PyTorch Geometric graph dispatchers required up to 15 minutes on memory-constrained systems.
3. **GPU Dependency & CUDA OOM Spikes:** The graph attention network required GPU acceleration. On CPU, inference took $> 12$ seconds per candidate, rendering 812-permutation scanning completely unviable.
4. **Lack of Native Dose Conditioning:** The graph architecture lacked continuous concentration conditioning, requiring awkward two-stage normalization.

*Preservation Notice:* The codebase is retained in `MEG-mod-main/` solely to support ablation studies for peer review.
