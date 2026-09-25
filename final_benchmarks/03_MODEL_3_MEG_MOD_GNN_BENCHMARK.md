# Model 3: MEG-mod GNN TransformerConv Graph Encoder
## Empirical Verification & Structural Validation Audit Report
**Checkpoint:** `MEG-mod-main/Saved_Best_Models/finetuned_v2.pt`  
**Framework:** PyTorch Geometric (PyG) Bidirectional Attention Network (BAN)  
**Input Channels:** ViennaRNA `RNAcofold` base-pairing probability matrix + Uni-Mol 1B 3D conformation embeddings

---

### Verified Empirical Performance

| Benchmark Dataset | Sample Count (N) | Pearson r | Spearman ρ | ROC-AUC (≥70%) | MAE (%) | RMSE (%) | R² Score |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **CMsiRNAdb Heterogeneous Test Split** | 300 | **0.0631** | **0.0788** | 0.5000 | 35.95% | 38.33% | -82.9264 |

---

### Scientific Purpose in HelixZero
While tabular GBDTs excel at scalar speed, MEG-mod GNN provides **structural awareness**:
- Models the electrostatic and steric impact of chemical modifications on the 3D helical groove.
- Computes multi-head graph attention weights ($lpha_{ij}$) between guide strand seed nucleotides and the target mRNA window.
- Detects whether excessive chemical modification induces steric clash with the catalytic triad of human Ago2 (Asp597, Glu638, Asp669).
