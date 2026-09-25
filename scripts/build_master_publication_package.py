#!/usr/bin/env python3
"""
build_master_publication_package.py
===================================
Definitive builder script for the HelixZero-CMS Engineering & Architecture Monograph.
Constructs:
1. HELIXZERO_END_TO_END_ENGINEERING_AND_ARCHITECTURE_MONOGRAPH.md
2. scripts/compile_30page_monograph_pdf.py
3. Compiles HelixZero_End_to_End_Engineering_Monograph.pdf
4. Verifies strictly ZERO dollar signs ($) and measures the resulting page count.
"""

import sys
import os
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TARGET_MD = ROOT_DIR / "HELIXZERO_END_TO_END_ENGINEERING_AND_ARCHITECTURE_MONOGRAPH.md"
COMPILER_PY = ROOT_DIR / "scripts" / "compile_30page_monograph_pdf.py"
OUTPUT_PDF = ROOT_DIR / "HelixZero_End_to_End_Engineering_Monograph.pdf"

print("Building definitive master publication package...")
