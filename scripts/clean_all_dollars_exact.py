from pathlib import Path

# Clean presentation_slides_part1.py
p1_path = Path("d:/Helixx/scripts/presentation_slides_part1.py")
lines1 = p1_path.read_text(encoding="utf-8").splitlines()

replacements_part1 = {
    195: '              <li><strong>Empirical Correlation:</strong> Achieves reasonable ranking on naked RNA (<em>r</em> &asymp; 0.65), but collapses completely on modified oligonucleotides (<em>r</em> &lt; 0.18).</li>',
    207: '              <li><strong>Data Leakage via Random Splits:</strong> Published test correlations (<em>r</em> &gt; 0.85) were artifacts of random splitting across sliding-window transcript tiles.</li>',
    263: '                <td>Sequence-only models fail entirely on fully modified oligonucleotides (<em>r</em> &lt; 0.20).</td>',
    412: '                <p><strong>Input:</strong> Lead 21-mer sequence + target dose (<em>C</em> &isin; [0.001, 10,000] nM)<br>',
    568: '            <p class="card-desc">Experimental transfection concentrations span <strong>over 5 orders of magnitude</strong> (0.001 nM to 10,000 nM).</p>',
    580: '              <li>Peak concentrations: 0.1 nM (12.4%), 1.0 nM (21.8%), 10.0 nM (44.1%), 100.0 nM (15.2%).</li>',
    592: "              <li><strong>2'-O-Methyl (2'-OMe, M):</strong> 41.2% of all modified positions (primary nuclease shield).</li>",
    593: "              <li><strong>2'-Fluoro (2'-F, F):</strong> 38.5% of all modified positions (high A-form RNA mimicry).</li>",
    594: '              <li><strong>Phosphorothioate (PS, S):</strong> 14.3% of backbone linkages (terminal exonuclease block).</li>',
    595: "              <li><strong>Emerging Chemistries:</strong> 6.0% (LNA, MOE, DNA, 2'-F-ANA, 5'-Vinylphosphonate, GalNAc).</li>",
    605: '            <p class="card-desc">Distribution of target variable (<em>y</em> = % Biological mRNA Knockdown):</p>',
    617: '              <li>High potency candidates (<em>y</em> &ge; 70%): 38.2% of dataset.</li>',
    618: '              <li>Inactive / resistant candidates (<em>y</em> &lt; 30%): 16.9% of dataset.</li>',
    668: '                <p>Identified identical sequence + chemistry + dose combinations across independent publications. Computed robust median knockdown values. Flagged and eliminated conflicting replicates where variance exceeded &sigma; &gt; 25%.</p>',
    674: '                <p>Eliminated assays tested at non-physiological concentrations (&gt; 50 &mu;M) where non-specific cytotoxicity dominates silencing, and removed assays with invalid exposure durations (&lt; 6h or &gt; 120h).</p>',
    709: '                  <td>After Replicate Aggregation (&sigma; &le; 25%)</td>',
    939: '                  <td><code>log<sub>10</sub>(Dose_nM)</code>, Relative Dose, Incubation Duration, Hepatic Cell Lineage flag (HepG2/Huh7 vs other).</td>',
    967: '              <li><strong>Rank 1: <code>log<sub>10</sub>(Dose_nM)</code> (Feature 513):</strong> Accounts for 18.4% of total tree split gain. Confirms that conditioning on exposure is paramount.</li>',
    1008: '            <p class="card-desc">In transcript tiling screens, adjacent 21-mers share 18 of 19 core base pairs (94.7% sequence identity). When partitioned randomly:</p>',
    1170: "              <li><strong>Joint Interaction Learning:</strong> Decision tree split nodes natively discover interaction thresholds between chemical positions and concentration (e.g. 2'-OMe at pos 2 requiring &ge; 0.5 nM for full efficacy).</li>"
}

