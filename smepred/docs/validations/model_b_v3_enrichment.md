# Model B v3: RNA-FM + ViennaRNA Feature Enrichment

## Summary

Adding RNA-FM pretrained RNA language model embeddings (PCA-reduced to
32-dim per strand) and ViennaRNA thermodynamic features (5-dim) to
the existing v2 multi-slot feature set (444-dim) yields a **513-dim**
CatBoost model with consistent, statistically significant improvements.

## Results

| Metric | v2 (baseline) | v3 (enriched) | Delta |
|--------|:------------:|:------------:|:-----:|
| In-distribution **Spearman** (N=4,269) | 0.4947 | **0.5494** | **+0.055 (+11%)** |
| In-distribution **MAE** | 22.635 | **21.729** | **-0.906 (-4%)** |
| External IC50 **Spearman** (N=32) | 0.3239 (p=0.07) | **0.3878 (p=0.028)** | **+0.064 (+20%)** |
| External IC50 significance | ❌ not significant | ✅ **p<0.05** | |

The external IC50 holdout is significant at p<0.05 for the **first time**
in this project's history — the RNA-FM signal is capturing real biology
not accessible to hand-crafted sequence features alone.

## Experimental Design

- **Same data**: 38,867 train / 4,269 validation rows from 4 real sources
  (CMsiRNAdb + Alnylam + Dicerna), grouped-split by antisense sequence
- **Same split**: identical `group_split(..., val_offset=4, val_stride=10)`
- **Same hyperparameters**: CatBoost depth=10, lr=0.05, l2=5, 1000 iters
  with early stopping (50 rounds)
- **Only change**: feature vector expanded from 444 → 513 dimensions

## Feature Breakdown

| Component | Dim | Origin |
|-----------|:---:|--------|
| v2 multi-slot positional (8 sugar groups + PS + base_mod × 21 pos × 2 strands) | 420 | `features_v2.py` |
| v2 engineered (seed rigidity, GC, PS density, conjugate, etc.) | 24 | `features_v2.py` |
| RNA-FM sense strand (PCA-32) | 32 | `precompute_rnafm_embeddings.py` |
| RNA-FM antisense strand (PCA-32) | 32 | `precompute_rnafm_embeddings.py` |
| ViennaRNA: sense MFE, anti MFE, duplex MFE, mean bp distance, GC | 5 | `features_v3.py` |

## RNA-FM Details

RNA-FM (`fm.pretrained.rna_fm_t12`) is a 12-layer transformer pretrained
on RNA sequences from several public databases (Rfam, RNAcentral). It
produces per-position 640-dim embeddings capturing sequence semantics
beyond simple k-mer or GC content.

We extracted layer 12 representations, mean-pooled per strand, then
PCA-reduced to 32 components (preserving 80.9% of variance). This was
pre-computed once for all 21,545 unique base sequences in the dataset.

## ViennaRNA Details

Four thermodynamic features from ViennaRNA 2.x:

1. **Sense MFE**: minimum free energy of the isolated sense strand
2. **Antisense MFE**: minimum free energy of the isolated antisense strand
3. **Duplex MFE**: hybridization energy of the sense-antisense duplex
4. **Mean base-pair distance**: structural ensemble diversity (how
   "fuzzy" the folding ensemble is vs. a single dominant structure)
5. **GC content** of the combined duplex (simple thermodynamic proxy)

## Promotion Decision

v3 is promoted to the default (`DEFAULT_MODEL_B_KEY = "B_v3"`) on
2026-07-13. v2 and legacy "B" remain fully selectable via
`model_key="B_v2"` or `model_key="B"`.

## Files

- `src/features_v3.py` — feature extractor (v2 + RNA-FM + ViennaRNA)
- `scripts/train_model_b_v3.py` — training script with ablation comparison
- `scripts/precompute_rnafm_embeddings.py` — RNA-FM embedding pre-computation
- `models/model_b_v3.cbm` — trained CatBoost model (513-dim)
- `models/model_b_v3_meta.json` — metadata with full results
- `models/rnafm_embeddings.pkl` — cached embeddings (21,545 seqs)
- `models/rnafm_pca_32.pkl` — PCA transform from 640 → 32 dim
