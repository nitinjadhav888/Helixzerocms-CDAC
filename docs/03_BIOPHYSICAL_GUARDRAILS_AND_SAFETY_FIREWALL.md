# HELIXZERO-CMS: BIOPHYSICAL GUARDRAILS & SAFETY FIREWALL SPECIFICATION
## Deterministic Penalty Engine & Whole-Transcriptome Off-Target Verification
**Authoritative Source Alignment:** `final_benchmarks/`  
**Classification:** Biophysical Validation & Pharmacological Safety Engine  
**Implementation Modules:** `smepred/src/biophysics.py` & `smepred/src/offtarget.py`  
**Institution:** High Performance Computing — Medical & BioInformatics Group, C-DAC, Pune

---

### 1. Executive Overview

Pure statistical machine learning models frequently suffer from "pathological edge-case exploitation"—proposing chemically extreme configurations (e.g., 100% phosphorothioate backbones or 100% Locked Nucleic Acids) that yield high synthetic potency scores in unconstrained algorithms but are cytotoxic or biologically inert in living cells.

HelixZero resolves this through a **dual-layer deterministic safety firewall**:
1. **The 4-Domain Deterministic Biophysical Penalty Engine**: Evaluates thermodynamic, nuclease, immunogenic, and cytotoxic constraints.
2. **The 2-Bit Whole-Transcriptome Off-Target Firewall**: Scans for both slicer-mediated (15-mer) and seed-mediated (positions 2–8) cross-reactivity across all 37,000+ human transcripts in $O(1)$ time.

---

### 2. The 4-Domain Deterministic Biophysical Penalty Engine

The biophysical engine computes a scaled penalty sum subtracted directly from the raw ML efficacy prediction:
$$\text{Adjusted Score} = \max\left(0.0, \min\left(100.0, \text{Raw ML Score} - \sum_{i=1}^4 \text{Penalty}_i\right)\right)$$

```
+---------------------------------------------------------------------------------------------------+
|                         4-DOMAIN DETERMINISTIC BIOPHYSICAL PENALTY ENGINE                         |
+--------------------------+--------------------------+-----------------------+---------------------+
| Domain 1: Thermodynamics | Domain 2: Serum Nuclease | Domain 3: Innate      | Domain 4: Seed      |
| & Unwinding Activation   | & Tandem di-PS Stability | Immunostimulatory TLR | Cytotoxicity        |
| (Empirical ΔΔG°37)       | (Terminal Exonuclease)   | (TLR7/8 2'-OMe Mask)  | (Janas et al. 2018) |
+--------------------------+--------------------------+-----------------------+---------------------+
```

#### 2.1 Domain 1: Thermodynamic Asymmetry & Duplex Unwinding Activation Barrier
- **Empirical Thermodynamic Perturbations ($\Delta\Delta G^\circ_{37}$)**:
  Chemical modifications perturb RNA duplex stability. Empirical $\Delta\Delta G^\circ_{37}$ increments from [`chem_alphabet.py`](file:///d:/Helixx/smepred/src/chem_alphabet.py) are integrated into terminal stability calculations:
  - $2'\text{-Fluoro (2'-F)}$: $-0.85\,\text{kcal/mol}$ (stabilizing, pre-organizes C3'-endo sugar pucker).
  - $2'\text{-O-Methyl (2'-OMe)}$: $-0.45\,\text{kcal/mol}$ (mildly stabilizing).
  - $2'\text{-Deoxy (DNA)}$: $+0.70\,\text{kcal/mol}$ (destabilizing to A-form RNA helix).
  - $\text{Phosphorothioate (PS)}$: $+0.40\,\text{kcal/mol}$ per stereorandom linkage.
- **Terminal Asymmetry**:
  $$\Delta G_{\text{effective, 5'}} = \Delta G_{\text{sequence, 5'}} + \sum_{j=1}^4 \Delta\Delta G_{\text{mod}, j}$$
  If the passenger 5'-end is more easily unwound than the guide 5'-end, passenger loading occurs, generating unintended off-target silencing and triggering a severe asymmetry penalty.
