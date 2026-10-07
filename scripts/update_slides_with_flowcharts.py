import re
from pathlib import Path

p1_path = Path("d:/Helixx/scripts/presentation_slides_part1.py")
content = p1_path.read_text(encoding="utf-8")

# 1. Update Slide 1
slide1_flowchart_html = """        <div class="pipeline-flowchart-bar">
          <div class="flow-step-node" data-deep-dive="takayuki_benchmark" title="Click to inspect Stage 1 Model A Details">
            <span class="flow-step-icon">⚡</span>
            <div class="flow-step-info">
              <strong>Stage 1: Model A (LightGBM)</strong>
              <span>214-D Sequence Core &bull; r = 0.88</span>
            </div>
          </div>
          <div class="flow-node-arrow">&rarr;</div>
          <div class="flow-step-node" data-deep-dive="heldout_multidose" title="Click to inspect Stage 2 Model B Details">
            <span class="flow-step-icon">🧪</span>
            <div class="flow-step-info">
              <strong>Stage 2: Model B (CatBoost)</strong>
              <span>517-D Unified Engine &bull; r = 0.84</span>
            </div>
          </div>
          <div class="flow-node-arrow">&rarr;</div>
          <div class="flow-step-node" data-deep-dive="biophysical_guardrails" title="Click to inspect 4-Domain Guardrails">
            <span class="flow-step-icon">🛡️</span>
            <div class="flow-step-info">
              <strong>Stage 3: Biophysics</strong>
              <span>4-Domain Safety Firewall</span>
            </div>
          </div>
          <div class="flow-node-arrow">&rarr;</div>
          <div class="flow-step-node" data-deep-dive="fda_blind_validation" title="Click to inspect FDA Blind Validation">
            <span class="flow-step-icon">💊</span>
            <div class="flow-step-info">
              <strong>Clinical Candidate</strong>
              <span>Sub-Second Lead Design</span>
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
              <div class="metric-item clickable-metric" data-deep-dive="takayuki_benchmark" title="Click for Takayuki evaluation breakdown">
                <span class="metric-val">r = 0.8788</span>
                <span class="metric-lbl">Model A (Takayuki Screen)</span>
              </div>
              <div class="metric-item clickable-metric" data-deep-dive="heldout_multidose" title="Click for Multi-Dose evaluation breakdown">
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
              <div class="metric-item clickable-metric" data-deep-dive="groupkfold_5251" title="Click for GroupKFold zero-leakage proof">
                <span class="metric-val">5,251</span>
                <span class="metric-lbl">Unique Sequence Groups</span>
              </div>
              <div class="metric-item clickable-metric" data-deep-dive="fda_blind_validation" title="Click for FDA clinical drug evaluation">
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
              <div class="metric-item clickable-metric" data-deep-dive="chemical_444_features" title="Click for 812-variant chemical scan details">
                <span class="metric-val">&lt; 0.10s</span>
                <span class="metric-lbl">812-Variant Scan</span>
              </div>
              <div class="metric-item clickable-metric" data-deep-dive="twobit_offtarget" title="Click for 2-bit transcriptome index details">
                <span class="metric-val">O(1)</span>
                <span class="metric-lbl">Transcriptome Bit-Lookup</span>
              </div>
            </div>
            <ul class="bullet-list">
              <li>Evaluates exonuclease serum stability, TLR7/8 immuno-masking, and Janas seed cytotoxicity.</li>
              <li>Generates unbroken A-form PDB models with B-factor chemical encoding for 3Dmol.js.</li>
            </ul>
          </div>
        </div>"""

pattern_slide1_body = re.compile(
    r'<div class="cards-grid cards-3">\s*<div class="card border-cyan">.*?</div>\s*</div>\s*</div>',
    re.DOTALL
)

# 2. Update Slide 12 with Vector Visual Bar and clickable rows
slide12_body = """        <div class="vector-bar-container" style="margin-bottom: 12px;">
          <div class="vector-segment seg-chem clickable-pill" style="flex: 444;" data-deep-dive="chemical_444_features" title="Click for 444-D Chemistry Breakdown">
            <span class="seg-title">444-D Synthetic Chemistry</span>
            <span class="seg-dims">420 Positional + 24 Global Descriptors</span>
          </div>
          <div class="vector-segment seg-fm clickable-pill" style="flex: 64;" data-deep-dive="rnafm_foundation" title="Click for 64-D RNA-FM Breakdown">
            <span class="seg-title">64-D RNA-FM</span>
            <span class="seg-dims">Transformer Embeddings</span>
          </div>
          <div class="vector-segment seg-thermo clickable-pill" style="flex: 30;" data-deep-dive="biophysical_guardrails" title="Click for ViennaRNA Thermodynamics">
            <span class="seg-title">5-D Thermo</span>
            <span class="seg-dims">&Delta;G Duplex / Opening</span>
          </div>
          <div class="vector-segment seg-dose clickable-pill" style="flex: 30;" data-deep-dive="hill_inversion" title="Click for Exposure &amp; Hill Inversion">
            <span class="seg-title">4-D Dose</span>
            <span class="seg-dims">&log;<sub>10</sub>(Dose_nM)</span>
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
                <tr class="clickable-row" data-deep-dive="chemical_444_features" title="Click to view 444 chemical features deep dive">
                  <td><strong>Passenger (Sense) Chemistry</strong><br><small>Indices 0 &ndash; 221</small></td>
                  <td>222</td>
                  <td>21 slots &times; 10 structural descriptors (210) + 12 strand-level descriptors = 222 dims. Evaluates passenger strand inactivation, 3'-GalNAc conjugation, and nuclease shielding.</td>
                </tr>
                <tr class="clickable-row" data-deep-dive="chemical_444_features" title="Click to view 444 chemical features deep dive">
                  <td><strong>Guide (Antisense) Chemistry</strong><br><small>Indices 222 &ndash; 443</small></td>
                  <td>222</td>
                  <td>21 slots &times; 10 structural descriptors (210) + 12 strand-level descriptors = 222 dims. Encodes seed-region flexibility (nt 2–8), cleavage center tolerance (nt 10–11), and 5'-VP anchoring.</td>
                </tr>
                <tr class="clickable-row" data-deep-dive="rnafm_foundation" title="Click to view RNA-FM foundation model deep dive">
                  <td><strong>RNA-FM Foundation Embeddings</strong><br><small>Indices 444 &ndash; 507</small></td>
                  <td>64</td>
                  <td>32-dim sense + 32-dim antisense PCA embeddings from 12-layer <code>rna_fm_t12</code> transformer. Captures transcript-wide evolutionary constraints.</td>
                </tr>
                <tr class="clickable-row" data-deep-dive="biophysical_guardrails" title="Click to view ViennaRNA thermodynamics deep dive">
                  <td><strong>ViennaRNA Thermodynamics</strong><br><small>Indices 508 &ndash; 512</small></td>
                  <td>5</td>
                  <td>Duplex binding free energy (&Delta;G<sub>duplex</sub>), ensemble free energy, MFE probability, and 5' guide/sense terminal opening energies.</td>
                </tr>
                <tr class="clickable-row" data-deep-dive="hill_inversion" title="Click to view dose covariates &amp; Hill inversion deep dive">
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
              <div class="metric-item clickable-metric" data-deep-dive="hill_inversion" title="Click for Dose Exposure &amp; Hill Inversion">
                <span class="metric-val">#1</span>
                <span class="metric-lbl">&log;<sub>10</sub>(Dose_nM) (18.4% Gain)</span>
              </div>
              <div class="metric-item clickable-metric" data-deep-dive="chemical_444_features" title="Click for AS Pos 2 Sugar Details">
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
        </div>"""

