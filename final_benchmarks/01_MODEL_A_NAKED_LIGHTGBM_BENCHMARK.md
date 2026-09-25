# Model A: Naked Baseline LightGBM GBDT Efficacy Predictor
## Empirical Verification & Benchmark Audit Report
**Checkpoint:** `smepred/models/lgb_model_normal.txt`  
**Training Source:** Novartis High-Throughput Screen (`normal_siRNA.csv`, N=4,310 siRNAs)  
**Algorithm:** Gradient Boosted Decision Tree (LightGBM)

---

### Verified Empirical Performance

| Benchmark Dataset | Sample Count (N) | Pearson r | Spearman ρ | ROC-AUC (≥70%) | MAE (%) | RMSE (%) | R² Score |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Takayuki Screen (Taka.csv)** | 702 | **0.8788** | **0.8734** | 0.9275 | 9.64% | 12.39% | 0.6525 |
| **Mixset 7-Studies (Mix.csv)** | 472 | **0.8291** | **0.8093** | 0.9456 | 17.35% | 20.32% | 0.4605 |
| **Huesken Held-Out (Hu.csv)** | 2,361 | **0.8044** | **0.8065** | 0.9099 | 6.99% | 9.18% | 0.6252 |
| **Negative Control (Model A on Modified Data)** | 2,576 | **0.1771** | **0.1645** | 0.5711 | 24.70% | 29.59% | -0.0901 |

---

### Architectural Design & Feature Representation
Model A processes naked, unmodified 21-mer siRNA duplexes. Its feature space captures:
1. **Thermodynamic Asymmetry ($\Delta\Delta G$):** Difference in free energy between the 5'-end of the antisense strand and 5'-end of the sense strand (Schwarz & Zamore rule).
2. **Positional Base Biases (Reynolds & Ui-Tei Heuristics):**
   - A/U enrichment at position 1 and positions 2–8 (seed region) of the antisense strand.
   - G/C enrichment at position 19 of the antisense strand.
   - Low overall GC content (30%–52%) to prevent duplex hyper-stability.
3. **Internal Motifs:** Exclusion of contiguous runs of 4+ Gs or Cs (G-quadruplex formation) and immunostimulatory motifs (5'-UGU-3').

### Critical Scientific Finding: Chemistry Blindness
When evaluated on chemically modified siRNAs (CMsiRNAdb Heterogeneous), Model A's Pearson correlation plunges to **0.1771**.
- This proves empirically that **naked sequence models cannot predict chemically modified oligonucleotides**.
- A naked sequence that scores 68.97% in Model A indicates excellent baseline sequence design, but its cellular efficacy will drop drastically (e.g. to 22.31% at 10 nM) if naked RNA is exposed to serum nucleases without stabilizing chemical modifications.
