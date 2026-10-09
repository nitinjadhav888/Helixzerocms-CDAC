# 08. DATA CLEANING & PREPROCESSING
## Quality Control, Deduplication, and Normalization Accounting
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  
**Cross-Reference Accounting:** `preprocessing_accounting.md`  

---

### 1. Data Cleaning Accounting Pipeline

To ensure absolute scientific rigor and data integrity, data preprocessing enforces strict quality-control gates across all ingested empirical records:

| Processing Step | Record Count ($N$) | Records Excluded | Justification & Exclusion Criteria |
| :--- | ---: | ---: | :--- |
| **Published CMsiRNAdb Total** | 43,153 | — | Initial release from PMC12870949 (January 2026). |
| **Multi-Slot Chemical Format Normalization** | 42,638 | 515 | Non-standard modification symbols unparseable into orthogonal slots or missing quantitative numerical readouts. |
| **Missing Sequence Verification** | 42,638 | 0 | Both sense and antisense sequences verified present and 100% parseable. |
| **Missing Efficacy Verification** | 42,638 | 0 | All retained records report quantitative percentage silencing readouts. |
| **GroupKFold Multi-Dose Clean Matrix** | **17,761** | 24,877 | Filtered strictly for entries possessing validated concentration titrations, incubation durations, and target gene metadata required for sequence-disjoint GroupKFold partitioning. |

---

### 2. Specific Data Cleaning Operations

1. **Knockdown Percentage Bounds Enforcement:**
   - Raw luciferase or qPCR ratios are converted to biological knockdown percentages:
     $$\text{KD\%} = 100.0 - \text{Remaining mRNA\%}.$$
   - Efficacy readouts are clamped to $[0.0, 100.0]\%$. Assay artifacts with negative values or values exceeding $120.0\%$ are discarded.

2. **Deduplication and Assay Replicate Aggregation:**
   - Where identical sequence-chemistry configurations were tested in multiple biological replicates under identical concentrations, assays were averaged to establish the empirical mean response.
   - Replicates tested at different concentrations were preserved as distinct dose titration points.

3. **Chemical Alphabet Canonicalization:**
   - Non-canonical strings (e.g. `2'-O-methyl`, `OMe`, `m`) mapped to standardized code `M`.
   - $2'$-Fluoro strings mapped to `F`.
   - Phosphorothioate linkages mapped to `S`.
   - Overhang notations (e.g. `dTdT`, `dUdU`, `TsT`) resolved to explicit $3'$ positions.

4. **Sequence Disjoint Grouping Key Generation:**
   - Terminal dinucleotide overhangs (positions 20–21) are stripped to extract the invariant 19-nucleotide core antisense guide sequence (`anti_seq`).
   - This core sequence acts as the invariant clustering key for `GroupKFold`, guaranteeing zero sequence leakage across splits.
