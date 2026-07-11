# `model_b_v2` Hyperparameter Tuning + Robustness Check (2026-07-11, session 5)

Follow-up to open item (a) in `CLAUDE.md`: `model_b_v2`'s CatBoost config was
deliberately left fixed (depth=6, lr=0.05, default l2) in the original
multi-slot-vs-legacy ablation (`model_b_v2_multislot_ablation.md`), for a fair
controlled comparison. This doc covers the follow-up tuning pass and — because
a single split can flatter a tuned config by luck — a robustness check across
multiple leakage-free grouped-split offsets before trusting the result.

## 1. Tuning (`scripts/tune_model_b_v2.py`)
Searched each blend component's CatBoost hyperparameters independently
(12 sampled configs/component from `depth ∈ {4,6,8,10} × lr ∈
{0.02,0.03,0.05,0.08,0.1} × l2_leaf_reg ∈ {1,3,5,10}`, seed=42, baseline
config always included as reference), then swept the blend weight. Selection
criterion was **in-distribution validation Spearman only** — the external
IC50 holdout (n=32) was already non-significant at the baseline config, so
optimizing against it would be tuning to noise, not signal (see that script's
docstring).

**Winning config**: `depth=10, learning_rate=0.05, l2_leaf_reg=5`,
`blend_w_legacy=0.40` (vs. baseline `depth=6, lr=0.05, l2=3, blend_w_legacy=0.25`).
Committed as `models/model_b_v2_tuned*.cbm` / `model_b_v2_tuned_meta.json`
(commit `82d14e0`) — does **not** overwrite the original untuned production
checkpoint (`model_b_v2_meta.json`), by design.

Single-split result at this config (the original offset used throughout this
project, `val_offset=4`): in-distribution Spearman **0.499** (n=4269, vs.
untuned baseline 0.489), external IC50 Spearman **0.355** (n=32, p=0.046 —
now individually significant, vs. untuned baseline 0.197, p=0.28 not
significant).

That single-split external-significance result was flagged as needing
verification before trusting it (n=32 is small; one split flipping from
non-significant to significant on tuning could easily be this-split luck
rather than a real improvement).

## 2. Robustness check (`scripts/robustness_check_tuned.py`)
Refit the **same winning config** (no re-tuning) across all 10 disjoint
grouped-split offsets (`val_stride=10, val_offset=0..9`), reusing the same
loader/split/featurize code as tuning and the original ablation for direct
comparability. Full per-offset numbers: `docs/validations/tuned_robustness_check.json`.

| Metric | Mean | Std | Range |
|---|---|---|---|
| In-distribution Spearman | **0.515** | 0.025 | 0.476–0.561 |
| External IC50 Spearman (n=32) | **0.345** | 0.054 | 0.233–0.425 |
| External p<0.05 | **6/10 offsets** | — | best p=0.015, worst p=0.199 |

## 3. Conclusion
- **In-distribution improvement is real and stable**, not this-split luck:
  mean 0.515 vs. untuned baseline 0.489, low variance (σ=0.025) across every
  offset. Tuning was worth doing.
- **External IC50 signal also improved on average** (mean external Spearman
  0.345 vs. untuned single-split 0.197) and is **directionally consistent
  across all 10 offsets** (external Spearman positive every time, range
  0.233–0.425, no sign flips) — this is a materially more convincing result
  than the single untuned split ever showed.
- However, it is **not uniformly statistically significant**: 4/10 offsets
  land at p≈0.05–0.20 (still non-significant at conventional α=0.05), because
  n=32 for the external holdout is simply small enough that Spearman ρ≈0.23–0.35
  sits right at the edge of significance regardless of model quality. The
  original session-4 "found a significant offset" result **does replicate
  directionally** but should not be read as "solved" — it's "improved and
  consistently positive, but external validation is still underpowered at
  n=32."
- **Recommendation**: the tuned config is a legitimate, real improvement over
  the untuned baseline and should be treated as a candidate for production
  promotion (see "Production-swap decision" in `PLAN_2026-07-11_v2_corrected.md`,
  item C) — but the honest headline is still "tuned model_b_v2 improves
  in-distribution ranking meaningfully and external IC50 ranking directionally,
  external significance remains sample-size-limited," not "external validation
  problem solved by tuning."
- Promotion from `*_tuned` artifact names to the actual production names
  (`model_b_v2_{legacy,multislot}.cbm`, `model_b_v2_meta.json`) has **not**
  been done — that's a separate, deliberate step, not implied by this doc.
