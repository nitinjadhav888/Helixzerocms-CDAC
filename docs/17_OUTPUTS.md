# 17. SYSTEM OUTPUTS & INTERPRETATION GUIDE
## Output Specifications, UI Screen Mappings, and Artifact Ledger
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. End-to-End Input-to-Output Mapping

| User Input | Computational Processing | Active Model | Primary Output Artifact / Screen | Biological & Clinical Meaning |
| :--- | :--- | :--- | :--- | :--- |
| **mRNA FASTA / GenBank** | Sliding 21-mer generation, 214-D thermodynamic extraction | Model A LightGBM | UI Tab: Naked Screening (`Outputs/AllcandNaked.png`) | Identifies all possible unmodified 21-mers ranked by predicted naked efficacy. |
| **mRNA Sequence** | ORF translation (AUG $\to$ Stop), biological filtering | Heuristic Domain Filter | UI Tab: Curated Leads (`Outputs/NakedCuratedRank.png`) | Identifies top non-redundant leads separated by $\ge 35$ nt across 5' UTR, CDS, and 3' UTR. |
| **Selected Lead siRNA** | Exhaustive single-site substitution scan | Unified CatBoost 517-D | UI Tab: Single-Mod Scan (`Outputs/SingleModscan.png`) | Evaluates 812 single-point permutations to identify highest-impact modification sites. |
| **Single Modification** | 3D coordinate synthesis with B-factor encoding | Continuous A-Form Generator | UI Tab: 3D Structure (`Outputs/SingleMod3D.png`) | Interactive 3Dmol.js rendering showing physical placement of chemical modification. |
| **Modified Duplex** | 2-bit packed transcriptome hash query | 2-Bit SIMD Engine | UI Tab: Off-Target Scan (`Outputs/SingleModOFFTarget.png`) | Flags 15-mer slicer cross-reactivity and microRNA-like seed match liabilities. |
| **Combinatorial Design**| Beam search ($W = 20$) optimizing ESC+ patterns | Unified CatBoost + Biophysics | UI Tab: Multi-Mod Scan (`Outputs/MultiModScan.png`) | Ranks multi-modified configurations balancing potency, nuclease shield, and low toxicity. |
| **Custom Architecture**| Multi-slot parameter parsing and scoring | Unified CatBoost 517-D | UI Tab: Custom Predict (`Outputs/PredictSingleVarientMM.png`)| Predicts knockdown %, $\text{IC}_{50}$, $p\text{IC}_{50}$, and biophysical deductions for user designs. |

---

### 2. Persistent Output File Ledger

The following output artifacts exist in the repository:

1. **Benchmark Ledgers (`final_benchmarks/`):**
   - `master_benchmark_metrics.csv`: Single source of truth containing verified $r, \rho, \text{AUC}, \text{MAE}, \text{RMSE}, R^2$ across all models and test partitions.
   - `ai_vs_human_chemist_5cases.csv`: 5-case head-to-head comparison between human medicinal chemists and HelixZero.
   - `siRNAmod_50_benchmark_results.csv`: External benchmark evaluation across 50 chemically modified siRNAs.
2. **Clinical Validation Reports:**
   - `final_benchmarks/siRNAmod_10_Sequences_and_Master_Benchmark_Report.pdf`: Formal PDF report of the master benchmark.
   - `fda_therapeutics_evaluation_report.pdf`: Independent validation report on the six commercial FDA therapeutics.
   - `model_validation_and_audit_report.pdf`: Senior data scientist code and model audit report.
3. **User Interface Visual Evidence (`Outputs/`):**
   - 19 high-resolution screenshots capturing every module of the active laboratory workbench (including `SingleMod3D.png`, `MM3D.png`, `MultiModRAnk.png`, `helixCopilot.png`).
