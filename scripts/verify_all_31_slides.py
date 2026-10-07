from pathlib import Path
import re

for fname in ["HelixZero_Software_Architecture_Presentation.html", "Paper/HelixZero_Software_Presentation.html"]:
    html = Path(f"d:/Helixx/{fname}").read_text(encoding="utf-8")
    any_dollar = False
    for s_num in range(1, 32):
        pat = rf'<section class="slide[^"]*" id="slide-{s_num}".*?</section>'
        m = re.search(pat, html, re.DOTALL)
        if m:
            if "$" in m.group(0):
                print(f"[{fname}] Slide {s_num:02d} HAS DOLLAR!")
                any_dollar = True
        else:
            print(f"[{fname}] Slide {s_num:02d} NOT FOUND!")
            any_dollar = True
    if not any_dollar:
        print(f"[{fname}] ALL 31 SLIDES ARE 100% CLEAN OF ANY '$' OR RAW LATEX!")
