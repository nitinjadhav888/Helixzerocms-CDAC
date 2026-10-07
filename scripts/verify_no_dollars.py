from pathlib import Path

for name in ["HelixZero_Software_Architecture_Presentation.html", "Paper/HelixZero_Software_Presentation.html"]:
    fpath = Path("d:/Helixx") / name
    text = fpath.read_text(encoding="utf-8")
    lines_with_dollar = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if "$" in line:
            lines_with_dollar.append((idx, line))
    print(f"File {name}: {len(lines_with_dollar)} lines with '$'")
    for idx, line in lines_with_dollar:
        print(f"  Line {idx}: {line[:120]}")
