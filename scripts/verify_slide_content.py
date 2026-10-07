from pathlib import Path
import re

html = Path("HelixZero_Software_Architecture_Presentation.html").read_text(encoding="utf-8")

slides = re.findall(r'<section class="slide[^"]*" id="slide-(\d+)".*?</section>', html, re.DOTALL)
print(f"Total slides matched: {len(slides)}")

target_slides = [2, 3, 6, 8, 9, 13, 14, 15, 17, 18, 19, 23, 24, 30]

for s_num in target_slides:
    pattern = rf'<section class="slide[^"]*" id="slide-{s_num}".*?</section>'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        content = match.group(0)
        has_dollar = "$" in content
        print(f"Slide {s_num:02d}: Contains '$': {has_dollar}")
        if has_dollar:
            for line in content.splitlines():
                if "$" in line:
                    print(f"   [DOLLAR FOUND] {line.strip()[:100]}")
    else:
        print(f"Slide {s_num:02d}: NOT FOUND")

# Also let's check Slide 2 text specifically
s2_match = re.search(r'<section class="slide[^"]*" id="slide-2".*?</section>', html, re.DOTALL)
if s2_match:
    print("\n--- SLIDE 2 BULLETS ---")
    for line in s2_match.group(0).splitlines():
        if "Joint Exposure" in line or "Sub-Second Search" in line:
            print(" ", line.strip())
