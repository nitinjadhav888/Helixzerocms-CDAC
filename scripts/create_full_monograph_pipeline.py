#!/usr/bin/env python3
"""
create_full_monograph_pipeline.py
=================================
Pipeline that generates:
1. Complete Markdown monograph with 14 full chapters and zero dollar signs ($).
2. Complete ReportLab Python script with 14 full chapters and zero dollar signs ($).
3. Compiles the PDF and verifies page count.
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TARGET_MD = ROOT_DIR / "HELIXZERO_END_TO_END_ENGINEERING_AND_ARCHITECTURE_MONOGRAPH.md"
TARGET_PY = ROOT_DIR / "scripts" / "compile_30page_monograph_pdf.py"
TARGET_PDF = ROOT_DIR / "HelixZero_End_to_End_Engineering_Monograph.pdf"

print("Starting complete monograph generation pipeline...")
