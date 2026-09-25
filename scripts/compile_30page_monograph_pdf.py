#!/usr/bin/env python3
"""
compile_30page_monograph_pdf.py
===============================
Master ReportLab PDF compiler for the comprehensive, exhaustive Engineering Monograph:
"HelixZero: Complete Engineering & Architecture Monograph — The Software, Machine
Learning, and Biophysical Journey from Research Gap to Production Platform"

Features:
- Clean, readable typography with strictly ZERO dollar signs or LaTeX math syntax.
- Lengthy, thorough, step-by-step explanations of each and every implementation detail.
- Standard publication font sizes (Body 8.5pt, Headings 13.5/10.5/9.5pt, Tables 7.2pt).
- NumberedCanvas with running header and footer with dynamic total page count ("Page X of Y").
- Complete 14-chapter narrative detailing biology, chemistry, 8 engineering hurdles,
  feature spaces, ML models, biophysics, safety, benchmarks, clinical cases, and full tech stack.
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path to import chapter modules
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Preformatted
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from monograph_ch01_ch03 import add_chapters_01_03
from monograph_ch04_ch06 import add_chapters_04_06
from monograph_ch07_ch09 import add_chapters_07_09
from monograph_ch10_ch12 import add_chapters_10_12
from monograph_ch13_ch14 import add_chapters_13_14

ROOT_DIR = SCRIPTS_DIR.parent
OUTPUT_PDF = ROOT_DIR / "HelixZero_End_to_End_Engineering_Monograph.pdf"


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas that writes dynamic total page count on every page."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Header on pages 2+
        if self._pageNumber > 1:
            self.drawString(46, 752, "HelixZero-CMS: Complete Engineering, Architecture & Biophysics Monograph")
            self.drawRightString(566, 752, "C-DAC BioComputing Consortium")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(46, 746, 566, 746)
        
        # Footer on all pages
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(566, 24, page_text)
        self.drawString(46, 24, "Technical Monograph | Centre for Development of Advanced Computing (C-DAC, Pune)")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(46, 34, 566, 34)
        
        self.restoreState()


def build_pdf():
    print(f"Compiling comprehensive engineering monograph to {OUTPUT_PDF}...")
    
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=46,
        rightMargin=46,
        topMargin=46,
        bottomMargin=46
    )
    
    # -------------------------------------------------------------
    # Typography Styles Dictionary
    # -------------------------------------------------------------
    title_style = ParagraphStyle(
        'CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=25,
        textColor=colors.HexColor("#0f2942"),
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=12
    )
    
    author_style = ParagraphStyle(
        'CoverAuthor',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=3
    )
    
    affil_style = ParagraphStyle(
        'CoverAffil',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=10
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=13.5,
        leading=17.5,
        textColor=colors.HexColor("#0f2942"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14.5,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    h3_style = ParagraphStyle(
        'Heading3_Custom',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#0f2942"),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        fontName='Helvetica',
        fontSize=9.0,
        leading=13.0,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4
    )
    
    body_bold = ParagraphStyle(
        'Body_Bold_Custom',
        fontName='Helvetica-Bold',
        fontSize=9.0,
        leading=13.0,
        textColor=colors.HexColor("#0f2942"),
        spaceAfter=4
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        fontName='Helvetica',
        fontSize=9.0,
        leading=13.0,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )
    
    callout_style = ParagraphStyle(
        'Callout_Text',
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.2,
        textColor=colors.HexColor("#0f2942")
    )
    
    table_cell = ParagraphStyle(
        'Table_Cell',
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.2,
        textColor=colors.HexColor("#1e293b")
    )
    
    table_cell_bold = ParagraphStyle(
        'Table_Cell_Bold',
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10.2,
        textColor=colors.HexColor("#0f2942")
    )
    
    table_cell_header = ParagraphStyle(
        'Table_Cell_Header',
        fontName='Helvetica-Bold',
        fontSize=8.0,
        leading=10.5,
        textColor=colors.white
    )
    
    code_style = ParagraphStyle(
        'Code_Block',
        fontName='Courier',
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor("#0f172a")
    )

    S = {
        'title': title_style,
        'subtitle': subtitle_style,
        'author': author_style,
        'affil': affil_style,
        'h1': h1_style,
        'h2': h2_style,
        'h3': h3_style,
        'body': body_style,
        'body_bold': body_bold,
        'bullet': bullet_style,
        'callout': callout_style,
        'tc': table_cell,
        'tcb': table_cell_bold,
        'tch': table_cell_header,
        'code': code_style
    }

    story = []

    # =========================================================================
    # COVER / TITLE BLOCK
    # =========================================================================
    story.append(Paragraph("HELIXZERO-CMS: COMPLETE ENGINEERING & ARCHITECTURE MONOGRAPH", title_style))
    story.append(Paragraph(
        "The Software Engineering, Machine Learning, and Biophysical Journey from Research Gap "
        "to Production Oligonucleotide Platform", subtitle_style
    ))
    story.append(Paragraph("<b>Nitin Jadhav & Technical Core Engineering Team</b>", author_style))
    story.append(Paragraph(
        "Centre for Development of Advanced Computing (C-DAC, Pune) | HPC-Medical & BioComputing Division<br/>"
        "In Collaboration with Bioinformatics & Molecular Pharmacology Research Group", affil_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0f2942"), spaceAfter=10))

    # Executive Summary Callout Box
    summary_html = (
        "<b>EXECUTIVE ENGINEERING SUMMARY:</b> This publication-grade technical monograph presents the end-to-end "
        "software architecture, algorithmic foundations, biophysical formulations, and empirical validation of "
        "<b>HelixZero-CMS</b>—an industrial-scale AI and biophysical platform for predicting the therapeutic potency, "
        "chemical modification profiles, and safety profiles of small interfering RNAs (siRNAs). Beginning with a rigorous "
        "critique of 40+ prior models and uncovering pervasive sequence identity data leakage, this document details "
        "the assembly of a 260,000+ assay data lake, the 5-axis <code>NucSlot</code> stereochemical ontology, the IEEE v5 "
        "two-stage hierarchical dosage engine, the 577-dimensional multi-scale feature space, the strictly monotonic calibration "
        "breakthrough, the 6-domain deterministic penalty engine, the sub-microsecond 2-bit binary off-target slicer, and "
        "complete in silico clinical validation against all 7 FDA-approved siRNA therapeutics."
    )
    summary_table = Table([[Paragraph(summary_html, callout_style)]], colWidths=[520])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#16a34a")),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # Metadata & Scope Table
    meta_data = [
        [Paragraph("<b>Platform Version</b>", table_cell_header), Paragraph("<b>Core Architecture</b>", table_cell_header), Paragraph("<b>Validated Datasets</b>", table_cell_header), Paragraph("<b>Target Species</b>", table_cell_header)],
        [Paragraph("HelixZero v5.4-Prod", table_cell), Paragraph("IEEE v5 Two-Stage + MEG-mod GNN", table_cell), Paragraph("22 Datasets (>260k Assays)", table_cell), Paragraph("Homo sapiens / Rodentia", table_cell)],
        [Paragraph("<b>Primary Metric (Honest)</b>", table_cell_header), Paragraph("<b>Calibration ECE</b>", table_cell_header), Paragraph("<b>Off-Target Latency</b>", table_cell_header), Paragraph("<b>Clinical Approval Concordance</b>", table_cell_header)],
        [Paragraph("Spearman ρ = 0.7463 (GroupKFold)", table_cell), Paragraph("0.018 (Strictly Monotonic)", table_cell), Paragraph("< 0.2 µs / transcript (2-Bit Slicer)", table_cell), Paragraph("7 of 7 FDA Drugs Validated", table_cell)]
    ]
    meta_table = Table(meta_data, colWidths=[130, 130, 130, 130])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f2942")),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#0f2942")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,1), [colors.HexColor("#f8fafc")]),
        ('ROWBACKGROUNDS', (0,3), (-1,3), [colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Table of Contents
    story.append(Paragraph("TABLE OF MONOGRAPH CHAPTERS", h2_style))
    toc_data = [
        [Paragraph("<b>Chapter 1</b>", table_cell_bold), Paragraph("The Molecular Biology & Pharmacology of RNA Interference (Ago2, DEDH, RNase A Mechanism)", table_cell)],
        [Paragraph("<b>Chapter 2</b>", table_cell_bold), Paragraph("The Critical Literature Survey & Architectural Deficiencies of Prior Art (40+ Models, 3 Fatal Flaws)", table_cell)],
        [Paragraph("<b>Chapter 3</b>", table_cell_bold), Paragraph("The Multi-Source Data Lake Assembly & Master Census (>260,000 Assays, 22 Datasets, Harmonization)", table_cell)],
        [Paragraph("<b>Chapter 4</b>", table_cell_bold), Paragraph("Forensic Data Cleaning & The Elimination of Identity Leakage (GroupKFold, Overhang Stripping, Normalization)", table_cell)],
        [Paragraph("<b>Chapter 5</b>", table_cell_bold), Paragraph("The 1-Character Tokenization Failure & The `NucSlot` 5-Axis Stereochemical Ontology (30-Mod Dictionary)", table_cell)],
        [Paragraph("<b>Chapter 6</b>", table_cell_bold), Paragraph("Multi-Scale Feature Engineering: 190-D Screening & 577-D Clinical Feature Spaces (24 Literature Formulas)", table_cell)],
        [Paragraph("<b>Chapter 7</b>", table_cell_bold), Paragraph("Machine Learning & Deep Learning Model Architectures (IEEE v5 Two-Stage, Hill Equation, MEG-mod PyG GNN)", table_cell)],
        [Paragraph("<b>Chapter 8</b>", table_cell_bold), Paragraph("The Calibration Dilemma: Overcoming Isotonic Step-Plateau Collapse (`StrictlyMonotonicCalibrator`)", table_cell)],
        [Paragraph("<b>Chapter 9</b>", table_cell_bold), Paragraph("The 6-Domain Deterministic Biophysical Penalty Engine (Structural Clash Audits, Hard Physical Realism)", table_cell)],
        [Paragraph("<b>Chapter 10</b>", table_cell_bold), Paragraph("High-Throughput Safety Engines & Combinatorial Optimization (2-Bit Slicer, Janas Viability, 3D PDB)", table_cell)],
        [Paragraph("<b>Chapter 11</b>", table_cell_bold), Paragraph("Comprehensive Empirical Benchmarks & Clinical Case Studies (7 Benchmarks, All 7 FDA Approved Drugs)", table_cell)],
        [Paragraph("<b>Chapter 12</b>", table_cell_bold), Paragraph("Production Software Engineering, REST API & DevOps (Directory Tree, 184 Pytest Suite, Docker)", table_cell)],
        [Paragraph("<b>Chapter 13</b>", table_cell_bold), Paragraph("The 8 Major Engineering Hurdles & Intellectual Breakthroughs (Forensic Problem-Solving Narrative)", table_cell)],
        [Paragraph("<b>Chapter 14</b>", table_cell_bold), Paragraph("Comprehensive Tech Stack, Libraries, Algorithms & DSA (Master Inventory & Architectural Defense)", table_cell)],
    ]
    toc_t = Table(toc_data, colWidths=[70, 450])
    toc_t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(toc_t)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SYSTEM BLUEPRINT DIAGRAM
    # =========================================================================
    story.append(Paragraph("End-to-End System Blueprint Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0f2942"), spaceAfter=8))
    
    blueprint_ascii = (
        "                               HELIXZERO-CMS END-TO-END PIPELINE BLUEPRINT\n"
        "  +-----------------------------------------------------------------------------------------------------+\n"
        "  |  RAW INPUTS: Sense & Antisense RNA Sequences | Chemical Modification Formats | Target Transcript    |\n"
        "  +--------------------------------------------------+--------------------------------------------------+\n"
        "                                                     |\n"
        "                                                     v\n"
        "  +-----------------------------------------------------------------------------------------------------+\n"
        "  |  STAGE 0: SANITIZATION & STEREOCHEMICAL TOKENIZATION (`core/nucslot.py`)                           |\n"
        "  |  - Strip 3' Overhangs (dTdT, UU, -3P) -> Isolated Overhang Channels                                 |\n"
        "  |  - 5-Axis NucSlot Mapping: [Base (A/C/G/U)] x [Sugar Pucker] x [2'-Ribose] x [Linkage] x [Conjugate] |\n"
        "  +--------------------------------------------------+--------------------------------------------------+\n"
        "                                                     |\n"
        "                                                     v\n"
        "  +-----------------------------------------------------------------------------------------------------+\n"
        "  |  STAGE 1: MULTI-SCALE FEATURE EXTRACTION ENGINE (`core/feature_extractor.py`)                      |\n"
        "  |  - 420-D Positional Matrix (21 nts x 20 channels) | 24-D Literature Formulas (Reynolds/Ui-Tei)       |\n"
        "  |  - 64-D Foundation Embeddings (RNA-FM + RNA-Ernie)| 5-D ViennaRNA Thermodynamics (delta G, open)    |\n"
        "  +-------------------------+------------------------------------------------+--------------------------+\n"
        "                            |                                                |\n"
        "                            v                                                v\n"
        "  +----------------------------------------------------+   +--------------------------------------------+\n"
        "  |  STAGE 2A: IEEE v5 TWO-STAGE POTENCY ENGINE        |   |  STAGE 2B: MEG-mod PyG GRAPH ATTENTION     |\n"
        "  |  - Stage 1 CatBoost Regressor (`module2_potency`)  |   |  - Bimodal Graph (Duplex + Target Complex) |\n"
        "  |    Predicts: Intrinsic pIC50 = -log10(IC50_in_M)   |   |  - 4x TransformerConv Layers (4 heads)     |\n"
        "  |  - Stage 2 CatBoost Regressor (`module3_response`) |   |  - Epistemic Uncertainty Estimation        |\n"
        "  |    Inputs: pIC50 + log10(Dose) + Cell + Platform   |   |    via 30 Monte Carlo Dropout Passes       |\n"
        "  |    Predicts: Observed % Remaining mRNA [0 to 100]  |   +---------------------+----------------------+\n"
        "  +-------------------------+--------------------------+                         |\n"
        "                            |                                                    |\n"
        "                            +------------------------+---------------------------+\n"
        "                                                     | Ensemble Blend: 0.85 GBDT + 0.15 GNN\n"
        "                                                     v\n"
        "  +-----------------------------------------------------------------------------------------------------+\n"
        "  |  STAGE 3: STRICTLY MONOTONIC CALIBRATOR (`core/calibrator.py`)                                      |\n"
        "  |  - Linear Variance Matching (m = sigma_true / sigma_pred; b = mu_true - m * mu_pred)                |\n"
        "  |  - Fritsch-Carlson Monotonic Cubic Spline (dy/dx > 0 strictly everywhere; ECE = 0.018)              |\n"
        "  +--------------------------------------------------+--------------------------------------------------+\n"
        "                                                     |\n"
        "                                                     v\n"
        "  +-----------------------------------------------------------------------------------------------------+\n"
        "  |  STAGE 4: 6-DOMAIN DETERMINISTIC BIOPHYSICAL PENALTY ENGINE (`biophysics/penalty_engine.py`)        |\n"
        "  |  - Domain 1: 5'-MID Pocket Clashes (LNA at AS pos 1: +8.0) | Domain 2: Slicer Rigidity (+6.5)       |\n"
        "  |  - Domain 3: Seed Destabilization (GNA Bonus: -2.0)         | Domain 4: Inverted Asymmetry (+7.0)   |\n"
        "  |  - Domain 5: Exonuclease Degradation (+4.5)                | Domain 6: Fatal 5'-AS GalNAc (+15.0)  |\n"
        "  |  Final Efficacy Score = clip(Score_Calibrated - Sum(Penalties) * 0.18, 0, 100)                      |\n"
        "  +--------------------------------------------------+--------------------------------------------------+\n"
        "                            |                                                |\n"
        "                            v                                                v\n"
        "  +----------------------------------------------------+   +--------------------------------------------+\n"
        "  |  STAGE 5A: HIGH-THROUGHPUT SAFETY ENGINE           |   |  STAGE 5B: PRODUCTION SERVING & INSPECTION |\n"
        "  |  - 2-Bit Binary Slicer (< 0.2 us / query)          |   |  - FastAPI Microservice (/api/v1/predict)   |\n"
        "  |  - Janas HeLa Phenotypic Cell Viability Filter     |   |  - Atomistic 3D PDB Coordinate Generation  |\n"
        "  |  - Whole-Transcriptome Off-Target Hash Index       |   |  - SQLite Write-Ahead Logging (WAL) Cache  |\n"
        "  +----------------------------------------------------+   +--------------------------------------------+\n"
        "  +-----------------------------------------------------------------------------------------------------+\n"
        "  |  OUTPUTS: Calibrated Potency Score | Clinical Knockdown % | Off-Target Census | 3D PDB Coordinates  |\n"
        "  +-----------------------------------------------------------------------------------------------------+"
    )
    story.append(Preformatted(blueprint_ascii, code_style))
    story.append(Spacer(1, 14))

    # =========================================================================
    # ADD CHAPTERS VIA MODULAR SUBROUTINES
    # =========================================================================
    print("Adding Chapters 1, 2, 3...")
    add_chapters_01_03(story, S)
    
    print("Adding Chapters 4, 5, 6...")
    add_chapters_04_06(story, S)
    
    print("Adding Chapters 7, 8, 9...")
    add_chapters_07_09(story, S)
    
    print("Adding Chapters 10, 11, 12...")
    add_chapters_10_12(story, S)
    
    print("Adding Chapters 13, 14, and Conclusion...")
    add_chapters_13_14(story, S)

    # Build the document
    print("Executing ReportLab document build...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print("Compilation complete!")


if __name__ == "__main__":
    build_pdf()
