# Model B v4: Positional-Aware CatBoost Chemical Engine
## Empirical Verification & Benchmark Audit Report
**Checkpoint:** `smepred/models/model_b_v4.cbm`  
**Training Source:** CMsiRNAdb & Cleaned Multi-Patent Clinical Database (N=42,638 entries)  
**Algorithm:** Symmetric Oblivious Decision Trees (CatBoost v4 GBDT)

---

### Verified Empirical Performance

| Benchmark Dataset | Sample Count (N) | Pearson r | Spearman ρ | ROC-AUC (≥70%) | MAE (%) | RMSE (%) | R² Score |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **CMsiRNAdb Homogeneous Held-Out** | 472 | **0.7401** | **0.7540** | 0.8745 | 18.05% | 21.48% | 0.3989 |
| **CMsiRNAdb Heterogeneous Held-Out** | 2,576 | **0.6217** | **0.6049** | 0.8077 | 18.95% | 22.74% | 0.3563 |

---

### Key Capabilities in Production
1. **20-bit NucSlot Chemical Schema:** Encodes base identity (A, C, G, U), 2'-ribose modification (2'-OMe, 2'-F, 2'-MOE, LNA, DNA, UNA, GNA, TNA), and backbone linkage (phosphodiester vs phosphorothioate) at every nucleotide position independently.
2. **Sub-25ms Inference Speed:** Enables exhaustive single-modification scanning across all 1,260 positions and multi-step beam search optimization.
3. **High Correlation on Homogeneous cm-siRNAs (0.7401):** Accurately ranks the impact of uniform 2'-ribose substitutions along the guide and passenger strands.
