import re
from pathlib import Path

scripts_dir = Path("d:/Helixx/scripts")

def clean_part1():
    p1 = scripts_dir / "presentation_slides_part1.py"
    txt = p1.read_text(encoding="utf-8")
    
    # Specific replacements
    replacements = [
        (r'\($r &lt; 0\.18\$\)', r'(<em>r</em> &lt; 0.18)'),
        (r'\($r &gt; 0\.85\$\)', r'(<em>r</em> &gt; 0.85)'),
        (r'\($r &lt; 0\.20\$\)', r'(<em>r</em> &lt; 0.20)'),
        (r'\(\$C \\in \[0\.001, 10000\]\$ nM\)', r'(<em>C</em> &isin; [0.001, 10,000] nM)'),
        (r'\(\$0\.001\\,\\text\{nM\}\$ to \$10,000\\,\\text\{nM\}\$\)', r'(0.001 nM to 10,000 nM)'),
        (r'\$0\.1\\,\\text\{nM\}\$ \(\$12\.4\\%\$\) , \$1\.0\\,\\text\{nM\}\$ \(\$21\.8\\%\$\) , \$10\.0\\,\\text\{nM\}\$ \(\$44\.1\\%\$\) , \$100\.0\\,\\text\{nM\}\$ \(\$15\.2\\%\$\)\.',
         r'0.1 nM (12.4%), 1.0 nM (21.8%), 10.0 nM (44.1%), 100.0 nM (15.2%).'),
        (r'\$41\.2\\%\$', r'41.2%'),
        (r'\$38\.5\\%\$', r'38.5%'),
        (r'\$14\.3\\%\$', r'14.3%'),
        (r'\$6\.0\\%\$', r'6.0%'),
        (r'\(\$y = \\%\\,\\text\{Biological mRNA Knockdown\}\$\)', r'(<em>y</em> = % Biological mRNA Knockdown)'),
        (r'\(\$y \\ge 70\\%\$\): \$38\.2\\%\$', r'(<em>y</em> &ge; 70%): 38.2%'),
        (r'\(\$y &lt; 30\\%\$\): \$16\.9\\%\$', r'(<em>y</em> &lt; 30%): 16.9%'),
        (r'\$\\sigma &gt; 25\\%\$', r'&sigma; &gt; 25%'),
        (r'\(\$&gt; 50\\,\\mu\\text\{M\}\$\)', r'(&gt; 50 &mu;M)'),
        (r'\(\$&lt; 6\\text\{h\}\$ or \$&gt; 120\\text\{h\}\$\)', r'(&lt; 6h or &gt; 120h)'),
        (r'\(\\\\sigma \\\\le 25\\%\)', r'(&sigma; &le; 25%)'),
        (r'\$\\log<sub>10</sub>\(\\\\text\{Dose\\\\_nM\}\)\$', r'<code>log<sub>10</sub>(Dose_nM)</code>'),
        (r'\$\\log<sub>10</sub>\(\\text\{Dose_nM\}\)\$', r'<code>log<sub>10</sub>(Dose_nM)</code>'),
        (r'\(\$94\.7\\%\$\)', r'(94.7%)'),
        (r'Pearson \$r &gt; 0\.88\$', r'Pearson <em>r</em> &gt; 0.88'),
        (r'collapses to \$r &lt; 0\.50\$', r'collapses to <em>r</em> &lt; 0.50'),
        (r'\(\$R<sup>2</sup> = 0\.4497\$\)', r'(R<sup>2</sup> = 0.4497)'),
        (r'<th>Spearman \$\\rho\$</th>', r'<th>Spearman &rho;</th>'),
        (r'\$r = 0\.8044 - 0\.8788\$', r'r = 0.8044 &ndash; 0.8788'),
        (r'\$\\ge 0\.5\\,\\text\{nM\}\$', r'&ge; 0.5 nM'),
    ]
    
    for pat, rep in replacements:
        txt = re.sub(pat, rep, txt)
        
    p1.write_text(txt, encoding="utf-8")
    print("Cleaned part 1")

def clean_part2():
    p2 = scripts_dir / "presentation_slides_part2.py"
    txt = p2.read_text(encoding="utf-8")
    
    replacements = [
        (r'\(\$\\lambda = 3\.0\$\)', r'(&lambda; = 3.0)'),
        (r'\$\\Delta\\text\{KD\} = \\text\{KD\}_\{\\text\{mod\}\} - \\text\{KD\}_\{\\text\{parent\}\}\$', r'&Delta;KD = KD<sub>mod</sub> &minus; KD<sub>parent</sub>'),
        (r'\(\$\\Delta\\Delta G\^\\circ_\{37\}\$\)', r'(&Delta;&Delta;G&deg;<sub>37</sub>)'),
        (r'\(\$&gt; -35\\,\\text\{kcal/mol\}\$\)', r'(&gt; &minus;35 kcal/mol)'),
        (r'\(\$10\.0\\,\\text\{nM\}\$ default\)', r'(10.0 nM default)'),
        (r'\$\\Delta\\Delta G\$', r'&Delta;&Delta;G'),
        (r'\$\\Delta\\text\{KD\}\$', r'&Delta;KD'),
        (r'\(\$0\.01\\,\\text\{nM\}\$ to \$100\\,\\text\{nM\}\$\)', r'(0.01 nM to 100 nM)'),
        (r'\$1\\,\\text\{nM\} \\to 10\\,\\text\{nM\} \\to 50\\,\\text\{nM\}\$', r'1 nM &rarr; 10 nM &rarr; 50 nM'),
        (r'\(\$\\ge 70\\%\$ KD\)', r'(&ge; 70% KD)'),
        (r'\(\$10\.0\\,\\text\{nM\}\$\)', r'(10.0 nM)'),
    ]
    
    for pat, rep in replacements:
        txt = re.sub(pat, rep, txt)
        
    p2.write_text(txt, encoding="utf-8")
    print("Cleaned part 2")

if __name__ == "__main__":
    clean_part1()
    clean_part2()
