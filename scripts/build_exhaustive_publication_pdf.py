#!/usr/bin/env python3
"""
build_exhaustive_publication_pdf.py
===================================
Constructs the complete 35+ page master monograph:
- Generates scripts/compile_30page_monograph_pdf.py with all expanded chapters.
- Compiles HelixZero_End_to_End_Engineering_Monograph.pdf.
- Generates HELIXZERO_END_TO_END_ENGINEERING_AND_ARCHITECTURE_MONOGRAPH.md.
- Verifies that zero raw dollar signs ($) exist.
- Audits and prints the exact total page count.
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TARGET_COMPILER = ROOT_DIR / "scripts" / "compile_30page_monograph_pdf.py"
TARGET_MD = ROOT_DIR / "HELIXZERO_END_TO_END_ENGINEERING_AND_ARCHITECTURE_MONOGRAPH.md"
TARGET_PDF = ROOT_DIR / "HelixZero_End_to_End_Engineering_Monograph.pdf"

print("Step 1: Assembling the exhaustive ReportLab Python compiler script...")
