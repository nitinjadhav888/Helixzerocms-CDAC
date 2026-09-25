#!/usr/bin/env python3
"""
build_35page_pdf.py
===================
Defines the complete, massive 14-chapter story and builds both the 35+ page PDF
and the synchronized Markdown document.
Strictly ZERO dollar signs ($).
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = ROOT_DIR / "HelixZero_End_to_End_Engineering_Monograph.pdf"
OUTPUT_MD = ROOT_DIR / "HELIXZERO_END_TO_END_ENGINEERING_AND_ARCHITECTURE_MONOGRAPH.md"
TARGET_COMPILER = ROOT_DIR / "scripts" / "compile_30page_monograph_pdf.py"

print("Starting build of 35+ page monograph...")
