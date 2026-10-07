import re
from pathlib import Path

content = Path("scripts/presentation_slides_part1.py").read_text(encoding="utf-8")
ids = re.findall(r'"id":\s*(\d+)', content)
print("Slide IDs in presentation_slides_part1.py:", ids)
