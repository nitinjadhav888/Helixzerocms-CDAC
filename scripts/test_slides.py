import ast
import traceback

def test_file(fname):
    print("Testing", fname)
    with open(fname, "r", encoding="utf-8") as f:
        src = f.read()
    try:
        ast.parse(src)
        print("  Parsed successfully!")
    except SyntaxError as e:
        print(f"  SyntaxError at line {e.lineno}, col {e.offset}:")
        print(f"  Line: {e.text}")
        lines = src.splitlines()
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        for i in range(start, end):
            prefix = "-> " if i + 1 == e.lineno else "   "
            print(f"{prefix}{i+1}: {lines[i]}")

if __name__ == "__main__":
    test_file("scripts/presentation_slides_part1.py")
    test_file("scripts/presentation_slides_part2.py")
