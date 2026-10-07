import re

def clean_slides_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Exact string replacements for complex equations
    replacements_exact = [
        # Slide 2 & 18 & 21
        (r"$$\mathcal{S} = \prod_{p=1}^{42} |\mathcal{M}_p| \approx 30^{42} \approx 1.09 \times 10^{62} \text{ configurations}$$",
         "S = &prod;<sub>p=1..42</sub> |M<sub>p</sub>| &asymp; 30<sup>42</sup> &asymp; 1.09 &times; 10<sup>62</sup> unique configurations"),
        (r"$$P(\text{Leakage}) = 1 - (1 - p_{\text{test}})^k \approx 1 - (1 - 0.2)^2 = 0.96 \quad (96.0\%)$$",
         "P(Leakage) = 1 &minus; (1 &minus; p<sub>test</sub>)<sup>k</sup> &asymp; 1 &minus; (1 &minus; 0.2)<sup>2</sup> = 0.96 (96.0%)"),
        (r"$$\text{Estimated } IC_{50} = C \times \left(\frac{100.0 - \widehat{\text{KD}}}{\widehat{\text{KD}}}\right) \quad (\text{nM})$$",
         "Estimated IC<sub>50</sub> = C &times; [ (100.0 &minus; KD<sub>pred</sub>) / KD<sub>pred</sub> ] (nM)"),
        (r"$$\text{Estimated } pIC_{50} = 9.0 - \log_{10}\Big(\max(10^{-4}, \text{Estimated } IC_{50})\Big)$$",
         "Estimated pIC<sub>50</sub> = 9.0 &minus; log<sub>10</sub>( max(10<sup>&minus;4</sup>, Estimated IC<sub>50</sub>) )"),
        (r"$$\text{Slot}_i = \Big( \text{Base}_i, \text{Sugar}_i, \text{Linkage}_i, \text{Terminal}_i, \text{Ligand}_i \Big)$$",
         "Slot<sub>i</sub> = ( Base<sub>i</sub>, Sugar<sub>i</sub>, Linkage<sub>i</sub>, Terminal<sub>i</sub>, Ligand<sub>i</sub> )"),
        (r"$$\widehat{\text{KD}} = \text{CatBoostRegressor}\Big( [\mathbf{x}_{444\text{-chem}}, \mathbf{z}_{64\text{-FM}}, \mathbf{t}_{5\text{-thermo}}, \mathbf{c}_{4\text{-dose}}] \Big)$$",
         "KD<sub>pred</sub> = CatBoostRegressor([ x<sub>444-chem</sub>, z<sub>64-FM</sub>, t<sub>5-thermo</sub>, c<sub>4-dose</sub> ])"),
        (r"$$f: (\mathbf{S}_{\text{chem}} \in \mathbb{R}^{444}, \mathbf{z}_{\text{FM}} \in \mathbb{R}^{64}, \mathbf{t}_{\text{thermo}} \in \mathbb{R}^5, \mathbf{c}_{\text{dose}} \in \mathbb{R}^4) \longrightarrow \widehat{\text{KD}} \in [0, 100]$$",
         "f: ( S<sub>chem</sub> &isin; &reals;<sup>444</sup>, z<sub>FM</sub> &isin; &reals;<sup>64</sup>, t<sub>thermo</sub> &isin; &reals;<sup>5</sup>, c<sub>dose</sub> &isin; &reals;<sup>4</sup> ) &rarr; KD &isin; [0, 100]"),
        (r"$$N_{\text{perms}} = 42 \text{ slots} \times 19.33 \text{ mods/slot} = 812 \text{ unique variants}$$",
         "N<sub>perms</sub> = 42 slots &times; 19.33 mods/slot = 812 unique single-site variants"),
        (r"$$\mathcal{L}_{\text{RMSE}}(\mathbf{y}, \widehat{\mathbf{y}}) = \sqrt{\frac{1}{N} \sum_{i=1}^N (y_i - \hat{y}_i)^2} + \lambda \sum_{j=1}^J w_j^2$$",
         "Loss(RMSE) = &radic;[ (1/N) &sum;(y<sub>i</sub> &minus; y&#770;<sub>i</sub>)<sup>2</sup> ] + &lambda; &sum; w<sub>j</sub><sup>2</sup>"),
        (r"$$\text{Encoding: } A = 00_2, \quad C = 01_2, \quad G = 10_2, \quad U/T = 11_2$$",
         "Encoding: A = 00<sub>2</sub>, C = 01<sub>2</sub>, G = 10<sub>2</sub>, U/T = 11<sub>2</sub>"),
        (r"$$\text{Helical Rise } (h) = 2.81\,\text{\AA}/\text{bp}, \quad \text{Helical Twist } (\theta) = 32.7^\circ \, (0.5708\,\text{rad}/\text{bp})$$",
         "Helical Rise (h) = 2.81 &Aring;/bp, Helical Twist (&theta;) = 32.7&deg; (0.5708 rad/bp)"),
    ]

    for orig, repl in replacements_exact:
        text = text.replace(orig, repl)

    # Clean double escaped variants as well
    for orig, repl in replacements_exact:
        double_orig = orig.replace('\\', '\\\\')
        text = text.replace(double_orig, repl)

    # General replacements
    subs = [
        # log10
        (r'\$\\?\\?log_\{10\}\(\\\\?text\{Dose\\\\?_nM\}\)\$', '<code>log<sub>10</sub>(Dose_nM)</code>'),
        (r'\$\\?\\?log_\{10\}\(\\\\?text\{Dose\}\)\$', '<code>log<sub>10</sub>(Dose)</code>'),
        (r'\\log_\{10\}\(\\text\{Dose\\_nM\}\)', 'log<sub>10</sub>(Dose_nM)'),
        (r'\$\\log_\{10\}\$', 'log<sub>10</sub>'),
        (r'\\log_\{10\}', 'log<sub>10</sub>'),

        # search & permutations
        (r'\$42\s*\\\\?times\s*19\.3\s*\\\\?approx\s*812\$', '42 &times; 19.3 &asymp; 812'),
        (r'\$42\s*\\\\?times\s*19\.33\s*\\\\?approx\s*812\$', '42 &times; 19.33 &asymp; 812'),
        (r'\$\(812,\s*517\)\$', '(812, 517)'),
        (r'\$1\\,\\text\{nM\}\s*\\\\?to\s*10\\,\\text\{nM\}\s*\\\\?to\s*50\\,\\text\{nM\}\$', '1 nM &rarr; 10 nM &rarr; 50 nM'),
        (r'\$pIC_\{50\}\s*\\\\?to\s*\\\\?text\{Hill\}\$', 'pIC<sub>50</sub> &rarr; Hill'),
        (r'pIC_\{50\}\s*\\to\s*\\text\{Hill\}', 'pIC<sub>50</sub> &rarr; Hill'),
        (r'\$pIC_\{50\}\$', 'pIC<sub>50</sub>'),
        (r'\$IC_\{50\}\$', 'IC<sub>50</sub>'),
        (r'pIC_\{50\}', 'pIC<sub>50</sub>'),
        (r'IC_\{50\}', 'IC<sub>50</sub>'),

        # energy & delta
        (r'\$\\Delta\\Delta G\^\\circ_\{37\}\$', '&Delta;&Delta;G&deg;<sub>37</sub>'),
        (r'\$\\Delta\\Delta G\$', '&Delta;&Delta;G'),
        (r'\\Delta\\Delta G\^\\circ_\{37\}', '&Delta;&Delta;G&deg;<sub>37</sub>'),
        (r'\\Delta\\Delta G', '&Delta;&Delta;G'),
        (r'\$\\Delta\\text\{KD\}\s*=\s*\\text\{KD\}_\{mod\}\s*-\s*\\text\{KD\}_\{parent\}\$', '&Delta;KD = KD<sub>mod</sub> &minus; KD<sub>parent</sub>'),
        (r'\\Delta\\text\{KD\}\s*=\s*\\text\{KD\}_\{mod\}\s*-\s*\\text\{KD\}_\{parent\}', '&Delta;KD = KD<sub>mod</sub> &minus; KD<sub>parent</sub>'),
        (r'\$\\Delta\\text\{KD\}\$', '&Delta;KD'),
        (r'\\Delta\\text\{KD\}', '&Delta;KD'),

        # lambda, sigma, inequalities
        (r'\$\\lambda\s*=\s*3\.0\$', '&lambda; = 3.0'),
        (r'\$\\lambda\$', '&lambda;'),
        (r'\$\\?\\?sigma\s*\\\\?le\s*25\\%\$', '&sigma; &le; 25%'),
        (r'\$\\ge\s*70\\%\$', '&ge; 70%'),
        (r'\\ge\s*70\\%', '&ge; 70%'),
        (r'\$y\s*\\ge\s*70\\%\$', 'y &ge; 70%'),
        (r'\$y\s*<\s*30\\%\$', 'y &lt; 30%'),
        (r'\$y\s*=\s*\\%\\,\\text\{Biological mRNA Knockdown\}\$', 'y = % Biological mRNA Knockdown'),
        (r'\$r\s*\\\\?approx\s*0\.65\$', 'r &asymp; 0.65'),
        (r'\$r\s*<\s*0\.18\$', 'r &lt; 0.18'),
        (r'\$r\s*<\s*0\.20\$', 'r &lt; 0.20'),
        (r'\$r\s*>\s*0\.85\$', 'r &gt; 0.85'),
        (r'\$r\s*=\s*0\.8291\$', 'r = 0.8291'),
        (r'\$r\s*=\s*0\.8788\$', 'r = 0.8788'),
        (r'\$r\s*=\s*0\.8359\$', 'r = 0.8359'),
        (r'\$r\s*=\s*0\.8334\$', 'r = 0.8334'),
        (r'\$r\s*=\s*0\.8187\$', 'r = 0.8187'),
        (r'\$r\s*=\s*0\.6776\$', 'r = 0.6776'),
        (r'\$r\s*=\s*0\.1771\$', 'r = 0.1771'),
        (r'\$r\s*=\s*0\.0631\$', 'r = 0.0631'),
        (r'\$r\$', '<em>r</em>'),

        # concentrations & numbers
        (r'\$>&gt;\s*(-?\d+)\\,\\text\{kcal/mol\}\$', '&gt; \\1 kcal/mol'),
        (r'\$>&gt;\s*50\\,\\mu\\text\{M\}\$', '&gt; 50 &mu;M'),
        (r'\$>&gt;\s*120\\text\{h\}\$', '&gt; 120h'),
        (r'\$&lt;\s*6\\text\{h\}\$', '&lt; 6h'),
        (r'\$0\.0\s*-\s*100\.0\$', '0.0% &ndash; 100.0%'),
        (r'\$0\.001\\,\\text\{nM\}\$', '0.001 nM'),
        (r'\$0\.01\\,\\text\{nM\}\$', '0.01 nM'),
        (r'\$0\.1\\,\\text\{nM\}\$', '0.1 nM'),
        (r'\$1\.0\\,\\text\{nM\}\$', '1.0 nM'),
        (r'\$10\.0\\,\\text\{nM\}\$', '10.0 nM'),
        (r'\$100\.0\\,\\text\{nM\}\$', '100.0 nM'),
        (r'\$100\\,\\text\{nM\}\$', '100 nM'),
        (r'\$10,000\\,\\text\{nM\}\$', '10,000 nM'),
        (r'\$C\s*\\in\s*\[0\.001,\s*10000\]\$', 'C &isin; [0.001, 10,000]'),
        (r'\$C\$', 'C'),
        (r'\$N\s*=\s*17,761\$', 'N = 17,761'),
        (r'\$N\s*\\\\?approx\s*2,400\$', 'N &asymp; 2,400'),
        (r'\$N\s*=\s*2,576\$', 'N = 2,576'),
        (r'\$N\$', '<em>N</em>'),
        (r'\$O\(1\)\$', 'O(1)'),
        (r'\$R\^2\s*=\s*-0\.0901\$', 'R<sup>2</sup> = &minus;0.0901'),
        (r'\$R\^2\$', 'R<sup>2</sup>'),
        (r'R\^2', 'R<sup>2</sup>'),
        (r'\$Hu\.csv\$', '<code>Hu.csv</code>'),
        (r'\$Mix\.csv\$', '<code>Mix.csv</code>'),
        (r'\$Taka\.csv\$', '<code>Taka.csv</code>'),
        (r'\$p_\{test\}\$', 'p<sub>test</sub>'),
        (r'\$-5\.0\$', '&minus;5.0'),
        (r'\$-8\.0\$', '&minus;8.0'),
        (r'\$0\.9312\$', '0.9312'),
        (r'\$0\.8187\$', '0.8187'),
        (r'\$0\.8359\$', '0.8359'),
        (r'\$0\.8334\$', '0.8334'),
        (r'\$0\.8788\$', '0.8788'),
        (r'\$0\.6776\$', '0.6776'),
        (r'\$0\.1771\$', '0.1771'),
    ]

    for pat, rep in subs:
        text = re.sub(pat, rep, text)

    # Any remaining percentages $12.4\%$ -> 12.4%
    text = re.sub(r'\$(\d+(?:\.\d+)?)\\\%\$', r'\1%', text)
    text = re.sub(r'\$(\d+(?:\.\d+)?)\%\$', r'\1%', text)

    # Clean any leftover standalone $
    # E.g. $10.0\,\text{nM}$ -> 10.0 nM
    text = re.sub(r'\$(\d+(?:\.\d+)?)\\,\\text\{nM\}\$', r'\1 nM', text)
    text = re.sub(r'\$(\d+(?:\.\d+)?)\\,\\text\{kcal/mol\}\$', r'\1 kcal/mol', text)

    return text

if __name__ == '__main__':
    for fpath in ['scripts/presentation_slides_part1.py', 'scripts/presentation_slides_part2.py']:
        cleaned = clean_slides_content(fpath)
        with open(fpath, 'w', encoding='utf-8') as out:
            out.write(cleaned)
        print(f"Cleaned {fpath}. Remaining '$' count: {cleaned.count('$')}")
