# Model B v3 — Locked Held-Out Test Set

## Why this exists

The original v3 validation (`model_b_v3_enrichment.md`) reported the
in-distribution Spearman (0.5494) on the **validation partition**, which is
also used for CatBoost early stopping. That number is therefore
tuning-adjacent / optimistic: it is not a clean estimate of generalization.
There was no third, untouched partition. This doc fixes that gap by
introducing a **locked test set** that is never used for early stopping or
any tuning.

## Method

`scripts/data/split_utils.py::group_split_3way` partitions the 43,136
training rows into three groups by **antisense sequence** (the same leakage
guard used everywhere in the v2/v3 pipelines), spread evenly across the
efficacy range:

| Partition | Selection | Rows |
|-----------|-----------|-----:|
| train     | remaining groups | 35,201 |
| val       | every 10th group (offset 5) | 3,765 |
| **test**  | every 10th group (offset 0) | **4,170** |

The **test partition's group keys are frozen to disk**
(`models/locked_test_groups.json`) on first run and reloaded on every later
run. Changing split offsets cannot move a frozen group out of test, so the
test set can never silently drift or be tuned against — the whole point of a
held-out test.

The model is trained on `train` only, with early stopping on `val`. `test`
is touched exactly once, at the end, for reporting.

## Results

| Metric | Partition | N | Spearman | MAE |
|--------|-----------|--:|---------:|----:|
| In-distribution (early-stopping-adjacent) | val | 3,765 | 0.5379 | 21.647 |
| **In-distribution (LOCKED, unseen)** | **test** | **4,170** | **0.5616** | **21.452** |
| Out-of-distribution (Alnylam IC50) | external | 32 | 0.3698 (p=0.037) | — |

## Interpretation

- The honest in-distribution generalization estimate is **0.5616**, slightly
  *above* the previously reported 0.5494 (which was on the early-stopping
  val set). The model is at least as good as earlier docs claimed — the
  earlier number was just optimistically placed, not wrong about direction.
- External IC50 significance holds (p=0.037 < 0.05), consistent with the
  original v3 result.

## Remaining caveats (carry-over, not resolved here)

1. **Single-source dominance.** Of the 35,201 train rows, 34,808 (98.9%)
   are CMsiRNAdb; the other three sources total ~393 rows. The "4 real
   sources" are effectively 1 large source + 3 tiny ones. The model likely
   overfits CMsiRNAdb assay specifics; true generalization rests on the
   n=32 external set.
2. **External set is small (n=32).** p=0.037 is real but fragile to a single
   outlier; a second independent IC50/knockdown source is the highest-value
   next step.
3. **Test is in-distribution** (same 4 sources). It guards against
   overfitting/tuning leakage but not against distribution shift. The
   external set covers that, weakly.
4. **Train set is 8/10 (35,201) vs the prior 9/10.** A conservative choice
   to keep test pure; a deployed model could be refit on train+val (all
   non-test data) later without touching the reported test number.

## Reproducibility

```
python -m smepred.scripts.train_model_b_v3
```

- Split logic: `scripts/data/split_utils.py`
- Frozen test keys: `models/locked_test_groups.json`
- ViennaRNA features are disk-cached (`models/vienna_features_cache.pkl`) so
  re-runs are fast and identical.