pattern_slide12_body = re.compile(
    r'<div class="cards-grid cards-2">\s*<div class="card border-cyan">\s*<div class="card-header">\s*<span class="card-tag">FEATURE GROUP BREAKDOWN</span>.*?</div>\s*</div>\s*</div>',
    re.DOTALL
)

# 3. Update Slide 14 table with clickable rows
slide14_table_old = """            <table class="tech-table">
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
                <tr>
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
                <tr style="background: rgba(248,113,113,0.1);">
                  <td><strong>CMsiRNAdb Hetero (Modified Negative Control)</strong></td>
                  <td>2,576</td>
                  <td><strong style="color: var(--red);">0.1771</strong></td>
                  <td><strong style="color: var(--red);">0.1645</strong></td>
                  <td><strong style="color: var(--red);">0.5711</strong></td>
                </tr>
              </tbody>
            </table>"""

slide14_table_new = """            <div style="font-size: 0.72rem; color: var(--accent); margin-bottom: 6px; font-family: var(--font-mono);">💡 Click any row below for evaluation methodology deep-dive</div>
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
                <tr class="clickable-row" data-deep-dive="takayuki_benchmark" title="Click to view Takayuki evaluation deep-dive">
                  <td><strong>Takayuki Screen (<code>Taka.csv</code>)</strong></td>
                  <td>702</td>
                  <td><strong>0.8788</strong></td>
                  <td><strong>0.8734</strong></td>
                  <td><strong>0.9275</strong></td>
                </tr>
                <tr class="clickable-row" data-deep-dive="takayuki_benchmark" title="Click to view benchmark evaluation details">
                  <td><strong>Mixset 7-Studies (<code>Mix.csv</code>)</strong></td>
                  <td>472</td>
                  <td><strong>0.8291</strong></td>
                  <td><strong>0.8093</strong></td>
                  <td><strong>0.9456</strong></td>
                </tr>
                <tr class="clickable-row" data-deep-dive="takayuki_benchmark" title="Click to view benchmark evaluation details">
                  <td><strong>Huesken Held-Out (<code>Hu.csv</code>)</strong></td>
                  <td>2,361</td>
                  <td><strong>0.8044</strong></td>
                  <td><strong>0.8065</strong></td>
                  <td><strong>0.9099</strong></td>
                </tr>
                <tr class="clickable-row" data-deep-dive="heldout_multidose" style="background: rgba(248,113,113,0.1);" title="Click to view chemistry blindness details">
                  <td><strong>CMsiRNAdb Hetero (Modified Negative Control)</strong></td>
                  <td>2,576</td>
                  <td><strong style="color: var(--red);">0.1771</strong></td>
                  <td><strong style="color: var(--red correlation);">0.1645</strong></td>
                  <td><strong style="color: var(--red);">0.5711</strong></td>
                </tr>
              </tbody>
            </table>"""

# Execute substitutions
old_s1 = pattern_slide1_body.search(content)
if old_s1:
    content = content[:old_s1.start()] + slide1_flowchart_html + content[old_s1.end():]
    print("Replaced Slide 1 body with Flowchart and clickable metrics.")
else:
    print("Warning: Slide 1 body pattern not matched.")

old_s12 = pattern_slide12_body.search(content)
if old_s12:
    content = content[:old_s12.start()] + slide12_body + content[old_s12.end():]
    print("Replaced Slide 12 body with Vector Visual Bar and clickable rows.")
else:
    print("Warning: Slide 12 body pattern not matched.")

if slide14_table_old in content:
    content = content.replace(slide14_table_old, slide14_table_new)
    print("Replaced Slide 14 table with clickable rows.")
else:
    print("Warning: Slide 14 table old snippet not found.")

p1_path.write_text(content, encoding="utf-8")
print("Saved presentation_slides_part1.py")
