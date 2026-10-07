import re
from pathlib import Path

html = Path("HelixZero_Software_Architecture_Presentation.html").read_text(encoding="utf-8")
m = re.search(r'<section class="slide[^"]*" id="slide-12".*?</section>', html, re.DOTALL)
if m:
    for line in m.group(0).splitlines():
        if "Passenger" in line or "Guide" in line or "Architecture Note" in line:
            print("  ", line.strip())
