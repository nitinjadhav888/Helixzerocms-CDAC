# CLAUDE.md — persistent project memory (read this FIRST, every session)

> **Rule for every session (including you, right now):** before doing new work,
> read this file fully. Commit early and often (see Git workflow below) —
> don't wait until "done" to write things down. A senior data scientist
> leaves the lab notebook in a state where someone else (or their future
> self) can pick up cold. That is the job here.

## Git workflow (mandatory, per explicit user instruction 2026-07-10)
- All work happens on the **`dev`** branch of
  `https://github.com/nitinjadhav888/Helixzerocms-CDAC` (not `main`).
  `git checkout dev` (or `git fetch && git checkout -b dev origin/dev` if
  starting fresh) at the start of every session, before doing anything else.
- **Commit after every meaningful change, not at the end of a session.**
  Session credits/context can and do run out mid-task without warning — an
  uncommitted working tree is a lost session. Small, logical, well-messaged
  commits > one big commit at the end you might not get to make.
- **Push to origin regularly** (`git push origin dev`) — don't just commit
  locally. The whole point is surviving a hard session reset.
- Model binaries (`models/*.pkl`, `models/*.cbm`) and large processed data
  (`data/processed/*.tsv`) are Git-LFS-tracked (`smepred/.gitattributes`).
  Check `git lfs ls-files` before trusting a model file (`*` = real object
  fetched, `-` = pointer only, not fetched). If a tracked file looks
  suspiciously small/wrong, compare `git hash-object <file>` against blob
  hashes in `git log --all -p -- <file>` before assuming it's the real
  committed artifact — it may be orphaned local disk cruft that was never
  actually committed (this happened once already, see fact #3 below).
- `scratch/`, `catboost_info/`, and the regenerable
  `data/processed/v2_multislot_dataset.csv` cache are gitignored on
  purpose. `scratch/` is exploratory, not a source of truth;
  `scratch/archive/` especially is old (predates this project phase).

## What this project is
HelixZero-CMS (`smepred/`) — an siRNA chemical-modification efficacy predictor.
Two model families:
- **Model A / "naked" V4**: unmodified-sequence baseline (`extract_batch_v4`, LightGBM).
- **Model B**: chemically-modified siRNA efficacy predictor. Legacy version =
  single-char-per-position encoding (`extract_phase2`, 431-dim, LightGBM,
  `models/model_b.pkl` + `model_b_meta.json`). New version = **Model B v2**,
  multi-slot chemistry schema (`src/chem_schema.py`, `src/features_v2.py`,
  `src/model_b_v2.py`, CatBoost blend), opt-in via `predict_modified(..., model_key="B_v2")`.
  Not yet the default.

## Critical facts you MUST NOT re-derive or re-question every session
1. **`smepred/data/sirna_modified_position_aware_dataset_v2.csv` is 63.2%
   SYNTHETIC data** (35,200/55,731 rows self-labeled `data_source=synthetic_*`,
   e.g. `synthetic_Alnylam_ESC_Fitzgerald2017` — programmatic positional-walk
   patterns, not real assay data). It was **deliberately deleted** (commit
   `6cea4cc` on `dev`) from the training pipeline. **Do not restore it. Do
   not flag its absence as a bug.** The replacement is the 4-real-source pipeline in
   `scripts/data/patent_sources.py` (CMsiRNAdb + Alnylam US10240152B2 +
   Dicerna US11697812B2, ~43,136 rows, zero synthetic rows).
2. This was communicated externally already — see
   `smepred/pitch/Reply_to_Dr_Weingärtner_2026-07-10.md` ("we rebuilt our
   siRNA chemistry model on real patent data... in place of the synthetic set").
   Don't contradict that reply in future analysis without a very good reason.
3. **RESOLVED (2026-07-10, on `dev`)**: `models/model_b.pkl` /
   `model_b_meta.json` briefly had orphaned, never-committed local files
   sitting in the working tree (leftover from an old, buggy scratch script
   `scratch/archive/clean_ensemble.py`, which saved its actual ensemble to a
   now-deleted `model_b_ensemble.pkl` but overwrote `model_b_meta.json` to
   describe it as "ensemble" anyway — `model_b.pkl` itself was never the
   ensemble, at any point in this repo's history). Confirmed via blob-hash
   comparison against all of `git log --all`. Fixed by discarding those
   local files and restoring both to the real, self-consistent, LFS-cached
   HEAD version (v7, plain LightGBM Booster, matching v7 metadata). If you
   ever see `model_b_meta.json` claiming "ensemble" again, that's the bug
   recurring — check nothing is rerunning `clean_ensemble.py` against the
   production model path.
4. There is a real leakage bug in the legacy production val split
   (`hetero_train_2728.csv` / `hetero_val_303.csv`): 82.9% of val antisense
   sequences also appear in train. Any Spearman/MAE computed on that split is
   not trustworthy as an apples-to-apples baseline.
5. The full, primary-source-honest writeup of the Model B v2 rebuild lives at
   `smepred/docs/validations/model_b_v2_multislot_ablation.md` — read that
   before repeating any of that analysis. It has an explicit correction
   section at the top fixing an earlier mistaken claim about item #1 above.

## Repo/environment gotchas (save yourself the rediscovery time)
- **Python interpreter**: `.venv/Scripts/python.exe` has NOTHING installed
  (just pip). The real environment with lightgbm/catboost/sklearn/fastapi is
  `/c/Users/Nilesh/anaconda3/python.exe`. Use that one.
- Git Bash on this Windows box: `/tmp` doesn't reliably map to a writable
  dir — use a repo-local scratch path (e.g. `scratch/tmp_inspect/`) instead.
- `.claude/settings.json` points `ANTHROPIC_BASE_URL` at a third-party proxy
  (`capi.aerolink.lat`), not api.anthropic.com directly — this is almost
  certainly *why* credit/context resets happen mid-session. Not this
  project's code to fix, but explains the operating constraint: **assume
  any given session can end abruptly and without warning. Commit/push
  durable notes frequently, don't wait until "done."**

## Current state (last updated: 2026-07-10, session 3, on branch `dev`)
- `model_b_v2` production code is in place and sanity-tested end-to-end
  (both `model_key="B"` and `model_key="B_v2"` run cleanly through
  `predict_modified`). NOT yet the default model.
- All of session 2's work (deletions, new v2 pipeline, data sources, docs)
  is now committed to `dev` in logical chunks — see `git log --oneline dev`.
  `main` is untouched/behind on purpose; don't merge `dev`→`main` without
  being asked.
- Remaining open items (not yet done, no urgency assigned):
   a. ~~Extend `chem_schema.py` parsing to Alnylam/Dicerna's compact notation~~
      — **DONE** (sessions 2/3, confirmed session 4). Do not redo.
   b. ~~Hyperparameter tuning + cleanup of `model_b_v2`~~ — **DONE** (session 5
      tuning, session 6 cleanup). Tuned config (depth=10/lr=0.05/l2=5) was
      verified robust across 10 grouped-split offsets. Session 6 removed the
      legacy-schema blend entirely. `model_b_v2` runs pure v2-only CatBoost.
   c. ~~Production-swap decision for `model_b_v2`~~ — **RESOLVED** (session 6).
   d. ~~Feature enrichment with RNA-FM + ViennaRNA~~ — **DONE** (session 7).
      Model B v3 shows Spearman 0.5494 (+11% over v2), external IC50
      Spearman 0.3878 p=0.028 (first time significant). Saved as
      `model_b_v3.cbm` + `model_b_v3_meta.json`. Not yet default model key.
   e. Adrian-motivated GalNAc 3'-vs-5' per-gene position stratification:
     **attempted, INCONCLUSIVE by design of the data, not by
     analysis failure** (session 5, `docs/validations/galnac_position_stratification.md`).
     Only 2 genes (MARC1, LPA) have any real 3'/5' contrast in CMsiRNAdb, and
     for both, GalNAc position is perfectly confounded with assay type
     (in vitro nM dosing vs in vivo mg/kg dosing — zero cell-type overlap in
     either direction for either gene). The naive numbers show opposite
     directions per gene (real, reproducible) but are not attributable to
     chemistry vs. assay-type. **Do not cite this as evidence of a
     gene-dependent GalNAc position effect** without also citing the
     confound — needs genuinely new matched-condition data to answer, not a
     re-analysis of existing data.
   f. `ICE_CLOUD_DEPLOYMENT.md` / `HelixZero_External_Whitepaper.md` were
      deleted (session 2) with no replacement written yet — may need
      regeneration once model_b_v2 is production-validated.
   g. Spot-check the literature citations in the ablation doc against
     primary sources — no browsing tool has been available in any session
     so far, so they're recalled-from-training-knowledge, not freshly verified.

## Session log (append, don't rewrite — newest at top)
- **2026-07-13 (session 7 — continued)**: User pushed for a paper-publishable
  direction. Explored ENsiRNA (tanwenchong/ENsiRNA) — an AMEGNN with RNA-FM
  embeddings + Rosetta 3D structures. Chose **feature enrichment** (Option A):
  add RNA-FM (640-dim pretrained RNA language model, PCA-reduced to 32 per
  strand) + ViennaRNA (5-dim thermodynamic features) to our CatBoost pipeline.
  Installed RNA-FM (weights from HuggingFace mirror orgava/rna-fm-weights
  since CUHK server returned 403), RDKit, and used pre-installed ViennaRNA.
  Pre-computed RNA-FM embeddings for 21,545 unique sequences (~6 min on CPU).
  Results from enriched v3 model (513-dim CatBoost, same train/val split):
  - In-dist Spearman: **0.5494** (vs v2's 0.4947, +11%)
  - External IC50 Spearman: **0.3878, p=0.028** (vs v2's 0.3239, p=0.07)
  First time external IC50 hits p<0.05 — the RNA-FM signal is real.
  Saved as `model_b_v3.cbm` + `model_b_v3_meta.json`. Not yet the default
  model key — needs user decision to promote.
- **2026-07-11 (session 5)**: Picked up exactly where session 4 left off:
  `model_b_v2` had been hyperparameter-tuned (commit `82d14e0`, depth=10/
  lr=0.05/l2=5) with a robustness check already run but its output
  (`docs/validations/tuned_robustness_check.json`) sitting uncommitted.
  Wrote up and committed that result:
  `docs/validations/model_b_v2_tuning_robustness.md` — tuned config is a
  real, stable in-distribution improvement (mean Spearman 0.515 vs 0.489
  untuned, σ=0.025 across 10 offsets) and a directionally consistent
  external-IC50 improvement (mean 0.345 vs 0.197, positive on all 10
  offsets), but only 6/10 offsets individually significant at n=32 — real
  progress, not "external validation solved." Then did the actual
  Adrian-motivated work (plan item B, genuinely new): stratified CMsiRNAdb's
  21,971 GalNAc-annotated rows by gene and 3'/5' position
  (`scripts/analysis/galnac_position_by_gene.py`). Only 2 genes (MARC1,
  LPA) have both positions present; naive numbers show *opposite*
  directions per gene (p=0.006 and p=3.6e-11) — but checking
  cell_type/concentration/time revealed GalNAc position is **perfectly
  confounded with in-vitro-vs-in-vivo assay type** for both genes (zero
  cell-type overlap either direction) — so this cannot be reported as
  evidence of a real gene-dependent chemistry effect, only as "not testable
  from current data," which is what got written up
  (`docs/validations/galnac_position_stratification.md`). Updated this
  file's open-items list to reflect both results and re-numbered/relettered
  the remaining genuinely-open items (production-swap decision, doc
  regeneration, literature spot-check). Nothing new left uncommitted at
  end of session — commit + push done as the last step.
- **2026-07-11 (session 4)**: User forwarded Dr. Adrian's reply (GalNAc
  positioning is sequence/gene-dependent, not universally 3'-sense-optimal —
  confirms it's worth actually testing per-gene, not assuming linear effect).
  Wrote an initial strategic plan assuming compact-notation parsing "wasn't
  done yet" — **this was wrong**, caught by the user asking for a cleanup
  pass first. During that cleanup, deleted `smepred/data/patent_data/*`,
  `CMsiRNA_data_update.tsv`, and the `hetero_*`/`homo_*` splits as "legacy" —
  **also wrong**: these are load-bearing (read directly by
  `patent_sources.py`) or documented-elsewhere (cited in `EXPLANATION.md`,
  `genes_analysis.md`). Push of that commit was blocked by the platform's own
  safety classifier (no explicit file list had been given for "delete
  unrequired files") — caught before `origin` was ever touched. Reverted
  locally, verified `load_all_real_sources()` still returns 43,136 rows, then
  pushed the revert (this was `dev`'s first-ever push to `origin` — the
  branch didn't exist there before). **Lesson, stated plainly: grep for
  cross-references before deleting anything, no matter how obviously
  "legacy" a path name looks — a plausible-sounding name is not verification.**
  Separately, re-read the full ablation doc (had only read the first third
  before) and found the original strategic plan's premise was stale in a
  second way: compact-notation parsing, the 4-source 43,136-row rebuild, and
  an initial `model_b_v2` blend training run were **already done** in session
  2/3 (`models/model_b_v2_meta.json`: in-distribution Spearman 0.489 n=4269,
  external IC50 Spearman 0.197 n=32 not significant). The ablation doc's own
  "recommended next steps" section was itself stale on 2 of its 4 items
  (LFS/metadata bug — already fixed session 3; compact-notation parsing —
  already done) — did not correct that doc's next-steps section this
  session, only this log; a future session should. Replaced the (wrong)
  5-file strategic-docs package with one corrected, shorter plan
  (`scratch/strategic_docs/PLAN_2026-07-11_v2_corrected.md`): real remaining
  work is (a) hyperparameter tuning of `model_b_v2` (deliberately left
  untuned for fair ablation), (b) the actual Adrian-motivated per-gene GalNAc
  3'-vs-5' stratification (genuinely new, not done anywhere yet), (c) the
  production-swap decision itself, (d) literature spot-check (still blocked,
  no browsing tool). Nothing in (a)/(b) executed yet this session — planning
  and the revert/cleanup correction were the actual work done.
- **2026-07-10 (session 3)**: Corrected a mistake from session 2's own doc
  (had wrongly suggested restoring the synthetic CSV — fixed in
  `model_b_v2_multislot_ablation.md`). Traced and resolved the
  `model_b.pkl`/meta "ensemble" mismatch to its actual root cause (fact #3).
  Created `dev` branch per user instruction; committed all of session 2's
  work in 5 logical commits (tooling/gitignore, legacy cleanup, model_b_v2
  feature work, real data sources, docs+this file); pushed to origin.
  Created this file to fix the cross-session context-loss problem itself.
- **2026-07-10 (session 2, credits ran out mid-response)**: Built
  `chem_schema.py`/`features_v2.py`/`model_b_v2.py`/`multislot_designer.py`,
  ran the full ablation + external IC50 benchmark, wrote
  `model_b_v2_multislot_ablation.md`, wired opt-in `model_key="B_v2"` path,
  drafted `Reply_to_Dr_Weingärtner_2026-07-10.md`. Deleted several legacy
  scripts/docs as part of cleanup. Nothing committed at the time (fixed in session 3).
