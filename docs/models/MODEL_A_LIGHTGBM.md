# MODEL A: NAKED SEQUENCE SELECTOR (LIGHTGBM GBDT)
## Upstream mRNA Transcript Scanner & Thermodynamic Asymmetry Scorer
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  
**Checkpoint Path:** `smepred/models/model_normal.txt` (`.pkl`)  
**Context Checkpoint:** `smepred/models/model_normal_context.txt`  

---

### 1. Model Profile & Architecture

- **Model Identifier:** Model A (Naked Baseline & Context Scanner)
- **Primary Function:** High-speed scanning of mRNA transcripts to identify top potent unmodified 21-mer siRNA candidates.
- **Algorithm:** LightGBM Gradient Boosted Decision Tree (GBDT)
- **Tree Configuration:** Asymmetric leaf-wise growth, 31 leaves, max depth 6, min data per leaf 20.
- **Objective Loss:** Huber regression ($\alpha = 0.9$):
  $$\mathcal{L}_{\text{Huber}}(y, \hat{y}) = \begin{cases} \frac{1}{2}(y - \hat{y})^2 & \text{if } |y - \hat{y}| \le \alpha \\ \alpha |y - \hat{y}| - \frac{1}{2}\alpha^2 & \text{otherwise} \end{cases}$$
- **Learning Schedule:** Learning rate $\eta = 0.03$, feature fraction 0.8.
- **Calibration:** Out-of-fold Isotonic Regression mapping margins to $[0.0, 100.0]\%$.

---

### 2. Feature Space (214 Dimensions)

Extracted via `smepred/src/features.py:extract_batch_v4()`:
1. **Positional Nucleotide One-Hot:** $21 \times 4 = 84$ features (A, C, G, U frequencies per position).
2. **Dinucleotide Frequencies:** 16 nearest-neighbor dinucleotide counts.
3. **Reynolds Rule Compliance Matrix:** 8 rational design criteria from Reynolds et al. (2004).
4. **Ui-Tei Criteria:** Thermodynamic asymmetry and base preferences from Ui-Tei et al. (2004).
5. **Thermodynamic Asymmetry:** Terminal duplex stability difference $\Delta\Delta G^\circ_{37} = \Delta G_{3p} - \Delta G_{5p}$.
6. **Local GC% Content:** Overall GC%, seed GC%, and terminal GC clamp.

---

### 3. Empirical Benchmarks

From `final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md`:

| Benchmark Task | Sample Count ($N$) | Pearson $r$ | Spearman $\rho$ | ROC-AUC | MAE (%) | RMSE (%) | $R^2$ Score |
| :--- | ---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Takayuki Screen (`Taka.csv`)** | 702 | **0.8788** | **0.8734** | 0.9275 | 9.64% | 12.39% | 0.6525 |
| **Mixset 7-Studies (`Mix.csv`)** | 472 | **0.8291** | **0.8093** | 0.9456 | 17.35% | 20.32% | 0.4605 |
| **Huesken Held-Out (`Hu.csv`)** | 2,361 | **0.8044** | **0.8065** | 0.9099 | 6.99% | 9.18% | 0.6252 |
| **Negative Control (CMsiRNAdb)** | 2,576 | **0.1771** | **0.1645** | 0.5711 | 24.70% | 29.59% | -0.0901 |

---

### 4. The Chemical Blindness Proof

Evaluating Model A as a negative control on chemically modified siRNAs ($N = 2,576$) results in a catastrophic performance collapse to $r = 0.1771$ ($R^2 = -0.0901$). This confirms that sequence alone explains less than 3% of efficacy variance in modified oligos, proving that chemistry-aware modeling is biologically mandatory.
