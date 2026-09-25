#!/usr/bin/env python3
"""
write_expanded_compiler.py
==========================
Generates the comprehensive, publication-grade, deeply pedagogical ReportLab compiler script:
`scripts/compile_30page_monograph_pdf.py`

Guarantees:
- Zero raw dollar signs ($).
- Clean, readable Unicode / plain text throughout.
- Full 14 chapters with exhaustive explanations.
- Dynamic NumberedCanvas running header and footer ("Page X of Y").
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TARGET = ROOT_DIR / "scripts" / "compile_30page_monograph_pdf.py"

print("Writing expanded compiler script in chunks...")

CHUNK_HEADER = '''#!/usr/bin/env python3
"""
compile_30page_monograph_pdf.py
===============================
Compiles the comprehensive, exhaustive, publication-grade Engineering Monograph for HelixZero-CMS:
"HelixZero: Complete Engineering & Architecture Monograph — The Software, Machine
Learning, and Biophysical Journey from Research Gap to Production Platform"

Features:
- Clean, readable typography with ZERO raw dollar signs or LaTeX math syntax.
- Lengthy, thorough, step-by-step pedagogical explanations of each and every implementation detail.
- Standard publication font sizes (Body 8.2pt, Headings 13/10/8.8pt, Tables 7.0pt).
- NumberedCanvas with running header and footer with dynamic total page count ("Page X of Y").
- Complete 14-chapter narrative detailing biology, chemistry, 8 engineering hurdles,
  feature spaces, ML models, biophysics, safety, benchmarks, clinical cases, and full tech stack.
"""

import os
import sys
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Preformatted
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

ROOT_DIR = Path(__file__).resolve().parent.parent
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
    
    styles = getSampleStyleSheet()
    
    # Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=19,
        leading=24,
        textColor=colors.HexColor("#0f2942"),
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        fontName='Helvetica',
        fontSize=10.5,
        leading=14.5,
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
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f2942"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3_Custom',
        fontName='Helvetica-Bold',
        fontSize=8.8,
        leading=11.8,
        textColor=colors.HexColor("#0284c7"),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.4,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        'Body_Bold',
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11.4,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        fontName='Helvetica',
        fontSize=8.0,
        leading=11.0,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )
    
    callout_style = ParagraphStyle(
        'Callout_Text',
        fontName='Helvetica-Oblique',
        fontSize=8.0,
        leading=11.0,
        textColor=colors.HexColor("#1e3a8a")
    )
    
    table_cell = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7.0,
        leading=9.2,
        textColor=colors.HexColor("#0f172a")
    )
    
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7.0,
        leading=9.2,
        textColor=colors.HexColor("#0f172a")
    )

    table_cell_header = ParagraphStyle(
        'TableCellHeader',
        fontName='Helvetica-Bold',
        fontSize=7.3,
        leading=9.6,
        textColor=colors.white
    )
    
    code_style = ParagraphStyle(
        'CodeStyle',
        fontName='Courier',
        fontSize=6.4,
        leading=8.0,
        textColor=colors.HexColor("#0f172a")
    )

    story = []
    
    def add_callout(text):
        p = Paragraph(f"<b>Key Engineering Takeaway:</b> {text}", callout_style)
        t = Table([[p]], colWidths=[520])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f7ff")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3b82f6")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

    def add_code_box(code_text):
        p = Preformatted(code_text.strip(), code_style)
        t = Table([[p]], colWidths=[520])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))
'''

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(CHUNK_HEADER)

print("Header chunk written successfully.")
