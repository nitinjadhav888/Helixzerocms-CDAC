import re

def fix_latex(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace common LaTeX sequences that might get corrupted by Python string escapes
    # e.g. \rho, \rightarrow, \tau, \theta, \times, \Delta, \sigma, \lambda, \mu, \le, \ge
    replacements = [
        (r'\rho', r'\\rho'),
        (r'\rightarrow', r'\\rightarrow'),
        (r'\to', r'\\to'),
        (r'\tau', r'\\tau'),
        (r'\theta', r'\\theta'),
        (r'\times', r'\\times'),
        (r'\Delta', r'\\Delta'),
        (r'\sigma', r'\\sigma'),
        (r'\lambda', r'\\lambda'),
        (r'\mu', r'\\mu'),
        (r'\le', r'\\le'),
        (r'\ge', r'\\ge'),
        (r'\approx', r'\\approx'),
        (r'\Big', r'\\Big'),
        (r'\hat', r'\\hat'),
    ]

    # But don't double escape if already escaped as \\
    for target, repl in replacements:
        # Match target not preceded by backslash
        pattern = r'(?<!\\)' + re.escape(target)
        content = re.sub(pattern, repl, content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed LaTeX in:", filepath)

fix_latex("scripts/presentation_slides_part1.py")
fix_latex("scripts/presentation_slides_part2.py")
