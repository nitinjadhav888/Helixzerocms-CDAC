import re
from pathlib import Path

html = Path("HelixZero_Software_Architecture_Presentation.html").read_text(encoding="utf-8")
for s in [1, 2, 3]:
    m = re.search(rf'<section class="slide[^"]*" id="slide-{s}".*?</section>', html, re.DOTALL)
    if m:
        clean = ' '.join(re.sub(r'<[^>]+>', ' ', m.group(0)).split())
        print(f"=== SLIDE {s} PREVIEW ===")
        print(clean[:300])
        print()
