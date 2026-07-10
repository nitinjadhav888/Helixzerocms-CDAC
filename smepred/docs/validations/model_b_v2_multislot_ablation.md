# Validation: Multi-Slot Chemistry Schema (v2) vs Legacy Single-Char Schema
*Generated 2026-07-10 by HelixZero-CMS Data Engineering (chem_schema.py / features_v2.py)*

## ⚠️ Scope & honesty disclaimer
This session had **no live internet/browsing tool available** — all literature
citations below are recalled from trained knowledge, not freshly fetched. They
are well-established, real papers I have high confidence in, but **should be
spot-checked against PubMed/journal PDFs before being cited externally**
(e.g. in the pitch deck or investor materials). All *numeric* results in this
document are freshly computed in this session and fully reproducible via the
scripts named below.

## What This Proves
The legacy per-position modification encoding (`M`/`F`/`L`/... single char)
used by the currently-deployed Model B forces sugar chemistry, backbone
linkage (PS), base modification, and terminal conjugates to compete for ONE
symbol per nucleotide. This document (1) proves that bug caused **real,
measurable information loss** in the actual training data, and (2) shows a
controlled, single-variable ablation in which fixing it improves prediction
quality, using a **leakage-free validation split** (a leakage bug in the
*current* production split is also identified and documented below).

## Literature basis for the new schema (`scratch/v2_pipeline/chem_schema.py`, `features_v2.py`)

