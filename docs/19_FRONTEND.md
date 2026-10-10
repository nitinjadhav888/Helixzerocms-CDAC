# 19. FRONTEND WORKBENCH & 3D VISUALIZATION
## Single-Page Laboratory Application, Design System, and WebGL Architecture
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  
**Primary Source File:** `smepred/app.html` (4,670 lines, 239.6 KB)  

---

### 1. Architectural Philosophy: Zero-Build High-Precision SPA

The HelixZero frontend is implemented as a self-contained, zero-build Single-Page Application (SPA) in `smepred/app.html`:
- **Zero Build Tooling Overhead:** Requires no Node.js, npm, Webpack, or Vite pipelines. The single HTML file contains complete CSS design systems, semantic HTML markup, and ES2022 asynchronous JavaScript.
- **Embedded WebGL Integration:** Leverages **3Dmol.js** (`v2.0.4`) via CDN for high-performance in-browser 3D molecular visualization of nucleic acid double helices.
- **Biomedical Research Design System (v2.6):** Engineered with a clinical laboratory dark theme:
  - *Surfaces:* Deep obsidian (`--bg: #070d18`), slate containers (`--surface: #0c1527`), elevated cards (`--surface2: #121e36`).
  - *Accents:* Nucleic cyan (`--accent: #00e5bf`), RNA indigo (`--accent2: #6366f1`), biophysical amber gold (`--accent-gold: #f59e0b`).
  - *Typography:* Plus Jakarta Sans (Display), Inter (Body text), JetBrains Mono (Sequence & code).

---

### 2. Functional Application Tabs & User Flows

The workbench organizes oligonucleotide drug design into five specialized research modules:

#### Module 01: Sequence Ingestion & Naked siRNA Discovery (`tab-input`)
- Ingests raw mRNA strings, gene accession symbols, or FASTA files.
- Provides one-click quick-load presets for clinically validated therapeutic genes (*PCSK9*, *TTR*, *ALAS1*, *HAO1*, *LDHA*).
- Displays candidate 21-mers in real-time tables with sorting by efficacy, biological transcript domain, thermodynamic asymmetry ($\Delta\Delta G$), and Janas toxicity. Efficacy scores and score bars are strictly bounded in $[0.00\%, 100.00\%]$.

#### Module 02: Positional Chemistry Permutation Scanner (`tab-single`)
- Takes any selected candidate siRNA duplex and executes an exhaustive single-modification scan across all 42 positions.
- Displays interactive positional efficacy heatmaps and waterfall charts identifying the highest-impact positions for chemical optimization.
- Features embedded 3D structural previews highlighting the modified residue.

#### Module 03: Combinatorial Multi-Mod Beam Search Optimizer (`tab-multi`)
- Explores combinatorial modification configurations using an autonomous beam search with complete 42-position positional coverage ($W = 25$, depth up to 42 duplex modifications).
- Allows scientists to constrain the search space to **Tier 0: FDA Clinical Core Chemistries** (Patisiran, Givlaari, Leqvio, Amvuttra standards: 2'-OMe `M`, 2'-F `F`, DNA `D`, PS `S`, 5'-VP `1`, and strictly position-7 GNA `8` classified as `Specialty ($$)`), or uncheck to explore all 30 innovative modifications including **Tier 1 Preclinical** (2'-MOE `E`, LNA `L`, ENA `Y`, UNA `6`) and **Tier 2 Extrapolated** chemistries. In Novel mode, results Pareto-interleave core anchors and innovative candidates so scientists discover diverse chemistries in the top results.
- Displays dynamic Chemical Evidence Badges (`Tier 0: FDA Core`, `Tier 1: Preclinical`, `Tier 2: Extrapolated`) and Reagent Synthesis Budget Tiers (`Standard ($)`, `Specialty ($$)`, `Exotic Custom ($$$)`) by aggregating modified positions across both strands while ignoring canonical ribonucleotides. (S)-GNA (`8`) displays `Tier 0: FDA Core` and `Specialty ($$)` budget tier.
- Displays real-time radar charts and bar breakdowns of biophysical penalty deductions (Helicase, Nuclease, TLR7/8, Seed Cytotoxicity).
- Enforces strict $[0.00\%, 100.00\%]$ visual bounds on all progress bars (`scoreBar`, `scoreBarSmall`).


#### Module 04: Standardized Nucleic Acid Modification Ontology (`tab-mods`)
- Comprehensive interactive directory of all 30 supported chemical modifications.
- Groups modifications across:
  1. *Backbone Linkages & Phosphate Mimics:* Phosphorothioate (PS), $5'$-VP, $5'$-Phosphate.
  2. *$2'$-Ribose Conformations:* $2'$-OMe, $2'$-F, $2'$-MOE, LNA, ENA, UNA, GNA, TNA, FANA.
  3. *Modified Nucleobases:* 5-methyl-C, Pseudouridine ($\Psi$), Inosine, 2,6-diaminopurine.
  4. *Terminal Conjugates & Inverted Caps:* Trivalent GalNAc, Inverted Abasic, Cholesterol.

#### Module 05: Conversational Scientific Co-Pilot
- Embedded laboratory assistant (`src/assistant_service.py`) grounded in HelixZero biophysical equations.
- Provides automated executive lead summaries, mechanism-of-action explanations, and clinical viability recommendations.

---

### 3. 3D WebGL Structural Visualization Architecture

HelixZero visualizes candidate duplexes by rendering standard PDB atomic coordinate files emitted dynamically by `smepred/src/pdb_generator.py`:
- **Continuous A-Form Topology:** Emits 504 atoms (21 base pairs $\times$ 24 atoms per pair) with unbroken backbone cartoons.
- **B-Factor Chemical Encoding:**
  - `90.0` $\to$ $2'$-Fluoro (Rendered in Pink).
  - `80.0` $\to$ $2'$-O-Methyl (Rendered in Amber Gold).
  - `70.0` $\to$ Phosphorothioate (Rendered in Emerald Green).
  - `60.0` $\to$ $2'$-MOE (Rendered in Cyan).
  - `50.0` $\to$ LNA (Rendered in Purple).
  - `85.0` $\to$ $2'$-Deoxy/DNA (Rendered in Blue).
- **Interactive Controls:** Full 3D rotation, pitch/yaw translation, zoom, and cartoon/stick toggle.
