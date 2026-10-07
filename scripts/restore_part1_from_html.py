import re
import json
from pathlib import Path

html = Path("HelixZero_Software_Architecture_Presentation.html").read_text(encoding="utf-8")

# Extract slideNotes
notes_matches = re.findall(r'window\.slideNotes\[(\d+)\]\s*=\s*(.*?);\n', html)
notes_dict = {}
for s_id, n_json in notes_matches:
    try:
        notes_dict[int(s_id)] = json.loads(n_json)
    except:
        notes_dict[int(s_id)] = n_json

print(f"Extracted notes for {len(notes_dict)} slides.")

# Extract slides 1 to 15
slides_p1 = []

for sid in range(1, 16):
    pat = rf'<!-- SLIDE {sid}: (.*?) -->\s*<section class="slide[^"]*" id="slide-{sid}">\s*<div class="slide-header">\s*<div class="slide-eyebrow">(.*?)</div>\s*<div class="slide-title-row">\s*<h2 class="slide-title">(.*?)</h2>\s*<div class="badges-group">(.*?)</div>\s*</div>\s*<p class="slide-subtitle">(.*?)</p>\s*</div>\s*<div class="slide-body">(.*?)</div>\s*<div class="slide-footer">(.*?)</div>\s*</section>'
    m = re.search(pat, html, re.DOTALL)
    if not m:
        # Fallback regex if comment slightly different
        pat2 = rf'<section class="slide[^"]*" id="slide-{sid}">\s*<div class="slide-header">\s*<div class="slide-eyebrow">(.*?)</div>\s*<div class="slide-title-row">\s*<h2 class="slide-title">(.*?)</h2>\s*<div class="badges-group">(.*?)</div>\s*</div>\s*<p class="slide-subtitle">(.*?)</p>\s*</div>\s*<div class="slide-body">(.*?)</div>\s*<div class="slide-footer">(.*?)</div>\s*</section>'
        m = re.search(pat2, html, re.DOTALL)
        if m:
            eyebrow = m.group(1).strip()
            title = m.group(2).strip()
            badges_raw = m.group(3).strip()
            subtitle = m.group(4).strip()
            body_html = m.group(5).strip()
            footer_ref = m.group(6).strip()
        else:
            print(f"FAILED TO EXTRACT SLIDE {sid}")
            continue
    else:
        eyebrow = m.group(2).strip()
        title = m.group(3).strip()
        badges_raw = m.group(4).strip()
        subtitle = m.group(5).strip()
        body_html = m.group(6).strip()
        footer_ref = m.group(7).strip()

    badges = re.findall(r'<span class="badge-pill">(.*?)</span>', badges_raw)
    note_text = notes_dict.get(sid, "")
    
    slides_p1.append({
        "id": sid,
        "eyebrow": eyebrow,
        "title": title,
        "subtitle": subtitle,
        "badges": badges,
        "body_html": body_html,
        "footer_ref": footer_ref,
        "notes": note_text
    })

print(f"Successfully extracted {len(slides_p1)} slides for Part 1.")

# Rebuild presentation_slides_part1.py
code_lines = [
    '"""',
    'presentation_slides_part1.py',
    'Contains slide definitions for Slides 1 through 15',
    '"""',
    '',
    'SLIDES_PART1 = ['
]

for s in slides_p1:
    code_lines.append(f"    # SLIDE {s['id']}: {s['title']}")
    code_lines.append("    {")
    code_lines.append(f"        \"id\": {s['id']},")
    code_lines.append(f"        \"eyebrow\": {json.dumps(s['eyebrow'])},")
    code_lines.append(f"        \"title\": {json.dumps(s['title'])},")
    code_lines.append(f"        \"subtitle\": {json.dumps(s['subtitle'])},")
    code_lines.append(f"        \"badges\": {json.dumps(s['badges'])},")
    code_lines.append("        \"body_html\": \"\"\"")
    code_lines.append(s['body_html'])
    code_lines.append("\"\"\",")
    code_lines.append(f"        \"footer_ref\": {json.dumps(s['footer_ref'])},")
    code_lines.append("        \"notes\": \"\"\"")
    code_lines.append(s['notes'])
    code_lines.append("\"\"\"")
    code_lines.append("    },")
    code_lines.append("")

code_lines.append("]")

Path("scripts/presentation_slides_part1.py").write_text("\n".join(code_lines) + "\n", encoding="utf-8")
print("Reconstructed scripts/presentation_slides_part1.py cleanly!")
