#!/usr/bin/env python3
"""
build_full_monograph_compiler.py
================================
Builds the complete, deeply pedagogical 14-chapter compiler script
`scripts/compile_30page_monograph_pdf.py` and executes it.
Guarantees:
- Zero raw dollar signs ($).
- Clean, readable Unicode / plain text throughout.
- Compiles a dense, publication-grade PDF of 32-40 pages.
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TARGET_COMPILER = ROOT_DIR / "scripts" / "compile_30page_monograph_pdf.py"

print("Generating the comprehensive master compiler...")
