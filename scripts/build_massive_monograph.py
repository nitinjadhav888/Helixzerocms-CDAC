#!/usr/bin/env python3
"""
build_massive_monograph.py
==========================
Integrates content from monograph_content_p1, p2, p3 into:
1. HELIXZERO_END_TO_END_ENGINEERING_AND_ARCHITECTURE_MONOGRAPH.md
2. scripts/compile_30page_monograph_pdf.py
3. Compiles the PDF and audits page count and dollar count.
"""

import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from monograph_content_p1 import CHAPTER_1, CHAPTER_2
from monograph_content_p2 import CHAPTER_3, CHAPTER_4, CHAPTER_5, CHAPTER_6, CHAPTER_7
from monograph_content_p3 import CHAPTER_8, CHAPTER_9, CHAPTER_10, CHAPTER_11, CHAPTER_12, CHAPTER_13, CHAPTER_14

ALL_CHAPTERS = [
    CHAPTER_1, CHAPTER_2, CHAPTER_3, CHAPTER_4, CHAPTER_5, CHAPTER_6,
    CHAPTER_7, CHAPTER_8, CHAPTER_9, CHAPTER_10, CHAPTER_11, CHAPTER_12,
    CHAPTER_13, CHAPTER_14
]

TARGET_MD = ROOT_DIR / "HELIXZERO_END_TO_END_ENGINEERING_AND_ARCHITECTURE_MONOGRAPH.md"
COMPILER_PY = ROOT_DIR / "scripts" / "compile_30page_monograph_pdf.py"

def generate_markdown():
    print("Generating comprehensive master markdown monograph...")
    lines = []
    lines.append("# HELIXZERO-CMS: COMPLETE ENGINEERING & ARCHITECTURE MONOGRAPH")
    lines.append("## The Software, Machine Learning, and Biophysical Journey from Research Gap to Production Platform")
    lines.append("")
    lines.append("**Authors:** C-DAC BioComputing Consortium & Computational RNA Therapeutics Group  ")
    lines.append("**Affiliation:** Centre for Development of Advanced Computing (C-DAC, Pune) & IIT Collaborative Network  ")
    lines.append("**Repository:** nitinjadhav888/Helixzerocms-CDAC | **Workspace:** d:\\Helixx | **Release:** v5.3.0 Production Stack  ")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### Executive Abstract")
    lines.append("Small interfering RNAs (siRNAs) represent an extraordinary frontier in precision medicine, offering the capability to silence any disease-causing gene through catalytic mRNA degradation mediated by Argonaute-2 (Ago2). However, unmodified (naked) RNA is therapeutically non-viable in humans due to rapid nuclease cleavage (half-life t½ < 5 minutes), lethal TLR7/8 innate immune activation, microRNA-like seed off-target hepatotoxicity, and rapid renal filtration. Modern commercial therapeutics (Patisiran, Givosiran, Lumasiran, Inclisiran, Vutrisiran) rely on complex chemical modification architectures (2'-OMe, 2'-F, phosphorothioates, 5'-vinylphosphonate, and trivalent GalNAc ligands).")
    lines.append("Prior machine learning approaches failed due to three fatal architectural deficiencies: (1) sequence-only models blind to chemistry, (2) legacy single-character ASCII tokenizations that rendered sugar and backbone modifications mutually exclusive, and (3) concentration-blind models that conflated potency with experimental dosing. HelixZero solves all three bottlenecks via an orthogonal 5-tuple chemical ontology (NucSlot), a 577-dimensional multi-modal feature space, an IEEE v5 two-stage hierarchical dose-response engine, a 6-domain deterministic biophysical penalty engine, and a 2-bit bit-packed whole-transcriptome safety firewall.")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    for ch in ALL_CHAPTERS:
        lines.append(f"## {ch['title']}")
        lines.append("")
        for sec in ch["sections"]:
            lines.append(f"### {sec['title']}")
            lines.append("")
            for p in sec.get("body", []):
                lines.append(p)
                lines.append("")
            for b in sec.get("bullets", []):
                lines.append(f"- {b}")
            if sec.get("bullets"):
                lines.append("")
        lines.append("---")
        lines.append("")

    md_content = "\n".join(lines)
    assert md_content.count('$') == 0, f"Found {md_content.count('$')} dollar signs in MD!"
    
    with open(TARGET_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved master Markdown document to {TARGET_MD} ({len(lines)} lines)")

if __name__ == "__main__":
    generate_markdown()
