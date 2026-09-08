# 📊 HelixZero IEEE v5 Benchmark Report — Molecular Therapy 15 siRNA Panel (N=30 Duplexes)

**Dataset Source**: *Molecular Therapy: Nucleic Acids* (Vol 36, March 2025, Table 1)  
**Evaluated Model**: HelixZero IEEE v5 Hierarchical Model Suite (Module 2 CatBoost pIC50 + Module 3 Knockdown %)  
**Validation Standard**: IEEE TNNLS / Bioinformatics Publication-Grade (Zero Sequence Leakage GroupKFold Protocol)

---

## 🎯 Quantitative Performance Metrics

| Metric | IEEE v5 Performance | Baseline Target |
| :--- | :---: | :---: |
| **Pearson Correlation (r)** | **0.5331** ⭐ | $> 0.7000$ |
| **Spearman Rank Correlation (rho)** | **0.5193** ⭐ | $> 0.7000$ |
| **Mean Absolute Error (MAE)** | **1.6658 log10(M)** | $< 0.8000$ |
| **Root Mean Squared Error (RMSE)** | **1.9503 log10(M)** | $< 1.0000$ |

---

## 🧬 Full 30 Duplex Benchmark Evaluation Table

| # | siRNA ID | Target | Is Mod | Exp IC50 (nM) | Exp pIC50 | IEEE v5 pIC50 | IEEE v5 IC50 (nM) | IEEE v5 Knockdown % | Error |
| :-: | :--- | :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| 1 | `siSER-1` | SERPINA1 | No | 4.4 | 8.3565 | **8.1391** | **7.2589** | **22.49%** | 0.2174 |
| 2 | `siSER-1m` | SERPINA1 | Yes | 100.0 | 7.0 | **8.2814** | **5.2315** | **49.94%** | 1.2814 |
| 3 | `siSER-2` | SERPINA1 | No | 0.11 | 9.9586 | **8.2354** | **5.8162** | **32.35%** | 1.7232 |
| 4 | `siSER-2m` | SERPINA1 | Yes | 27.2 | 7.5654 | **8.4013** | **3.9696** | **57.28%** | 0.8359 |
| 5 | `siSER-3` | SERPINA1 | No | 0.33 | 9.4815 | **8.1036** | **7.877** | **24.26%** | 1.3779 |
| 6 | `siSER-3m` | SERPINA1 | Yes | 100.0 | 7.0 | **8.2229** | **5.9853** | **49.79%** | 1.2229 |
| 7 | `siSER-4` | SERPINA1 | No | 0.032 | 10.4949 | **8.6406** | **2.2877** | **48.56%** | 1.8543 |
| 8 | `siSER-4m` | SERPINA1 | Yes | 0.027 | 10.5686 | **8.4333** | **3.6869** | **60.89%** | 2.1353 |
| 9 | `siSER-5` | SERPINA1 | No | 0.2 | 9.699 | **8.6141** | **2.4314** | **51.9%** | 1.0849 |
| 10 | `siSER-5m` | SERPINA1 | Yes | 0.23 | 9.6383 | **8.5268** | **2.9732** | **59.12%** | 1.1115 |
| 11 | `siSER-6` | SERPINA1 | No | 2.74 | 8.5622 | **8.1492** | **7.0932** | **21.93%** | 0.413 |
| 12 | `siSER-6m` | SERPINA1 | Yes | 100.0 | 7.0 | **8.2869** | **5.1652** | **49.38%** | 1.2869 |
| 13 | `siSER-7` | SERPINA1 | No | 0.56 | 9.2518 | **8.3423** | **4.5471** | **36.94%** | 0.9095 |
| 14 | `siSER-7m` | SERPINA1 | Yes | 100.0 | 7.0 | **8.3445** | **4.5234** | **59.03%** | 1.3445 |
| 15 | `siSER-8` | SERPINA1 | No | 1.3 | 8.8861 | **8.341** | **4.5605** | **37.65%** | 0.5451 |
| 16 | `siSER-8m` | SERPINA1 | Yes | 0.15 | 9.8239 | **8.3642** | **4.3232** | **57.04%** | 1.4597 |
| 17 | `siSER-9` | SERPINA1 | No | 0.16 | 9.7959 | **8.4312** | **3.7048** | **42.88%** | 1.3647 |
| 18 | `siSER-9m` | SERPINA1 | Yes | 100.0 | 7.0 | **8.3926** | **4.0493** | **60.2%** | 1.3926 |
| 19 | `siSER-10` | SERPINA1 | No | 0.001 | 12.0 | **8.6711** | **2.1324** | **48.98%** | 3.3289 |
| 20 | `siSER-10m` | SERPINA1 | Yes | 0.004 | 11.3979 | **8.4591** | **3.4744** | **59.45%** | 2.9388 |
| 21 | `siAGT-1` | AGT | No | 0.0007 | 12.1549 | **8.6133** | **2.4359** | **53.89%** | 3.5416 |
| 22 | `siAGT-1m` | AGT | Yes | 0.0001 | 13.0 | **8.5127** | **3.071** | **58.19%** | 4.4873 |
| 23 | `siAGT-2` | AGT | No | 0.04 | 10.3979 | **8.1829** | **6.5634** | **24.26%** | 2.215 |
| 24 | `siAGT-2m` | AGT | Yes | 100.0 | 7.0 | **8.2744** | **5.3159** | **51.12%** | 1.2744 |
| 25 | `siAGT-3` | AGT | No | 0.13 | 9.8861 | **8.3421** | **4.5491** | **38.13%** | 1.544 |
| 26 | `siAGT-3m` | AGT | Yes | 4.9 | 8.3098 | **8.332** | **4.6563** | **59.55%** | 0.0222 |
| 27 | `siAGT-4` | AGT | No | 0.0004 | 12.3979 | **9.2235** | **0.5978** | **64.15%** | 3.1744 |
| 28 | `siAGT-4m` | AGT | Yes | 0.022 | 10.6576 | **8.9401** | **1.148** | **60.87%** | 1.7175 |
| 29 | `siAGT-5` | AGT | No | 0.01 | 11.0 | **8.1329** | **7.364** | **32.28%** | 2.8671 |
| 30 | `siAGT-5m` | AGT | Yes | 0.21 | 9.6778 | **8.3742** | **4.2249** | **56.65%** | 1.3036 |