| Design decision | Grounding study |
|---|---|
| Sugar/linkage/base-mod/conjugate are independent, co-occurring slots | Deleavey & Damha 2012, *Chem. Biol.* 19(8):937-954 (review) |
| Full 2'-F/2'-OMe modification tolerated/beneficial | Allerson et al. 2005, *J. Med. Chem.* 48(4):901-4 |
| Seed region (AS pos 2-8) intolerant of rigid/bulky sugars (LNA/MOE/ENA) | Bramsen et al. 2009, *NAR* 37(9):2867-81; Elmén et al. 2005 (already validated in this repo, `elmen_2005_validation.md`) |
| AS position 1 requires a free 5'-phosphate or stable mimic for RISC/Ago2 loading | Schirle & MacRae 2012, *Science* (Ago2 crystal structure, MID-domain phosphate pocket); Parmar et al. 2016, *ChemBioChem* 17(11):985-9 (5'-vinylphosphonate mimic) |
| Thermodynamic 5' asymmetry governs guide-strand selection | Khvorova, Reynolds, Jayasena 2003 / Schwarz et al. 2003, *Cell* 115 |
| PS linkages belong at strand termini, not internally | Behlke 2008, *Oligonucleotides* 18(4):305-19; Sakamuri et al. 2020 (already validated in this repo, `sakamuri_2020_validation.md`) |
| GalNAc conjugate identity/positioning is a first-class, RISC-relevant feature | Nair et al. 2014, *JACS* 136(49):16958-61; Weingärtner et al. 2020 (already validated in this repo, `weingartner_2020_validation.md`) |
| Sequence-composition covariates (GC%, terminal clamp, 5' base identity) remain predictive independent of chemistry | Reynolds et al. 2004, *Nat. Biotechnol.* 22(3):326-30 |
| Positional one-hot + engineered thermodynamic-style covariates outperform pure categorical encoding | Vert et al. 2006, *BMC Bioinformatics* 7:520 (DSIR); Huesken et al. 2005, *Nat. Biotechnol.* 23(8):995-1001 |
| Near-duplicate/analog leakage inflates validation metrics unless split is group-aware | Walters & Barzilay 2020, *J. Chem. Inf. Model.* (general QSAR/cheminformatics best practice) |

## Empirical validation of the parser itself (before any modeling)

1. **Vocabulary coverage**: `chem_schema.parse_modification_name` was run against
   all 268 unique compositional modification-name strings mined from CMsiRNAdb
   (`scratch/mod_types_full.json`). **267/268 (99.6%) parsed successfully**; the
   sole failure is a deliberately-flagged OCR artifact ("Piwi/Argonaute/Zwille
   domain" — a protein-domain name that leaked into the modification-type
   column, not real chemistry).

2. **H1 — AS position 1 rigidity (Bramsen 2009 / Elmén 2005 prediction: LNA here should be ~absent in real designs)**:
   Across 42,638 parsed CMsiRNAdb rows, AS pos-1 sugar chemistry is
   79.4% 2'-OMe, 14.6% unmodified ribose, 3.6% DNA, 2.3% 2'-F, and **0.00% LNA**.
   Matches literature expectation exactly.

3. **H2 — GalNAc conjugate positioning (Nair 2014 / Weingärtner 2020 prediction: antisense-conjugated designs should not appear in viable clinical/patent chemistry)**:
   Of all rows carrying a GalNAc conjugate, **100% are on the sense strand**
   (dominant position: sense pos 22, i.e. a 3'-terminal pseudo-position beyond
   a 21-mer body — the canonical triantennary-GalNAc attachment point);
   **antisense GalNAc conjugation: 0 occurrences in 42,638 rows.**

4. **H3 — PS linkage terminal-vs-internal placement (Behlke 2008 / Sakamuri 2020 prediction)**:
   Antisense PS-linkage frequency by position: **80.5% at pos 1-2, 61.8-67.0%
   at pos 21-22, and ≤0.1% at every internal position (pos 5-16).** A clean,
   near-binary terminal-only pattern, exactly as predicted.

## Root-cause bug, quantified

The legacy training data (`smepred/data/patent_data/clean_training_set.csv`,
the descendant of the now-deleted `scripts/data/parse_sirnamod.py`) encodes
`sense_mod` / `anti_mod` as one character per position. Counting characters
across 39,164 rows (~1.6M nucleotide positions): the PS-linkage symbol `'S'`
appears only **126 times (~0.03%)**. But H3 above proves phosphorothioate
chemistry is *actually present* in the source patent language at ~80% of
antisense terminal positions. **The legacy pipeline was silently discarding
essentially all backbone-linkage information** — a real, quantified,
root-cause bug, not a theoretical concern.

## A leakage bug in the *current production* validation split

Before trusting any comparison, we audited the existing `hetero_train_2728.csv`
/ `hetero_val_303.csv` split used to report the deployed ensemble's headline
metric (Spearman 0.3158, MAE 51.2, per `models/model_b_meta.json`):

- **1,516 / 1,829 (82.9%)** of validation-set antisense base sequences
  **also appear in the training set** (same duplex, different chemistry variant).
- **372 rows are EXACT duplicates** (identical sequence *and* identical
  chemistry) present in **both** train and validation.

This is the textbook "near-duplicate leakage" failure mode (Walters & Barzilay
2020) and is expected given CMsiRNAdb's patent-derived "positional walk"
structure: 1,894 distinct antisense sequences each appear with ≥5 chemistry
variants (22,808 / 42,638 rows, 53.5% of the dataset). **This means the
deployed model's reported 0.3158 Spearman cannot be directly compared to
anything computed on a proper group-held-out split** — including the results
below. (It's also a different target variable — cross-assay IC50 vs.
in-distribution % inhibition — so the two numbers were never apples-to-apples
in the first place; flagging both issues for the record.)

## Controlled ablation: legacy schema vs v2 schema

**Method**: single dataset (CMsiRNAdb, 42,638 rows after sanity filtering),
single leakage-free split (grouped by antisense base sequence, deterministic
efficacy-stratified holdout — see `scratch/v2_pipeline/train_compare.py`),
single algorithm (CatBoost, identical hyperparameters, identical random seed).
**The only variable changed is the feature representation.** The "legacy"
feature set is built by first collapsing the parsed chemistry back down to a
single char/position using the empirically-calibrated priority order that
reproduces the historical ~0.03-0.12% PS-symbol density (`legacy_encode.py`),
then running it through the actual production `extract_phase2()` function
unmodified. The "v2" feature set uses the full multi-slot representation
(`features_v2.py`, 444-dim).

| Model | Spearman ρ | MAE |
|---|---:|---:|
| Legacy single-char schema (`extract_phase2`, faithful reproduction) | 0.4607 | 22.44 |
| **V2 multi-slot schema** (`features_v2`) | **0.4917** | **21.95** |

**+6.7% relative Spearman improvement, -2.2% MAE**, from the schema fix alone,
holding data/split/algorithm constant.

### Top-20 V2 feature importances (sanity check: do the literature-grounded features actually matter?)
Ranked by CatBoost importance — GC composition (Reynolds 2004) dominates as
expected, but literature-motivated chemistry features the legacy schema
could never see are prominently represented:
- `as_pos1_5p_phosphate_mimic` — rank 3 (Schirle 2012 / Parmar 2016)
- `as_5p_weak_end_AU` — rank 7 (Khvorova/Schwarz 2003 asymmetry)
- `as_pos7_is_flexible_exotic` — rank 8 (Bramsen 2009 seed tolerance)
- `as_5p_terminal_PS_frac` — rank 10, `ss_3p_terminal_PS_frac` — rank 16 (Behlke 2008 / Sakamuri 2020 — the exact information the legacy schema was losing)

Full importances in `scratch/v2_pipeline/ablation_report.json`.

## Conclusion
✅ **VALIDATED (with honest caveats):** The root-cause hypothesis is confirmed
both mechanistically (parser tests, H1-H3) and empirically (controlled
ablation: +6.7% Spearman, -2.2% MAE from the schema fix alone). A real
leakage bug in the current production validation split was also found and
documented. This is a **modest, single-source, in-distribution** result on
CMsiRNAdb % inhibition — it is **not yet** a validated replacement for the
deployed cross-assay IC50 ensemble, and should not be presented as one until
the next steps below are completed.

## Update: real external IC50 benchmark, reproduced honestly (`eval_external_ic50.py`)

We reproduced the archived `validate_model_b_ic50.py` methodology exactly
(Alnylam patent Table 4 sequences + Table 2 duplex map + Table 8 real IC50
potency values, `ic50_hepg2_qpcr_nM` column) and ran three models against it
with **zero retraining on this benchmark** (true external test):

| Model | N | Spearman ρ vs -log10(IC50) | p-value |
|---|---:|---:|---:|
| Currently deployed `model_b.pkl` | 32 | 0.1652 | 0.366 |
| Ablation: legacy schema, trained on CMsiRNAdb only | 32 | 0.0492 | 0.789 |
| **Ablation: v2 schema, trained on CMsiRNAdb only** | 32 | **0.1205** | 0.511 |

**Two honesty-critical findings here:**

1. **The `heldout_ic50_spearman: 0.3158` figure in `models/model_b_meta.json`
   could not be reproduced.** Running the archived validation script against
   the actual file `models/model_b.pkl` currently loads (a plain LightGBM
   `Booster`, not the "ensemble" the metadata claims) gives **0.1652**, not
   0.3158, and is not statistically significant (n=32, p=0.37). Either the
   metadata is stale, the deployed artifact was swapped without updating the
   metadata, or a different eval subset/methodology produced that number. This
   should be treated as **unverified** until reconciled — flagging for
   awareness, not fixed in this pass.

2. **This specific patent extraction has zero recoverable PS/conjugate
   annotation** (confirmed: no lowercase `'s'` linkage marker in any of the
   280 source sequences) — so it is a conservative, worst-case test for the
   v2 schema; any gain here can only come from sugar-chemistry/positional
   representation, not the backbone-chemistry fix that mattered most
   in-distribution. Under that handicap, v2 still improves 2.4x over the
   legacy ablation (0.049 → 0.121) but **does not beat the currently deployed
   model (0.165)** — expected, since the deployed model was trained on a
   much larger *combined* multi-source dataset, while both ablation models
   here were deliberately trained on CMsiRNAdb alone to keep the comparison
   controlled. None of these three correlations are individually significant
   at n=32; report directionally, not as a headline number.

## Correction (superseded below — do not restore this file)
An earlier draft of this note flagged `sirna_modified_position_aware_dataset_v2.csv`
(55,731 rows, one of the three sources the archived `train_model_b.py` combined
into the currently-deployed model) as a "provenance gap" that needed restoring.
That was wrong and has been corrected: its own `data_source` column shows
**35,200 / 55,731 rows (63.2%) are explicitly self-labeled `synthetic_*`**
(e.g. `synthetic_Alnylam_ESC_Fitzgerald2017`), i.e. programmatically-generated
positional-walk chemistry patterns on top of real sequences, not real assay
data. Only 20,530 rows (`data_source = cmsirnadb`) were real. Deleting this
file and rebuilding on the 4 real (non-synthetic) patent/CMsiRNAdb sources
— which is exactly what "Production integration" below does — was the
correct, deliberate call, consistent with prior discussion and the
`Reply_to_Dr_Weingärtner` note ("we rebuilt our siRNA chemistry model on real
patent data... in place of the synthetic set we had before"). **Do not
restore this file into training.** It should stay deleted; recoverable via
`git show HEAD~N:...` only for forensic/audit purposes, never as a training input.

## Production integration (this pass)

Consolidated from `scratch/` into clean production modules and retrained on
**all 4 real sources combined** (43,136 rows: CMsiRNAdb 42,638 + Alnylam
US10240152B2 Tables 2/4/8 108 + recovered Table 13/14 7 + Dicerna
US11697812B2 Table 2 383), same leakage-free grouped split:

- `smepred/src/chem_schema.py` — multi-slot parser + legacy bridge functions
- `smepred/src/features_v2.py` — literature-grounded feature extractor
- `smepred/src/model_b_v2.py` — serving wrapper (blend of legacy+v2 CatBoost)
- `smepred/scripts/data/patent_sources.py` — reproducible per-source ingestion (fixes the Table 13 bug, keeps Dicerna's DNA-lowercase and Alnylam's 2'-OMe-lowercase notations separate)
- `smepred/scripts/train_model_b_v2.py` — single reproducible retrain entrypoint
- `smepred/src/predictor.py` — additive `model_key="B_v2"` path (existing `"B"` path untouched/unaffected — regression-tested)

Final combined result (`smepred/models/model_b_v2_meta.json`, blend = 25% legacy + 75% v2, chosen on the larger in-distribution set):

| Test | N | Spearman |
|---|---:|---:|
| In-distribution (grouped, leakage-free) | 4,269 | 0.489 |
| External real IC50 (never trained on) | 32 | 0.197 (p=0.28, not significant) |

Deliberately **not** wired as the default `"B"` model — its calibration
against the live API's `_normalize_scores(mode="rescale")` hasn't been
validated, and the tiny external test is directional, not conclusive. Safe
to A/B via `model_key="B_v2"` today.

## Recommended next steps (not yet done — need explicit go-ahead before this scale of work)
1. **(Revised — do NOT restore the synthetic CSV; see correction above.)**
   Reconcile the `models/model_b_meta.json` vs `models/model_b.pkl` metric
   discrepancy: the metadata claims an "ensemble" (`model_b_v8_patent.pkl` +
   `finetuned_clean.pkl` blend, headline `0.3158` Spearman) but the file that
   actually loads is a single plain LightGBM Booster reproducing `0.165`. This
   also looks like a genuine local Git-LFS issue independent of the synthetic-data
   question — `model_b.pkl` is LFS-tracked (18.7MB real object per `git log`)
   but the local working copy is a smaller (1.49MB) non-LFS file that predates
   it, and `git lfs pull` silently refuses to overwrite it because it's "locally
   modified." Needs a deliberate decision (force `git lfs checkout`? re-point
   metadata? re-export the real ensemble?) before trusting either artifact.
2. Extend `chem_schema.py`-based parsing to the Alnylam/Dicerna patent tables
   (they use the *compact* lowercase/uppercase/`dT` notation, not compositional
   English names — a separate parser, already prototyped in
   `parse_compact_notation.py`) and combine all sources into one leakage-free,
   grouped-split multi-source training set. This is the real production
   retrain and is a substantially larger effort than this session's ablation.
3. Only then hyperparameter-tune and consider a production swap — this
   session's CatBoost config was intentionally left untuned/fixed on both
   sides of every comparison, for fairness, not for best absolute performance.
4. Spot-check the literature citations against primary sources before any
   external/investor-facing claim (no browsing tool was available this session).
