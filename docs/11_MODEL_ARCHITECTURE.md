# 11. MODEL ARCHITECTURE & MATHEMATICAL FORMULATIONS
## Algorithmic Formulations, Loss Objectives, and Potency Inversion
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. Mathematical Architecture of the Unified CatBoost Core

The flagship engine (`smepred/models/unified_dose_catboost.cbm`) employs an ensemble of symmetric oblivious decision trees:
$$\hat{f}(\mathbf{x}) = \sum_{m=1}^M \gamma_m h_m(\mathbf{x}),$$
where $M = 1,500$ iterations, $h_m(\mathbf{x})$ is an oblivious decision tree of depth $D = 6$, and $\gamma_m$ is the step length scaled by learning rate $\eta = 0.035$.

#### 1.1 Oblivious (Symmetric) Decision Trees
Unlike standard asymmetric decision trees (such as XGBoost or LightGBM) that grow depth-first or leaf-wise, oblivious trees use the identical split condition across all nodes at the same tree depth $d \in \{1, \dots, 6\}$:
$$s_d = \mathbb{I}(x_{j_d} > \theta_d).$$
This architectural constraint provides three decisive advantages:
1. **Regularization against Overfitting:** Limits tree complexity to $2^D = 64$ terminal leaves per tree, preventing memorization of rare chemical modifications.
2. **Fast Vectorized Inference:** An input sample is evaluated by computing a 6-bit index via SIMD bitwise operations, executing in $< 0.1\text{ }\mu\text{s}$ per candidate on CPU.
3. **No Target Leakage:** CatBoost's ordered boosting calculates split gradients using random permutations of data, eliminating target leakage during cross-validation.

#### 1.2 Loss Objective
The model minimizes Root Mean Squared Error (RMSE) with $L_2$ leaf regularization ($\lambda = 3.0$):
$$\mathcal{L}(\mathbf{y}, \hat{\mathbf{y}}) = \sqrt{\frac{1}{N} \sum_{i=1}^N (y_i - \hat{f}(\mathbf{x}_i))^2} + \frac{\lambda}{2} \sum_{m=1}^M \sum_{j=1}^{64} w_{m,j}^2.$$

---

### 2. Analytical Closed-Form Hill Equation Inversion

In classical quantitative pharmacology, concentration-dependent receptor silencing follows the empirical Hill equation:
$$y(C) = 100 \cdot \frac{C^h}{\text{IC}_{50}^h + C^h},$$
where $y(C)$ is the observed percentage target knockdown $[0, 100]\%$, $C$ is the assay concentration in nanomolar (nM), $\text{IC}_{50}$ is the half-maximal inhibitory concentration, and $h$ is the Hill cooperativity coefficient.

#### 2.1 Closed-Form Inversion Derivation
Given a predicted biological knockdown $y = \hat{f}(\mathbf{x})$ at screening concentration $C$:
$$y \cdot (\text{IC}_{50}^h + C^h) = 100 \cdot C^h$$
$$y \cdot \text{IC}_{50}^h = (100 - y) \cdot C^h$$
$$\text{IC}_{50}^h = C^h \cdot \left(\frac{100 - y}{y}\right)$$
$$\text{IC}_{50} = C \cdot \left(\frac{100 - y}{y}\right)^{1/h}.$$

In the standard physiological regime for therapeutic oligonucleotides, single-site RISC-mRNA catalytic cleavage exhibits uncooperative binding ($h = 1.0$):
$$\text{IC}_{50} \, [\text{nM}] = C \cdot \left(\frac{100 - y}{y}\right).$$

#### 2.2 Intrinsic Potency ($p\text{IC}_{50}$) Derivation
To express potency on a standard logarithmic scale:
$$\text{IC}_{50} \, [\text{Molar}] = \text{IC}_{50} \, [\text{nM}] \times 10^{-9}$$
$$p\text{IC}_{50} = -\log_{10}(\text{IC}_{50} \, [\text{M}]) = 9.0 - \log_{10}(\text{IC}_{50} \, [\text{nM}]).$$

**Boundary Handling (`smepred/src/predictor.py:807-810`):**
To prevent numerical division-by-zero or logarithmic singularity when predicted knockdown approaches $0\%$ or $100\%$, $y$ is strictly bounded:
$$y_{\text{safe}} = \max(1.0, \min(99.0, y)).$$
This evaluates in under 5 microseconds, eliminating iterative numerical optimization.

---

### 3. Model A Mathematical Formulation (Naked GBDT)

Model A (`smepred/models/model_normal.txt`) scans unmodified mRNA transcripts. It grows asymmetric decision trees minimizing Huber loss ($\alpha = 0.9$):
$$\mathcal{L}_{\text{Huber}}(y, \hat{y}) = \begin{cases} 
\frac{1}{2}(y - \hat{y})^2 & \text{if } |y - \hat{y}| \le \alpha \\ 
\alpha |y - \hat{y}| - \frac{1}{2}\alpha^2 & \text{otherwise} 
\end{cases}$$

Raw predictions are calibrated through out-of-fold Isotonic Regression:
$$f_{\text{iso}}(z) = \arg\min_g \sum_{i=1}^N (y_i - g(z_i))^2 \quad \text{subject to } g(z_i) \le g(z_j) \text{ for } z_i \le z_j.$$

---

### 4. Feature Attribution & Mechanistic Importance

Feature importance computed across all CatBoost trees via split gain:
1. **Feature 513: $\log_{10}(\text{Dose\_nM})$ (18.4% Gain):** Primary driver of knockdown response, confirming the necessity of dose conditioning.
2. **Antisense Position 2 Sugar Class (11.2% Gain):** Governs seed region nucleation and off-target suppression.
3. **Antisense Position 10 Chemistry (8.7% Gain):** Governs compatibility with the catalytic cleavage site of the Ago2 PIWI domain.
4. **Duplex Free Energy $\Delta G_{\text{duplex}}$ (6.4% Gain):** Governs passenger strand displacement energetics.
5. **RNA-FM Principal Component 1 (5.1% Gain):** Captures sequence-intrinsic evolutionary conservation.
