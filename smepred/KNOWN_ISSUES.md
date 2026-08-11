# HelixZero-CMS: Diagnostic Gotchas & Known Pipeline Issues

This document records technical gotchas, script traps, and pipeline scoring subtleties identified during benchmark audits. Refer to this document before writing new diagnostic, benchmarking, or validation scripts to prevent reintroducing resolved issues.

---

## 1. 19-mer vs. 21-mer Sequence Slicing Trap
* **Symptom / Drift**: Diagnostic scripts passing 19-mer core sequences (e.g. `CAAAAUUGGGCUUUUAAAA`) to `calculate_adjusted_efficacy()` produce score drift compared to the live pipeline (`predict_modified()`).
* **Root Cause**: `predictor.predict_modified()` evaluates full 21-mer sequences including 2-nucleotide overhangs (`CAAAAUUGGGCUUUUAAAATT`). Terminal index matching in `biophysics.py` relies on exact 21-mer indexing.
* **Guideline**: Always pass complete 21-mer RNA sequence strings to `predictor.predict_modified()` and `biophysics.calculate_adjusted_efficacy()`.

---

## 2. Protection Penalty Floor on Unmodified Parent Baselines
* **Symptom / Behavior**: Card 1 (`naked_baseline`) and Card 2 (`model_b_baseline`) scores for unmodified parent sequences include an automatic ~5.76% deduction.
* **Root Cause**: In `predictor.py`, `calculate_adjusted_efficacy()` is called on parent sequences using `base_sense` and `base_antisense` identical to `sense` and `antisense`. Protection-dependent penalty functions (`nuclease_penalty`, `risc_penalty`, `serum_penalty`) evaluate 2'-modification coverage and PS backbone linkages, which by definition are 0% on unmodified RNA.
* **Guideline**: Understand that UI Badge Delta ($\text{Card 3} - \text{Card 2}$) compares modified candidates against a baseline that includes this structural protection floor. For pure sequence-intrinsic baseline comparisons, evaluate Thermodynamic, Immuno, and Synthesis penalties independently.

---

## 3. Biophysics Penalty Point Scaling Factor (`_PENALTY_ADJUSTMENT_FACTOR = 0.18`)
* **Symptom / Arithmetic Discrepancy**: Summing raw penalty points directly (e.g., 60.0 raw points for `siAGT-3`) does not equal the percentage score drop.
* **Root Cause**: Raw biophysics penalty points are scaled by `_PENALTY_ADJUSTMENT_FACTOR = 0.18` (calibrated to align with published Alnylam ESC+ and Khvorova lab design literature).
* **Guideline**: To compute exact percentage deductions:
  $$\text{Percentage Deduction (\%)} = \left(\sum \text{Raw Penalty Points}\right) \times 0.18$$

---

## 4. Intra-Scaffold Modification Ranking vs. Base Sequence Priors
* **Symptom / Behavior**: Card 1 (Naked) and Card 2 (Ensemble) scores exhibit zero variance among candidates sharing the same parent scaffold (e.g., the 10 `VS-129` variants in `SARS.pdf`).
* **Root Cause**: Card 1 and Card 2 evaluate the unmodified parent sequence prior. They cannot rank chemical modification variants within the same scaffold.
* **Guideline**: Evaluate intra-scaffold modification ranking performance on Card 3 Adjusted (or the modification delta), which incorporates modification-specific terminal destabilization and modification features.

---

## 5. Stratified Bootstrap for Small Imbalanced Datasets
* **Symptom / Variance Discrepancy**: Plain bootstrap resampling on small datasets ($n=15$ or $n=20$) produces wider, noisy confidence intervals due to degenerate resamples lacking positive/negative instances.
* **Root Cause**: Unstratified sampling can draw resamples with zero or one instance of a class.
* **Guideline**: Always use **1,000x Stratified Bootstrap resampling** (drawing with replacement separately within positive and negative subsets to preserve the exact class ratio in every resample) and disclose this explicitly in reports.
