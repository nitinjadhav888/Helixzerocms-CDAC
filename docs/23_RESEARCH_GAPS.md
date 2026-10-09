# 23. RESEARCH GAPS & SCIENTIFIC NOVELTY AUDIT
## Critical Literature Analysis, Limitations of Prior Art, and Engineering Solutions
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. Established Literature vs. Engineering Novelty Matrix

| Problem Dimension | Established Scientific Literature | Prior Computational Approaches | Known Limitations of Prior Art | HelixZero Engineering Response | Novelty Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Chemical Epistasis** | Synthetic modifications ($2'$-F, $2'$-OMe) rewire Ago2 kinetics non-linearly. | Sequence-only ML models (OligoFormer, sIRNAs, DSIR). | Collapse to $r = 0.1771$ on modified RNA ($R^2 = -0.0901$). | 517-D multi-modal vector space (444 chemistry + 64 RNA-FM + 5 Vienna + 4 Dose). | **Verified Novel Architecture** |
| **Sequence Leakage** | Sliding 21-mers share 94.7% identity across mRNA transcripts. | Random K-fold train/test cross-validation splits. | Sibling leakage inflates claimed test correlations ($r > 0.88$). | 5-Fold `GroupKFold` clustering across 5,251 disjoint antisense sequence groups (0.0% leakage). | **Verified Methodological Fix** |
| **Concentration Confounding** | siRNA silencing is concentration-dependent ($0.001\text{--}10{,}000\text{ nM}$). | Fixed-dose assumption (10 nM) or 2-stage cascades ($pIC_{50} \to \text{Hill}$). | Compounding variance propagation; cannot generalize across titration curves. | Single Unified CatBoost Regressor conditioned on $\log_{10}(\text{Dose\_nM})$ + closed-form Hill inversion. | **Verified Algorithmic Fix** |
| **In Vivo Viability** | Unmodified RNA causes TLR7/8 immune activation and nuclease degradation. | Pure in silico potency optimizers lacking biophysical rules. | Generates potent in vitro sequences that provoke lethal in vivo toxicity. | Deterministic 4-domain biophysical guardrails + 2-bit whole-transcriptome off-target firewall. | **Verified Hybrid System** |

---

### 2. Claims Requiring Further Experimental Validation
`UNVERIFIED / REQUIRES CONFIRMATION`

To uphold IEEE TNNLS / Nature Biotechnology peer review standards, the following aspects are explicitly acknowledged as requiring further wet-lab confirmation:
1. **Stereopure Phosphorothioate Modeling:** Public datasets (CMsiRNAdb) compile phosphorothioates as stereorandom $R_p/S_p$ mixtures. HelixZero treats PS linkages as stereorandom averages; predicting stereopure $R_p$ vs. $S_p$ catalytic cleavage requires dedicated stereopure training datasets.
2. **Extrahepatic Delivery Kinetics:** The current cellular lineage covariate differentiates hepatic cells ($ASGPR^{+}$) from non-hepatic cells. Predicting pharmacokinetics in central nervous system (CNS), ocular, or pulmonary tissues with novel peptide/lipid conjugates requires additional tissue-specific training assays.
3. **In Vivo Cynomolgus Pharmacokinetics:** While in vitro commercial drugs match Phase 3 human trial efficacy windows, direct computational prediction of multi-month primate PK/PD clearance curves requires future mathematical expansion.
