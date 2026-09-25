# write_final_monograph.py - Part 1
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TARGET_COMPILER = ROOT_DIR / "scripts" / "compile_30page_monograph_pdf.py"
TARGET_MD = ROOT_DIR / "HELIXZERO_END_TO_END_ENGINEERING_AND_ARCHITECTURE_MONOGRAPH.md"

print("Starting generation of exhaustive monograph assets...")
