# HISTORICAL MODEL: IEEE V5 TWO-STAGE CASCADING ENGINE
## Cascading Potency-to-Assay Formulation and Compounded Error Analysis
**Status:** `VERIFIED — HISTORICAL / ABLATION ARCHIVE`  
**Archive Location:** `helixzero_ieee_v5/`  

---

### 1. Model Profile & Architectural Design

- **Model Identifier:** HelixZero IEEE v5 Cascading Engine
- **Architectural Formulation:** Two-stage cascading pipeline attempting to decouple intrinsic thermodynamic compound potency from experimental concentration response:
  - **Stage 1 (Module 2 Potency Engine):** CatBoost Regressor (`module2_potency_pIC50.cbm`) trained on $N = 35,982$ multi-dose rows to predict intermediate compound potency ($pIC_{50}$).
  - **Stage 2 (Module 3 Assay Response Engine):** CatBoost Regressor (`module3_assay_response.cbm`) predicting observed percentage knockdown by passing predicted $\hat{pIC}_{50}$ and assay concentration through a sigmoidal Hill response layer.

---

### 2. Empirical Benchmark Comparison

Evaluated on the standardized multi-dose validation lake:

| Metric | IEEE v5 Two-Stage Pipeline | Single Unified CatBoost Regressor | Architectural Advantage |
| :--- | :---: | :---: | :--- |
| **Pearson Correlation ($r$)** | 0.8187 | **0.8359** | **+0.0172 (+2.1% Higher Correlation)** |
| **Spearman Rank ($\rho$)** | 0.8245 | **0.8558** | **+0.0313 (+3.8% Better Ranking)** |
| **ROC-AUC ($\ge 70\%$)** | 0.9142 | **0.9312** | **+0.0170 Superior Discrimination** |
| **Root Mean Squared Error (RMSE)**| 18.25% | **17.02%** | **-1.23% Lower Prediction Error** |

---

### 3. Engineering Justification for Retirement

The IEEE v5 two-stage architecture was retired from active production serving due to **Compounding Variance Propagation**:
1. In a two-stage cascade, any residual estimation error in Stage 1 ($\hat{pIC}_{50} = pIC_{50} + \epsilon_1$) acts as a noisy feature in Stage 2.
2. Because the Hill sigmoid is non-linear ($y \propto C / (10^{9 - pIC_{50}} + C)$), errors in the steep transition region of the curve are exponentially amplified:
   $$\text{Var}(\hat{y}) \approx \left(\frac{\partial f}{\partial pIC_{50}}\right)^2 \text{Var}(\epsilon_1) + \text{Var}(\epsilon_2).$$
3. By contrast, a **Single Unified CatBoost Regressor** directly trained on $[ \mathbf{x}_{513}, \log_{10}(C), \text{covars} ]$ learns the continuous joint surface in a single optimization step, eliminating intermediate variance propagation and improving test accuracy from $r = 0.8187$ to $r = 0.8359$.

*Preservation Notice:* The two-stage engine is preserved in `helixzero_ieee_v5/` to document this scientific ablation for journal peer review.
