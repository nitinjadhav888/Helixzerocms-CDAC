"""
presentation_slides_part1.py
Contains slide definitions for Slides 1 through 15
"""

SLIDES_PART1 = [
    # SLIDE 1: Helix-Zero: Unified, Chemistry-Aware Machine Learning & High-Throughput Software Architecture for Therapeutic siRNA Design
    {
        "id": 1,
        "eyebrow": "EXECUTIVE TECHNICAL OVERVIEW | C-DAC PUNE HPC-M&BA",
        "title": "Helix-Zero: Unified, Chemistry-Aware Machine Learning & High-Throughput Software Architecture for Therapeutic siRNA Design",
        "subtitle": "An End-to-End Data Science & Software Engineering Journey: From 517-D Multi-Modal Feature Spaces to Sub-Second In Silico Screening",
        "badges": ["Dual-Stage ML Core", "Model A: LightGBM (214-D)", "Model B: CatBoost (517-D)", "Zero-Leakage GroupKFold", "Sub-Second In Silico Screening"],
        "body_html": """
<div class="pipeline-flowchart-bar">
  <div class="flow-step-node" data-deep-dive="takayuki_benchmark" title="Click: Explore Stage 1 LightGBM 214-D Screen">
    <span class="flow-step-icon">⚡</span>
    <div class="flow-step-info">
      <strong>Stage 1: Model A</strong>
      <span>LightGBM (214-D) &bull; &lt; 0.05s</span>
    </div>
  </div>
  <div class="flow-node-arrow">&rarr;</div>
  <div class="flow-step-node" data-deep-dive="heldout_multidose" title="Click: Explore Stage 2 CatBoost 517-D Chemistry Core">
    <span class="flow-step-icon">🔬</span>
    <div class="flow-step-info">
      <strong>Stage 2: Model B</strong>
      <span>CatBoost (517-D) &bull; Multi-Dose</span>
    </div>
  </div>
  <div class="flow-node-arrow">&rarr;</div>
  <div class="flow-step-node" data-deep-dive="biophysical_guardrails" title="Click: Explore 4-Domain Safety Firewall">
    <span class="flow-step-icon">🛡️</span>
    <div class="flow-step-info">
      <strong>Stage 3: Biophysics</strong>
      <span>4-Domain Safety Firewall</span>
    </div>
  </div>
  <div class="flow-node-arrow">&rarr;</div>
  <div class="flow-step-node" data-deep-dive="fda_blind_validation" title="Click: Explore Blind Clinical Validation">
    <span class="flow-step-icon">💊</span>
    <div class="flow-step-info">
      <strong>Clinical Lead</strong>
      <span>FDA Drug-Grade Design</span>
    </div>
  </div>
</div>

<div class="cards-grid cards-3">
          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">DUAL-STAGE ML CORE</span>
              <h3>Model A (LightGBM) &amp; Model B (CatBoost)</h3>
            </div>
            <p class="card-desc">An integrated two-stage machine learning system decoupling canonical transcript screening from synthetic chemical optimization:</p>
            <div class="metric-row">
              <div class="metric-item clickable-metric" data-deep-dive="takayuki_benchmark" title="Click for Takayuki Screen Benchmark Evaluation">
                <span class="metric-val">r = 0.8788</span>
                <span class="metric-lbl">Model A (Takayuki Screen)</span>
              </div>
              <div class="metric-item clickable-metric" data-deep-dive="heldout_multidose" title="Click for Held-Out Multi-Dose Evaluation">
                <span class="metric-val">r = 0.8359</span>
                <span class="metric-lbl">Model B (Held-Out Multi-Dose)</span>
              </div>
            </div>
            <ul class="bullet-list">
              <li><strong>Stage 1 (Model A &ndash; LightGBM, 214-D):</strong> High-speed transcript-wide screening using Reynolds/Ui-Tei rules, thermodynamic asymmetry (&Delta;&Delta;G&deg;<sub>37</sub>), and ViennaRNA target opening accessibility in &lt; 0.05s.</li>
              <li><strong>Stage 2 (Model B &ndash; CatBoost, 517-D):</strong> Multi-modal chemical optimization mapping 444 chemical slots, 64 RNA-FM foundation embeddings, 5 thermodynamic features, and 4 continuous dose covariates with closed-form <em>pIC<sub>50</sub></em> / <em>IC<sub>50</sub></em> Hill derivations.</li>
            </ul>
          </div>

          <div class="card border-purple">
            <div class="card-header">
              <span class="card-tag">DATA &amp; INTEGRITY</span>
              <h3>Zero-Leakage GroupKFold Auditing</h3>
            </div>
            <p class="card-desc">Trained on <strong>17,761 experimentally measured assays</strong> across 5,251 independent antisense sequence clusters, strictly withholding sequence overlaps.</p>
            <div class="metric-row">
              <div class="metric-item clickable-metric" data-deep-dive="groupkfold_5251" title="Click for GroupKFold Leakage Proof Details">
                <span class="metric-val">5,251</span>
                <span class="metric-lbl">Unique Sequence Groups</span>
              </div>
              <div class="metric-item clickable-metric" data-deep-dive="fda_blind_validation" title="Click for FDA Blind Validation Details">
                <span class="metric-val">100%</span>
                <span class="metric-lbl">FDA Blind Sensitivity</span>
              </div>
            </div>
            <ul class="bullet-list">
              <li>Guarantees zero sequence memorization across train and test folds.</li>
              <li>Validated blindly on all 6 FDA-approved commercial drugs (mean KD = 65.04% @ 10 nM).</li>
            </ul>
          </div>

          <div class="card border-emerald">
            <div class="card-header">
              <span class="card-tag">SAFETY &amp; STRUCTURAL PIPELINE</span>
              <h3>Deterministic Biophysics &amp; 3D Modeling</h3>
            </div>
            <p class="card-desc">Real-time biophysical guardrails combined with a <strong>2-bit whole-transcriptome off-target firewall</strong> and automated continuous 3D PDB generation.</p>
            <div class="metric-row">
              <div class="metric-item clickable-metric" data-deep-dive="chemical_444_features" title="Click for 444 Chemical Slot Breakdown">
                <span class="metric-val">&lt; 0.10s</span>
                <span class="metric-lbl">812-Variant Scan</span>
              </div>
              <div class="metric-item clickable-metric" data-deep-dive="twobit_offtarget" title="Click for 2-Bit Transcriptome Bit-Lookup Details">
                <span class="metric-val">O(1)</span>
                <span class="metric-lbl">Transcriptome Bit-Lookup</span>
              </div>
            </div>
            <ul class="bullet-list">
              <li>Evaluates exonuclease serum stability, TLR7/8 immuno-masking, and Janas seed cytotoxicity.</li>
              <li>Generates unbroken A-form PDB models with B-factor chemical encoding for 3Dmol.js.</li>
            </ul>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: C-DAC HPC-M&BA Technical Stack; Davis et al. (NAR 2025, gkaf479); Bai et al. (Bioinformatics 2024, btae180); Khvorova & Watts (Nat. Biotechnol. 2017); Chen et al. (J. Med. Chem. 2026).",
        "notes": """
<p>Good morning respected mentors and colleagues.</p><p>In my previous presentation here at C-DAC Pune, I covered the biological fundamentals of RNA interference. Today, I am excited to present the complete Data Science, Machine Learning, and Software Engineering journey of Helix-Zero—a project I have developed over the last 8 months.</p><p>The objective was to build an end-to-end platform that can design and optimize therapeutic siRNAs with clinical chemical modifications in sub-second time.</p><p>As you can see on this executive summary slide, our system is powered by three main breakthroughs:
1. First, a coordinated Two-Stage Machine Learning architecture:
   - In Stage 1, we use Model A—a LightGBM model operating on 214 sequence, thermodynamic, and transcript accessibility features—to rapidly screen entire mRNA transcripts in under 50 milliseconds down to top naked sequence leads (achieving r = 0.8788 on Takayuki and r = 0.8044 on Huesken).
   - In Stage 2, we use Model B—our Single Unified CatBoost model operating on a 517-dimensional multi-modal vector space (combining 444 chemical slot encodings, 64 RNA-FM foundation embeddings, 5 ViennaRNA constants, and 4 continuous dose covariates). It achieves a 0.8359 correlation on held-out multi-dose screens and derives analytical pIC50 and IC50 values via dynamic Hill inversion.
2. Second, we enforced strict sequence-level GroupKFold splitting across 5,251 independent sequence clusters, guaranteeing zero data leakage and validating blindly across all 6 FDA-approved drugs.
3. Third, we wrapped the models in deterministic biophysical guardrails, a 2-bit whole-transcriptome off-target firewall, and instant 3D double-helix modeling.</p><p>Today, I will walk you through every step of this engineering journey.</p>
"""
    },

    # SLIDE 2: Problem Formulation: The High-Dimensional Combinatorial Space of Modified Oligonucleotides
    {
        "id": 2,
        "eyebrow": "MATHEMATICAL & COMPUTATIONAL FORMULATION",
        "title": "Problem Formulation: The High-Dimensional Combinatorial Space of Modified Oligonucleotides",
        "subtitle": "Why Traditional Bioinformatic Sequence Matchers Fail on Synthetic Therapeutic Architectures",
        "badges": ["Combinatorial Explosion", "30^42 State Space", "Exposure Confounding", "517-D Unified Vector"],
        "body_html": """
<div class="cards-grid cards-2">
          <div class="card border-rose">
            <div class="card-header">
              <span class="card-tag">THE COMPUTATIONAL CHALLENGE</span>
              <h3>Discrete Combinatorial Explosion</h3>
            </div>
            <p class="card-desc">A standard therapeutic siRNA duplex comprises 21 passenger (sense) nucleotides and 21 guide (antisense) nucleotides (42 ordered positional slots).</p>
            <div class="formula-box">
              S = &prod;<sub>p=1..42</sub> |M<sub>p</sub>| &asymp; 30<sup>42</sup> &asymp; 1.09 &times; 10<sup>62</sup> unique configurations
            </div>
            <ul class="bullet-list">
              <li><strong>Alphabet Limitation:</strong> Canonical 4-letter alphabets ({A, C, G, U}) cannot represent 2'-ribose modifications (2'-OMe, 2'-F, LNA, MOE), phosphorothioate backbones (PS, PS2), or terminal ligands (GalNAc, 5'-VP).</li>
              <li><strong>Non-Linear Epistasis:</strong> Chemical modifications interact non-linearly. A 2'-F substitution at guide position 14 boosts RISC cleavage kinetics, whereas the exact same modification at guide position 10 destroys slicer activity.</li>
              <li><strong>Continuous Label Disconnect:</strong> Experimental potency is reported as % Knockdown at varying concentrations (0.01 nM to 100 nM). Models without dose covariates suffer from <em>exposure confounding</em>.</li>
            </ul>
          </div>

          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">HELIX-ZERO FORMULATION</span>
              <h3>Orthogonal Multi-Modal Regression</h3>
            </div>
            <p class="card-desc">We formalize siRNA optimization as a supervised multi-modal continuous mapping conditioned on sequence, synthetic chemistry, and physical dose:</p>
            <div class="formula-box">
              f: ( S<sub>chem</sub> &isin; &reals;<sup>444</sup>, z<sub>FM</sub> &isin; &reals;<sup>64</sup>, t<sub>thermo</sub> &isin; &reals;<sup>5</sup>, c<sub>dose</sub> &isin; &reals;<sup>4</sup> ) &rarr; KD &isin; [0, 100]
            </div>
            <ul class="bullet-list">
              <li><strong><span class="clickable-pill" data-deep-dive="chemical_444_features" title="Click: 444 Chemical Slot Breakdown" style="color: var(--accent); text-decoration: underline;">S<sub>chem</sub> &isin; &reals;<sup>444</sup></span> (Synthetic Chemistry):</strong> 42 positional slots &times; (4 base + 4 sugar + 2 linkage encodings) + global chemical counts and modification ratios.</li>
              <li><strong><span class="clickable-pill" data-deep-dive="rnafm_foundation" title="Click: RNA-FM 64-D Foundation Embeddings" style="color: var(--accent); text-decoration: underline;">z<sub>FM</sub> &isin; &reals;<sup>64</sup></span> (Biological Foundation):</strong> 100M-parameter RNA-FM embeddings capturing evolutionary fitness and base-pairing context (PCA-compressed to 64 top axes).</li>
              <li><strong><span class="clickable-pill" data-deep-dive="biophysical_guardrails" title="Click: ViennaRNA Thermodynamics" style="color: var(--accent); text-decoration: underline;">t<sub>thermo</sub> &isin; &reals;<sup>5</sup></span> (Biophysical Thermodynamics):</strong> ViennaRNA duplex free energy (&Delta;G<sub>duplex</sub>), ensemble energy, MFE probability, and terminal opening energies.</li>
              <li><strong><span class="clickable-pill" data-deep-dive="heldout_multidose" title="Click: Continuous Dose Covariates" style="color: var(--accent); text-decoration: underline;">c<sub>dose</sub> &isin; &reals;<sup>4</sup></span> (Experimental Exposure):</strong> Continuous <code>log<sub>10</sub>(Dose_nM)</code>, relative dose ratio, incubation duration, and hepatic lineage flag.</li>
              <li><strong>Output KD &isin; [0, 100]:</strong> Continuous predicted percentage of target mRNA knockdown (0% = inactive, 100% = complete silencing).</li>
            </ul>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: Khvorova & Watts (Nat. Biotechnol. 2017, 35:238\u2013248); Martinelli (Cornell, 2023); Chernolovskaya & Zenkova (Curr. Opin. Mol. Ther. 2010, 12:158\u2013167).",
        "notes": """
<p>Why is this problem so challenging from a computer science perspective?</p><p>In clinical reality, 100% of FDA-approved siRNAs are chemically modified. Across 42 nucleotide positions, when you support 30 different chemical modifications, the total number of possible combinations is 30 to the power of 42—which is roughly 10 to the power of 62. That is larger than the number of atoms in our solar system!</p><p>On top of this massive search space, we face two big machine learning hurdles:
1. Chemical modifications do not act linearly. Changing position 14 to 2'-fluoro improves slicing activity, but putting that same modification at position 10 destroys slicing because it interferes with the protein's catalytic core.
2. In public databases, experiments are done at wildly different doses—from 0.01 nM up to 100 nM. If your machine learning model does not know the dose, it gets confused. A weak drug at 50 nM might show 80% knockdown, while a potent drug at 0.1 nM might show only 30% knockdown.</p><p>Helix-Zero solves this by formulating the problem as a unified multi-modal regression:
Look closely at the formula on the right:
f: ( S_chem in R^444, z_FM in R^64, t_thermo in R^5, c_dose in R^4 ) -> KD in [0, 100]</p><p>Here is what each part of this formula means:
- f is our CatBoost decision tree regression function.
- S_chem has 444 dimensions: across all 42 positions, it encodes the 4 nucleotide bases, the 4 sugar modification types (like 2'-OMe and 2'-F), the phosphate backbone linkages (like phosphorothioate), and global chemical totals.
- z_FM has 64 dimensions: these are deep biological embeddings extracted from RNA-FM, a 100-million parameter foundation model trained on evolutionary RNA sequences.
- t_thermo has 5 dimensions: thermodynamic duplex binding and terminal opening energies calculated by ViennaRNA.
- c_dose has 4 dimensions: the physical drug concentration in log10(nM), incubation time, and cell lineage.
These four orthogonal components sum up to exactly 517 features (444 + 64 + 5 + 4 = 517).
The output KD is a continuous scalar from 0 to 100 percent, giving the exact biological knockdown. Because dose is an intrinsic input, this single formula can predict entire dose-response titration curves without any cascading error.</p>
"""
    },

    # SLIDE 3: The Computational Landscape: Three Generations of siRNA Efficacy Modeling
    {
        "id": 3,
        "eyebrow": "COMPUTATIONAL LITERATURE REVIEW | 2004\u20132026",
        "title": "The Computational Landscape: Three Generations of siRNA Efficacy Modeling",
        "subtitle": "A Critical Review of Heuristic Rules, Classical Machine Learning, and Deep Learning Architectures in Real-World Drug Design",
        "badges": ["Literature Review", "Reynolds & Ui-Tei (2004)", "Classical ML (2006-2020)", "OligoFormer (2024)", "MEG-mod GNN (2026)"],
        "body_html": """
<div class="cards-grid cards-3">
          <div class="card border-rose">
            <div class="card-header">
              <span class="card-tag">GEN 1: RULE-BASED HEURISTICS</span>
              <h3>Reynolds &amp; Ui-Tei Rules (2004&ndash;2010)</h3>
            </div>
            <p class="card-desc">Empirical criteria evaluating nucleotide composition, GC content, and terminal thermodynamic asymmetry.</p>
            <ul class="bullet-list">
              <li><strong>Canonical 4-Letter Alphabet Only:</strong> Evaluates only unmodified RNA ({A, C, G, U}). Completely blind to 2'-ribose modifications (2'-OMe, 2'-F) and phosphorothioate backbones required in 100% of clinical therapeutics.</li>
              <li><strong>Linear Additivity Assumption:</strong> Treats individual nucleotide positions as independent additive terms, ignoring complex secondary structure opening energetics and non-linear epistasis.</li>
              <li><strong>Empirical Breakdown on Modified RNA:</strong> While moderately predictive on naked RNA (<em>r</em> &asymp; 0.65), correlation collapses to baseline (<em>r</em> &lt; 0.18) on chemically modified oligonucleotides (Davis et al., NAR 2025).</li>
            </ul>
          </div>

          <div class="card border-yellow">
            <div class="card-header">
              <span class="card-tag">GEN 2: CLASSICAL MACHINE LEARNING</span>
              <h3>DSIR, BiRNA, &amp; SMEpred (2006&ndash;2020)</h3>
            </div>
            <p class="card-desc">Linear regression (Lasso), Support Vector Machines (SVM), and Random Forests trained on early academic screens.</p>
            <ul class="bullet-list">
              <li><strong>Restricted Training Corpora:</strong> Trained on small early screens (e.g. Novartis Huesken 2006, <em>N</em> = 2,431 siRNAs; Takayuki 2013) that were exclusively unmodified naked sequences.</li>
              <li><strong>Sliding-Window Data Leakage:</strong> Published models frequently partitioned overlapping 21-mer tiling windows randomly, creating sequence memorization rather than learning generalizable biological SAR rules.</li>
              <li><strong>Fixed-Concentration Assumption:</strong> Assumed static screening doses (e.g. fixed 10 nM or 100 nM), leaving models unable to predict non-linear concentration-response titration curves or binding affinities.</li>
            </ul>
          </div>

          <div class="card border-purple">
            <div class="card-header">
              <span class="card-tag">GEN 3: MODERN DEEP LEARNING</span>
              <h3>OligoFormer (2024) &amp; MEG-mod GNN (2026)</h3>
            </div>
            <p class="card-desc">Transformers and Graph Neural Networks integrating RNA foundation models (RNA-FM, RNAErnie) and atomic graphs (Uni-Mol).</p>
            <ul class="bullet-list">
              <li><strong>OligoFormer (Bai et al., Bioinformatics 2024):</strong> Combines 100M-parameter RNA-FM embeddings with ViennaRNA thermodynamics for naked sequences, but remains fundamentally restricted to canonical 4-letter RNA ({A, C, G, U}).</li>
              <li><strong>MEG-mod (Chen et al., J. Med. Chem. 2026):</strong> Advanced multiview GNN integrating Uni-Mol 1B, RNAErnie, and RNAcofold duplex graphs for modified RNA (reported test <em>r</em> = 0.9171). However, it relies on multi-GB precomputed embedding lookups, lacks native continuous dosage conditioning (<code>log<sub>10</sub>(Dose_nM)</code>), and graph convolutions create substantial latency during interactive combinatorial searches.</li>
              <li><strong>The Architectural Gap:</strong> Published literature decouples naked sequence triage (OligoFormer) from modified lead modeling (MEG-mod). Helix-Zero bridges this with a unified, sub-second two-stage pipeline.</li>
            </ul>
          </div>
        </div>
""",
        "footer_ref": "Research References: Reynolds et al. (Nat. Biotechnol. 2004, 22:326\u2013330); Huesken et al. (Nat. Biotechnol. 2005, 23:995\u20131001); Bai et al. (Bioinformatics 2024, 40:btae180); Chen et al. (J. Med. Chem. 2026, 69:13434\u201313451); Davis et al. (NAR 2025, 53:gkaf479).",
        "notes": """
<p>When we surveyed over twenty years of published siRNA literature, we found that prior computational approaches fall into three distinct generations:</p><p>1. Generation 1 consists of the classic heuristic rules from 2004—such as Reynolds, Ui-Tei, and Amarzguioui. These rules look at simple base composition and terminal thermodynamic asymmetry on canonical RNA. They work reasonably well on naked RNA, but because they only know A, C, G, and U, they are 100% blind to chemical modifications like 2'-O-methyl or 2'-fluoro. When tested on modified RNA, their correlation collapses below 0.18.</p><p>2. Generation 2 introduced classical machine learning—like DSIR, BiRNA, and early SMEpred. These models applied SVMs and Random Forests, but they were trained on early datasets like the 2006 Novartis Huesken screen. Because they used random train/test splits across overlapping sliding-window tiles, many of them suffered from sequence memorization. Furthermore, they were trained at fixed doses, so they could not predict titration curves.</p><p>3. Generation 3 brought modern deep learning. Here, two major published papers stand out:
   - First, OligoFormer by Bai et al. in Bioinformatics 2024. OligoFormer did a fantastic job combining 100M-parameter RNA-FM foundation model embeddings with ViennaRNA thermodynamics. But OligoFormer's vocabulary is strictly limited to canonical 4-letter RNA; it cannot design or evaluate synthetic chemical modifications.
   - Second, MEG-mod by Chen et al. in the Journal of Medicinal Chemistry 2026. MEG-mod is an impressive multiview Graph Neural Network that combines Uni-Mol 1-billion-parameter molecular embeddings, RNAErnie language models, and RNAcofold duplex graphs, achieving strong correlation on benchmark test splits. However, from a practical software deployment perspective, MEG-mod requires multi-gigabyte precomputed embedding dictionaries and complex graph convolutions that make interactive, sub-second combinatorial scanning difficult without dedicated GPU clusters. In addition, it models efficacy as a static scalar without native continuous dosage conditioning.</p><p>This forensic analysis defined our goal for Helix-Zero: build a fast, coordinated two-stage platform that first uses LightGBM (Model A) to screen naked sequences transcript-wide, and then uses a Single Unified CatBoost model (Model B) with 517 features and continuous dose conditioning to optimize chemical modifications in sub-second time.</p>
"""
    },

    # SLIDE 4: Literature Review: Forensic Research-Gap Analysis Across 12 Foundational Papers
    {
        "id": 4,
        "eyebrow": "EVIDENCE-DRIVEN ENGINEERING | PRIMARY SOURCES",
        "title": "Literature Review: Forensic Research-Gap Analysis Across 12 Foundational Papers",
        "subtitle": "Systematic Mapping of Published Research to Helix-Zero Architectural Decisions and Concrete Implementations",
        "badges": ["12 Primary Papers", "Peer-Review Rigor", "Gap Extraction", "Empirical Mapping"],
        "body_html": """
<div class="table-container">
          <table class="tech-table">
            <thead>
              <tr>
                <th style="width: 22%;">Research Paper &amp; Author</th>
                <th style="width: 26%;">Identified Limitation / Scientific Gap</th>
                <th style="width: 26%;">Helix-Zero Design Decision</th>
                <th style="width: 26%;">Concrete Code Implementation</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Davis et al. (NAR 2025)</strong><br><small>Fully chemically modified siRNA dataset (N = 2,576)</small></td>
                <td>Sequence-only models fail entirely on fully modified oligonucleotides (<em>r</em> &lt; 0.20).</td>
                <td>Engineered 444-D positional slot architecture covering 30 chemical modifications.</td>
                <td><code>smepred/src/features_v4.py</code><br><code>build_base_513()</code></td>
              </tr>
              <tr>
                <td><strong>Dominic D. Martinelli (2023)</strong><br><small>Cornell ML for modified siRNA activity</small></td>
                <td>Demonstrated ML can predict chemical activity, but two-stage pIC<sub>50</sub> &rarr; Hill cascades compound error.</td>
                <td>Consolidated into a Single Unified Dose-Aware CatBoost regressor with dynamic covariates.</td>
                <td><code>smepred/src/model_b_v4.py</code><br><code>predict_from_slots()</code></td>
              </tr>
              <tr>
                <td><strong>Chernolovskaya &amp; Zenkova (2010)</strong><br><small>Chemical modification of siRNA review</small></td>
                <td>Documented position-specific sensitivity (e.g. catalytic slicing disruption at positions 10–11).</td>
                <td>Formulated orthogonal multi-slot schema preserving spatial alignment to Ago2 active site.</td>
                <td><code>smepred/src/chem_schema.py</code><br><code>NucSlot</code> class</td>
              </tr>
              <tr>
                <td><strong>Hoerter &amp; Walter (RNA 2007)</strong><br><small>Serum degradation asymmetry &amp; PS kinetics</small></td>
                <td>Unmodified 3' overhangs degrade in blood serum within minutes via 3' exonucleases.</td>
                <td>Implemented deterministic nuclease penalty requiring tandem phosphorothioate (PS) caps at positions 20–21.</td>
                <td><code>smepred/src/biophysics.py</code><br><code>calculate_nuclease_penalty()</code></td>
              </tr>
              <tr>
                <td><strong>Janas et al. (Mol. Cell 2018)</strong><br><small>Empirical 6-mer seed toxicity database (4,096 rows)</small></td>
                <td>Specific 6-mer seeds drive severe miRNA-like off-target hepatotoxicity regardless of on-target efficacy.</td>
                <td>Integrated microsecond hash table lookup of 4,096 hexamers with position 2 2'-OMe rescue logic.</td>
                <td><code>smepred/src/filters.py</code><br><code>check_seed_rescue()</code></td>
              </tr>
              <tr>
                <td><strong>Bai et al. (Bioinformatics 2024)</strong><br><small>OligoFormer foundation model</small></td>
                <td>100M-parameter RNA-FM embeddings provide evolutionary conservation but ignore synthetic chemistry.</td>
                <td>Extracted 64-D live RNA-FM embeddings (PCA-32 per strand) and fused them with chemical slot vectors.</td>
                <td><code>smepred/src/features_v4.py</code><br><code>_rnafm_features()</code></td>
              </tr>
              <tr>
                <td><strong>Mandelli et al. (bioRxiv 2024)</strong><br><small>Intrinsic determinants of siRNA efficacy</small></td>
                <td>Identified GC asymmetry, terminal thermodynamics, and local opening free energies as dominant drivers.</td>
                <td>Combined ViennaRNA nearest-neighbor constants with terminal asymmetry calculations (&Delta;&Delta;G).</td>
                <td><code>smepred/src/features_v4.py</code><br><code>_vienna_features()</code></td>
              </tr>
              <tr>
                <td><strong>Park et al. (ACS Omega)</strong><br><small>MD thermodynamic parameters for modified RNA</small></td>
                <td>Modified base pairs alter duplex melting temperatures and local unwinding activation barriers.</td>
                <td>Incorporated empirical free energy adjustments (&Delta;&Delta;G&deg;<sub>37</sub>) for 2'-OMe, 2'-F, and PS linkages.</td>
                <td><code>smepred/src/biophysics.py</code><br><code>calculate_thermo_penalty()</code></td>
              </tr>
            </tbody>
          </table>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: Comprehensive audit of primary literature stored in workspace ReferencePapers / Research Papers directory; full bibliographic mapping verified against production source code.",
        "notes": """
<p>Every single component in Helix-Zero comes from a specific lesson in the research literature. Nothing was invented out of thin air.</p><p>On this slide, you see how eight key papers directly shaped our code:</p><ul><li>Davis et al. in NAR 2025 gave us our gold-standard dataset of fully modified siRNAs, proving sequence models fail without chemical features.</li><li>Dominic Martinelli in 2023 showed that machine learning works for modified siRNAs, but his two-stage cascade multiplied errors. That taught us to use a single unified model instead.</li><li>Chernolovskaya and Zenkova's review taught us where modifications are tolerated and where they break the active site, leading to our NucSlot schema.</li><li>Hoerter and Walter in RNA 2007 proved that unmodified ends get eaten by blood nucleases in minutes. That gave us our phosphorothioate end-capping rule in biophysics.py.</li><li>Janas et al. in Molecular Cell 2018 screened all 4,096 possible seed hexamers to map liver toxicity. We loaded their entire table into memory for microsecond seed toxicity screening.</li><li>And Bai et al.'s OligoFormer in 2024 showed the power of RNA foundation models. We extracted 64 foundation features from RNA-FM and fused them with our chemical features.</li></ul>
"""
    },

    # SLIDE 5: What Helix-Zero Does Differently: Solving the Four Core Vulnerabilities of Prior Work
    {
        "id": 5,
        "eyebrow": "SCIENTIFIC & ARCHITECTURAL DIFFERENTIATION",
        "title": "What Helix-Zero Does Differently: Solving the Four Core Vulnerabilities of Prior Work",
        "subtitle": "Clear Technical Demarcation Between Established Biological Concepts and Original Software Engineering",
        "badges": ["Original Engineering", "Zero Hallucination", "517-D Unified Vector", "O(1) Off-Target Lookup"],
        "body_html": """
<div class="cards-grid cards-2">
          <div class="card border-yellow">
            <div class="card-header">
              <span class="card-tag">ESTABLISHED BIOLOGY FROM LITERATURE</span>
              <h3>What Was Already Known in the Field</h3>
            </div>
            <ul class="bullet-list">
              <li><strong>RNAi Mechanism:</strong> Dicer processing, guide strand incorporation into Argonaute-2, passenger strand unwinding, and endonucleolytic cleavage between positions 10 and 11 (Fire 1998, Elbashir 2001).</li>
              <li><strong>Thermodynamic Asymmetry:</strong> The 5' guide strand terminus must be less stably paired than the 5' sense terminus for preferential RISC loading (Schwarz &amp; Zamore 2003, Khvorova 2003).</li>
              <li><strong>Clinical Motifs:</strong> Heavy 2'-OMe / 2'-F alternating patterns and terminal phosphorothioates enhance in vivo half-life and prevent immune sensing (Alnylam ESC/ESC+ designs; Janas 2018).</li>
              <li><strong>Seed Toxicity:</strong> 6-mer microRNA-like off-target binding in the 3' UTR of unintended human transcripts drives hepatotoxicity (Jackson 2006, Janas 2018).</li>
            </ul>
          </div>

          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">ORIGINAL HELIX-ZERO ENGINEERING</span>
              <h3>What We Built, Combined, &amp; Solved</h3>
            </div>
            <ul class="bullet-list">
              <li><strong>Continuous 517-D Unified Space:</strong> First architecture to natively combine 444-D orthogonal chemical slots, 64-D live RNA-FM foundation embeddings, 5-D ViennaRNA thermodynamics, and 4-D dynamic dose covariates into a single vector.</li>
              <li><strong>Single Unified Dose-Aware Model:</strong> Replaced compounding two-stage cascades with a single CatBoost forest, learning joint chemistry-dose interactions without GNN latency or CUDA out-of-memory spikes.</li>
              <li><strong>Deterministic Multi-Domain Penalty Engine:</strong> Hard-coded biophysical rules (unwinding barrier, tandem PS exonuclease kinetics, TLR7/8 immuno-masking) acting as a firewall against unviable ML predictions.</li>
              <li><strong>2-Bit Packed Whole-Transcriptome Firewall:</strong> Engineered a bitpacked O(1) exact-match lookup across 37,000+ human transcripts, completing safety screening in microsecond response times.</li>
              <li><strong>Automated Continuous 3D PDB Generator:</strong> Algorithmic emission of continuous A-form double-helix PDB models with B-factor modification encoding for instant 3Dmol.js rendering.</li>
            </ul>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: Original Helix-Zero Engineering / Implementation; Khvorova & Watts (Nat. Biotechnol. 2017); Schirle et al. (Science 2014, PDB 4W5N); Uppuladinne, Sonavane et al. (JBSD 2019).",
        "notes": """
<p>To be clear and scientifically honest, this slide shows what biology was already known versus what software engineering we actually built.</p><p>We do not claim to have discovered RNA interference or thermodynamic asymmetry. Those are established biological facts discovered by Fire, Zamore, and Khvorova.</p><p>What we DID build and engineer are five original solutions:
1. The 517-dimensional vector that merges chemical slots, RNA-FM embeddings, thermodynamics, and dose.
2. The unified CatBoost model that eliminates cascading two-stage error and throws away brittle GNNs.
3. The deterministic biophysical penalty engine that prevents the model from recommending fragile or toxic molecules.
4. The 2-bit bitpacked off-target firewall that checks 37,000 human transcripts in microseconds.
5. And the automated 3D PDB generator that outputs continuous double-helix models with color-coded modifications right in the browser.</p>
"""
    },

    # SLIDE 6: Complete System Architecture: The Consolidated 4-Stage Production Pipeline
    {
        "id": 6,
        "eyebrow": "SYSTEM TOPOLOGY & DATA FLOW PIPELINE",
        "title": "Complete System Architecture: The Consolidated 4-Stage Production Pipeline",
        "subtitle": "Modular End-to-End Execution Flow From Target mRNA Scanning to 3D Structural Validation",
        "badges": ["FastAPI Core", "Consolidated 4-Stage Flow", "Sub-Second Latency", "Docker Microservice"],
        "body_html": """
<div class="cards-grid cards-1">
          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">PRODUCTION PIPELINE TOPOLOGY</span>
              <h3>End-to-End Data Flow Architecture</h3>
            </div>
            <div class="pipeline-diagram">
              <div class="pipeline-step">
                <div class="step-num">STEP 1</div>
                <h4>Target mRNA Scanning &amp; Lead Selection</h4>
                <p><strong>Input:</strong> Target mRNA FASTA transcript<br>
                <strong>Engine:</strong> Model A (Naked LightGBM GBDT, 214-D)<br>
                <strong>Filtering:</strong> Reynolds criteria, Ui-Tei classification, GC window (30–65%), terminal asymmetry (&Delta;&Delta;G&deg;<sub>37</sub>)<br>
                <strong>Output:</strong> Top-ranked 21-mer naked candidates</p>
                <div class="step-badge">Takayuki r = 0.8788 | Huesken r = 0.8044</div>
              </div>
              <div class="pipeline-arrow">&darr;</div>
              <div class="pipeline-step">
                <div class="step-num">STEP 2</div>
                <h4>Unified Dose-Aware Chemical Optimization</h4>
                <p><strong>Input:</strong> Lead 21-mer sequence + target dose (<em>C</em> &isin; [0.001, 10,000] nM)<br>
                <strong>Engine:</strong> Single Unified CatBoost Regressor (517-D)<br>
                <strong>Algorithms:</strong> Single-mod scan (812 variants in &lt; 0.1s) &amp; Multi-mod beam search (ESC/ESC+ motifs)<br>
                <strong>Output:</strong> Predicted Knockdown % + closed-form derived pIC<sub>50</sub> &amp; IC<sub>50</sub></p>
                <div class="step-badge">Held-Out r = 0.8359 | ROC-AUC = 0.9312</div>
              </div>
              <div class="pipeline-arrow">&darr;</div>
              <div class="pipeline-step">
                <div class="step-num">STEP 3</div>
                <h4>Deterministic Biophysical Guardrails &amp; Safety Filter</h4>
                <p><strong>Engine:</strong> 4-Domain Deterministic Biophysical Penalty Engine<br>
                <strong>Auditing:</strong> Duplex unwinding barrier (&Delta;&Delta;G), tandem di-PS serum exonuclease kinetics, TLR7/8 immuno-masking, Janas 6-mer seed cytotoxicity<br>
                <strong>Output:</strong> Adjusted Clinical Efficacy Score (0.0% &ndash; 100.0%) with granular deduction audit</p>
                <div class="step-badge">Serum Protection Guaranteed | Seed Toxicity Mitigated</div>
              </div>
              <div class="pipeline-arrow">&darr;</div>
              <div class="pipeline-step">
                <div class="step-num">STEP 4</div>
                <h4>2-Bit Off-Target Firewall &amp; 3D Molecular Modeling</h4>
                <p><strong>Safety:</strong> 2-bit packed O(1) transcriptome-wide exact match &amp; seed mismatch search<br>
                <strong>Structure:</strong> Continuous A-form double-helix PDB generator (504 atoms) with B-factor chemical encoding<br>
                <strong>Output:</strong> Interactive 3Dmol.js rendering + formal clinical safety report</p>
                <div class="step-badge">PDB 4W5N Guided | Continuous Backbone Rendering</div>
              </div>
            </div>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: docs/00_MASTER_SYSTEM_ARCHITECTURE.md; final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md; smepred/api/main.py.",
        "notes": """
<p>This diagram shows how Helix-Zero works from start to finish across four clean steps:</p><p>Step 1: The user gives an mRNA transcript—like human PCSK9. Model A, our LightGBM sequence model, scans every 21-mer position and picks the top naked sequences based on thermodynamic asymmetry and target site openness.</p><p>Step 2: Those top sequences enter our Unified CatBoost model. The user picks their desired concentration—for example, 10 nM. The model evaluates either an 812-permutation single-modification scan in under 0.1 seconds, or generates clinical multi-modification patterns like Alnylam ESC+. It predicts the knockdown percentage and derives the IC50.</p><p>Step 3: Candidates pass through our Biophysical Guardrails. This checks if the ends have phosphorothioate protection against blood enzymes, penalizes duplexes that are too tight to unwind, checks for immune motifs, and screens for seed toxicity.</p><p>Step 4: The 2-bit off-target firewall checks the entire human transcriptome in microseconds to ensure no unintended genes are cut, and our 3D engine generates a clean PDB file to show the double helix right in the browser.</p>
"""
    },

    # SLIDE 7: Data Acquisition & Provenance: The 10-Resource Public Scientific Taxonomy
    {
        "id": 7,
        "eyebrow": "DATA REPOSITORIES & EXPERIMENTAL PROVENANCE",
        "title": "Data Acquisition & Provenance: The 10-Resource Public Scientific Taxonomy",
        "subtitle": "Exhaustive Aggregation of Canonical Sequence Screens, Modified Titrations, and Structural Receptors",
        "badges": ["10 Public Repositories", "40,255 Raw Records", "17,761 Curated Assays", "PDB 4W5N"],
        "body_html": """
<div class="table-container">
          <table class="tech-table">
            <thead>
              <tr>
                <th style="width: 25%;">Resource Name &amp; Dataset</th>
                <th style="width: 15%;">Sample Count (<em>N</em>)</th>
                <th style="width: 20%;">Oligonucleotide Chemistry</th>
                <th style="width: 40%;">Role in Helix-Zero Software Pipeline</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>CMsiRNAdb Master Corpus</strong><br><small>Curated modified siRNA database</small></td>
                <td>40,255 assays<br>(17,761 multi-dose)</td>
                <td>Extensively modified (2'-OMe, 2'-F, PS, DNA, LNA)</td>
                <td>Primary training corpus for Model B Unified CatBoost Regressor across continuous concentration titrations.</td>
              </tr>
              <tr>
                <td><strong>Davis et al. (NAR 2025)</strong><br><small>Nucleic Acids Research Benchmark</small></td>
                <td>2,576 assays<br>(1,796 held-out)</td>
                <td>Fully modified 21-mers (alternating 2'-OMe/2'-F, terminal PS)</td>
                <td>Heterogeneous multi-dose held-out test set (<code>hetero_val_303.csv</code>) for out-of-distribution evaluation.</td>
              </tr>
              <tr>
                <td><strong>Homogeneous Multi-Dose Set</strong><br><small>Standardized titration cohort</small></td>
                <td>472 assays</td>
                <td>Uniform modification motifs with full dose curves</td>
                <td>Controlled multi-dose held-out test set (<code>homo_val.csv</code>) for verifying dose-response monotonicity.</td>
              </tr>
              <tr>
                <td><strong>Novartis Screen (Huesken et al. 2005)</strong><br><small>Nature Biotechnology (<code>Hu.csv</code>)</small></td>
                <td>2,361 assays</td>
                <td>Unmodified canonical RNA (A, C, G, U)</td>
                <td>Golden benchmark for Model A naked sequence screening engine and cross-validation against published baselines.</td>
              </tr>
              <tr>
                <td><strong>Takayuki Screen (<code>Taka.csv</code>)</strong><br><small>High-potency cross-species screen</small></td>
                <td>702 assays</td>
                <td>Unmodified canonical RNA</td>
                <td>External validation for Model A sequence-intrinsic biophysical heuristics (r = 0.8788).</td>
              </tr>
              <tr>
                <td><strong>Mixset 7-Studies (<code>Mix.csv</code>)</strong><br><small>Multi-laboratory cross-platform set</small></td>
                <td>472 assays</td>
                <td>Unmodified canonical RNA</td>
                <td>Stress-test benchmark for Model A transfer robustness across heterogeneous laboratory protocols (r = 0.8291).</td>
              </tr>
              <tr>
                <td><strong>Janas et al. Seed Viability Table</strong><br><small>Molecular Cell (2018)</small></td>
                <td>4,096 hexamers</td>
                <td>Empirical human hepatocyte viability %</td>
                <td>In-memory cached lookup table in <code>filters.py</code> for predicting and mitigating seed-mediated cytotoxicity.</td>
              </tr>
              <tr>
                <td><strong>NCBI RefSeq Human Transcriptome</strong><br><small>GRCh38.p14 annotated mRNA</small></td>
                <td>37,000+ transcripts<br>(&gt; 100M bp)</td>
                <td>Full-length coding &amp; 3' UTR sequences</td>
                <td>Indexed into 2-bit bitpacked hash stores for sub-microsecond whole-transcriptome off-target filtering.</td>
              </tr>
              <tr>
                <td><strong>Human Argonaute-2 Receptor</strong><br><small>PDB ID: 4W5N (2.90 Å crystal structure)</small></td>
                <td>1 complex</td>
                <td>Ago2 with guide RNA &amp; target mRNA</td>
                <td>Structural template for geometric spatial alignment, catalytic slice verification, and 3D PDB backbone generation.</td>
              </tr>
              <tr>
                <td><strong>FDA Commercial Therapeutics</strong><br><small>Inclisiran, Patisiran, Givosiran, etc.</small></td>
                <td>6 approved drugs</td>
                <td>Clinical ESC / ESC+ chemistries</td>
                <td>Strict out-of-distribution blind control panel; withheld from training to test clinical plausibility.</td>
              </tr>
            </tbody>
          </table>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: datasets_audit.md; final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md; Schirle et al. (Science 2014, PDB 4W5N).",
        "notes": """
<p>Where does our data come from?</p><p>This table outlines the 10 public data resources we brought together:
- For training our modification model, we pulled the CMsiRNAdb master collection of 40,255 raw assays, which we cleaned down to 17,761 high-quality multi-dose assays.
- For our held-out test sets, we isolated 1,796 assays from the recent Davis et al. 2025 paper in Nucleic Acids Research, plus 472 standardized homogeneous titration curves.
- For our naked sequence model, we used three gold-standard public screens: Huesken (2,361 siRNAs), Takayuki (702 siRNAs), and Mixset (472 siRNAs).
- For safety and structural validation, we pulled the Janas seed toxicity database (4,096 rows), the full human transcriptome of 37,000 transcripts, and the high-resolution crystal structure of human Argonaute-2 (PDB 4W5N).
- And for final validation, we withheld all 6 FDA-approved siRNA drugs to test our model as a blind control.</p>
"""
    },

    # SLIDE 8: Dataset Statistics: Quantifying Chemical Diversity, Dose Heterogeneity, & Label Distributions
    {
        "id": 8,
        "eyebrow": "DATA SCIENCE METRICS & EXPLORATORY AUDIT",
        "title": "Dataset Statistics: Quantifying Chemical Diversity, Dose Heterogeneity, & Label Distributions",
        "subtitle": "Rigorous Empirical Accounting of the 17,761-Assay Training Corpus Across 5 Decades of Concentration",
        "badges": ["N = 17,761 Assays", "5 Decades of Dose", "30 Chemistry Classes", "Continuous Target [0, 100]"],
        "body_html": """
<div class="cards-grid cards-3">
          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">DOSE TITRATION DIVERSITY</span>
              <h3>Concentration Dynamic Range</h3>
            </div>
            <p class="card-desc">Experimental transfection concentrations span <strong>over 5 orders of magnitude</strong> (0.001 nM to 10,000 nM).</p>
            <div class="metric-row">
              <div class="metric-item">
                <span class="metric-val">10.0 nM</span>
                <span class="metric-lbl">Primary Screen Mode</span>
              </div>
              <div class="metric-item">
                <span class="metric-val">68</span>
                <span class="metric-lbl">Distinct Dose Levels</span>
              </div>
            </div>
            <ul class="bullet-list">
              <li>Peak concentrations: 0.1 nM (12.4%), 1.0 nM (21.8%), 10.0 nM (44.1%), 100.0 nM (15.2%).</li>
              <li>Dose is transformed to <code>log<sub>10</sub>(Dose_nM)</code> to linearize biological Hill receptor occupancy.</li>
            </ul>
          </div>

          <div class="card border-purple">
            <div class="card-header">
              <span class="card-tag">CHEMICAL COMPOSITION</span>
              <h3>Modification Frequency Across 42 Slots</h3>
            </div>
            <p class="card-desc">Distribution of synthetic chemical modifications across the 17,761 training duplexes:</p>
            <ul class="bullet-list">
              <li><strong>2'-O-Methyl (2'-OMe, M):</strong> 41.2% of all modified positions (primary nuclease shield).</li>
              <li><strong>2'-Fluoro (2'-F, F):</strong> 38.5% of all modified positions (high A-form RNA mimicry).</li>
              <li><strong>Phosphorothioate (PS, S):</strong> 14.3% of backbone linkages (terminal exonuclease block).</li>
              <li><strong>Emerging Chemistries:</strong> 6.0% (LNA, MOE, DNA, 2'-F-ANA, 5'-Vinylphosphonate, GalNAc).</li>
              <li>Positional bias: 2'-F dominates guide positions 2, 6, 14; 2'-OMe dominates passenger strand.</li>
            </ul>
          </div>

          <div class="card border-emerald">
            <div class="card-header">
              <span class="card-tag">LABEL DISTRIBUTION</span>
              <h3>Continuous Knockdown Target</h3>
            </div>
            <p class="card-desc">Distribution of target variable (<em>y</em> = % Biological mRNA Knockdown):</p>
            <div class="metric-row">
              <div class="metric-item">
                <span class="metric-val">58.4%</span>
                <span class="metric-lbl">Mean Knockdown</span>
              </div>
              <div class="metric-item">
                <span class="metric-val">&plusmn;24.7%</span>
                <span class="metric-lbl">Std. Deviation</span>
              </div>
            </div>
            <ul class="bullet-list">
              <li>High potency candidates (<em>y</em> &ge; 70%): 38.2% of dataset.</li>
              <li>Inactive / resistant candidates (<em>y</em> &lt; 30%): 16.9% of dataset.</li>
              <li>Evaluated with continuous RMSE loss rather than arbitrary binary thresholding.</li>
            </ul>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: datasets_audit.md; final_benchmarks/master_benchmark_metrics.csv; smepred/data/modification_codes.json.",
        "notes": """
<p>Here are the key numbers behind our 17,761 training assays:</p><p>First, concentration: previous models assumed every experiment was done at 10 nM. But in reality, assays span five orders of magnitude—from 1 picomolar up to 10 micromolar. By taking the log10 of concentration, we turn this into a smooth linear covariate that directly models physical receptor binding.</p><p>Second, chemical modifications: about 80% of all modifications in our dataset are 2'-O-methyl and 2'-fluoro, which matches real-world clinical drugs. 2'-Fluoro is common in the seed and cleavage areas because it does not clash with the protein, while 2'-O-methyl covers the rest of the molecule for nuclease protection. Phosphorothioates make up 14%, placed mostly at the ends.</p><p>Third, our target variable is continuous biological knockdown percentage. The average is 58%, with 38% of candidates achieving strong knockdown of 70% or higher. We train on the exact continuous percentage using RMSE so our model can tell the difference between an 80% drug and a 95% drug.</p>
"""
    },

    # SLIDE 9: Data Cleaning & Quality Control: The Multi-Stage Filtering and Harmonization Pipeline
    {
        "id": 9,
        "eyebrow": "DATA ENGINEERING & QC PIPELINE",
        "title": "Data Cleaning & Quality Control: The Multi-Stage Filtering and Harmonization Pipeline",
        "subtitle": "Eliminating Ambiguous Sequences, Normalizing Conflicting Chemistry Notations, and Aggregating Replicates",
        "badges": ["QC Pipeline", "Replicate Harmonization", "Notation Normalization", "Outlier Pruning"],
        "body_html": """
<div class="cards-grid cards-2">
          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">SYSTEMATIC QC STAGES</span>
              <h3>The 4-Step Data Sanitation Protocol</h3>
            </div>
            <div class="pipeline-diagram">
              <div class="pipeline-step">
                <div class="step-num">STAGE 1</div>
                <h4>Sequence Sanitization &amp; Length Normalization</h4>
                <p>Pruned all sequences with degenerate ambiguity codes (N, X, R, Y). Filtered non-canonical duplexes, strictly enforcing 21-nt sense and 21-nt antisense duplex topology (19-bp core + 2-nt 3' overhangs).</p>
              </div>
              <div class="pipeline-arrow">&darr;</div>
              <div class="pipeline-step">
                <div class="step-num">STAGE 2</div>
                <h4>Chemical Notation Harmonization</h4>
                <p>Public datasets use fragmented, conflicting notations (e.g. <code>mU</code>, <code>fU</code>, <code>[2omeU]</code>, <code>U*</code>, <code>2F-U</code>). Built a deterministic compiler that parses all historical syntax into standardized <code>NucSlot</code> tuples.</p>
              </div>
              <div class="pipeline-arrow">&darr;</div>
              <div class="pipeline-step">
                <div class="step-num">STAGE 3</div>
                <h4>Replicate Harmonization &amp; Noise Filtration</h4>
                <p>Identified identical sequence + chemistry + dose combinations across independent publications. Computed robust median knockdown values. Flagged and eliminated conflicting replicates where variance exceeded &sigma; &gt; 25%.</p>
              </div>
              <div class="pipeline-arrow">&darr;</div>
              <div class="pipeline-step">
                <div class="step-num">STAGE 4</div>
                <h4>Non-Physiological Outlier Pruning</h4>
                <p>Eliminated assays tested at non-physiological concentrations (&gt; 50 &mu;M) where non-specific cytotoxicity dominates silencing, and removed assays with invalid exposure durations (&lt; 6h or &gt; 120h).</p>
              </div>
            </div>
          </div>

          <div class="card border-purple">
            <div class="card-header">
              <span class="card-tag">DATA ACCOUNTING AUDIT</span>
              <h3>Attrition Funnel: Raw Data to Golden Corpus</h3>
            </div>
            <table class="tech-table" style="margin-top: 10px;">
              <thead>
                <tr>
                  <th>Processing Stage</th>
                  <th>Row Count</th>
                  <th>Retention</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Raw CMsiRNAdb Records</td>
                  <td>40,255</td>
                  <td>100.0%</td>
                </tr>
                <tr>
                  <td>After Sequence &amp; Length Standardization</td>
                  <td>28,410</td>
                  <td>70.6%</td>
                </tr>
                <tr>
                  <td>After Chemical Notation Harmonization</td>
                  <td>22,180</td>
                  <td>55.1%</td>
                </tr>
                <tr>
                  <td>After Replicate Aggregation (&sigma; &le; 25%)</td>
                  <td>19,340</td>
                  <td>48.0%</td>
                </tr>
                <tr>
                  <td><strong>Final Production Training Corpus (Model B)</strong></td>
                  <td><strong>17,761</strong></td>
                  <td><strong>44.1%</strong></td>
                </tr>
              </tbody>
            </table>
            <div class="mentor-box" style="margin-top: 14px;">
              <strong>Data Engineering Takeaway:</strong> Discarding 55.9% of noisy, contradictory, and uncurated public records was the primary driver of out-of-distribution generalization.
            </div>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: preprocessing_accounting.md; datasets_audit.md; smepred/src/parser.py; smepred/src/chem_schema.py.",
        "notes": """
<p>In machine learning, bad data produces bad models. If you train on noisy public data, the model just memorizes lab errors.</p><p>This slide shows our 4-stage data cleaning funnel:
1. In Stage 1, we removed ambiguous sequences with Ns and Xs, and strictly standardized everything to standard 21-mer duplexes.
2. In Stage 2, we solved a major practical headache: chemical notation chaos. One paper writes 'mU', another writes '[2omeU]', another writes 'U*'. We wrote an automated compiler that standardizes all these variations into our clean NucSlot format.
3. In Stage 3, we handled duplicate experiments. When different papers tested the same compound at the same dose, we took the median score. If two papers disagreed by more than 25%, we discarded the conflicting data.
4. In Stage 4, we removed crazy outliers—like tests at 50 micromolar where cells were poisoned, or experiments that only ran for 2 hours.</p><p>As the table shows, we started with 40,255 records and kept the cleanest 17,761. Throwing away the noisy 56% was the best decision we made for real-world accuracy.</p>
"""
    },

    # SLIDE 10: Biological-to-Computational Representation: The Orthogonal NucSlot Data Schema
    {
        "id": 10,
        "eyebrow": "DATA STRUCTURES & MOLECULAR MODELING",
        "title": "Biological-to-Computational Representation: The Orthogonal NucSlot Data Schema",
        "subtitle": "Decomposing Complex Synthetic Oligonucleotide Chemistry into Orthogonal 5-Attribute Positional Tuples",
        "badges": ["NucSlot Schema", "Orthogonal Attributes", "Python Dataclass", "smepred/src/chem_schema.py"],
        "body_html": """
<div class="cards-grid cards-2">
          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">DATA STRUCTURE DESIGN</span>
              <h3>The 5-Attribute Orthogonal NucSlot Tuple</h3>
            </div>
            <p class="card-desc">Instead of treating a modified nucleotide as an arbitrary single-letter string (e.g. 'm' or 'f'), HelixZero models each of the 42 positions as an orthogonal chemical tuple:</p>
            <div class="formula-box">
              Slot<sub>i</sub> = ( Base<sub>i</sub>, Sugar<sub>i</sub>, Linkage<sub>i</sub>, Terminal<sub>i</sub>, Ligand<sub>i</sub> )
            </div>
            <ul class="bullet-list">
              <li><strong>Base Identity (4 classes):</strong> Adenine (A), Cytosine (C), Guanine (G), Uracil (U).</li>
              <li><strong>Sugar Conformation (12 classes):</strong> Ribose (2'-OH), 2'-O-Methyl (2'-OMe), 2'-Fluoro (2'-F), 2'-Deoxy (DNA), LNA (Locked), MOE (2'-O-methoxyethyl), etc.</li>
              <li><strong>Phosphate Linkage (3 classes):</strong> Phosphodiester (PO), Phosphorothioate (PS), Phosphorodithioate (PS2).</li>
              <li><strong>Terminal Capping (4 classes):</strong> 5'-Phosphate, 5'-Vinylphosphonate (5'-VP), 3'-Inverted Abasic, None.</li>
              <li><strong>Ligand Conjugate (3 classes):</strong> Tri-antennary GalNAc, Cholesterol, None.</li>
            </ul>
          </div>

          <div class="card border-purple">
            <div class="card-header">
              <span class="card-tag">PRODUCTION PYTHON IMPLEMENTATION</span>
              <h3>Source Code Excerpt: <code>smepred/src/chem_schema.py</code></h3>
            </div>
            <div class="code-box">
<pre><span class="code-kw">@dataclass</span>(<span class="code-param">frozen</span>=<span class="code-kw">True</span>)
<span class="code-kw">class</span> <span class="code-func">NucSlot</span>:
    <span class="code-str">&quot;&quot;&quot;Orthogonal representation of a single nucleotide slot.&quot;&quot;&quot;</span>
    base: <span class="code-func">str</span>          <span class="code-comment"># 'A', 'C', 'G', 'U'</span>
    sugar: <span class="code-func">str</span> = <span class="code-str">"RNA"</span>  <span class="code-comment"># 'RNA', '2OME', '2F', 'DNA', 'LNA', 'MOE'</span>
    linkage: <span class="code-func">str</span> = <span class="code-str">"PO"</span> <span class="code-comment"># 'PO', 'PS', 'PS2'</span>
    terminal: <span class="code-func">str</span> = <span class="code-str">""</span>  <span class="code-comment"># '5P', '5VP', '3INV'</span>
    ligand: <span class="code-func">str</span> = <span class="code-str">""</span>    <span class="code-comment"># 'GALNAC', 'CHOL'</span>

    <span class="code-kw">def</span> <span class="code-func">to_vector</span>(<span class="code-param">self</span>) -&gt; np.ndarray:
        <span class="code-str">&quot;&quot;&quot;One-hot encodes slot into orthogonal chemical properties.&quot;&quot;&quot;</span>
        v_base = _encode_base(<span class="code-param">self</span>.base)       <span class="code-comment"># 4-dim</span>
        v_sugar = _encode_sugar(<span class="code-param">self</span>.sugar)    <span class="code-comment"># 12-dim</span>
        v_link = _encode_link(<span class="code-param">self</span>.linkage)    <span class="code-comment"># 3-dim</span>
        v_term = _encode_term(<span class="code-param">self</span>.terminal)   <span class="code-comment"># 4-dim</span>
        <span class="code-kw">return</span> np.concatenate([v_base, v_sugar, v_link, v_term])
</pre>
            </div>
            <div class="mentor-box" style="margin-top: 10px;">
              <strong>Software Benefit:</strong> Decouples base pairing from chemical resistance. A 2'-OMe Uracil shares base pairing with natural U, but shares nuclease stability with 2'-OMe Adenine.
            </div>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: Original Helix-Zero Engineering; smepred/src/chem_schema.py; Chernolovskaya & Zenkova (Curr. Opin. Mol. Ther. 2010).",
        "notes": """
<p>How do you represent a modified RNA molecule inside code?</p><p>In the past, tools tried to use single letters like 'm' or 'f'. But that breaks down immediately. If you call a modified Uracil 'm', the computer forgets that it still pairs with Adenine!</p><p>To solve this cleanly, we created the NucSlot dataclass in chem_schema.py. Every single position on the molecule is broken into five independent parts:
1. Base: A, C, G, or U.
2. Sugar: normal RNA, 2'-OMe, 2'-Fluoro, DNA, or LNA.
3. Linkage: phosphodiester or phosphorothioate.
4. Terminal cap: like 5'-vinylphosphonate.
5. Ligand: like GalNAc for liver targeting.</p><p>This simple separation is powerful: the model learns base-pairing rules from the Base, and learns stability and toxicity rules from the Sugar and Linkage.</p>
"""
    },

    # SLIDE 11: Feature Engineering: Architecture of the 517-Dimensional Multi-Modal Space
    {
        "id": 11,
        "eyebrow": "FEATURE ENGINEERING & VECTOR ENCODING",
        "title": "Feature Engineering: Architecture of the 517-Dimensional Multi-Modal Space",
        "subtitle": "Seamless Integration of Positional Synthetic Chemistry, Deep Evolutionary Representations, Thermodynamics, and Exposure",
        "badges": ["517 Dimensions", "Multi-Modal Fusion", "Live RNA-FM", "ViennaRNA Thermodynamics"],
        "body_html": """
<div class="cards-grid cards-1">
          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">FEATURE VECTOR STRUCTURE</span>
              <h3>Concatenated 517-Dimensional Multi-Modal Vector Topology</h3>
            </div>
            <div class="vector-bar-container">
              <div class="vector-segment seg-chem" style="width: 50%;">
                <span class="seg-title">Positional Chemistry Slots</span>
                <span class="seg-dims">444 Dimensions (Indices 0 &ndash; 443)</span>
                <span class="seg-desc">21 Sense + 21 Antisense Slots &times; Orthogonal Properties</span>
              </div>
              <div class="vector-segment seg-fm" style="width: 25%;">
                <span class="seg-title">RNA-FM Foundation</span>
                <span class="seg-dims">64 Dimensions (444 &ndash; 507)</span>
                <span class="seg-desc">Live rna_fm_t12 PCA-32 Embeddings</span>
              </div>
              <div class="vector-segment seg-thermo" style="width: 13%;">
                <span class="seg-title">ViennaRNA</span>
                <span class="seg-dims">5 Dims (508 &ndash; 512)</span>
                <span class="seg-desc">&Delta;G, MFE, Ensemble</span>
              </div>
              <div class="vector-segment seg-dose" style="width: 12%;">
                <span class="seg-title">Dose Covars</span>
                <span class="seg-dims">4 Dims (513 &ndash; 516)</span>
                <span class="seg-desc">log10(C), Relative Dose</span>
              </div>
            </div>
            <div class="cards-grid cards-2" style="margin-top: 14px;">
              <div class="flow-step">
                <strong>Why This Topology Was Selected:</strong>
                <p>Tree-based models (CatBoost) excel at tabular feature splits but cannot natively extract evolutionary sequence patterns. Conversely, deep foundation models (RNA-FM) capture evolutionary conservation across billions of RNA transcripts but are completely blind to synthetic chemical modifications. Fusing them into a single 517-D vector bridges deep structural representation with synthetic chemical rules.</p>
              </div>
              <div class="code-box">
<pre><span class="code-kw">def</span> <span class="code-func">build_unified_features</span>(
    sense_slots, anti_slots, conc_nM=<span class="code-num">10.0</span>, is_hepatic=<span class="code-num">1.0</span>, time_h=<span class="code-num">24.0</span>
) -&gt; np.ndarray:
    <span class="code-str">&quot;&quot;&quot;Builds the 517-D vector (513 base + 4 dose/cell covariates).&quot;&quot;&quot;</span>
    base_513 = build_base_513(sense_slots, anti_slots) <span class="code-comment"># 444 chem + 64 FM + 5 Vienna</span>
    log_c = np.log10(max(<span class="code-num">1e-4</span>, <span class="code-func">float</span>(conc_nM)))
    log_c_rel = log_c - <span class="code-num">1.0</span>                             <span class="code-comment"># Relative to 10 nM median</span>
    t_norm = <span class="code-func">float</span>(time_h) / <span class="code-num">24.0</span>                      <span class="code-comment"># Normalized duration</span>
    hep = <span class="code-func">float</span>(is_hepatic)                            <span class="code-comment"># Cell lineage flag</span>
    <span class="code-kw">return</span> np.concatenate([base_513, [log_c, log_c_rel, t_norm, hep]])
</pre>
              </div>
            </div>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: docs/01_UNIFIED_DOSE_AWARE_CATBOOST_ENGINE.md; smepred/src/features_v4.py; Chen et al. (RNA-FM, 2022); Lorenz et al. (ViennaRNA 2.0, 2011).",
        "notes": """
<p>This slide shows how our 517-dimensional feature vector is put together in code:</p><p>It consists of four connected blocks:
- Block 1 (444 features): Positional chemistry across all 21 sense and 21 antisense slots.
- Block 2 (64 features): Evolutionary foundation model embeddings extracted from the 100M-parameter RNA-FM transformer (32 components per strand).
- Block 3 (5 features): Real-time thermodynamics from ViennaRNA, like duplex binding energy and melting probability.
- Block 4 (4 features): Dose covariates—most importantly log10(Dose in nM), plus exposure time and cell lineage.</p><p>Why combine them like this?
Decision trees like CatBoost are great at hard tabular splits, but they cannot read evolutionary patterns. Foundation models like RNA-FM are great at evolutionary patterns, but they know nothing about synthetic chemistry. Combining them gives our model both deep biological context and exact chemical awareness.</p>
"""
    },

    # SLIDE 12: Granular Feature Accounting: Dimensions, Physical Meaning, & Importance Ranking
    {
        "id": 12,
        "eyebrow": "FEATURE IMPORTANCE & SELECTION RATIONALE",
        "title": "Granular Feature Accounting: Dimensions, Physical Meaning, & Importance Ranking",
        "subtitle": "Empirical Feature Attribution Proves Dose, Seed Sugar, and Cleavage Thermodynamics Drive Potency",
        "badges": ["Feature Attribution", "SHAP Importance", "Top 5 Features", "Physical Rationale"],
        "body_html": """
<div class="vector-bar-container" title="Click any segment for granular technical breakdown">
  <div class="vector-segment seg-chem clickable-pill" style="width: 85.88%; cursor: pointer;" data-deep-dive="chemical_444_features" title="Click: 444 Chemistry Features Deep Dive">
    <div class="seg-title">Synthetic Chemistry (444 Dims &bull; 85.9%)</div>
    <div class="seg-dims">42 slots &times; 10 descriptors (420) + 24 global features</div>
  </div>
  <div class="vector-segment seg-fm clickable-pill" style="width: 12.38%; cursor: pointer;" data-deep-dive="rnafm_foundation" title="Click: RNA-FM 64-D Foundation Embeddings">
    <div class="seg-title">RNA-FM (64 Dims)</div>
    <div class="seg-dims">Transformer PCA</div>
  </div>
  <div class="vector-segment seg-thermo clickable-pill" style="width: 0.97%; min-width: 55px; cursor: pointer;" data-deep-dive="biophysical_guardrails" title="Click: ViennaRNA Thermodynamics">
    <div class="seg-title">Thermo (5)</div>
  </div>
  <div class="vector-segment seg-dose clickable-pill" style="width: 0.77%; min-width: 50px; cursor: pointer;" data-deep-dive="heldout_multidose" title="Click: Continuous Dose Covariates">
    <div class="seg-title">Dose (4)</div>
  </div>
</div>

<div class="cards-grid cards-2">
          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">FEATURE GROUP BREAKDOWN</span>
              <h3>Granular Vector Accounting</h3>
            </div>
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Feature Modality</th>
                  <th>Dims</th>
                  <th>Biological &amp; Computational Rationale</th>
                </tr>
              </thead>
              <tbody>
                <tr class="clickable-row" data-deep-dive="chemical_444_features" title="Click: 444 Chemical Slot Breakdown">
                  <td><strong>Passenger (Sense) Chemistry</strong><br><small>Indices 0 &ndash; 221</small></td>
                  <td>222</td>
                  <td>21 slots &times; 10 structural descriptors (210) + 12 strand-level descriptors = 222 dims. Evaluates passenger strand inactivation, 3'-GalNAc conjugation, and nuclease shielding.</td>
                </tr>
                <tr class="clickable-row" data-deep-dive="chemical_444_features" title="Click: 444 Chemical Slot Breakdown">
                  <td><strong>Guide (Antisense) Chemistry</strong><br><small>Indices 222 &ndash; 443</small></td>
                  <td>222</td>
                  <td>21 slots &times; 10 structural descriptors (210) + 12 strand-level descriptors = 222 dims. Encodes seed-region flexibility (nt 2–8), cleavage center tolerance (nt 10–11), and 5'-VP anchoring.</td>
                </tr>
                <tr class="clickable-row" data-deep-dive="rnafm_foundation" title="Click: RNA-FM 64-D Foundation Embeddings">
                  <td><strong>RNA-FM Foundation Embeddings</strong><br><small>Indices 444 &ndash; 507</small></td>
                  <td>64</td>
                  <td>32-dim sense + 32-dim antisense PCA embeddings from 12-layer <code>rna_fm_t12</code> transformer. Captures transcript-wide evolutionary constraints.</td>
                </tr>
                <tr class="clickable-row" data-deep-dive="biophysical_guardrails" title="Click: ViennaRNA Thermodynamics">
                  <td><strong>ViennaRNA Thermodynamics</strong><br><small>Indices 508 &ndash; 512</small></td>
                  <td>5</td>
                  <td>Duplex binding free energy (&Delta;G<sub>duplex</sub>), ensemble free energy, MFE probability, and 5' guide/sense terminal opening energies.</td>
                </tr>
                <tr class="clickable-row" data-deep-dive="heldout_multidose" title="Click: Continuous Dose Covariates">
                  <td><strong>Assay Exposure Covariates</strong><br><small>Indices 513 &ndash; 516</small></td>
                  <td>4</td>
                  <td><code>log<sub>10</sub>(Dose_nM)</code>, Relative Dose, Incubation Duration, Hepatic Cell Lineage flag (HepG2/Huh7 vs other).</td>
                </tr>
                <tr>
                  <td><strong>TOTAL UNIFIED FEATURE VECTOR</strong></td>
                  <td><strong>517</strong></td>
                  <td><strong>100% continuous and tabular representation</strong></td>
                </tr>
              </tbody>
            </table>
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 8px; line-height: 1.35; padding: 6px 10px; background: rgba(34,211,238,0.05); border-left: 2px solid var(--accent); border-radius: 4px;">
              <strong>Architecture Note:</strong> Rather than an ultra-sparse 1,302-dim matrix (42 &times; 31 mods) that overfits rare chemistries, each slot uses 10 dense physical descriptors (8 sugar classes, PS linkage, base mod), yielding 420 positional + 24 global = 444 chemical features.
            </div>
          </div>

          <div class="card border-emerald">
            <div class="card-header">
              <span class="card-tag">EMPIRICAL IMPORTANCE</span>
              <h3>Top 5 Most Influential Model Features</h3>
            </div>
            <p class="card-desc">Feature importance computed via CatBoost split gain across the 17,761-assay training corpus:</p>
            <div class="metric-row">
              <div class="metric-item">
                <span class="metric-val">#1</span>
                <span class="metric-lbl">&log;<sub>10</sub>(Dose_nM) (18.4% Gain)</span>
              </div>
              <div class="metric-item">
                <span class="metric-val">#2</span>
                <span class="metric-lbl">AS Pos 2 Sugar (11.2% Gain)</span>
              </div>
            </div>
            <ul class="bullet-list" style="margin-top: 10px;">
              <li><strong>Rank 1: <code>log<sub>10</sub>(Dose_nM)</code> (Feature 513):</strong> Accounts for 18.4% of total tree split gain. Confirms that conditioning on exposure is paramount.</li>
              <li><strong>Rank 2: Antisense Position 2 Sugar Class:</strong> Governs initial seed nucleation into the target mRNA and suppresses miRNA-like toxicity.</li>
              <li><strong>Rank 3: Antisense Position 10 Sugar &amp; Base:</strong> Directly controls the catalytic slicing geometry of the Argonaute-2 PIWI domain.</li>
              <li><strong>Rank 4: Duplex Free Energy (&Delta;G<sub>duplex</sub>, Feature 510):</strong> Balances duplex stability against RISC passenger-strand unwinding activation barriers.</li>
              <li><strong>Rank 5: RNA-FM Principal Component 1:</strong> Captures sequence-intrinsic evolutionary conservation and base-pairing propensities.</li>
            </ul>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: smepred/src/features_v4.py; CatBoost feature importance logs; Davis et al. (NAR 2025); Janas et al. (Mol. Cell 2018).",
        "notes": """
<p>To understand how our 444 chemical features are built:
Each of the 21 nucleotide positions on both strands is mapped into 10 orthogonal chemical descriptors (8 sugar classes including 2'-OMe and 2'-F, plus phosphorothioate backbone linkage and base modification). That gives 21 x 10 = 210 features per strand, plus 12 global descriptors like GalNAc conjugation, seed rigidity, and GC composition, resulting in 222 dimensions per strand, or 444 chemical features in total.</p><p>When we inspect which features our trained model actually uses, the results make complete biological sense:
The number one most influential feature is log10(Dose)—accounting for over 18% of all decision splits. This proves our point: you cannot accurately predict siRNA activity without knowing the dose.
The number two feature is the sugar modification at guide position 2. This is the seed nucleation anchor that initiates target binding and controls seed toxicity.
The number three feature is position 10—the exact spot where Argonaute-2 slices the target mRNA.
Rank four is the duplex binding energy, and Rank five is the primary component from our RNA foundation model.
This gives us tremendous confidence: the model is making decisions based on the core physics and biology of RNA interference.</p>
"""
    },

    # SLIDE 13: Data Splitting & Zero Leakage: Mathematical Proof of GroupKFold Enforcement
    {
        "id": 13,
        "eyebrow": "DATA INTEGRITY & PEER-REVIEW RIGOR",
        "title": "Data Splitting & Zero Leakage: Mathematical Proof of GroupKFold Enforcement",
        "subtitle": "Why Standard Random Splits Cause Severe Sequence Memorization Fraud in Published Literature",
        "badges": ["GroupKFold", "Zero Sequence Leakage", "5,251 Clusters", "IEEE TNNLS Compliance"],
        "body_html": """
<div class="cards-grid cards-2">
          <div class="card border-rose">
            <div class="card-header">
              <span class="card-tag">THE FRAUD OF RANDOM SPLITTING</span>
              <h3>Mathematical Proof of Sequence Leakage</h3>
            </div>
            <p class="card-desc">In transcript tiling screens, adjacent 21-mers share 18 of 19 core base pairs (94.7% sequence identity). When partitioned randomly:</p>
            <div class="formula-box">
              P(Leakage) = 1 &minus; (1 &minus; p<sub>test</sub>)<sup>k</sup> &asymp; 1 &minus; (1 &minus; 0.2)<sup>2</sup> = 0.96 (96.0%)
            </div>
            <ul class="bullet-list">
              <li><strong>Sequence Memorization:</strong> With a 20% test set, 96% of test candidates have a near-identical sequence sibling in the training set.</li>
              <li><strong>False Generalization:</strong> Published models claiming test Pearson <em>r</em> &gt; 0.88 using random splits simply memorized transcript identity rather than learning SAR rules.</li>
              <li>When evaluated on truly novel genes, their performance collapses to <em>r</em> &lt; 0.50.</li>
            </ul>
          </div>

          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">THE HELIX-ZERO SOLUTION</span>
              <h3>Strict 5-Fold GroupKFold by Core Sequence</h3>
            </div>
            <p class="card-desc">HelixZero groups all N = 17,761 assays strictly by <strong>unique core antisense sequence</strong> (<code>anti_seq</code>):</p>
            <div class="metric-row">
              <div class="metric-item clickable-metric" data-deep-dive="groupkfold_5251" title="Click for GroupKFold Leakage Proof Details">
                <span class="metric-val">5,251</span>
                <span class="metric-lbl">Independent Groups</span>
              </div>
              <div class="metric-item clickable-metric" data-deep-dive="groupkfold_5251" title="Click for GroupKFold Leakage Proof Details">
                <span class="metric-val">0.0%</span>
                <span class="metric-lbl">Sequence Overlap</span>
              </div>
            </div>
            <ul class="bullet-list">
              <li><strong>Zero Leakage Guarantee:</strong> Every sequence cluster—including all its modification permutations, concentration titrations, and replicates—resides strictly in train OR test, never both.</li>
              <li><strong>Cross-Validation Metric:</strong> 5-Fold GroupKFold CV achieves <strong>r = 0.6776</strong> (R<sup>2</sup> = 0.4497) on 100% unseen sequences.</li>
              <li><strong>Held-Out Generalization:</strong> Achieves <strong>r = 0.8359</strong> on the held-out multi-dose benchmark, proving genuine out-of-distribution transfer.</li>
            </ul>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: docs/05_AUTHORITATIVE_BENCHMARKS_AND_CLINICAL_VALIDATION.md; final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md; IEEE TNNLS Peer Review Directive.",
        "notes": """
<p>This slide shows how we guaranteed zero data leakage.</p><p>In many published papers, models report high test correlations above 0.88. But when you look closely, they used simple random train/test splits.
Why is that bad?
In a typical screen, you design siRNAs by sliding a window across an mRNA. Adjacent siRNAs share 18 out of 19 base pairs—that is 95% identical!
If you do a random 80/20 split, there is a 96% chance that a test candidate has an almost identical twin in the training set. The model does not learn biology; it just memorizes the gene.</p><p>To prevent this, we grouped all 17,761 assays into 5,251 clusters based strictly on the unique antisense sequence.
In our 5-fold GroupKFold cross-validation, a sequence and all of its modifications and doses are either in training OR in testing—never in both.
That is why our cross-validation correlation is a realistic r = 0.6776 on totally unseen genes, proving real generalizability.</p>
"""
    },

    # SLIDE 14: Model A: Canonical Naked Sequence Screening Engine (LightGBM)
    {
        "id": 14,
        "eyebrow": "STAGE 1 MACHINE LEARNING SUBSYSTEM",
        "title": "Model A: Canonical Naked Sequence Screening Engine (LightGBM)",
        "subtitle": "Prioritizing Lead Duplexes via 214 Sequence-Intrinsic Features, Thermodynamic Asymmetry, and Reynolds Rules",
        "badges": ["Model A", "LightGBM GBDT", "214 Features", "Reynolds / Ui-Tei Heuristics"],
        "body_html": """
<div class="cards-grid cards-2">
          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">STAGE 1 ARCHITECTURE</span>
              <h3>LightGBM 214-D Sequence Engine</h3>
            </div>
            <p class="card-desc">Screens raw mRNA transcripts into candidate 21-mers and predicts intrinsic naked potency:</p>
            <ul class="bullet-list">
              <li><strong>Thermodynamic Asymmetry (&Delta;&Delta;G&deg;<sub>37</sub>):</strong> Evaluates terminal base-pairing free energy differential (&Delta;G<sub>end3</sub> &minus; &Delta;G<sub>end5</sub>) enforcing preferential guide strand RISC loading.</li>
              <li><strong>Reynolds 8-Rule Matrix:</strong> Positional base preferences (A at pos 6, U at pos 10, low GC at pos 19).</li>
              <li><strong>Ui-Tei Functional Classes:</strong> Class Ia/Ib sorting based on terminal dinucleotide thermodynamics.</li>
              <li><strong>Target mRNA Accessibility:</strong> Computes target site opening free energy (&Delta;G<sub>open</sub>) using ViennaRNA <code>RNAplfold</code>.</li>
            </ul>
          </div>

          <div class="card border-purple">
            <div class="card-header">
              <span class="card-tag">EMPIRICAL VALIDATION &amp; NEGATIVE CONTROL</span>
              <h3>Empirical Accuracy on Standard Datasets</h3>
            </div>
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Benchmark Dataset</th>
                  <th><em>N</em></th>
                  <th>Pearson <em>r</em></th>
                  <th>Spearman &rho;</th>
                  <th>ROC-AUC</th>
                </tr>
              </thead>
              <tbody>
                <tr class="clickable-row" data-deep-dive="takayuki_benchmark" title="Click: Takayuki Screen Benchmark Evaluation">
                  <td><strong>Takayuki Screen (<code>Taka.csv</code>)</strong></td>
                  <td>702</td>
                  <td><strong>0.8788</strong></td>
                  <td><strong>0.8734</strong></td>
                  <td><strong>0.9275</strong></td>
                </tr>
                <tr>
                  <td><strong>Mixset 7-Studies (<code>Mix.csv</code>)</strong></td>
                  <td>472</td>
                  <td><strong>0.8291</strong></td>
                  <td><strong>0.8093</strong></td>
                  <td><strong>0.9456</strong></td>
                </tr>
                <tr>
                  <td><strong>Huesken Held-Out (<code>Hu.csv</code>)</strong></td>
                  <td>2,361</td>
                  <td><strong>0.8044</strong></td>
                  <td><strong>0.8065</strong></td>
                  <td><strong>0.9099</strong></td>
                </tr>
                <tr class="clickable-row" style="background: rgba(248,113,113,0.1);" data-deep-dive="heldout_multidose" title="Click: Held-Out Multi-Dose Benchmark Evaluation">
                  <td><strong>CMsiRNAdb Hetero (Modified Negative Control)</strong></td>
                  <td>2,576</td>
                  <td><strong style="color: var(--red);">0.1771</strong></td>
                  <td><strong style="color: var(--red);">0.1645</strong></td>
                  <td><strong style="color: var(--red);">0.5711</strong></td>
                </tr>
              </tbody>
            </table>
            <div class="mentor-box" style="margin-top: 10px;">
              <strong>The Chemistry Blindness Proof:</strong> Model A achieves r = 0.8044 &ndash; 0.8788 on naked RNA, but collapses to r = 0.1771 on modified RNA (R<sup>2</sup> = &minus;0.0901). This proves naked models cannot design modified therapeutics.
            </div>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: docs/02_MODEL_A_NAKED_SEQUENCE_SELECTOR.md; final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md; Reynolds et al. (2004); Ui-Tei et al. (2004).",
        "notes": """
<p>In Step 1 of our pipeline, we use Model A to scan the target mRNA for promising naked sequences before applying any chemistry.</p><p>Model A is a LightGBM model trained on 214 sequence features. It evaluates terminal thermodynamic asymmetry—ensuring the 5' guide end is loose so Argonaute-2 picks up the correct strand—plus the Reynolds rules and target opening energy.</p><p>As the table shows, on standard naked RNA screens, Model A is very accurate: achieving Pearson r = 0.88 on Takayuki, 0.83 on Mixset, and 0.80 on Huesken.</p><p>However, look at the highlighted red row: when we test Model A on chemically modified siRNAs, its score drops all the way down to 0.1771.
This proves that even an excellent sequence model is completely blind to chemistry, which makes our second model, Model B, mandatory.</p>
"""
    },

    # SLIDE 15: Model B: The Single Unified Dose-Aware CatBoost Regressor
    {
        "id": 15,
        "eyebrow": "FLAGSHIP PREDICTIVE ENGINE | 517-D GBDT",
        "title": "Model B: The Single Unified Dose-Aware CatBoost Regressor",
        "subtitle": "Native Concentration Conditioning, Symmetric Oblivious Decision Trees, and Closed-Form Hill Inversion",
        "badges": ["CatBoost Regressor", "517-D Unified Vector", "Zero Cascading Variance", "Hill Closed-Form"],
        "body_html": """
<div class="cards-grid cards-2">
          <div class="card border-cyan">
            <div class="card-header">
              <span class="card-tag">ALGORITHM &amp; FORMULATION</span>
              <h3>Unified Direct Potency Modeling</h3>
            </div>
            <p class="card-desc">Directly maps 517-D chemical, foundation, thermodynamic, and concentration inputs to continuous mRNA knockdown %:</p>
            <div class="formula-box">
              KD<sub>pred</sub> = CatBoostRegressor([ x<sub>444-chem</sub>, z<sub>64-FM</sub>, t<sub>5-thermo</sub>, c<sub>4-dose</sub> ])
            </div>
            <ul class="bullet-list">
              <li><strong>Oblivious Trees:</strong> Uses symmetric decision trees that act as robust index lookups, providing natural L2 regularization against tabular overfitting.</li>
              <li><strong>Joint Interaction Learning:</strong> Decision tree split nodes natively discover interaction thresholds between chemical positions and concentration (e.g. 2'-OMe at pos 2 requiring &ge; 0.5 nM for full efficacy).</li>
              <li><strong>Elimination of Cascading Errors:</strong> Bypasses the variance amplification of two-stage (pIC<sub>50</sub> &rarr; Hill) cascades.</li>
            </ul>
          </div>

          <div class="card border-emerald">
            <div class="card-header">
              <span class="card-tag">DYNAMIC PHARMACOKINETICS</span>
              <h3>Dynamic Inversion of the Hill Equation</h3>
            </div>
            <p class="card-desc">Derives intrinsic binding affinity (pIC<sub>50</sub> and IC<sub>50</sub>) analytically from predicted knockdown % at concentration C:</p>
            <div class="formula-box">
              Estimated IC<sub>50</sub> = C &times; [ (100.0 &minus; KD<sub>pred</sub>) / KD<sub>pred</sub> ] (nM)
            </div>
            <div class="formula-box">
              Estimated pIC<sub>50</sub> = 9.0 &minus; log<sub>10</sub>( max(10<sup>&minus;4</sup>, Estimated IC<sub>50</sub>) )
            </div>
            <ul class="bullet-list">
              <li><strong>Closed-Form Stability:</strong> No non-linear numerical solver iterations required during inference; runs in microsecond CPU time.</li>
              <li><strong>Consistency:</strong> Monotonically couples predicted phenotypic efficacy with intrinsic biochemical potency.</li>
            </ul>
          </div>
        </div>
""",
        "footer_ref": "Research References / Technical Basis: docs/01_UNIFIED_DOSE_AWARE_CATBOOST_ENGINE.md; smepred/src/model_b_v4.py; Prokhorenkova et al. (NeurIPS 2018, CatBoost).",
        "notes": """
<p>This slide presents our main predictive engine: Model B, the Unified Dose-Aware CatBoost Regressor.</p><p>Why CatBoost?
CatBoost builds symmetric decision trees called oblivious trees. This means the same split criterion is used across the entire depth level, which acts as a strong natural defense against overfitting in tabular data.</p><p>Most importantly, because the tree sees chemical features and dose together in one vector, it learns how chemistry and dose interact. For example, it learns that a candidate with 2'-OMe at position 2 might need 0.5 nM to show full activity, while a 2'-fluoro design reaches that same activity at 0.05 nM.</p><p>And for biologists who need IC50 and pIC50 values, we analytically derive them using the inverted Hill formula shown on the right. This gives clean, instant pharmacokinetic numbers in microseconds without needing complex numerical curve fitters.</p>
"""
    },

]
