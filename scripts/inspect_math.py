import re

for fname in ['scripts/presentation_slides_part1.py', 'scripts/presentation_slides_part2.py']:
    with open(fname, encoding='utf-8') as f:
        text = f.read()
    matches = re.findall(r'\$\$?[^$\n]+\$\$?', text)
    print(f"{fname}: {len(matches)} math blocks")
    unique_matches = sorted(set(matches))
    for m in unique_matches[:40]:
        print("  ", m)
