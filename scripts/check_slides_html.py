import re
from pathlib import Path

html = Path("HelixZero_Software_Architecture_Presentation.html").read_text(encoding="utf-8")
slides = re.findall(r'<section class="slide[^"]*" id="slide-(\d+)"', html)
print(f"Total slides in HTML: {len(slides)}")
print("Slide numbers:", slides)
