# HelixZero-CMS: Diagnostic Gotchas & Known Pipeline Issues (Release 5.3.0)

> **Official Technical Gotchas & Pipeline Rules Manual**  
> **Target Audience**: Data Scientists, Bioinformatics Engineers, Peer Reviewers  
> **Release Version**: 5.3.0 (IEEE v5 + CatBoost GBDT + PyTorch GNN Production Stack)  

---

## 1. 3'-Overhang Structural Cap Stripping (19-nt Core vs. 21-nt Duplex)

* **Symptom / Scoring Drift**: Feeding naked sequences with trailing shorthand (`dT`, `dTdT`, `D`) to `predict_ieee_v5.py` causes scoring drift compared to modified sequences where overhangs were stripped.
* **Root Cause**: `helixzero_ieee_v5/predict_ieee_v5.py` featurizes core 19-nt nucleotide positions into `NucSlot` chemical ontology slots. If the naked sequence contains trailing `D` or `dTdT` caps (making it 20-nt or 21-nt), it gets fed into `features_v4.py` with a different length than the 19-nt modified core, causing feature vector mismatch.
* **Pipeline Rule**: Always strip 3'-end overhang caps (`dT`, `dTdT`, `D`, `dTdT-3'`) using `_strip_3p_overhang()` before passing sequences to `predict_sirna_potency()` or `features_v4.batch_features_v4()`.

---

## 2. Dose-Aware Log-Concentration Transformation Rule

* **Symptom / Score Corruption**: Stage 2 (`module3_assay_response.cbm`) output returns near 0% or invalid knockdown values.
* **Root Cause**: Stage 2 expects concentration in $\log_{10}$ scale:
  $$\text{X}_{\text{dose}} = \log_{10}(\text{concentration\_nM} + 1e-6)$$
  Passing raw concentration values (e.g. `10.0` instead of $\log_{10}(10.0 + 1e-6) \approx 1.0$) corrupts tree split evaluation.
* **Pipeline Rule**: Always log-transform assay concentration in nM using `np.log10(conc_nM + 1e-6)` before feeding it into Stage 2 `module3_assay_response.cbm`.

---

## 3. Foundation Model PCA Embedding Cache Fallback

* **Symptom / Prediction Attenuation**: Inference on novel sequences not present in `rnafm_embeddings.pkl` or `rnaernie_embeddings.pkl` shows slight (~2-3%) score attenuation.
* **Root Cause**: `features_v4.py` looks up pre-computed 640-d RNA-FM and 768-d RNA-Ernie foundation model embeddings and transforms them via PCA to 64-d vectors. For un-cached novel sequences, `features_v4.py` safely returns zero-padded float32 arrays (`np.zeros(32)`).
* **Pipeline Rule**: For novel sequences, run offline embedding pre-computation via `RNA-FM` / `RNA-Ernie` to populate `rnafm_embeddings.pkl` and `rnaernie_embeddings.pkl` in `smepred/models/` for full embedding accuracy.

---

## 4. PyTorch MEG-mod GNN Serving & Device Fallback (`gnn_serving.py`)

* **Symptom / CUDA Memory Failure**: PyTorch GNN inference crashes during large batch processing on limited GPU memory.
* **Root Cause**: `gnn_serving.py` loads `finetuned_v2.pt` (PyTorch GATv2 model) on GPU (`cuda`) if available. Constructing CoFold secondary structure graphs for batches $>5,000$ items can spike VRAM.
* **Pipeline Rule**: `gnn_serving.py` includes a safe CPU fallback. For batch sizes $>2,000$ candidates, pass `DEVICE = torch.device('cpu')` or process in mini-batches of 500 items.

---

## 5. 19-mer vs. 21-mer Slicing in `biophysics.py`

* **Symptom / Drift**: Diagnostic scripts passing 19-mer core sequences to `calculate_adjusted_efficacy()` produce score drift compared to `predict_modified()`.
* **Root Cause**: `predictor.predict_modified()` evaluates full 21-mer sequences including 2-nucleotide overhangs (`CAAAAUUGGGCUUUUAAAATT`). Terminal index matching in `biophysics.py` relies on exact 21-mer indexing.
* **Pipeline Rule**: Always pass complete 21-mer RNA sequence strings to `predictor.predict_modified()` and `biophysics.calculate_adjusted_efficacy()`.

---

## 6. Protection Penalty Floor on Unmodified Parent Baselines

* **Symptom / Behavior**: Baseline scores for unmodified parent sequences include an automatic ~5.76% structural protection deduction.
* **Root Cause**: In `predictor.py`, `calculate_adjusted_efficacy()` called on unmodified parent sequences evaluates nuclease, serum, and RISC protection functions. 2'-modification coverage and PS backbone linkages are by definition 0% on unmodified RNA.
* **Pipeline Rule**: Understand that UI Badge Delta ($\text{Card 3} - \text{Card 2}$) compares modified candidates against a baseline that includes this structural protection floor.

---

## 7. Biophysics Penalty Point Scaling Factor (`_PENALTY_ADJUSTMENT_FACTOR = 0.18`)

* **Symptom / Arithmetic Discrepancy**: Summing raw penalty points directly (e.g. 60.0 raw points) does not equal percentage score drop.
* **Root Cause**: Raw biophysics penalty points are scaled by `_PENALTY_ADJUSTMENT_FACTOR = 0.18` (calibrated to align with published Alnylam ESC+ and Khvorova lab design literature).
* **Pipeline Rule**: Compute exact percentage deductions using:
  $$\text{Percentage Deduction (\%)} = \left(\sum \text{Raw Penalty Points}\right) \times 0.18$$

---

## 8. Zero Sequence-Leakage GroupKFold Requirement

* **Symptom / Over-Optimistic Validation Metrics**: Evaluating model accuracy using standard random 80/20 train/test splits reports artificially high metrics ($\rho > 0.85$).
* **Root Cause**: Random splits place modified variants of the *same guide sequence* in both train and test sets, causing sequence identity leakage.
* **Pipeline Rule**: Always evaluate multi-mod siRNA models using **5-Fold GroupKFold cross-validation grouped by unique antisense sequence (`anti_seq`)** to measure true unseen sequence generalization.
