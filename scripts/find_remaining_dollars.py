with open('scripts/presentation_slides_part1.py', 'r', encoding='utf-8') as f:
    lines1 = f.readlines()
print("PART 1 REMAINING:")
for i, l in enumerate(lines1, 1):
    if '$' in l:
        print(f"L{i}: {l.strip()}")

with open('scripts/presentation_slides_part2.py', 'r', encoding='utf-8') as f:
    lines2 = f.readlines()
print("\nPART 2 REMAINING:")
for i, l in enumerate(lines2, 1):
    if '$' in l:
        print(f"L{i}: {l.strip()}")
