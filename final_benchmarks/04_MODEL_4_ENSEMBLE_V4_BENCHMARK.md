# Model 4: Calibrated Hybrid Ensemble v4
## Empirical Verification Report: Machine Learning + Biophysical Guardrails
**Components:** Model B v4 CatBoost + MEG-mod GNN + 7 Biophysical Penalty Engines  
**Modules Active:** `smepred/src/biophysics.py`, `smepred/src/calibrator.py`

---

### Verified Empirical Performance

| Benchmark Dataset | Sample Count (N) | Pearson r | Spearman ρ | ROC-AUC (≥70%) | MAE (%) | RMSE (%) | R² Score |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **CMsiRNAdb Homogeneous Test Set** | 472 | **0.7335** | **0.7469** | 0.8687 | 20.09% | 23.76% | 0.2646 |
| **CMsiRNAdb Heterogeneous Test Set** | 2,576 | **0.6176** | **0.6018** | 0.8059 | 19.31% | 23.16% | 0.3327 |

---

### The 7 Biophysical Penalty Engines
The hybrid ensemble enforces physical biological realities that purely statistical models overlook:
1. **Nuclease Penalty:** Penalizes designs with unprotected pyrimidines (U/C) in endonuclease cleavage hotspots.
2. **Immuno Penalty:** Penalizes sequences containing Toll-like receptor (TLR7/8) activation motifs unless shielded by 2'-OMe.
3. **RISC Cleavage Penalty:** Enforces that positions 10–11 of the antisense strand remain cleavage-competent (avoids bulky modifications like LNA at the scissile phosphate).
4. **Thermodynamic Asymmetry Penalty:** Penalizes designs where the passenger strand 5'-end is looser than the guide strand 5'-end.
5. **Serum Stability Penalty:** Rewards terminal phosphorothioate (PS) dinucleotide caps against 3'-exonucleases.
6. **Synthesis Complexity Penalty:** Penalizes excessive clustering of sterically hindered nucleotides that reduce solid-phase synthesis yield.
7. **Exotic Chemistry Stacking Penalty:** Penalizes unvalidated combinations of experimental modifications.
