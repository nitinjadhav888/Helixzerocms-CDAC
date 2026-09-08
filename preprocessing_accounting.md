# CMsiRNAdb Preprocessing Accounting

| Step | N | Removed | Reason |
|:---|---:|---:|:---|
| Published CMsiRNAdb total | 43,153 | — | Source: PMC12870949 (Jan 2026) |
| Loaded from processed CSV | 42,638 | 515 | Multi-slot parsing, format normalization |
| Drop missing sense_seq / anti_seq | — | 0 | Sequences not parseable |
| Drop missing efficacy | — | 0 | No silencing % reported |
| Drop missing patent_id / target_gene | — | — | Required for zero-leakage grouping |
| **Final analysis set** | **42,638** | **515** | **Used in all benchmarks** |

> The gap of 515 entries (1.2%) between published total and our analysis set is due to: (1) multi-slot chemical notation parsing failures for non-standard modification codes, (2) entries with missing quantitative efficacy values (qualitative-only), and (3) entries without a parseable patent identifier for zero-leakage grouping.

*Generated: 2026-08-13 09:39 UTC*