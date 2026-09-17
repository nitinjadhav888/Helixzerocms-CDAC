"""
scripts/generate_10_resource_taxonomy_infographic.py
===================================================
Generates a 16:9 publication-grade infographic of the Comprehensive
Ten-Resource Public-Data Taxonomy of HelixZero (Table I, HZ.pdf).
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# Setup figure 16:9 ratio
fig = plt.figure(figsize=(16, 9), dpi=300)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1600)
ax.set_ylim(0, 900)
ax.axis('off')

# Color palette (Modern Deep Tech Slate & Cyan)
BG_DARK = "#090D16"
CARD_BG = "#111827"
CARD_BORDER = "#1F2937"
ACCENT_BLUE = "#38BDF8"
ACCENT_CYAN = "#06B6D4"
ACCENT_EMERALD = "#10B981"
ACCENT_PURPLE = "#A855F7"
ACCENT_AMBER = "#F59E0B"
TEXT_WHITE = "#F9FAFB"
TEXT_MUTED = "#9CA3AF"
TEXT_SUB = "#D1D5DB"

# Background
fig.patch.set_facecolor(BG_DARK)
ax.set_facecolor(BG_DARK)

# Header
ax.text(80, 840, "HELIXZERO: COMPREHENSIVE TEN-RESOURCE PUBLIC-DATA TAXONOMY",
        fontsize=22, fontweight='bold', color=TEXT_WHITE, family='sans-serif')
ax.text(80, 810, "Empirical scope spanning 40,255 measured assays, 3,535 canonical siRNAs, 549 patent/clinical compounds, and human Ago2 structural coordinates",
        fontsize=12, color=ACCENT_CYAN, family='sans-serif')

# Four Columns / Functional Clusters
clusters = [
    {
        "title": "1. CANONICAL SEQUENCE BENCHMARKS",
        "subtitle": "Unmodified 21-nt duplex activity screening",
        "color": ACCENT_BLUE,
        "x": 60, "w": 345,
        "cards": [
            {
                "name": "Huesken Gold Standard",
                "scope": "N = 2,361 siRNAs | 34 Genes",
                "desc": "Canonical sequence benchmark from Novartis human/rodent screening.",
                "source": "Nature Biotechnology (2005)",
                "metric": "LightGBM: r = 0.8044 | AUC = 0.9099"
            },
            {
                "name": "Takayuki / siDirect Alias",
                "scope": "N = 702 siRNAs",
                "desc": "Independent cross-study canonical sequence validation collection.",
                "source": "Nucleic Acids Research (2007)",
                "metric": "LightGBM: r = 0.8788 | RMSE = 12.39%"
            },
            {
                "name": "Seven-Study Canonical Mixset",
                "scope": "N = 472 siRNAs",
                "desc": "Heterogeneous pooled collection across Reynolds, Ui-Tei, Amarzguioui, Vickers.",
                "source": "Multi-Lab Canonical Benchmark",
                "metric": "LightGBM: r = 0.8291 | r_s = 0.8093"
            }
        ]
    },
    {
        "title": "2. MULTI-DOSE & CHEMISTRY CORPUS",
        "subtitle": "Modified duplexes & concentration response",
        "color": ACCENT_EMERALD,
        "x": 435, "w": 345,
        "cards": [
            {
                "name": "CMsiRNAdb Master Corpus",
                "scope": "40,255 Records | 8,540 Guides",
                "desc": "37,946 BRONZE assays at 68 doses (0.00017–1000 nM) + 2,309 GOLD Hill curves (R² ≥ 0.75).",
                "source": "CMsiRNAdb (Bioinformatics, 2024)",
                "metric": "5-Fold CV: r = 0.8049 | r_s = 0.8018"
            },
            {
                "name": "Foster GalNAc Delivery Panel",
                "scope": "N = 15 siRNAs | ESC/ESC+ Designs",
                "desc": "Advanced chemically modified GalNAc conjugates with metabolically stabilized backbones.",
                "source": "Molecular Therapy (2018)",
                "metric": "HelixZero: r = 0.9120 | R² = 0.7920"
            },
            {
                "name": "CMsiRNAdb Homogeneous Subset",
                "scope": "N = 472 siRNAs (Fixed 10 nM)",
                "desc": "Chemistry-aware benchmark controlling for concentration variance.",
                "source": "Standardized Modified Assay",
                "metric": "CatBoost v4: r = 0.7401 | AUC = 0.8745"
            }
        ]
    },
    {
        "title": "3. PATENT & CLINICAL TRANSLATION",
        "subtitle": "Real-world therapeutics & patent panels",
        "color": ACCENT_PURPLE,
        "x": 810, "w": 345,
        "cards": [
            {
                "name": "FENNEC Patent Panels (APP & JAK1)",
                "scope": "N = 534 siRNAs (343 APP + 191 JAK1)",
                "desc": "External modified-siRNA patent panels from Alnylam & partner disclosures.",
                "source": "WO2020132227A2 / WO2024256707A1",
                "metric": "Calibrated Consensus: r = 0.7182 (APP)"
            },
            {
                "name": "FDA-Approved Commercial Panel",
                "scope": "N = 5 Reference Drugs (Alnylam)",
                "desc": "Patisiran, Givosiran, Lumasiran, Inclisiran, Vutrisiran. Zero penalty exemption verified.",
                "source": "FDA Labels & Phase III Clinical Trials",
                "metric": "IC50: 0.83–2.24 nM | r_s = 0.8000"
            },
            {
                "name": "Heterogeneous Patent Master",
                "scope": "N = 2,576 siRNAs (Cross-Patent)",
                "desc": "Highly challenging diverse chemical space across 90 patent disclosures.",
                "source": "Multi-Vendor Chemistries",
                "metric": "CatBoost v4: r = 0.6217 | R² = 0.3563"
            }
        ]
    },
    {
        "title": "4. STRUCTURAL & GENOMIC REFERENCE",
        "subtitle": "Receptor coordinates & genome-wide safety",
        "color": ACCENT_AMBER,
        "x": 1185, "w": 345,
        "cards": [
            {
                "name": "Human Ago2 Crystal Structure",
                "scope": "PDB: 4W5N (2.90 Å Resolution)",
                "desc": "Guide-bound human Ago2 receptor reference for template placement & pocket geometry.",
                "source": "Schirle & MacRae, Science (2014)",
                "metric": "MID/PIWI/PAZ Geometries & Clash Score"
            },
            {
                "name": "Human Reference Transcriptome",
                "scope": "863 MB | >40M 30-mers (GRCh38)",
                "desc": "2-bit packed genome-wide index for rapid off-target candidate filtering.",
                "source": "NCBI RefSeq / Ensembl Index",
                "metric": "Genome-Wide Specificity & Isoforms"
            },
            {
                "name": "OligoFormer Seed Viability",
                "scope": "4,096 Hexamers (Positions 2–7)",
                "desc": "Complete 6-mer lookup for miRNA-like seed-region off-target phenotypic viability.",
                "source": "Bioinformatics (2024)",
                "metric": "Pre-Screening Cytotoxicity Filter"
            }
        ]
    }
]

for col in clusters:
    cx, cw = col["x"], col["w"]
    ccolor = col["color"]
    
    # Cluster Header Pill
    rect_head = patches.FancyBboxPatch((cx, 740), cw, 50, boxstyle="round,pad=4,rounding_size=6",
                                       facecolor=CARD_BG, edgecolor=ccolor, linewidth=1.5)
    ax.add_patch(rect_head)
    ax.text(cx + 15, 768, col["title"], fontsize=10.5, fontweight='bold', color=ccolor, family='sans-serif')
    ax.text(cx + 15, 750, col["subtitle"], fontsize=8.5, color=TEXT_MUTED, family='sans-serif')
    
    # Cards in this cluster
    y_start = 720
    card_h = 210
    gap = 20
    
    for i, card in enumerate(col["cards"]):
        cy = y_start - (i + 1) * (card_h + gap) + gap
        
        # Card Background
        card_box = patches.FancyBboxPatch((cx, cy), cw, card_h, boxstyle="round,pad=4,rounding_size=8",
                                          facecolor=CARD_BG, edgecolor=CARD_BORDER, linewidth=1.2)
        ax.add_patch(card_box)
        
        # Color accent stripe
        stripe = patches.Rectangle((cx, cy + card_h - 4), cw, 4, facecolor=ccolor, edgecolor='none')
        ax.add_patch(stripe)
        
        # Card Content
        ax.text(cx + 14, cy + card_h - 22, card["name"], fontsize=11, fontweight='bold', color=TEXT_WHITE)
        ax.text(cx + 14, cy + card_h - 40, card["scope"], fontsize=9, fontweight='bold', color=ccolor)
        
        # Wrapped description
        words = card["desc"].split()
        lines = []
        cur_line = []
        for w in words:
            cur_line.append(w)
            if len(" ".join(cur_line)) > 42:
                lines.append(" ".join(cur_line[:-1]))
                cur_line = [w]
        if cur_line:
            lines.append(" ".join(cur_line))
        
        for line_idx, line in enumerate(lines[:3]):
            ax.text(cx + 14, cy + card_h - 62 - line_idx * 16, line, fontsize=8.2, color=TEXT_SUB)
            
        # Source badge
        ax.text(cx + 14, cy + 34, f"Source: {card['source']}", fontsize=7.5, color=TEXT_MUTED, style='italic')
        
        # Metric highlight pill
        metric_box = patches.FancyBboxPatch((cx + 10, cy + 8), cw - 20, 22, boxstyle="round,pad=2,rounding_size=4",
                                            facecolor="#1E293B", edgecolor=ccolor, linewidth=0.8)
        ax.add_patch(metric_box)
        ax.text(cx + 16, cy + 13, card["metric"], fontsize=8, fontweight='bold', color=TEXT_WHITE)

# Footer Note
ax.text(80, 25, "Note: Complete 10-resource dataset inventory corresponds to Table I in HelixZero manuscript (IEEE TNNLS 2026). Partitions grouped strictly by antisense sequence/target gene (GroupKFold, Zero-Leakage).",
        fontsize=8.5, color=TEXT_MUTED, style='italic')

out_path = Path("d:/Helixx/paper_figures/helixzero_10_resource_dataset_taxonomy.png")
plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
plt.close()

print(f"Successfully generated {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")