- **Unwinding Activation Barrier**:
  Ago2 requires the passenger strand to be unwound and expelled following nicking. Duplexes with excessive total stabilization ($\Delta\Delta G_{\text{duplex}} < -8.0\,\text{kcal/mol}$) are penalized for impaired unwinding kinetics; duplexes with insufficient stability ($\Delta\Delta G_{\text{duplex}} > -2.0\,\text{kcal/mol}$) are penalized for premature dissociation.

#### 2.2 Domain 2: Serum Nuclease & Exonuclease Protection
- Unmodified phosphodiester bonds at terminal overhangs are rapidly degraded by serum $3'\rightarrow 5'$ exonucleases (e.g., ERI1).
- **Tandem Phosphorothioate Kinetics**:
  - Full tandem di-PS linkages at terminal $3'\text{-overhangs}$ (positions 20 and 21) confer complete exonuclease resistance ($0.0$ penalty).
  - Isolated single-PS linkages or unmodified RNA overhangs incur an exonuclease degradation penalty ($0.6$ to $0.8$).

#### 2.3 Domain 3: Innate Immunostimulatory Motif Suppression
- Single-stranded and double-stranded RNAs can activate endosomal Toll-Like Receptors:
  - **TLR7**: Recognizes uridine-rich single-stranded RNA motifs (e.g., `5'-UGGC-3'`, `5'-UGU-3'`).
  - **TLR8**: Recognizes GU-rich motifs (e.g., `5'-GUUC-3'`).
- Activation triggers massive pro-inflammatory cytokine release (IFN-$\alpha$, TNF-$\alpha$, IL-6).
- **The 2'-OMe Shield**:
  Placement of a bulky $2'\text{-O-methyl}$ group at the 2'-position sterically disrupts receptor dimerization in the TLR7/8 ligand-binding pocket. The engine scans for unmasked immunostimulatory motifs and applies severe penalizations unless protected by 2'-OMe.

#### 2.4 Domain 4: MicroRNA-Like Seed Cytotoxicity
- Guide strand nucleotides 2–8 (the seed region) can bind with partial complementarity to hundreds of cellular mRNA 3'-UTRs, repressing essential survival genes (microRNA-like off-target silencing).
- The engine checks seed heptamer sequences against the Janas et al. (2018) empirical human hepatocyte cell-viability database. Unfavorable seeds (< 50% cell viability) receive substantial safety downweightings.

---

### 3. The 2-Bit Whole-Transcriptome Off-Target Firewall

The whole-transcriptome firewall (`smepred/src/offtarget.py`) screens prospective siRNAs against the complete human reference transcriptome (Ensembl GRCh38, 37,000+ transcripts):

```
Candidate siRNA Duplex (21-nt Guide Strand)
                    │
                    ▼
     [2-Bit Bit-Packed Binary Hash Index]
                    │
   ┌────────────────┴────────────────┐
   ▼                                 ▼
Slicer-Mediated Check             Seed-Mediated Check
(Contiguous 15-mer match)         (Positions 2–8 match)
   │                                 │
   ├─ If match found on              ├─ Evaluates 3'-UTR match density
   │  non-target transcript:         │  across transcriptome
   │  VETO! (CLEARED: FALSE)         │  Applies graded off-target
   │                                 │  downweighting
   └─ Safe -> Proceed                └─ Safe -> Pass to ranker
```

- **Binary Representation**: Transcripts are encoded using 2 bits per nucleotide (`A=00`, `C=01`, `G=10`, `U=11`), reducing the human transcriptome memory footprint from multiple gigabytes to < 120 MB in RAM.
- **Slicer Veto Rule**: If an antisense candidate contains $\ge 15$ contiguous nucleotides identical to any unintended transcript, it can mediate off-target endonucleolytic slicing by Ago2. Such candidates are **immediately disqualified** (`status: TOXIC`, `isSafe: false`).
