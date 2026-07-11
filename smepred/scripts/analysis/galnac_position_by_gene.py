"""
galnac_position_by_gene.py -- Adrian-motivated question: is GalNAc conjugate
position (3'-sense vs 5'-sense) on efficacy gene/sequence-dependent, or
does it have a consistent universal direction?

Only CMsiRNAdb (`data/processed/CMsiRNA_data_update.tsv`) has any real GalNAc
positional variation -- confirmed separately (see
`docs/validations/model_b_v2_multislot_ablation.md` / PLAN_2026-07-11_v2) that
the Alnylam/Dicerna patent-table sources carry zero recoverable GalNAc
annotation at all (0/280 sequences have any conjugate marker), so they cannot
contribute to this question.

GalNAc position is read directly off `Modification_Types_Sense_strand`: the
conjugate entry (`...GalNAc...`) has no numeric `N*` prefix and is appended to
the `||`-joined list either first (before position 1 -> 5'-sense) or last
(after the final position -> 3'-sense). No internal-position GalNAc entries
were observed in this dataset.

IMPORTANT CAVEAT (found by this script, not assumed going in): whichever way
the per-gene numbers come out, check `Cell_Type`/`Concentration`/
`Time_of_administration` before treating a position difference as a chemistry
effect -- see output for whether assay-type is confounded with position for
the genes analyzed.
"""
from __future__ import annotations
import json
from pathlib import Path

import pandas as pd
from scipy.stats import mannwhitneyu

CMS_TSV = Path(__file__).parent.parent.parent / "data/processed/CMsiRNA_data_update.tsv"
OUT_PATH = Path(__file__).parent.parent.parent / "docs/validations/galnac_position_stratification.json"


def galnac_position(mod_type_string: str) -> str | None:
    parts = [p.strip() for p in str(mod_type_string).split("||")]
    gal_idx = [i for i, p in enumerate(parts) if "GalNAc" in p]
    if not gal_idx:
        return None
    i = gal_idx[0]
    if i == 0:
        return "5prime"
    if i == len(parts) - 1:
        return "3prime"
    return "internal"  # not observed in practice, but don't silently mislabel if it occurs


def main():
    df = pd.read_csv(CMS_TSV, sep="\t", low_memory=False)
    gal = df[df["Modification_Types_Sense_strand"].astype(str).str.contains("GalNAc", case=False, na=False)].copy()
    gal["galnac_pos"] = gal["Modification_Types_Sense_strand"].astype(str).apply(galnac_position)
    gal["Inhibition"] = pd.to_numeric(gal["Inhibition"], errors="coerce")
    gal = gal[gal["Inhibition"].between(-50, 150)]
    gal["Inhibition"] = gal["Inhibition"].clip(0, 100)

    per_gene_counts = gal.groupby(["Target_Gene", "galnac_pos"]).size().unstack(fill_value=0)
    genes_with_both = per_gene_counts[
        (per_gene_counts.get("3prime", 0) > 0) & (per_gene_counts.get("5prime", 0) > 0)
    ].index.tolist()

    results = {
        "purpose": (
            "Test whether GalNAc 3'-sense vs 5'-sense position has a "
            "consistent-direction efficacy effect, or is gene-dependent "
            "(per Dr. Adrian's 2026-07-11 reply)."
        ),
        "total_rows_with_galnac_annotation": int(len(gal)),
        "n_genes_with_any_galnac_data": int(gal["Target_Gene"].nunique()),
        "per_gene_position_counts": {
            g: {k: int(v) for k, v in row.items()} for g, row in per_gene_counts.to_dict(orient="index").items()
        },
        "genes_with_both_positions_present": genes_with_both,
        "per_gene_comparison": [],
    }

    for gene in genes_with_both:
        sub = gal[gal["Target_Gene"] == gene]
        g3 = sub[sub["galnac_pos"] == "3prime"]
        g5 = sub[sub["galnac_pos"] == "5prime"]
        u, p = mannwhitneyu(g3["Inhibition"], g5["Inhibition"], alternative="two-sided")

        def assay_summary(d):
            return {
                "cell_type": d["Cell_Type"].value_counts().to_dict(),
                "concentration": d["Concentration"].value_counts().to_dict(),
                "time_of_administration": d["Time_of_administration"].value_counts().to_dict(),
                "n_unique_antisense": int(d["Antisense_seqence"].nunique()),
            }

        assay_3 = assay_summary(g3)
        assay_5 = assay_summary(g5)
        # confounded iff the two position groups don't share ANY cell type
        confounded = len(set(assay_3["cell_type"]) & set(assay_5["cell_type"])) == 0

        results["per_gene_comparison"].append({
            "gene": gene,
            "n_3prime": int(len(g3)),
            "n_5prime": int(len(g5)),
            "mean_inhibition_3prime": float(g3["Inhibition"].mean()),
            "mean_inhibition_5prime": float(g5["Inhibition"].mean()),
            "median_inhibition_3prime": float(g3["Inhibition"].median()),
            "median_inhibition_5prime": float(g5["Inhibition"].median()),
            "mannwhitney_p": float(p),
            "direction": "5prime_higher" if g5["Inhibition"].mean() > g3["Inhibition"].mean() else "3prime_higher",
            "assay_confounded_with_position": confounded,
            "assay_3prime": assay_3,
            "assay_5prime": assay_5,
        })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {OUT_PATH}")
    print(json.dumps({k: v for k, v in results.items() if k != "per_gene_position_counts"}, indent=2))


if __name__ == "__main__":
    main()
