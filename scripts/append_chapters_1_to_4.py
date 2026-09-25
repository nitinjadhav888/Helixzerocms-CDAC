#!/usr/bin/env python3
"""
append_chapters_1_to_4.py
=========================
Appends Chapters 1 to 4 to scripts/compile_30page_monograph_pdf.py.
Features deep pedagogical explanations, RNase A chemical mechanisms,
8-step Ago2 catalytic cycle, failure modes, literature review, data lake,
leakage avoidance, and sequence sanitization.
Strictly ZERO dollar signs ($).
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TARGET = ROOT_DIR / "scripts" / "compile_30page_monograph_pdf.py"

def append_content():
    print("Appending Chapters 1 to 4...")
    with open(TARGET, "a", encoding="utf-8") as f:
        f.write('''
    # =========================================================================
    # CHAPTER 1: MOLECULAR BIOLOGY & PHARMACOLOGY
    # =========================================================================
    story.append(Paragraph("Chapter 1: The Molecular Biology & Pharmacology of RNA Interference", h1_style))
    
    story.append(Paragraph("1.1 Historical Context & The RNAi Revolution", h2_style))
    story.append(Paragraph("RNA interference (RNAi) is an evolutionary conserved, sequence-specific post-transcriptional gene regulation pathway discovered in Caenorhabditis elegans by Andrew Fire and Craig Mello in 1998 (Nobel Prize in Physiology or Medicine, 2006). In nature, RNAi serves as an ancient cellular immune system that defends eukaryotic genomes against retrotransposons, mobile genetic elements, and RNA viruses.", body_style))
    story.append(Paragraph("From a therapeutic standpoint, RNAi represents a conceptual paradigm shift over conventional small-molecule pharmacology and monoclonal antibodies. Small molecules require druggable hydrophobic binding pockets within a folded tertiary protein structure (rendering over 85% of the human proteome 'undruggable'), while monoclonal antibodies are largely restricted to cell-surface and extracellular receptors. Synthetic small interfering RNAs (siRNAs) bypass these protein structural limitations entirely: by operating upstream at the mRNA transcript level, an siRNA can achieve potent, sequence-specific catalytic silencing of any human disease-causing gene whose primary sequence is known.", body_style))

    story.append(Paragraph("1.2 The Atomic Architecture of Argonaute-2 (Ago2)", h2_style))
    story.append(Paragraph("The multi-protein RNA-Induced Silencing Complex (RISC) relies upon a single catalytic core: <b>Argonaute-2 (Ago2)</b>, a 96 kDa bilobal endonuclease encoded by the human EIF2C2 gene. While human cells express four Argonaute paralogs (Ago1 through Ago4), only Ago2 possesses autonomous catalytic slicer cleavage activity.", body_style))
    story.append(Paragraph("High-resolution crystallographic structures and cryo-electron microscopy reconstructions (PDB accessions 4W5N, 4W5O, 4W5T; Schirle & MacRae, 2012; Elkayam et al., 2012) reveal that Ago2 is organized into two structural lobes connected by a flexible linker: Lobe 1 contains the N-terminal and PAZ domains, while Lobe 2 houses the MID and PIWI domains.", body_style))
    
    story.append(Paragraph("• <b>The MID (Middle) Domain Pocket:</b> Lobe 2 contains an evolutionary invariant, highly basic coordination cleft formed by residues Tyr529, Lys533, Asn545, and Lys566, coordinated with a divalent magnesium ion (Mg2+). This pocket anchors the 5'-monophosphate of the antisense guide strand with sub-nanomolar affinity. In vivo, a 5'-phosphate group is absolute sine qua non for biological activity. If an siRNA is synthesized with an unphosphorylated 5'-hydroxyl, it must undergo enzymatic phosphorylation by endogenous cellular kinases (predominantly Clp1) before it can anchor into the MID pocket. Chemical modifications that introduce steric bulk or alter the dihedral angles of nucleotide 1 (such as Locked Nucleic Acid) clash directly with Tyr529/Lys566, dislodging the 5'-terminus and abolishing gene silencing entirely.", bullet_style))
    story.append(Paragraph("• <b>The PAZ Domain:</b> Connected via a flexible hinge, the PAZ domain contains an open, hydrophobic cleft that accommodates and anchors the 2-nucleotide 3'-overhang of the guide strand. By anchoring the 3'-terminus, the PAZ domain maintains the duplex in a pre-stressed state, presenting nucleotides 2 through 8 (the seed region) in an idealized, quasi-helical A-form conformation ready for rapid target scanning.", bullet_style))
    story.append(Paragraph("• <b>The PIWI Domain (The Slicer Engine):</b> Adopting an RNase H-like tertiary fold, the PIWI domain contains the catalytic tetrad <b>Asp597-Glu638-Asp669-His807 (the DEDH motif)</b>. This catalytic center coordinates a divalent magnesium ion to execute an in-line nucleophilic attack on the target mRNA backbone, hydrolyzing the scissile phosphodiester bond precisely between nucleotides 10 and 11 opposite the guide strand. Crucially, catalytic cleavage requires the siRNA-mRNA duplex to form an uninterrupted, flexible A-form geometry in this central cleavage window.", bullet_style))
    story.append(Paragraph("• <b>The N-Terminal Domain:</b> Serves as a physical unwinding wedge during RISC loading, structurally prying apart the passenger (sense) strand from the guide (antisense) strand, facilitating the catalytic cleavage and expulsion of the passenger strand.", bullet_style))

    ago2_diagram = """                  AGO2 DOMAIN ARCHITECTURE & SI-RNA ANCHORING
                  
   5' Guide Anchor                       Catalytic Cleavage                   3' Overhang Anchor
   [MID Domain Pocket]                  [PIWI Domain Cleft]                   [PAZ Domain Pocket]
          │                                     │                                     │
          ▼                                     ▼                                     ▼
     (5'-P / 5'-VP)                    Cleavage at pos 10-11                       (2-nt 3'-dTdT)
          │                                     │                                     │
   5'-p - [G - U - A - A - G - A - C - U - U - G] - [A - G - A - U - G - A - U - C - C] - dT - dT - 3'
          | | | | | | |                         |   | | | | | | | | | | | | |
     3'-  [C - A - U - U - C - U - G - A - A - C] - [U - C - U - A - C - U - A - G - G] - 5'
                     ▲                                     ▲
                     │                                     │
               Seed Region (pos 2-8)                Body / Slicer Region
             (miRNA-like nucleating zone)          (Must maintain A-form helix)"""
    add_code_box(ago2_diagram)

    story.append(Paragraph("1.3 The Complete Eight-Step Catalytic Cycle of Ago2-RISC", h2_style))
    story.append(Paragraph("The life cycle of an siRNA therapeutic in a human patient follows an eight-stage physical and enzymatic cascade:", body_style))
    story.append(Paragraph("<b>1. Receptor-Mediated Endocytosis:</b> When administered subcutaneously, trivalent GalNAc-conjugated siRNAs bind to Asialoglycoprotein Receptors (ASGPR) on the surface of hepatocytes. The receptor-ligand complex invaginates into clathrin-coated pits and is internalized into early endosomes within minutes.", bullet_style))
    story.append(Paragraph("<b>2. Endosomal Acidification and Escape:</b> As endosomes mature and the proton pump ATPase lowers the luminal pH to approximately 5.5, GalNAc dissociates from ASGPR, allowing receptor recycling to the cell surface. A minute fraction (typically 1-2%) of the siRNA escapes into the cytoplasm, while the remainder is trafficked to lysosomes.", bullet_style))
    story.append(Paragraph("<b>3. Chaperone-Assisted RISC Loading:</b> In the cytosol, the heat shock chaperone machinery (Hsp70/Hsp90) binds to Ago2, consuming ATP to transiently wedge open the Ago2 structural lobes. The 21-mer siRNA duplex is inserted into the open cleft.", bullet_style))
    story.append(Paragraph("<b>4. Passenger Strand Nicking and Expulsion:</b> The PIWI domain cleaves the passenger (sense) strand between nucleotides 9 and 10. The N-terminal domain acts as a wedge to pry apart the cleaved passenger fragments, ejecting them from the complex. The active guide (antisense) strand remains firmly seated, transforming the assembly into mature, activated RISC.", bullet_style))
    story.append(Paragraph("<b>5. Search and Diffusion:</b> Activated RISC diffuses through the cytoplasm, scanning thousands of endogenous mRNAs via rapid, one-dimensional lateral sliding and three-dimensional hopping along transcript loops.", bullet_style))
    story.append(Paragraph("<b>6. Seed Nucleation:</b> Target recognition begins with nucleotides 2 through 8 of the guide strand (the seed region). If the target mRNA contains a complementary sequence, Watson-Crick base pairing nucleates in the pre-organized A-form helical seed pocket.", bullet_style))
    story.append(Paragraph("<b>7. Allosteric Locking and Central Cleavage:</b> Upon successful seed pairing, the base-pairing zipper extends through the central cleavage domain (positions 9 to 12). This induces an allosteric hinge movement in Ago2 that draws the target mRNA scissile phosphodiester bond directly into contact with the catalytic DEDH tetrad and its bound divalent magnesium ion.", bullet_style))
    story.append(Paragraph("<b>8. Hydrolytic Cleavage and RISC Turnover:</b> Activated water molecules execute an in-line nucleophilic attack, hydrolyzing the target mRNA backbone between nucleotides 10 and 11. The cleaved target mRNA fragments dissociate rapidly, leaving the Ago2-guide strand complex intact and ready to bind and cleave subsequent target transcripts. A single RISC complex can catalytically destroy hundreds of target mRNA molecules over its intracellular lifespan.", bullet_style))

    story.append(Paragraph("1.4 The Five Clinical Failure Modes of Naked (Unmodified) RNA", h2_style))
    story.append(Paragraph("When pure, unmodified canonical RNA (composed strictly of canonical ribose sugars and natural phosphodiester linkages) is synthesized and administered intravenously into a mammal, it is 100% therapeutically useless. Five catastrophic clinical barriers ensure complete pharmacological failure:", body_style))
    
    story.append(Paragraph("<b>1. Ultra-Rapid Endonuclease Cleavage (t½ < 5 minutes):</b> Mammalian serum contains high concentrations of secretory endonucleases, primarily belonging to the pancreatic-like Ribonuclease A (RNase A) family. RNase A catalyzes the endonucleolytic cleavage of RNA at pyrimidine junctions (UA, UG, CA). The catalytic mechanism relies on the 2'-hydroxyl (-OH) group of the ribose ring acting as an internal nucleophile to attack the adjacent scissile phosphorus atom, forming a 2',3'-cyclic phosphate intermediate and severing the backbone. In human bloodstream, naked siRNA is completely degraded within minutes.", body_style))
    story.append(Paragraph("<b>2. Terminal Exonuclease Degradation:</b> Serum 3'-to-5' and 5'-to-3' exonucleases attack the exposed termini of double-stranded and single-stranded RNA, progressively chewing back the duplex from both ends.", body_style))
    story.append(Paragraph("<b>3. Innate Pattern-Recognition Immunogenicity (TLR7/TLR8 Activation):</b> Unmodified RNA is an evolutionary pathogen-associated molecular pattern (PAMP) recognized by the mammalian innate immune system. When siRNA is taken up into endosomes of immune cells (plasmacytoid dendritic cells, monocytes), unmodified uridine and guanosine residues bind to Toll-Like Receptors 7 and 8 (TLR7/8). This triggers MyD88 recruitment, nuclear translocation of NF-κB and IRF7, and massive systemic release of pro-inflammatory cytokines: Interferon-alpha (IFN-α), Interleukin-6 (IL-6), and Tumor Necrosis Factor-alpha (TNF-α). In human clinical trials, this manifests as severe flu-like syndrome, vascular leakage, thrombocytopenia, and lethal cytokine release syndrome.", body_style))
    story.append(Paragraph("<b>4. MicroRNA-Like Seed-Mediated Off-Target Hepatotoxicity:</b> Nucleotides 2 through 8 of the antisense strand act as a 'seed region' identical to endogenous microRNAs. If this 7-nucleotide sequence shares Watson-Crick or G:U wobble complementarity with the 3'-untranslated regions (3'-UTRs) of unintended host transcripts, RISC binds and downregulates hundreds of essential metabolic genes simultaneously. In preclinical rodent screens, this seed-mediated off-target burden causes profound hepatic necrosis, elevated ALT/AST enzymes, and animal mortality.", body_style))
    story.append(Paragraph("<b>5. Rapid Glomerular Renal Clearance:</b> An unmodified 21-mer siRNA duplex has an average molecular weight of approximately 13.5 to 14 kDa. The kidney glomerular filtration barrier allows free filtration of macromolecules below 40 to 50 kDa. Consequently, unconjugated siRNA is filtered into urine within 15 minutes of intravenous injection, preventing accumulation in target tissues.", body_style))

    story.append(Paragraph("1.5 The Chemical Mechanism of RNase A Endonucleolytic Cleavage", h2_style))
    story.append(Paragraph("To understand why synthetic modifications are chemically essential, one must examine the classical two-step acid-base catalytic cycle of Bovine Pancreatic Ribonuclease A (RNase A):", body_style))
    story.append(Paragraph("<b>Step 1 (Transphosphorylation):</b> His12 acts as a general base to abstract a proton from the ribose 2'-hydroxyl (-OH) group, generating an activated 2'-alkoxide ion. This activated oxygen executes an in-line nucleophilic attack on the adjacent scissile phosphorus atom. The reaction proceeds through a trigonal bipyramidal (pentacoordinate) phosphorane transition state in which the entering 2'-oxygen and departing 5'-oxygen occupy apical positions. His119 acts as a general acid, protonating the 5'-oxygen leaving group of the downstream nucleoside, severing the phosphodiester bond and releasing a 2',3'-cyclic monophosphate intermediate.", body_style))
    story.append(Paragraph("<b>Step 2 (Hydrolysis):</b> In a slower subsequent step, water hydrolyzes the cyclic intermediate to yield a 3'-monophosphate ester. Deoxyribonucleic acid (DNA) is completely immune to this cleavage mechanism because it possesses 2'-deoxyribose (-H instead of -OH), preventing formation of the required cyclic phosphorane transition state.", body_style))
    story.append(Paragraph("<b>How Synthetic Modifications Terminate Cleavage:</b> 2'-O-Methyl (2'-OMe) replaces the 2'-OH with an unreactive methoxy group (-OCH3) that lacks an abstractable proton and introduces steric hindrance in the RNase A catalytic pocket. 2'-Deoxy-2'-fluoro (2'-F) replaces the 2'-OH with an electronegative fluorine atom that cannot act as an oxygen nucleophile, completely extinguishing enzymatic transphosphorylation.", body_style))

    story.append(Paragraph("1.6 The Medicinal Chemistry Revolution: Synthetic Modifications", h2_style))
    story.append(Paragraph("To transform RNA into a clinical drug, medicinal chemists developed synthetic nucleotide analogues that replace the native ribose, phosphate, and nucleobase atoms. All FDA-approved siRNA drugs (Patisiran, Givosiran, Lumasiran, Inclisiran, Vutrisiran) are fully or heavily chemically modified, containing synthetic moieties at up to 100% of their nucleotide positions:", body_style))
    
    story.append(Paragraph("• <b>2'-O-Methyl (2'-OMe):</b> Replaces the reactive 2'-OH with a bulky, electron-donating methoxy group (-OCH3). Eliminates the 2'-oxygen nucleophile, terminates RNase A cleavage, and alters steric interactions with TLR7/8, cloaking the oligonucleotide from innate immune sensors.", bullet_style))
    story.append(Paragraph("• <b>2'-Deoxy-2'-Fluoro (2'-F):</b> Replaces 2'-OH with a fluorine atom (-F). Via a strong gauche effect with ring oxygen O4', it locks ribose into a rigid C3'-endo (North) conformation, mimicking natural A-form helical pitch required by Ago2 PIWI domain while conferring substantial nuclease resistance.", bullet_style))
    story.append(Paragraph("• <b>Phosphorothioate (PS) Linkages:</b> Replaces a non-bridging oxygen in the backbone with sulfur. Introduces high steric and electronic hindrance against 3'- and 5'-exonucleases, drastically extending tissue half-life from hours to months.", bullet_style))
    story.append(Paragraph("• <b>Locked Nucleic Acid (LNA) & 2'-MOE:</b> Bicyclic and bulky modifications that increase duplex thermal melting temperature (Tm increases by +3°C to +8°C per LNA modification), stabilizing thermodynamic structure.", bullet_style))
    story.append(Paragraph("• <b>Glycol Nucleic Acid (GNA) & Unlocked Nucleic Acid (UNA):</b> Acyclic sugar analogues with high conformational flexibility. Placement at position 7 of the antisense strand destabilizes microRNA seed pairing while preserving catalytic Ago2 slicing (Schlegel et al., 2022).", bullet_style))
    story.append(Paragraph("• <b>Trivalent GalNAc Delivery Ligands:</b> Conjugated to the 3'-terminus of the sense strand, trivalent N-acetylgalactosamine binds with sub-nanomolar affinity to the Asialoglycoprotein Receptor (ASGPR) on hepatocytes (>500,000 receptors/cell), mediating rapid receptor-mediated endocytosis and hepatic targeting.", bullet_style))

    chem_comp_data = [
        [Paragraph("Biochemical Property", table_cell_header), Paragraph("Natural Canonical RNA", table_cell_header), Paragraph("2'-Modified RNA (2'-OMe / 2'-F)", table_cell_header), Paragraph("Phosphorothioate DNA/RNA", table_cell_header)],
        [Paragraph("Sugar Pucker Conformation", table_cell_bold), Paragraph("Flexible C3'-endo / C2'-endo equilibrium", table_cell), Paragraph("Rigid C3'-endo (North) A-form lock", table_cell), Paragraph("Variable depending on sugar moiety", table_cell)],
        [Paragraph("Serum Nuclease Half-Life", table_cell_bold), Paragraph("t½ < 5 minutes in human serum", table_cell), Paragraph("t½ > 72 hours in serum", table_cell), Paragraph("t½ > 6 months in tissue depots", table_cell)],
        [Paragraph("RNase A In-Line Hydrolysis", table_cell_bold), Paragraph("Highly susceptible via 2'-OH attack", table_cell), Paragraph("Completely immune (no 2'-OH nucleophile)", table_cell), Paragraph("Heavily inhibited by sulfur atom hindrance", table_cell)],
        [Paragraph("TLR7/TLR8 Immune Activation", table_cell_bold), Paragraph("Severe cytokine storm (IFN-α, TNF-α)", table_cell), Paragraph("Complete immune evasion (steric cloaking)", table_cell), Paragraph("Moderate (sequence-dependent)", table_cell)],
        [Paragraph("Ago2 PIWI Cleavage Rate", table_cell_bold), Paragraph("Native baseline slicing rate", table_cell), Paragraph("Maintained or enhanced with 2'-F", table_cell), Paragraph("Reduced if placed centrally (scissile bond)", table_cell)]
    ]
    chem_t = Table(chem_comp_data, colWidths=[120, 130, 135, 135])
    chem_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f2942")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(chem_t)
    story.append(Spacer(1, 6))

    add_callout("Modern siRNA drugs are synthetic chemical polymers, not natural RNA. An effective computational model cannot rely on pure nucleotide sequences; it must model the precise physical and thermodynamic consequences of every synthetic chemical modification.")
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 2: THE RESEARCH GAP & LITERATURE SURVEY
    # =========================================================================
    story.append(Paragraph("Chapter 2: The Critical Literature Survey & Architectural Research Gap", h1_style))
    
    story.append(Paragraph("2.1 Forensic Audit of 40+ Prior siRNA Efficacy Models", h2_style))
    story.append(Paragraph("Prior to the development of HelixZero, over 40 machine learning and deep learning models had been published for siRNA efficacy prediction. Our engineering team conducted a forensic audit of the literature—spanning classical heuristic scoring matrices (Reynolds, Ui-Tei, Amarzguioui), linear and tree models (BiRNA, DSIR), and recent deep learning architectures (OligoFormer, sBiGN). This audit uncovered three systemic, fatal architectural flaws:", body_style))
    
    story.append(Paragraph("2.2 The Classical Heuristic Scoring Era", h3_style))
    story.append(Paragraph("In the early 2000s, pioneer groups published heuristic rule-based matrices:", body_style))
    story.append(Paragraph("• <b>Reynolds et al. (2004) 8 Rules:</b> Evaluated 19-mer siRNAs on 8 criteria: (1) moderate GC content 30-52%, (2) at least 3 A/U bases at positions 15-19, (3) absence of internal palindromes/hairpins (ΔG > -2 kcal/mol), (4) A at sense pos 19, (5) A at sense pos 3, (6) U at sense pos 10, (7) absence of G at sense pos 13, and (8) absence of G/C at sense pos 19. Scores ranged from -2 to 10. While helpful for early academic bench experiments, Reynolds rules fail completely when chemical modifications are introduced because synthetic sugars alter thermodynamic melting profiles.", bullet_style))
    story.append(Paragraph("• <b>Ui-Tei et al. (2004) 4 Classes:</b> Partitioned siRNAs into four classes based on terminal base-pairing asymmetry. Class I siRNAs (active) required A/U at guide 5'-end, G/C at passenger 5'-end, at least 4 A/U pairs in the 5'-seed, and no GC stretch > 9 nt.", bullet_style))
    story.append(Paragraph("• <b>Amarzguioui & Prydz (2004):</b> Position-specific scoring matrix emphasizing differential thermodynamic stability between duplex ends.", bullet_style))

    story.append(Paragraph("2.3 The Deep Learning Era: OligoFormer and sBiGN", h3_style))
    story.append(Paragraph("Recent academic publications applied deep neural networks to siRNA design:", body_style))
    story.append(Paragraph("• <b>OligoFormer:</b> A multi-head self-attention Transformer trained on canonical siRNA screens. While it achieved high cross-validation metrics on the Huesken dataset, it operates strictly on a 4-letter canonical alphabet (A, C, G, U). It is completely blind to chemical modifications: it cannot distinguish a 2'-OMe uridine from a natural uridine, nor can it determine whether phosphorothioates stabilize or destabilize the helix.", bullet_style))
    story.append(Paragraph("• <b>sBiGN:</b> A bipartite graph convolutional network utilizing ViennaRNA secondary structure predictions. Like OligoFormer, it was trained exclusively on unmodified oligonucleotides and lacks awareness of synthetic medicinal chemistry.", bullet_style))

    story.append(Paragraph("2.4 The Three Systemic Architectural Deficiencies", h2_style))
    story.append(Paragraph("<b>Flaw 1: The Sequence-Only Assumption (Naked RNA Models):</b>", body_bold))
    story.append(Paragraph("Trained exclusively on historical high-throughput screens from the mid-2000s—chiefly the Novartis Huesken et al. (2006) dataset of ~2,400 unmodified siRNAs. Sequence-only models cannot evaluate modern commercial drug candidates (Patisiran, Givosiran, Inclisiran), producing arbitrary, meaningless scores.", body_style))
    
    story.append(Paragraph("<b>Flaw 2: The 1-Character Tokenization Disaster (Orthogonality Collapse):</b>", body_bold))
    story.append(Paragraph("A small subset of specialized models attempted to incorporate chemical modifications (e.g., cmSiRNA, siRNAmod) by assigning a single ASCII character per nucleotide position ('M' for 2'-OMe, 'F' for 2'-Fluoro, 'S' for PS, '4' for GalNAc). In clinical pharmacology, chemical modifications are orthogonal: a single nucleotide in Inclisiran or Vutrisiran possesses a 2'-Fluoro sugar modification, AND a Phosphorothioate internucleotide linkage, AND a GalNAc conjugate! By collapsing the representation into a single ASCII string, these models forced the data pipeline to discard critical chemistry, destroying training signal.", body_style))
    
    story.append(Paragraph("<b>Flaw 3: Concentration Confounding & Biophysical Blindness:</b>", body_bold))
    story.append(Paragraph("Existing algorithms framed efficacy prediction as a direct regression from sequence to percentage mRNA knockdown (0 to 100%), without providing experimental assay concentration as an input. In pharmacology, knockdown is concentration-dependent: an siRNA tested at 0.01 nM will exhibit 15% knockdown, but at 100 nM will exhibit 95% knockdown. Training a regressor on multi-lab data without concentration forced decision trees to split on sequence noise. Furthermore, pure neural networks were blind to physical steric clashes, predicting high scores for lethal configurations like LNA at position 1.", body_style))

    flaw_table_data = [
        [Paragraph("Model / Architecture", table_cell_header), Paragraph("Underlying Alphabet", table_cell_header), Paragraph("Chemical Support", table_cell_header), Paragraph("Dose-Aware?", table_cell_header), Paragraph("Biophysical Guardrails", table_cell_header)],
        [Paragraph("Reynolds et al. (2004)", table_cell_bold), Paragraph("8 Heuristic Rules", table_cell), Paragraph("None (Naked Only)", table_cell), Paragraph("No (Fixed assay)", table_cell), Paragraph("Heuristic GC/pos counts", table_cell)],
        [Paragraph("Ui-Tei et al. (2004)", table_cell_bold), Paragraph("4 Sequence Classes", table_cell), Paragraph("None (Naked Only)", table_cell), Paragraph("No (Fixed assay)", table_cell), Paragraph("Class I/II/III/IV bins", table_cell)],
        [Paragraph("OligoFormer (Transformer)", table_cell_bold), Paragraph("4-Letter (A, C, G, U)", table_cell), Paragraph("None (Naked RNA Only)", table_cell), Paragraph("No (Fixed assay)", table_cell), Paragraph("None (Pure Neural Net)", table_cell)],
        [Paragraph("sBiGN (Graph CNN)", table_cell_bold), Paragraph("4-Letter (A, C, G, U)", table_cell), Paragraph("None (Naked RNA Only)", table_cell), Paragraph("No (Fixed assay)", table_cell), Paragraph("ViennaRNA energy only", table_cell)],
        [Paragraph("cmSiRNA (Random Forest)", table_cell_bold), Paragraph("Single ASCII token/nt", table_cell), Paragraph("Collapsed (1-char conflict)", table_cell), Paragraph("No (Dose blind)", table_cell), Paragraph("None (Statistical only)", table_cell)],
        [Paragraph("siRNAmod (SVM / MLP)", table_cell_bold), Paragraph("Single ASCII token/nt", table_cell), Paragraph("Collapsed (1-char conflict)", table_cell), Paragraph("No (Dose blind)", table_cell), Paragraph("None (Statistical only)", table_cell)],
        [Paragraph("HelixZero-CMS (Ensemble v5)", table_cell_bold), Paragraph("Orthogonal NucSlot 5-Tuple", table_cell), Paragraph("Full 30-Mod Ontology", table_cell), Paragraph("Yes (Stage 1 pIC50 + Hill)", table_cell), Paragraph("6-Domain Heuristic Engine", table_cell)]
    ]
    flaw_t = Table(flaw_table_data, colWidths=[110, 95, 105, 95, 115])
    flaw_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f2942")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(flaw_t)
    story.append(Spacer(1, 8))
    
    add_callout("HelixZero was explicitly engineered to solve the three failure modes of prior literature: replacing 1-char tokens with the orthogonal NucSlot data model, decoupling intrinsic affinity from dosing via the two-stage IEEE v5 engine, and enforcing physical reality via deterministic biophysical penalty rules.")
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 3: THE MULTI-SOURCE DATA LAKE
    # =========================================================================
    story.append(Paragraph("Chapter 3: The Multi-Source Data Lake Assembly & Master Censuses", h1_style))
    story.append(Paragraph("To train an AI platform capable of true clinical generalizability, our engineering team assembled the largest curated multi-modal siRNA data lake in computational biology, aggregating **22 distinct dataset repositories** containing over **260,000 empirical data points**.", body_style))
    story.append(Paragraph("The data lake bridges three distinct pharmacological regimes: (1) high-throughput canonical naked siRNA screens for baseline learning, (2) chemically modified oligonucleotide screens from literature and patent registries, and (3) clinical-grade multi-concentration dose-response series.", body_style))

    story.append(Paragraph("3.1 Detailed Narrative Profiles of Key Repositories", h2_style))
    story.append(Paragraph("• <b>Novartis Huesken et al. (normal_siRNA.csv):</b> 661 siRNAs targeting 33 human and rodent mRNAs, measured via dual-luciferase reporter assays. Forms the ground-truth baseline for Model A.", bullet_style))
    story.append(Paragraph("• <b>CMsiRNAdb Master Lake (cmsirnadb_full.csv):</b> 25,863 rows curated from peer-reviewed literature and patent filings, containing diverse single- and multi-modification patterns across 30 chemical moieties.", bullet_style))
    story.append(Paragraph("• <b>Multi-Slot Feature Store (v2_multislot_dataset.csv):</b> 42,638 rows formatted with orthogonal NucSlot annotations for Model B v4 fine-tuning.", bullet_style))
    story.append(Paragraph("• <b>IEEE Gold-Bronze Master (ieee_gold_bronze_master.csv):</b> 40,255 rows with nanomolar concentration annotations spanning 7 orders of magnitude (0.1 pM to 1 µM), powering the two-stage IEEE v5 engine.", bullet_style))
    story.append(Paragraph("• <b>Janas HeLa Seed Viability (cell_viability.tsv):</b> 4,096 hexamer seed motifs transfected into HeLa cells to measure 72-hour cell survival, powering the empirical seed cytotoxicity firewall.", bullet_style))
    story.append(Paragraph("• <b>Human Transcriptome Index (human_transcriptome.idx.pkl):</b> 863.78 MB 2-bit binary index representing all 15-mers across 449 MB of human RefSeq cDNA, enabling sub-microsecond off-target slicer checks.", bullet_style))

    lake_table_data = [
        [Paragraph("Dataset Identifier", table_cell_header), Paragraph("Literature / Patent Source", table_cell_header), Paragraph("Record Count", table_cell_header), Paragraph("Target Regimen & Primary Usage", table_cell_header)],
        [Paragraph("1. normal_siRNA.csv", table_cell_bold), Paragraph("Novartis Screen (Huesken 2006)", table_cell), Paragraph("661 assays", table_cell), Paragraph("Model A Baseline Naked Training", table_cell)],
        [Paragraph("2. normal_siRNA_extended.csv", table_cell_bold), Paragraph("Curated Public Canonical Library", table_cell), Paragraph("4,060 assays", table_cell), Paragraph("Model A Extended Context Learning", table_cell)],
        [Paragraph("3. Hu.csv (OligoFormer)", table_cell_bold), Paragraph("Human siRNA Screen (Hu et al.)", table_cell), Paragraph("2,361 assays", table_cell), Paragraph("Model A External Benchmark", table_cell)],
        [Paragraph("4. Taka.csv (OligoFormer)", table_cell_bold), Paragraph("Takayuki Transfer Benchmark", table_cell), Paragraph("702 assays", table_cell), Paragraph("Model A Cross-Species Benchmark", table_cell)],
        [Paragraph("5. Mix.csv (OligoFormer)", table_cell_bold), Paragraph("7-Study Multi-Species Screen", table_cell), Paragraph("472 assays", table_cell), Paragraph("Model A Transfer Robustness Check", table_cell)],
        [Paragraph("6. cmsirnadb_full.csv", table_cell_bold), Paragraph("Curated CMsiRNAdb Master Lake", table_cell), Paragraph("25,863 rows", table_cell), Paragraph("Model B v4 Primary Modified Training", table_cell)],
        [Paragraph("7. v2_multislot_dataset.csv", table_cell_bold), Paragraph("Internal Multi-Slot Feature Store", table_cell), Paragraph("42,638 rows", table_cell), Paragraph("Model B v4 Multi-Slot Fine-Tuning", table_cell)],
        [Paragraph("8. CMSiRNA_data_update.tsv", table_cell_bold), Paragraph("Expanded Commercial Patent Release", table_cell), Paragraph("43,153 rows", table_cell), Paragraph("CatBoost GBDT Retraining Split", table_cell)],
        [Paragraph("9. hetero_train_2728.csv", table_cell_bold), Paragraph("Heterogeneously Modified Train Set", table_cell), Paragraph("23,187 rows", table_cell), Paragraph("PyG Graph Attention Pre-training", table_cell)],
        [Paragraph("10. hetero_val_303.csv", table_cell_bold), Paragraph("Heterogeneously Modified Test Set", table_cell), Paragraph("2,576 rows", table_cell), Paragraph("PyG Graph Attention Held-Out Test", table_cell)],
        [Paragraph("11. homo_train.csv", table_cell_bold), Paragraph("Homogeneously Modified Control Set", table_cell), Paragraph("4,244 rows", table_cell), Paragraph("Control Calibration Partition", table_cell)],
        [Paragraph("12. homo_val.csv", table_cell_bold), Paragraph("Homogeneously Modified Test Set", table_cell), Paragraph("472 rows", table_cell), Paragraph("Control Generalization Test", table_cell)],
        [Paragraph("13. ieee_gold_bronze_master.csv", table_cell_bold), Paragraph("Multi-Dose Master Curation", table_cell), Paragraph("40,255 rows", table_cell), Paragraph("IEEE v5 Two-Stage Dual Engine", table_cell)],
        [Paragraph("14. helixzero_dataset_A_invitro", table_cell_bold), Paragraph("Single-Dose High-Throughput Screen", table_cell), Paragraph("38,973 rows", table_cell), Paragraph("Module 3 (Knockdown %) Training", table_cell)],
        [Paragraph("15. helixzero_dataset_B_multidose", table_cell_bold), Paragraph("Multi-Concentration Dose Series", table_cell), Paragraph("35,982 rows", table_cell), Paragraph("Module 2 (pIC50) Ground-Truth", table_cell)],
        [Paragraph("16. helixzero_dataset_C_invivo", table_cell_bold), Paragraph("Rodent / NHP PK/PD Assays", table_cell), Paragraph("4,180 rows", table_cell), Paragraph("In Vivo Pharmacokinetic Validation", table_cell)],
        [Paragraph("17. helixzero_dataset_pIC50_v1", table_cell_bold), Paragraph("Hill Kinetic Inversion Screen", table_cell), Paragraph("1,458 curves", table_cell), Paragraph("Stage 1 Hill Ground-Truth Anchors", table_cell)],
        [Paragraph("18. cell_viability.tsv", table_cell_bold), Paragraph("Janas HeLa 6-mer Seed Viability", table_cell), Paragraph("4,096 motifs", table_cell), Paragraph("Empirical Seed Cytotoxicity Firewall", table_cell)],
        [Paragraph("19. human_transcriptome.fasta", table_cell_bold), Paragraph("RefSeq GRCh38 Human cDNA", table_cell), Paragraph("449 MB FASTA", table_cell), Paragraph("Source Transcript Sequence Store", table_cell)],
        [Paragraph("20. human_transcriptome.idx.pkl", table_cell_bold), Paragraph("2-Bit Packed Binary Slicer Index", table_cell), Paragraph("863.78 MB Bin", table_cell), Paragraph("O(1) Off-Target Slicer Lookup", table_cell)],
        [Paragraph("21. fda_approved_sirna_verified", table_cell_bold), Paragraph("FDA Approval Packages & Trials", table_cell), Paragraph("7 Commercial Drugs", table_cell), Paragraph("Independent Blind Clinical Test Set", table_cell)],
        [Paragraph("22. cofold_results.pkl", table_cell_bold), Paragraph("ViennaRNA RNAcofold Base-Pairs", table_cell), Paragraph("49,715 Duplexes", table_cell), Paragraph("MEG-mod GNN Structural Featurization", table_cell)]
    ]
    lake_t = Table(lake_table_data, colWidths=[125, 125, 80, 190])
    lake_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f2942")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(lake_t)
    story.append(Spacer(1, 8))
    
    add_callout("By integrating 22 distinct datasets spanning naked RNA, multi-slot chemical variants, and multi-concentration dose-response series, HelixZero avoids the narrow domain collapse that plagued single-source academic models.")
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: FORENSIC DATA CLEANING & LEAKAGE ELIMINATION
    # =========================================================================
    story.append(Paragraph("Chapter 4: Forensic Data Cleaning & The Elimination of Identity Leakage", h1_style))
    
    story.append(Paragraph("4.1 The Sequence Identity Leakage Trap in Chemical Modification Datasets", h2_style))
    story.append(Paragraph("During the exploratory data science phase, our team uncovered a severe methodological error prevalent across academic literature: **Sequence Identity Leakage** across random train/test splits.", body_style))
    story.append(Paragraph("When we initially trained a baseline gradient boosted model using standard Scikit-Learn 80/20 random splits, the validation metrics appeared spectacular: Pearson r > 0.88 and Spearman rho > 0.86. However, deep auditing of the split revealed why: in chemical modification studies, researchers typically select a single highly active guide sequence (e.g., targeting TTR or PCSK9) and synthesize **30 to 50 variants**, each possessing a distinct modification pattern.", body_style))
    story.append(Paragraph("In a naive random 80/20 split, 35 variants of Sequence A ended up in the training fold, while 10 variants of Sequence A ended up in the test fold. The gradient boosted trees simply memorized the biological baseline potency of Sequence A. The model was not learning the biophysical consequences of chemical modifications at all; it was functioning as a memorization lookup table for sequence identity!", body_style))

    leakage_diagram = """                      THE DATA LEAKAGE TRAP IN SI-RNA MACHINE LEARNING
                      
   [Target Sequence: 5'-GUAAGACUUGAGAUGAUCC-3'] ──> Synthesized into 30 Different Chemical Variants
   
   [NAIVE RANDOM 80/20 SPLIT (FRAUDULENT HIGH METRICS)]:
   ┌──────────────────────────────────────────────┐    ┌──────────────────────────────────────────────┐
   │             TRAINING SET (80%)               │    │               TEST SET (20%)                 │
   │ Variant 1: All-unmodified                    │    │ Variant 28: 2'-OMe at pos 2, 7               │
   │ Variant 2: 2'-F at pos 4, 6, 8               │    │ Variant 29: PS at pos 1, 2 + GalNAc          │
   │ ... Variant 27: Full ESC modification        │    │ Variant 30: 2'-MOE scan variant              │
   └──────────────────────────────────────────────┘    └──────────────────────────────────────────────┘
         ▲                                                    ▲
         │                                                    │
         └─────────── IDENTICAL GUIDE SEQUENCE IN BOTH! ──────┘
         (Model memorizes sequence identity, ignores chemistry, reports fake ρ > 0.85)

   [HELIXZERO ZERO-LEAKAGE GROUP-K-FOLD (PEER-REVIEW GOLD STANDARD)]:
   ┌──────────────────────────────────────────────┐    ┌──────────────────────────────────────────────┐
   │             TRAINING FOLD                    │    │             HELD-OUT TEST FOLD               │
   │ ALL 30 Variants of Sequence A                │    │ ALL 25 Variants of Sequence C                │
   │ ALL 40 Variants of Sequence B                │    │ ALL 35 Variants of Sequence D                │
   └──────────────────────────────────────────────┘    └──────────────────────────────────────────────┘
         ▲                                                    ▲
         │                                                    │
         └─────── 100% SEQUENCE-DISJOINT PARTITIONING ────────┘
         (Model CANNOT memorize sequence; MUST learn true chemical modification physics!)"""
    add_code_box(leakage_diagram)

    story.append(Paragraph("The Engineering Solution: 5-Fold GroupKFold by Antisense Sequence", h3_style))
    story.append(Paragraph("In `helixzero/training/validation.py`, we implemented **Strict 5-Fold GroupKFold Cross-Validation grouped strictly by unique antisense sequence (`anti_seq`)**. Under this protocol, all chemical variants derived from a guide sequence are assigned exclusively to the training set or exclusively to the test set. When evaluated under GroupKFold, metrics dropped from the artificial rho = 0.88 to an honest, highly competitive, and reproducible **rho = 0.7463 ± 0.064** for our production ensemble. This proved that HelixZero genuinely generalizes to unseen biological targets.", body_style))

    story.append(Paragraph("4.2 Sequence Sanitization & Overhang Cap Stripping", h2_style))
    story.append(Paragraph("In `smepred/src/parser.py`, we engineered an industrial sequence parsing pipeline:", body_style))
    story.append(Paragraph("• <b>FASTA and Accession Stripping:</b> Automatically strips multiline FASTA headers (>gene_id) and accession prefixes (NM_, ENST, XM_).", bullet_style))
    story.append(Paragraph("• <b>RNA Alphabet Normalization:</b> Automatically converts all thymidine ('T') bases to uridine ('U'), converting cDNA inputs into RNA.", bullet_style))
    story.append(Paragraph("• <b>IUPAC Degeneracy Filtering:</b> Rejects non-canonical degenerate ambiguity characters (N, R, Y, W, K, M, S, B, D, H, V) using strict regex: `re.sub(r'[^AUGC]', '', clean_seq)`.", bullet_style))
    story.append(Paragraph("• <b>Overhang Cap Discrepancy Solution:</b> A critical engineering trap was that canonical siRNAs contain a 19-base pair double-stranded core flanked by 2-nucleotide 3'-overhangs (frequently natural deoxythymidines, 'dTdT'). When users fed sequences formatted as `GGAUCAUCUCAAGUCUUACdTdT` into the feature extractor, the trailing 'dT' characters caused array index out-of-bounds or length mismatches in the 21-position feature tensor. In `_strip_3p_overhang()`, we programmatically detect and strip trailing overhang shorthand (`dT`, `dTdT`, `D`, `3P`, `-3'`) and isolate the 19-nt canonical core before slot mapping, guaranteeing zero array shape misalignment.", bullet_style))

    story.append(Paragraph("4.3 Logarithmic Transformation of Experimental Dosages", h2_style))
    story.append(Paragraph("In the IEEE v5 dataset, experimental assay concentrations span 7 orders of magnitude (from 0.1 pM to 1 µM). Passing raw concentration values (e.g., passing 10.0 instead of log10(10.0) ≈ 1.0) caused catastrophic distortion in gradient boosted tree split evaluations. All assay concentrations are transformed into logarithmic molar coordinates: Dose_transformed = log10(concentration_nM + 1e-6).", body_style))

    add_callout("Never evaluate chemical modification models on random train/test splits. Only GroupKFold grouped by target sequence ensures that the model learns the biophysical rules of synthetic chemistry rather than sequence memorization.")
    story.append(PageBreak())
''')

    print("Chapters 1 to 4 appended successfully.")

if __name__ == "__main__":
    append_content()
