"""
split_utils.py -- reproducible leakage-free grouped splits for Model B.

Grouping is by antisense sequence (Row.group_key) so that near-identical
duplexes never straddle two partitions (the leakage guard used across the
v2 / v3 pipelines).

The TEST partition is LOCKED: its group keys are written to disk on the
first run and reloaded on every later run. This guarantees the test set can
never silently drift or be tuned against -- even if the split offsets are
later changed -- which is the whole point of a held-out test.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

import pandas as pd

MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
DEFAULT_LOCK_PATH = MODELS_DIR / "locked_test_groups.json"


def group_split(rows, val_stride=10, val_offset=4):
    """2-way grouped split (legacy -- kept for v2 parity)."""
    keys = pd.Series([r.group_key for r in rows])
    eff = pd.Series([r.efficacy for r in rows])
    grp_mean = eff.groupby(keys).mean().sort_values(ascending=False)
    val_groups = set(grp_mean.index[val_offset::val_stride])
    is_val = keys.isin(val_groups).to_numpy()
    return ([r for r, v in zip(rows, is_val) if not v],
            [r for r, v in zip(rows, is_val) if v])


def _group_order(rows):
    """Return group keys sorted by descending mean efficacy (stable order)."""
    keys = pd.Series([r.group_key for r in rows])
    eff = pd.Series([r.efficacy for r in rows])
    grp_mean = eff.groupby(keys).mean().sort_values(ascending=False)
    return list(grp_mean.index)


def _load_locked(path: Path):
    if path.exists():
        with open(path) as f:
            return set(json.load(f))
    return None


def _save_locked(test_groups, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(sorted(test_groups), f, indent=2)


def group_split_3way(rows, val_stride=10, val_offset=5, test_offset=0,
                     lock_path: Optional[Path] = None):
    """3-way grouped split: train / val (early-stopping) / locked test.

    Partitioning is by group index in the descending-efficacy-ordered group
    list, so each partition spans the full efficacy range:
        test  <- groups at index i where i % stride == test_offset
        val   <- groups at index i where i % stride == val_offset
        train <- everything else
    With stride=10 this is ~80% / 10% / 10%.

    `lock_path`: if it exists, the locked test groups are loaded from it and
    forced as the test partition (ignoring test_offset). On first run the
    chosen test groups are written there so the set is frozen forever.
    """
    lock_path = Path(lock_path) if lock_path else DEFAULT_LOCK_PATH
    ordered = _group_order(rows)

    locked = _load_locked(lock_path)
    if locked is not None:
        test_groups = locked
    else:
        test_groups = {ordered[i] for i in range(len(ordered))
                       if i % val_stride == test_offset}
        _save_locked(test_groups, lock_path)

    val_groups = {ordered[i] for i in range(len(ordered))
                  if i % val_stride == val_offset}

    train, val, test = [], [], []
    for r in rows:
        if r.group_key in test_groups:
            test.append(r)
        elif r.group_key in val_groups:
            val.append(r)
        else:
            train.append(r)
    return train, val, test
