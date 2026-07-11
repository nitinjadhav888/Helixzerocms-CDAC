# GalNAc 3'-Sense vs 5'-Sense Position: Per-Gene Stratification (2026-07-11, session 5)

Motivated directly by Dr. Adrian's reply (2026-07-11): GalNAc conjugate
positioning effects on efficacy are likely **sequence/gene-dependent**, not a
single universal "3'-sense is always better" rule. This was flagged in
`PLAN_2026-07-11_v2_corrected.md` (item B) as the one genuinely new,
un-investigated piece of follow-up work from his reply. Script:
`scripts/analysis/galnac_position_by_gene.py`. Raw output:
`docs/validations/galnac_position_stratification.json`.

## Data availability (checked first, not assumed)
Only **CMsiRNAdb** (`data/processed/CMsiRNA_data_update.tsv`) has any
recoverable GalNAc positional annotation — confirmed previously that the
Alnylam/Dicerna patent-table sources carry **zero** conjugate markers at all
(0/280 sequences). Of 43,153 CMsiRNAdb rows, **21,971** have a parseable
GalNAc entry in `Modification_Types_Sense_strand`, always at either the very
start (5'-sense, before position 1) or very end (3'-sense, after the last
position) of the modification list — no internal-position placements observed.

**11 genes** have any GalNAc-conjugated rows at all. Of those, **9 are
3'-sense-only** (AGT, ANGPTL3, APP, CTNNB1, HSD17B13, INHBE, MAPT, PLN,
PNPLA3 — 21,208 rows total, zero position contrast possible). Only **2 genes**
have rows at *both* positions: **MARC1** (142 @ 3', 512 @ 5') and **LPA**
(26 @ 3', 123 @ 5').

## Naive result (position vs. mean/median Inhibition, ignoring assay context)

| Gene | n(3') | n(5') | mean Inhibition 3' | mean Inhibition 5' | Direction | Mann-Whitney p |
|---|---|---|---|---|---|---|
| MARC1 | 142 | 512 | 54.5 | 61.9 | **5' higher** | 0.0059 |
| LPA | 26 | 123 | 86.9 | 51.3 | **3' higher** | 3.6e-11 |

Taken at face value, this is a striking confirmation of Adrian's point: the
two genes disagree on direction, both with p≪0.05.

## The confound that has to be reported (found by checking, not assumed)
Before treating either result as a real chemistry effect, `Cell_Type` /
`Concentration` / `Time_of_administration` were checked per position group,
per gene — and **both genes turn out to be perfectly confounded**:

- **MARC1**: 3'-sense rows are 100% *in vitro* (primary mouse hepatocytes /
  Mus musculus cells, nM dosing, 24h). 5'-sense rows are 100% *in vivo*
  (transgenic mice, mg/kg dosing, 28 days). **Zero overlap** in cell type
  between the two position groups.
- **LPA**: same pattern — 3'-sense is 100% *in vitro* (primary human
  hepatocytes, nM, 48h), 5'-sense is 100% *in vivo* (transgenic mice, mg/kg,
  14–28 days). **Zero overlap**.

In both cases, GalNAc position is a perfect stand-in for "in vitro cell-culture
assay" vs. "in vivo animal-dosing assay" — two measurement regimes that are
not comparable on the raw `Inhibition` % scale regardless of chemistry (different
PK/biodistribution, dosing units, timescales, and — critically for GalNAc
specifically — GalNAc-ASGPR-mediated hepatocyte uptake is an *in vivo/whole-
liver* phenomenon that has limited relevance to a dish of hepatocytes in the
first place). There is **no within-gene, within-assay-type comparison
available** — not even a partial one — because the position and the assay
type never co-occur in either direction for either gene.

## Honest conclusion
**This dataset cannot answer Adrian's question**, in either direction, for
either gene. The apparent "genes disagree" result above is real in the sense
that the numbers are exactly as reported, but it is not evidence of a
chemistry-driven positional effect — it is near-certainly (at minimum,
inseparably) an assay-type effect. Reporting the naive numbers as "GalNAc
position affects efficacy in a gene-dependent way" without this caveat would
be a materially misleading claim from real data, not a lie, but a
correlation/confound error that matters. Per the plan's explicit instruction
("report honestly whichever way it comes out, including 'not enough data to
say' as a legitimate conclusion") — that is the finding here: **not testable
from current real-data sources.**

## What would actually answer the question
- New/different real data with matched assay conditions (same cell type or
  same in vivo model, same dosing, same duration) varying *only* GalNAc
  position, for more than one gene. Not present in any source currently
  loaded by `patent_sources.py`.
- Alternatively, restrict to a literature meta-analysis of studies that
  directly vary GalNAc position under matched conditions (this is exactly
  the kind of claim that would need the still-blocked citation spot-check,
  item (d) in the plan, before being asserted external-facing).
- Do **not** attempt to "fix" this by normalizing across assay type
  statistically (e.g. z-scoring within cell type) — with zero overlap, there
  is no shared reference point to normalize against; the position effect and
  the assay effect are not merely correlated, they are mathematically
  unidentifiable from each other in this data.

## Status
Adrian's question remains open and **should not be assumed answered** by
this analysis — this is a negative/inconclusive result, not a null result to
discard. If new matched-condition GalNAc position data becomes available
(real, not synthetic — see `CLAUDE.md` fact #1 on why synthetic data is
excluded), rerun `scripts/analysis/galnac_position_by_gene.py` against it.
