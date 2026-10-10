# HELIXZERO-CMS: MODEL A (NAKED SEQUENCE SELECTOR) SPECIFICATION
## Transcriptome Tiling, Thermodynamic Asymmetry & Initial Candidate Selection
**Authoritative Source Alignment:** `final_benchmarks/`  
**Classification:** Baseline Sequence Optimization Engine  
**Model Artifact:** `smepred/models/lgb_naked_model.txt` (LightGBM Gradient Boosted Regressor)  
**Institution:** High Performance Computing — Medical & BioInformatics Group, C-DAC, Pune

---

### 1. Role in the HelixZero Pipeline

**Model A** executes **Step 1** of the HelixZero platform. When an investigator submits a full-length mRNA transcript (e.g., *PCSK9*, *TTR*, *KRAS*), Model A:
1. Tiles the target transcript using a sliding 21-nucleotide window ($19\text{-bp}$ canonical duplex core + $2\text{-nt}$ $3'\text{-terminal}$ overhangs).
2. Evaluates every candidate duplex for thermodynamic asymmetry and sequence-intrinsic efficacy.
3. Ranks and filters candidates to return the top $N$ lead unmodified sequences for subsequent chemical modification scanning by the Unified Dose-Aware CatBoost engine.

---

### 2. Theoretical Biophysics & Feature Space

Model A operates strictly on the unmodified RNA sequence, evaluating classical thermodynamic and empirical rules established in the RNAi literature:

#### 2.1 Thermodynamic Asymmetry (The Schwarz-Zamore Rule)
For catalytic RNAi to proceed, the RNA-Induced Silencing Complex (RISC) must preferentially load the antisense (guide) strand and expel the sense (passenger) strand.
- In 2003, Schwarz et al. and Khvorova et al. discovered that RISC loading directionality is governed by the relative thermodynamic stability of the two duplex termini.
- Model A calculates the 5' antisense end-opening free energy ($\Delta G_{\text{anti}, 5'}$) and the 5' sense end-opening free energy ($\Delta G_{\text{sense}, 5'}$) using nearest-neighbor enthalpy and entropy parameters (Xia et al., 1998):
  $$\Delta\Delta G_{\text{asymmetry}} = \Delta G_{\text{sense}, 5'} - \Delta G_{\text{anti}, 5'}$$
- A positive $\Delta\Delta G_{\text{asymmetry}}$ indicates that the 5' guide terminus is thermodynamically looser (lower stability), facilitating its preferential capture by the basic MID domain pocket of human Argonaute-2.

#### 2.2 Reynolds Criteria & Ui-Tei Functional Classes
Model A encodes all 8 empirical criteria established by Reynolds et al. (2004) and Ui-Tei et al. (2004):
1. **Moderate GC Content (31.6% to 52.6%)**: Enforces optimal hybridization kinetics without excessive duplex rigidity.
2. **Terminal Stability Asymmetry**: Low internal stability at the 5' antisense end (positions 1–4 $\ge -6.5\,\text{kcal/mol}$).
3. **Absence of Inverted Repeats**: Penalizes self-complementary sequences forming internal hairpins ($T_m > 20^\circ\text{C}$).
4. **Sense Position 19 Adenine**: Enforces an A-U base pair at the 5' guide terminus.
5. **Sense Position 3 Adenine**: Enforces Uracil at antisense position 17, preventing rigid G-C clamps in the seed-adjacent duplex.
6. **Sense Position 10 Uracil**: Corresponds to position 10 of the guide strand opposite the catalytic scissile bond, conferring local flexibility for catalytic divalent magnesium coordination.
7. **Sense Position 13 Non-Guanine**: Avoids steric clashes with the PIWI loop.
8. **Sense Position 19 Non-GC**: Minimizes stability at the 3' passenger terminus.

---

### 3. Empirical Benchmarks & Scientific Rigor

Model A was evaluated across the standard gold-standard unmodified siRNA datasets:

