# HelixZero-CMS
## A Computational Engine for siRNA Chemical Modification Design

**Prepared by:** Nitin Jadhav, AI/ML Intern — C-DAC Pune
**Contact:** nitinjadhav882003@gmail.com | linkedin.com/in/nitinjadhav888

---

## 1. The Problem

A raw siRNA sequence is therapeutically useless on its own. Without chemical protection it degrades within minutes in the bloodstream, triggers immune responses, and fails to reach its target gene. Chemical modifications solve all of this — but the number of possible modification patterns for a single siRNA exceeds **10⁶⁸ combinations**. No lab in the world can synthesize and test even a tiny fraction of that space.

HelixZero-CMS was built to navigate this space computationally, so researchers can identify the best chemical architectures before touching a pipette.

---

## 2. What the Platform Does

The platform takes a raw gene sequence as input and guides the researcher through three steps:

**Step 1 — Find the best unmodified candidates**
Given an mRNA target, the platform generates every possible 21-mer siRNA duplex and ranks them by predicted silencing activity. It simultaneously screens each candidate for known seed-region toxicity using a database of 4,097 experimentally validated hexamers.

**Step 2 — Profile single chemical modifications**
For any candidate, the platform tests all 1,260 possible single-modification variants across both strands in seconds, identifying which chemical additions improve efficacy or neutralize toxicity.

**Step 3 — Stack modifications automatically**
The platform's Beam Search algorithm intelligently combines multiple modifications together — building towards architectures similar to established clinical chemistries (like ESC or ESC+) — while automatically avoiding biologically harmful patterns. It navigates billions of possibilities and delivers the top-ranked designs in under 20 seconds.

---

## 3. Why the Scores Are Biologically Meaningful

The raw machine learning score is adjusted by a **5-domain biophysics engine**. Each domain independently checks whether a design respects real-world biological constraints:

| Domain | What It Checks |
|--------|----------------|
| **Nuclease Resistance** | Is the siRNA protected from enzymatic degradation in serum? |
| **Immunogenicity** | Does the design avoid triggering the innate immune system (TLR7/8)? |
| **RISC Loading** | Can the guide strand correctly load into the Ago2 silencing complex? |
| **Thermodynamics** | Is the duplex structurally stable — not too rigid, not too loose? |
| **Serum Stability** | Are the strand termini properly capped for survival in blood plasma? |

This engine was designed specifically to move beyond early RNAi thermodynamic rules, many of which have since been qualified by clinical data. The penalty weights were calibrated against four FDA-approved siRNA drugs — Givosiran, Lumasiran, Vutrisiran, and Nedosiran — all of which score correctly without false penalties.

---

## 4. Clinical Validation

| Drug | Company | Approved | Score |
|------|---------|---------|-------|
| Givosiran | Alnylam | 2019 | 59.9 |
| Lumasiran | Alnylam | 2020 | ≥ 50 |
| Vutrisiran | Alnylam | 2022 | ≥ 50 |
| Nedosiran | Dicerna | 2023 | ≥ 50 |

All four drugs pass every biophysical constraint check without any false penalties, confirming that the engine does not incorrectly penalize proven clinical chemistry.

---

## 5. The Road Ahead

The current model is trained on publicly available datasets. The critical next step is **iterative wet lab integration**:

The platform proposes novel chemical architectures from unexplored regions of modification space. A synthesis partner produces the top candidates. Real assay results are then fed back into the model as new training data. With each cycle, predictions become increasingly accurate — especially for novel modification chemistries that lack public training data — and the process systematically uncovers patentable, clinically superior siRNA designs in the current crowded IP landscape.

---

*HelixZero-CMS is a research platform developed during an internship at C-DAC Pune.*
*All intellectual property rights are retained by the author.*
