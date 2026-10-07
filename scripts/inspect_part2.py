with open('scripts/presentation_slides_part2.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if '"id":' in line or 'SLIDE ' in line:
            print(f"{idx}: {line.strip()}")