| Evaluation Dataset | Description | Sample Count ($N$) | Pearson $r$ | Spearman $\rho$ | ROC-AUC ($\ge 70\%$) | MAE (%) | RMSE (%) | $R^2$ Score |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Takayuki Screen** | Multi-gene screen | 702 | **0.8788** | **0.8734** | **0.9275** | 9.64% | 12.39% | 0.6525 |
| **Mixset 7-Studies** | Cross-study pooled benchmark | 472 | **0.8291** | **0.8093** | **0.9456** | 17.35% | 20.32% | 0.4605 |
| **Huesken Gold-Standard** | Novartis 34-gene screen | 2,361 | **0.8044** | **0.8065** | **0.9099** | 6.99% | 9.18% | 0.6252 |

---

### 4. The Negative Control Experiment: Proof of Chemistry Blindness

To scientifically establish why naked sequence models cannot design clinical therapeutics, Model A was evaluated against the heterogeneous, chemically modified **CMsiRNAdb Hetero Benchmark** ($N = 2,576$ modified assays):

| Evaluated Model | Evaluation Dataset | Pearson $r$ | Spearman $\rho$ | ROC-AUC | MAE (%) | RMSE (%) | $R^2$ Score |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Model A (Naked LightGBM)** | CMsiRNAdb Hetero (Chemistry Blind) | **0.1771** | **0.1645** | **0.5711** | 24.70% | 29.59% | **-0.0901** |
| **HelixZero Unified CatBoost** | CMsiRNAdb Hetero (Chemistry Aware) | **0.8334** | **0.8383** | **0.9291** | 13.20% | 17.44% | **0.6185** |

#### Peer-Review Conclusion:
The catastrophic failure of Model A on modified siRNAs ($r = 0.1771$, $R^2 = -0.0901$) conclusively demonstrates that:
1. **Chemical modifications fundamentally re-write the rules of oligonucleotide thermodynamics and Ago2 interactions.**
2. A sequence-only model, regardless of how deep or well-trained, is completely blind to chemical substitutions.
3. Model A serves as an essential **upstream filter** to identify functional naked sequences, which are then optimized by the **Unified Dose-Aware CatBoost Engine**.

---

### 5. Strictly Monotonic Probability Calibration & Output Clamping

Raw leaf outputs from gradient-boosted regression trees trained with Huber loss naturally compress towards the empirical sample mean (~45% to 65% knockdown). To map raw tree predictions onto physically interpretable, assay-aligned percentage knockdown distributions, Model A utilizes an explicit out-of-fold monotonic calibrator (`smepred/models/calibrator_naked.pkl`).
#### 5.1 Mathematical Calibration Formulation
- The calibration engine (`smepred/src/calibrator.py`) applies a **Strictly Monotonic Variance-Matching Transformation**:
  $$\hat{y}_{\text{calibrated}} = m \cdot x_{\text{raw}} + c$$
  where $m = 1.5165$ and $c = -25.892$ were empirically derived via out-of-fold variance expansion on validated screening benchmarks.
- Monotonicity is guaranteed ($\frac{\partial \hat{y}}{\partial x} > 0$), ensuring that sequence rank orders established by the thermodynamic feature tree ensemble are strictly preserved without rank inversion.

#### 5.2 Deterministic Boundary Clamping
- Because linear calibration of extreme high-affinity sequences ($x_{\text{raw}} > 83.0\%$) can mathematically exceed 100.0%, strict biological boundary clamping is enforced:
  $$\hat{y}_{\text{final}} = \text{np.clip}(\hat{y}_{\text{calibrated}}, 0.0, 100.0)$$
- Enforced in both the core prediction backend ([`smepred/src/predictor.py`](file:///d:/Helixx/smepred/src/predictor.py)) and UI visualization layers ([`smepred/app.html`](file:///d:/Helixx/smepred/app.html)), guaranteeing that candidate knockdown efficacy is bounded strictly within $[0.00\%, 100.00\%]$.