for line_num, new_content in replacements_part1.items():
    idx = line_num - 1
    if idx < len(lines1):
        if '$' in lines1[idx]:
            print(f"[P1 L{line_num}] Replacing: {lines1[idx][:60]}...")
            lines1[idx] = new_content
        else:
            print(f"[P1 L{line_num}] Warning: line {line_num} does not contain '$': {lines1[idx]}")

p1_path.write_text("\n".join(lines1) + "\n", encoding="utf-8")
print("Saved part 1.")

# Clean presentation_slides_part2.py
p2_path = Path("d:/Helixx/scripts/presentation_slides_part2.py")
lines2 = p2_path.read_text(encoding="utf-8").splitlines()

replacements_part2 = {
    127: '              <li><strong>L2 Leaf Regularization (&lambda; = 3.0):</strong> Penalizes extreme leaf weights to prevent overfitting on rare chemical modification patterns.</li>',
    215: '              <li><strong>Differential Delta:</strong> Computes &Delta;KD = KD<sub>mod</sub> &minus; KD<sub>parent</sub>, instantly pinpointing potency hotspots.</li>',
    266: '              <li><strong>Domain 1: Duplex Unwinding Barrier (&Delta;&Delta;G&deg;<sub>37</sub>):</strong> Over-stabilized duplexes (&gt; &minus;35 kcal/mol) jam the Argonaute-2 helicase unwinding mechanism, preventing passenger strand discard. Over-stabilized candidates receive a scaled unwinding penalty.</li>',
    478: '              <li><strong>Parameter Sliders:</strong> Configurable concentration (10.0 nM default), incubation duration, and cell lineage selection.</li>',
    492: '              <li><strong>Heuristic Metrics:</strong> Displays start/end coordinates, GC%, Reynolds score, and terminal asymmetry &Delta;&Delta;G.</li>',
    571: '              <li><strong>Delta KD Ranking:</strong> Displays baseline KD%, modified KD%, &Delta;KD, and stability score.</li>',
    621: '              <li><strong>Titration Curves:</strong> Simulates biological response across 5 decades (0.01 nM to 100 nM).</li>',
    635: '              <li><strong>Zero Flat-Lining:</strong> Verifies that varying dose from 1 nM &rarr; 10 nM &rarr; 50 nM produces distinct scores.</li>',
    992: '              <li><strong>Proof 3 (Multi-Dose Efficacy Discrimination):</strong> Held-out ROC-AUC of 0.9312 proves the model reliably separates high-potency clinical leads (&ge; 70% KD) from ineffective candidates.</li>',
    1002: '            <p class="card-desc">All 6 FDA-approved siRNAs were strictly withheld from training and evaluated at standard screening dose (10.0 nM):</p>'
}

for line_num, new_content in replacements_part2.items():
    idx = line_num - 1
    if idx < len(lines2):
        if '$' in lines2[idx]:
            print(f"[P2 L{line_num}] Replacing: {lines2[idx][:60]}...")
            lines2[idx] = new_content
        else:
            print(f"[P2 L{line_num}] Warning: line {line_num} does not contain '$': {lines2[idx]}")

p2_path.write_text("\n".join(lines2) + "\n", encoding="utf-8")
print("Saved part 2.")

# Clean generate_helixzero_presentation.py
gen_path = Path("d:/Helixx/scripts/generate_helixzero_presentation.py")
gen_txt = gen_path.read_text(encoding="utf-8")

old_mathjax = """<!-- MathJax for rendering LaTeX equations offline/online -->
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>"""

new_mathjax = """<!-- Clean native typography without external math scripts -->"""

if old_mathjax in gen_txt:
    gen_txt = gen_txt.replace(old_mathjax, new_mathjax)
    gen_path.write_text(gen_txt, encoding="utf-8")
    print("Cleaned MathJax from generate_helixzero_presentation.py")
else:
    print("MathJax snippet not found in generate_helixzero_presentation.py")
