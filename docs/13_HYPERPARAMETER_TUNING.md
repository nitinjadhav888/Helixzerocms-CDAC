# 13. HYPERPARAMETER TUNING & SENSITIVITY ANALYSIS
## Optimization Schedules, Grid Sweeps, and Regularization Rationale
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  
**Tuning Script Reference:** `scripts/optimize_unified_catboost_loop.py`  

---

### 1. Optimization Strategy and Search Space

Hyperparameter sweeps were performed using sequence-disjoint `GroupKFold` cross-validation to select parameters that generalize across novel genes rather than memorizing batch noise:

| Hyperparameter | Evaluated Grid Range | Optimal Value Selected | Selection Rationale |
| :--- | :--- | :---: | :--- |
| **Tree Depth ($D$)** | $\{4, 6, 8, 10\}$ | **6** | Depth 6 provides $2^6 = 64$ terminal leaves per tree. Depth 4 under-fit chemical epistatic interactions ($r = 0.642$), while depth 8 over-fit rare modification tokens with no gain on held-out sets ($r = 0.672$). |
| **Learning Rate ($\eta$)** | $\{0.01, 0.02, 0.035, 0.05, 0.1\}$ | **0.035** | Learning rate 0.035 with 1,500 iterations minimized validation RMSE smoothly without gradient oscillation. |
| **$L_2$ Leaf Regularization ($\lambda$)**| $\{1.0, 3.0, 5.0, 10.0\}$ | **3.0** | $\lambda = 3.0$ heavily penalizes extreme leaf weights, stabilizing predictions on rare modifications such as UNA and ENA. |
| **Number of Iterations ($M$)**| $\{800, 1200, 1500, 2000\}$ | **1500** | Cross-validation validation loss reached its global plateau between 1,200 and 1,500 rounds. |
| **Loss Function** | $\{\text{RMSE}, \text{MAE}, \text{Huber}\}$ | **RMSE** | RMSE penalizes large outlier errors, providing better ranking calibration ($\rho = 0.6752$) than MAE. |

---

### 2. Empirical Validation Results Across Grid Configurations

Results from `scripts/optimize_unified_catboost_loop.py`:

```text
===================================================================================================
DEPTH   LEARNING RATE   L2 REG   MEAN CV PEARSON r   MEAN CV RMSE (%)   STATUS
===================================================================================================
4       0.040           3.0      0.6421 +/- 0.038    22.84%             Underfitting
6       0.020           3.0      0.6698 +/- 0.031    21.92%             Sub-optimal Convergence
6       0.035           3.0      0.6776 +/- 0.028    21.57%             OPTIMAL (Production Choice)
6       0.050           3.0      0.6745 +/- 0.033    21.78%             Slight Overfitting
8       0.035           3.0      0.6712 +/- 0.041    22.05%             Overfitting to Rare Mods
8       0.035           5.0      0.6684 +/- 0.039    22.14%             Over-regularized Depth 8
===================================================================================================
```

---

### 3. Early Stopping Dynamics

During 5-fold cross-validation, an early stopping patience of 100 rounds was applied. In all five folds, the optimal iteration count occurred between 1,120 and 1,380 iterations. For the final production model trained on the full clean dataset ($N = 17,761$), 1,500 iterations were selected with learning rate 0.035, providing smooth convergence and maximum generalization.
