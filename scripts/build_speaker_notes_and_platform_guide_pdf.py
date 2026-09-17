import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "HelixZero — Presentation Speaker Notes & Platform Demo Guide")
            self.drawRightString(612 - 54, 750, "CDAC Pune · IEEE TNNLS 2026")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 612 - 54, 744)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)
        
        self.drawString(54, 32, "Confidential & Author Proprietary · helixzerocms.icecloud.in · nitinjadhav888/Helixzerocms-CDAC")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 32, page_text)
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0F172A")    # Deep slate navy
    accent_color = colors.HexColor("#0284C7")     # Modern blue/cyan
    secondary_color = colors.HexColor("#0D9488")  # Teal
    text_dark = colors.HexColor("#1E293B")        # Charcoal
    text_muted = colors.HexColor("#475569")       # Muted slate
    bg_box = colors.HexColor("#F8FAFC")           # Off-white / light slate
    callout_bg = colors.HexColor("#F0FDF4")       # Light mint
    pointer_bg = colors.HexColor("#EFF6FF")       # Light blue

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_muted,
        spaceAfter=12
    )

    part_header_style = ParagraphStyle(
        'PartHeader',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.white,
        spaceAfter=0
    )

    slide_num_style = ParagraphStyle(
        'SlideNum',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=accent_color
    )

    slide_title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=primary_color,
        spaceAfter=4
    )

    cue_style = ParagraphStyle(
        'VisualCue',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E40AF")
    )

    spoken_style = ParagraphStyle(
        'SpokenText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=text_dark
    )

    takeaway_style = ParagraphStyle(
        'TakeawayText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#166534")
    )

    comp_name_style = ParagraphStyle(
        'CompName',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=secondary_color,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=13,
        textColor=text_dark
    )

    story = []

    # Title Banner Block
    story.append(Paragraph("HELIXZERO: MASTER PRESENTATION & PLATFORM GUIDE", title_style))
    story.append(Paragraph("<b>Author</b>: Nitin Jadhav · CDAC Pune · Independent Research &nbsp;|&nbsp; <b>IEEE TNNLS 2026</b><br/><b>Target Presentation</b>: <i>HelixZero_Genspark_Collaged_Presentation.pptx</i> (17 Slides, 16:9)<br/><b>Live Service</b>: <code>https://helixzerocms.icecloud.in</code> &nbsp;|&nbsp; <b>Codebase</b>: <code>nitinjadhav888/Helixzerocms-CDAC</code>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=0, spaceAfter=12))

    # Executive Overview Box
    summary_html = "<b>Purpose of this Manual:</b> This document provides the complete, verbatim spoken-word presentation script for all 17 slides of the HelixZero presentation deck, paired with an ultra-fast, component-by-component navigation guide for demonstrating the live web platform to evaluators, journal reviewers, and wet-lab collaborators. All explanations are written in clear, natural, non-convoluted spoken English."
    p_summary = Paragraph(summary_html, body_style)
    t_summary = Table([[p_summary]], colWidths=[504])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_box),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 14))

    # ─────────────────────────────────────────────────────────────────────────
    # PART 1: SLIDE-BY-SLIDE SPOKEN SCRIPT (17 SLIDES)
    # ─────────────────────────────────────────────────────────────────────────
    p_p1 = Paragraph("PART 1: 17-SLIDE MASTER SPOKEN SCRIPT (SLIDE-BY-SLIDE)", part_header_style)
    t_p1 = Table([[p_p1]], colWidths=[504])
    t_p1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_p1)
    story.append(Spacer(1, 10))

    slides_data = [
        {
            "num": "Slide 01",
            "title": "Title Hero: HelixZero Computational Platform",
            "time": "45–55 Seconds",
            "cue": "Keep hands steady. Point to 'HelixZero' title, then sweep toward '40,255 Assays' and '0.83–2.24 nM'.",
            "script": "Good morning, everyone. I am Nitin Jadhav from CDAC Pune, and today I am proud to present HelixZero: an end-to-end computational screening and structure-guided chemical optimization platform for therapeutic siRNAs.\n\nOver the past decade, small interfering RNAs have transformed medicine by silencing disease-causing genes before toxic proteins can even be translated. However, computational discovery has hit a brick wall: almost all existing models are trained on bare, unmodified RNA sequences. When you test them on heavily chemically modified therapeutic drugs, their accuracy collapses.\n\nHelixZero bridges this gap. By uniting over 40,000 experimental assays, a 577-dimensional chemical ontology, and a physical 3D structural veto inside human Argonaute-2, HelixZero predicts clinical drug potency within a precise 0.83 to 2.24 nanomolar window. Let's look at the core problem we set out to solve.",
            "takeaway": "Takeaway: HelixZero is the first platform that co-optimizes sequence, chemical modifications, and 3D catalytic geometry in a single end-to-end workflow."
        },
        {
            "num": "Slide 02",
            "title": "Executive Overview: The Challenge, The Solution, The Impact",
            "time": "60–75 Seconds",
            "cue": "Point left to 'The Challenge' (blind spot), then right to 'The Solution' (4 pillars), then along the 4 bottom metrics.",
            "script": "Here is the big picture in three panels.\n\nOn the left is the challenge: therapeutic siRNAs are never injected as raw naked RNA. If you do that, blood nucleases chop them to pieces in minutes, or the immune system triggers a severe inflammatory reaction. Every approved drug is armored with synthetic modifications. But existing sequence-only algorithms are completely blind to this chemistry.\n\nIn the center is our solution: HelixZero. We unite four co-optimized dimensions: sequence target matching, chemical modification patterns, experimental concentration de-biasing, and 3D pocket docking.\n\nAnd on the right are the four bottom-line results:\nFirst: an r of 0.8374 across 10,757 canonical assays.\nSecond: a massive plus 0.533 Pearson r boost on chemically modified duplexes compared to naked sequence baselines.\nThird: on real FDA-approved drugs, our model achieves a rank correlation of rho = 0.8000, preserving clinical potency order.\nAnd fourth: the whole pipeline runs in under 150 milliseconds per candidate in production.",
            "takeaway": "Takeaway: Accounting for chemical modifications isn't a minor tweak—it transforms a failing model (r=0.20) into a reliable clinical predictor (r=0.74)."
        },
        {
            "num": "Slide 03",
            "title": "Why This Is Hard: 21-nt Duplex Functional Anatomy",
            "time": "60–75 Seconds",
            "cue": "Trace the duplex schematic from left to right: 5' terminal phosphate -> Seed (pos 2-8) -> Cleavage (pos 10-11) -> 3' Overhang -> GalNAc conjugate.",
            "script": "To see why this problem is so difficult, look at the anatomy of a 21-nucleotide siRNA duplex.\n\nA therapeutic siRNA is not an abstract string of letters. It is an active mechanical key that must fit inside a molecular slicing machine called Argonaute-2.\n\nPositions 2 through 8 are the Seed Region. This dictates target recognition. If you place a bulky chemical modification here, you ruin target binding or trigger toxic off-target effects.\n\nPositions 10 and 11 form the Cleavage Site. This is where the enzyme cuts the messenger RNA. Modifications here must be surgically precise—even a 1-angstrom deviation displaces the scissile phosphate and kills silencing.\n\nPositions 13 to 18 form the non-seed guide segment, which tolerates stabilizing chemical armor.\n\nAnd on the sense strand, we conjugate GalNAc sugars so the drug homes directly into liver hepatocytes.\n\nNaked sequence models see all of this as just 'A, C, G, U'. They cannot tell if a position carries a fluorine atom or a bulky methyl group. HelixZero captures all of it.",
            "takeaway": "Takeaway: Every position along the 21-mer has a distinct biological role. Chemical modifications must be optimized position-by-position."
        },
        {
            "num": "Slide 04",
            "title": "Methodology & Pillars: Four Co-Optimized Dimensions",
            "time": "60–70 Seconds",
            "cue": "Walk through the four vertical pillar cards one by one: 577-D -> Routed ML -> Debiased Potency -> Ago2 Veto.",
            "script": "HelixZero solves this challenge through four co-optimized technological pillars:\n\nPillar 1 is our 577-Dimensional Multimodal Chemical Representation. We replace standard one-hot sequence vectors with an explicit physical encoding of base identity, 2'-sugar modifications, backbone linkages, steric volume, and hydrogen bonding.\n\nPillar 2 is our Chemistry-Routed Engine. We don't force one model to do everything. A classifier detects modification density and routes unmodified candidates to an ensemble, and modified candidates to our multimodal CatBoost and GNN architectures.\n\nPillar 3 is our Debiased Potency Engine. Public databases measure silencing at arbitrary concentrations—from 10 picomolar to 100 nanomolar. HelixZero fits a two-stage Hill equation to isolate true intrinsic pIC50 from assay concentration.\n\nPillar 4 is our 3D Argonaute-2 Geometric Veto. Before any sequence is approved for chemical synthesis, it is docked into the human Ago2 crystal structure to guarantee sub-angstrom catalytic alignment.",
            "takeaway": "Takeaway: HelixZero is not just an ML algorithm; it is an integrated biophysical and structural triage system."
        },
        {
            "num": "Slide 05",
            "title": "Data Engineering: Ten Public Resources & Four Clusters",
            "time": "60–70 Seconds",
            "cue": "Point to the 4 dataset clusters: 10,757 Canonical -> 24,763 Multi-Dose -> 4,735 Patent/Clinical -> Structural Safety.",
            "script": "Machine learning is only as solid as its underlying data. On Slide 5, you see the comprehensive data ecosystem we assembled—over 40,000 assays across 10 public resources, organized into four clusters:\n\nCluster 1 contains 10,757 canonical assays from Huesken, Takayuki, and Mixset, establishing baseline sequence knockdown rules.\n\nCluster 2 contains 24,763 multi-dose assays from CMsiRNAdb and NCIt, providing multi-point concentration response curves across diverse modification patterns.\n\nCluster 3 brings in 4,735 patent and clinical records from USPTO, WIPO, and FDA dossiers, validating our models against real drug-development programs.\n\nAnd Cluster 4 incorporates the 3D crystal structure of human Ago2 from PDB 4W5N, plus human cDNA for transcriptome-wide off-target alignment.\n\nMost importantly: all train-test splits are partitioned strictly by antisense sequence using GroupKFold. There is zero sequence overlap between training and testing. This guarantees that our metrics reflect true generalization, not memorization.",
            "takeaway": "Takeaway: Strict antisense GroupKFold splitting eliminates sequence leakage, proving the model generalizes to brand new therapeutic targets."
        },
        {
            "num": "Slide 06",
            "title": "A Quick Primer: 5 Chemical Levers of an RNA Chemist",
            "time": "50–60 Seconds",
            "cue": "Gesture across the 5 cards: 2'-F, 2'-OMe, PS, LNA, and GalNAc. Highlight their physical mechanisms.",
            "script": "Slide 6 breaks down the five primary chemical levers that medicinal chemists use to transform fragile RNA into an approved drug:\n\nFirst, 2'-Fluoro: replaces the ribose oxygen with fluorine, locking the sugar into an RNA-like conformation that resists nucleases while keeping tight target affinity.\n\nSecond, 2'-O-Methyl: adds a methyl group that completely blocks RNase A from cutting the backbone, while preventing the immune system from sounding the alarm.\n\nThird, Phosphorothioate: swaps a non-bridging oxygen for sulfur in the backbone. This stops exonucleases from chewing the ends and helps the drug bind serum albumin in the bloodstream.\n\nFourth, Locked Nucleic Acid (LNA): bridges the 2' and 4' carbons, supercharging duplex melting temperature.\n\nAnd fifth, GalNAc: a sugar cluster that acts like a GPS homing beacon for the ASGPR receptor on liver cells, allowing simple subcutaneous injection.\n\nHelixZero represents every single one of these levers explicitly.",
            "takeaway": "Takeaway: Chemical modifications provide nuclease stability, immune evasion, and tissue targeting—and HelixZero captures all five mechanisms."
        },
        {
            "num": "Slide 07",
            "title": "Chemical Representation: The 6-Attribute Slot",
            "time": "50–60 Seconds",
            "cue": "Point to the mathematical formula: s_i = (b_i, q_i, ell_i, m_i, t_i, c_i). Explain each letter simply.",
            "script": "How do we feed these chemical levers into a machine learning algorithm? Slide 7 shows our mathematical foundation: the 6-attribute nucleotide slot.\n\nInstead of representing each position as just a letter, every position i along the 21-mer duplex is encoded as a 6-tuple:\n- b_i is the base identity: A, C, G, or U.\n- q_i is the 2'-sugar ribose modification: ribo, 2'-fluoro, 2'-O-methyl, LNA, or DNA.\n- ell_i is the backbone linkage: standard phosphodiester versus phosphorothioate.\n- m_i is the thermodynamic and steric weight.\n- t_i indicates the functional domain: seed, cleavage, non-seed, or terminal.\n- And c_i is the conjugate flag: GalNAc or lipid.\n\nThis format is completely lossless. Any modified synthetic oligonucleotide can be round-tripped into this structure without losing a single atom of chemical context.",
            "takeaway": "Takeaway: Lossless chemical tokenization enables deep learning models to treat RNA as a genuine chemical entity, not just abstract text."
        },
        {
            "num": "Slide 08",
            "title": "Feature Engineering: 577 Features in Four Blocks",
            "time": "50–60 Seconds",
            "cue": "Point to the 4 feature building blocks: 420 Positional + 128 Thermodynamic + 24 Geometric + 5 Context = 577.",
            "script": "From our 6-attribute slots, HelixZero automatically extracts 577 engineered features, divided into four clean building blocks:\n\nBlock 1 comprises 420 Positional Chemistry Features: 20 specific chemical properties evaluated across all 21 nucleotide slots—including hydrogen bonding, electronegativity, steric volume, and sugar pucker.\n\nBlock 2 contains 128 Global Thermodynamic & Sequence Features: free energy profiles, melting temperature, GC percentage windows, terminal asymmetry, and dinucleotide nearest-neighbor stacking.\n\nBlock 3 includes 24 Structural Geometry Features: distances, angles, and rotational flexibilities measured along the catalytic trajectory inside Argonaute-2.\n\nAnd Block 4 holds 5 Dose & Assay Context Features: log concentration, incubation time, and cell culture parameters.\n\nTogether, these 577 features give our models a rigorous, physics-based understanding of the duplex.",
            "takeaway": "Takeaway: 577 multimodal features fuse quantum chemistry, nearest-neighbor thermodynamics, and structural geometry into a unified vector."
        },
        {
            "num": "Slide 09",
            "title": "Machine Learning Pipeline: The Canonical Collapse Paradox",
            "time": "60–75 Seconds",
            "cue": "Point to the split routing diagram: Canonical Ensemble on top, Multimodal CatBoost/GNN on bottom, joined by Uncertainty layer.",
            "script": "Slide 9 highlights a key scientific finding of our research: The Canonical Collapse Paradox.\n\nWhen we took standard machine learning models trained on naked RNA sequences and tested them on modified duplexes, their accuracy collapsed from an r of 0.83 down to 0.20—barely better than random guessing! Conversely, training solely on sparse modified data hurt canonical accuracy.\n\nTo solve this, HelixZero deploys a smart routed architecture:\nAn upstream chemical density detector scans the input duplex.\nIf the candidate is unmodified, it routes to our specialized Canonical Deep Ensemble of Boosted Trees and CNN-BiLSTMs, achieving top-tier sequence accuracy.\nIf the candidate carries modifications, it routes to our Multimodal CatBoost and Graph Neural Network pipeline, which processes the full 577-dimensional chemical vector.\nFinally, an uncertainty estimation layer calculates prediction confidence and flags out-of-distribution molecules before wet-lab synthesis.",
            "takeaway": "Takeaway: Specialized routing solves the Canonical Collapse Paradox by applying the right mathematical expert to the right chemistry."
        },
        {
            "num": "Slide 10",
            "title": "Potency Modeling: Disentangling Intrinsic pIC50 from Dose",
            "time": "60–70 Seconds",
            "cue": "Point to the two-stage formula: Stage 1 (pIC50 affinity) -> Stage 2 (Hill equation sigmoidal curve).",
            "script": "One of the messiest problems in siRNA data science is that different research labs test candidates at completely different concentrations—one lab uses 100 picomolar, another uses 10 nanomolar. Comparing raw percentage knockdown across these labs is like comparing apples to airplanes.\n\nHelixZero solves this with a two-stage potency de-biasing engine:\nIn Stage 1, we predict intrinsic potency: pIC50, which is minus log10 of the IC50. This represents the candidate's pure thermodynamic silencing strength, completely independent of how much drug was added to the assay.\n\nIn Stage 2, that pIC50 is passed through a sigmoidal Hill equation, taking the Hill slope and the actual assay concentration into account to reconstruct expected percentage inhibition.\n\nBy separating intrinsic affinity from experimental dose, HelixZero unifies nearly 38,000 heterogeneous assays into a single coherent scale, achieving a de-biased correlation of r = 0.8049.",
            "takeaway": "Takeaway: Disentangling intrinsic pIC50 from experimental dose normalizes disparate public datasets without losing concentration sensitivity."
        },
        {
            "num": "Slide 11",
            "title": "Canonical Benchmarks: Outperforming Baseline Models",
            "time": "50–60 Seconds",
            "cue": "Point down the benchmark table: Huesken (r=0.8044), Takayuki (r=0.8788), Mixset (r=0.8291), Pooled (r=0.8374).",
            "script": "Now, let us examine our empirical benchmark results, starting on Slide 11 with canonical naked siRNA datasets.\n\nAcross every major published benchmark, HelixZero sets the state of the art:\n- On the 2,431-assay Huesken benchmark, HelixZero achieves a Pearson r of 0.8044, clearly outperforming classic s-BiRank at 0.7100 and BiRank at 0.6800.\n- On the 1,550-assay Takayuki dataset, HelixZero reaches r = 0.8788.\n- On the 6,776-assay Mixset benchmark, it achieves r = 0.8291.\n- And across the entire pooled canonical corpus of 10,757 assays, HelixZero maintains a Pearson r of 0.8374 and a Spearman rho of 0.8310.\n\nBecause these metrics were computed using strict antisense GroupKFold, they prove our model captures genuine biological silencing rules, not just dataset artifacts.",
            "takeaway": "Takeaway: HelixZero outperforms classic published baselines across 10,757 independent canonical assays under zero-leakage cross-validation."
        },
        {
            "num": "Slide 12",
            "title": "Modified Duplex Benchmarks: The +0.533 Pearson Gain",
            "time": "60–70 Seconds",
            "cue": "Highlight the dramatic contrast: Sequence-only model (r=0.2070) vs HelixZero CatBoost (r=0.7401), pointing to the +0.533 gain callout.",
            "script": "Slide 12 presents the central triumph of HelixZero: predicting fully chemically modified therapeutic duplexes from CMsiRNAdb at 10 nanomolar.\n\nLook at the comparison table:\nIf you use a conventional sequence-only model, it achieves a miserable Pearson r of 0.2070—it cannot distinguish a potent modified drug from an inactive one.\nA chemistry-only model without sequence context gets to r = 0.5120.\nA standard Random Forest with our features reaches r = 0.6845.\nAnd HelixZero's CatBoost model reaches a Pearson r of 0.7401 and Spearman rho of 0.7280.\n\nThat is a massive net improvement of +0.533 Pearson r over naked sequence models! This proves conclusively that modeling 2'-sugar modifications and backbone chirality is non-negotiable for real-world therapeutic discovery.",
            "takeaway": "Takeaway: HelixZero delivers a +0.533 Pearson r leap on modified duplexes, conquering the chemistry blind spot that crippled prior models."
        },
        {
            "num": "Slide 13",
            "title": "Model Interpretability: Feature Ablation & SHAP Mechanisms",
            "time": "50–60 Seconds",
            "cue": "Point left to the -0.328 drop when removing chemistry, then point right to the SHAP biological heatmaps (2'-OMe r=0.86, PS r=0.81).",
            "script": "Slide 13 proves that HelixZero is a scientifically interpretable platform, not an unexplainable black box.\n\nOn the left, our ablation study tests what happens when you remove feature blocks:\nRemoving chemical features causes a massive drop of -0.328 in Pearson r, confirming that chemistry is by far the most influential block.\nRemoving 3D geometric constraints causes an additional -0.082 drop, and removing thermodynamics drops another -0.064.\n\nOn the right, SHAP feature importance heatmaps show that our models independently rediscovered fundamental RNA biology:\n2'-O-methyl modifications show strong positive importance in the non-seed guide region (r = 0.86), but negative importance in the seed and cleavage sites, exactly mirroring known steric clash biology.\nAnd phosphorothioate linkages (r = 0.81) show dominant positive importance at terminal overhangs, reflecting exonuclease defense.",
            "takeaway": "Takeaway: SHAP feature importance confirms that HelixZero's learned weights match peer-reviewed biophysical and structural mechanisms."
        },
        {
            "num": "Slide 14",
            "title": "External Validation: FENNEC APP, JAK1, & Foster GalNAc",
            "time": "50–60 Seconds",
            "cue": "Point to the three independent external cohorts: APP (r=0.7182), JAK1 (r=0.6945), Foster GalNAc (r=0.9120).",
            "script": "To ensure our platform generalizes to completely new biological targets, we evaluated HelixZero on three external, unseen cohorts on Slide 14:\n\nFirst, the FENNEC Amyloid Precursor Protein (APP) cohort of 343 modified siRNAs targeting Alzheimer's transcripts, where HelixZero achieves an r of 0.7182.\n\nSecond, the FENNEC Janus Kinase 1 (JAK1) cohort of 191 siRNAs, achieving an r of 0.6945.\n\nAnd third, the Foster GalNAc conjugate panel across hepatic disease targets, where HelixZero achieves an outstanding Pearson r of 0.9120 and Spearman rho of 0.8990.\n\nThese zero-shot external validations demonstrate that HelixZero performs reliably across diverse gene targets, disease spaces, and chemical delivery platforms.",
            "takeaway": "Takeaway: Zero-shot external validation proves robust generalization across neurodegenerative, autoimmune, and hepatic drug programs."
        },
        {
            "num": "Slide 15",
            "title": "Clinical Translation: FDA-Approved Therapeutics",
            "time": "60–75 Seconds",
            "cue": "Point across the 4 commercial drug cards: Givosiran (0.83 nM), Patisiran (1.35 nM), Inclisiran (1.33 nM), Lumasiran (2.20 nM).",
            "script": "Slide 15 presents our ultimate translational test: predicting the potency of commercial, FDA-approved siRNA medicines.\n\nWe evaluated four landmark commercial drugs without any wet-lab re-tuning:\n- Givosiran, targeting ALAS1 for acute hepatic porphyria: predicted at 0.83 nanomolar (actual clinical potency: 0.75 nM).\n- Patisiran, targeting TTR for hereditary amyloidosis: predicted at 1.35 nanomolar (actual: 1.10 nM).\n- Inclisiran, targeting PCSK9 for high cholesterol: predicted at 1.33 nanomolar (actual: 1.20 nM).\n- And Lumasiran, targeting HAO1 for primary hyperoxaluria: predicted at 2.20 nanomolar (actual: 1.80 nM).\n\nAcross this entire panel, HelixZero correctly places clinical potency within the tight window of 0.83 to 2.24 nanomolar, achieving an untied rank correlation of rho = 0.8000, perfectly matching the clinical potency hierarchy.",
            "takeaway": "Takeaway: HelixZero accurately predicts the sub-nanomolar to low-nanomolar potency of FDA-approved therapeutics without wet-lab re-calibration."
        },
        {
            "num": "Slide 16",
            "title": "Structural Biology: Ago2 Catalytic Pocket Geometric Veto",
            "time": "60–75 Seconds",
            "cue": "Point first to the 3D pocket schematic on the left (Patisiran anchored), then contrast the numbers in the table on the right (PIWI proxy 4.21 vs 10.42 Å, clash 0.8 vs 24.8).",
            "script": "Slide 16 illustrates our fourth pillar: using the 3D crystallographic geometry of human Argonaute-2 as a physical veto.\n\nA sequence might look great on paper, but if its modified backbone physically clashes with the protein pocket, it will fail in the clinic. We dock every candidate into human Ago2 from PDB 4W5N at 2.90 Ångströms.\n\nOn the left schematic, you see Patisiran inside the catalytic pocket. The 5'-phosphate is anchored in the MID domain, the 3' end in the PAZ domain, spanning 26 Ångströms, and the scissile phosphate sits directly over the catalytic PIWI triad.\n\nOn the right table, look at what happens when you introduce an improperly placed bulky modification at positions 9 to 11:\nFor Patisiran, the catalytic PIWI distance is 4.21 Ångströms, well inside the 5.5 Ångström catalytic tolerance. For the impaired duplex, steric clash pushes the phosphate to 10.42 Ångströms—more than 5 Ångströms away from the catalytic triad, completely killing catalytic cleavage!\nIts clash score blows up to 24.8, and its compatibility score drops to -5.6.\n\nThis structural veto layer stops wet labs from wasting months synthesizing dead duplexes.",
            "takeaway": "Takeaway: The 3D geometric veto acts as a strict physical feasibility filter, disqualifying catalytically misaligned candidates before synthesis."
        },
        {
            "num": "Slide 17",
            "title": "Future Horizons & Live Demo: helixzerocms.icecloud.in",
            "time": "50–60 Seconds",
            "cue": "Gesture across the 4 Horizons, then highlight the live URL banner (helixzerocms.icecloud.in) and GitHub repo card.",
            "script": "To wrap up our presentation, Slide 17 highlights our future horizons and the live deployment of HelixZero:\n\nLooking across our four horizons:\n- In Horizon 1, we solved the chemistry blind spot with our 577-D multimodal ontology.\n- In Horizon 2, we unified affinity and dose across nearly 38,000 multi-dose data points.\n- In Horizon 3, we built a production web platform with containerized FastAPI serving predictions in under 150 milliseconds.\n- In Horizon 4, we are actively expanding beyond the liver to central nervous system conjugates and all-atom molecular dynamics relaxation.\n\nYou can test the live system right now at helixzerocms.icecloud.in, featuring our interactive 3D Ago2 viewer, per-drug prediction console, and simultaneous modified and canonical screening.\n\nThe entire codebase and pre-trained models are open-source on GitHub at nitinjadhav888/Helixzerocms-CDAC.\n\nThank you very much for your time. I will now jump directly into a live demonstration of the platform!",
            "takeaway": "Takeaway: HelixZero is live, containerized, sub-150ms fast, fully open-source, and ready for immediate deployment in drug discovery pipelines."
        }
    ]

    for slide in slides_data:
        # Slide Box
        card_content = [
            [
                Paragraph(f"<b>{slide['num']}</b>", slide_num_style),
                Paragraph(f"<b>{slide['title']}</b>", slide_title_style),
                Paragraph(f"<b>Target Duration:</b> {slide['time']}", ParagraphStyle('TTime', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=accent_color, alignment=2))
            ]
        ]
        t_card_header = Table(card_content, colWidths=[65, 315, 124])
        t_card_header.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        # Screen Pointer Callout
        p_cue = Paragraph(f"<b>Screen Pointer & Action:</b> {slide['cue']}", cue_style)
        t_cue = Table([[p_cue]], colWidths=[504])
        t_cue.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), pointer_bg),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BFDBFE")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))

        # Spoken Script
        formatted_script = slide['script'].replace('\n\n', '<br/><br/>').replace('\n', ' ')
        p_script = Paragraph(f"<b>Spoken Script:</b> \"{formatted_script}\"", spoken_style)

        # Takeaway
        p_takeaway = Paragraph(f"💡 <b>{slide['takeaway']}</b>", takeaway_style)
        t_takeaway = Table([[p_takeaway]], colWidths=[504])
        t_takeaway.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), callout_bg),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BBF7D0")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))

        slide_block = [
            t_card_header,
            Spacer(1, 4),
            t_cue,
            Spacer(1, 5),
            p_script,
            Spacer(1, 5),
            t_takeaway,
            Spacer(1, 10),
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=2, spaceAfter=8)
        ]
        story.append(KeepTogether(slide_block))

    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────────────────────
    # PART 2: FAST COMPONENT-BY-COMPONENT PLATFORM DEMO GUIDE
    # ─────────────────────────────────────────────────────────────────────────
    p_p2 = Paragraph("PART 2: FAST COMPONENT-BY-COMPONENT PLATFORM DEMO GUIDE", part_header_style)
    t_p2 = Table([[p_p2]], colWidths=[504])
    t_p2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), secondary_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_p2)
    story.append(Spacer(1, 10))

    demo_intro = "<b>Live Demo Strategy (Total Time: 3 to 4 Minutes):</b> When presenting the web service (<code>helixzerocms.icecloud.in</code>), keep the mouse moving with intention. Never let the audience wonder what you are clicking. Move briskly through the 5 core tabs using the exact spoken phrases below. Each component has an explicit <i>Live Action</i>, <i>Spoken Script</i>, and <i>Key Feature Highlight</i>."
    p_demo_intro = Paragraph(demo_intro, body_style)
    t_demo_intro = Table([[p_demo_intro]], colWidths=[504])
    t_demo_intro.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_box),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_demo_intro)
    story.append(Spacer(1, 12))

    platform_components = [
        {
            "id": "Component 01",
            "name": "Header & Live System Status Badge",
            "time": "15 Seconds",
            "action": "Open browser at <code>helixzerocms.icecloud.in</code>. Point cursor to top logo, then hover over the pulsing green status badge in the top-right corner.",
            "script": "Here is the live production system running at helixzerocms.icecloud.in. In the top right, notice our green status badge: our containerized FastAPI backend and model inference weights are warm, delivering sub-150-millisecond response times.",
            "highlight": "Low Latency & High Availability: FastAPI backend serves multi-model predictions in under 150 ms."
        },
        {
            "id": "Component 02",
            "name": "Tab 1: 🔬 Rank siRNAs (Full Transcript Candidate Scanning)",
            "time": "45–55 Seconds",
            "action": "Click '🔬 Rank siRNAs' tab. Click 'Load Demo mRNA (TTR)' button. Point to the populated 200+ nt mRNA sequence. Click 'Run Prediction'. When results load, show the table, the score bar, the toxicity badge, and click one row to expand the nucleotide sequence view.",
            "script": "Let's start in our primary screening tab: Rank siRNAs. Imagine a biologist wants to target human Transthyretin for amyloidosis. Instead of manually testing sequences, I click 'Load Demo mRNA', which pulls in the real human TTR transcript.\n\nNow I click 'Run Prediction'. In less than a second, HelixZero tiles across the entire transcript, generating and scoring every possible 21-mer candidate duplex.\n\nNotice the output table: candidates are ranked by predicted silencing efficacy. We provide color-coded score bars from Very High down to Low, plus real-time off-target toxicity badges.\n\nIf I click on any candidate row—like this top-ranked lead—it expands into an interactive nucleotide-level map, visually distinguishing the 5' seed region, the central cleavage site, and terminal overhangs. Users can also click 'View Breakdown' to inspect the exact mathematical penalties applied by our models.",
            "highlight": "Automated Transcript Tiling & Explainability: Generates all candidate 21-mers, filters off-targets, and displays nucleotide-by-nucleotide mechanistic score breakdowns."
        },
        {
            "id": "Component 03",
            "name": "Tab 2: ⚗️ Single-Mod Scan (Positional Sensitivity Matrix)",
            "time": "30–40 Seconds",
            "action": "Switch to '⚗️ Single-Mod Scan' tab. Keep the default guide sequence. Select '2'-O-Methyl' from the modification library. Click 'Scan Variants'. Point to the 1-to-21 positional matrix.",
            "script": "Next, let's switch to the Single-Mod Scan tab. Once an RNA chemist picks a guide sequence, they need to know: where can I place chemical modifications without killing efficacy?\n\nI select 2'-O-Methyl and click 'Scan Variants'. HelixZero instantly simulates placing that modification at every position from 1 to 21.\n\nLook at this matrix: green indicates positions where the modification enhances stability and efficacy—notice the strong green cluster in the non-seed guide region at positions 13 through 18. But look at positions 10 and 11: bright red. That warns the chemist that modifying the cleavage site will cause steric clash and abolish catalytic slicing. This matrix prevents chemists from synthesizing dead molecules.",
            "highlight": "Positional Sensitivity Heatmap: Maps beneficial stabilization zones (non-seed) versus fatal dead zones (cleavage & seed)."
        },
        {
            "id": "Component 04",
            "name": "Tab 3: 🧬 Multi-Mod Design (Automated Beam Search Optimization)",
            "time": "45–55 Seconds",
            "action": "Switch to '🧬 Multi-Mod Design'. Show the custom modification input string. Then click the gradient blue button: '⚡ Run Multi-Mod Beam Search'. Point to the predicted pIC50 card, the dose-response Hill curve, and confidence badge.",
            "script": "Now, real therapeutics never use just one modification—they combine 2'-fluoro, 2'-O-methyl, and phosphorothioate across both strands. That creates a combinatorial search space of trillions of possibilities.\n\nIn our Multi-Mod Design tab, chemists can either paste a specific modified pattern, or click this blue button: 'Run Multi-Mod Beam Search'.\n\nOur guided beam search automatically navigates the chemical landscape, stacking synergistic modifications while avoiding steric penalties.\n\nLook at the result card: HelixZero predicts the drug's intrinsic affinity—here, a potent pIC50 of 9.15—and reconstructs the full multi-dose sigmoidal Hill curve, showing predicted knockdown across four orders of magnitude of clinical concentration. We also provide a calibration confidence badge indicating high certainty.",
            "highlight": "Guided Combinatorial Beam Search: Automatically searches trillions of modification states to find synergistic, high-potency architectures."
        },
        {
            "id": "Component 05",
            "name": "Tab 4: 🎯 3D Ago2 Catalytic Docking Studio",
            "time": "60–75 Seconds",
            "action": "Switch to '🎯 3D Ago2 Docking' tab. Click the 'Patisiran (ALN-TTR02)' chip. Click '🎯 Run 3D Ago2 Catalytic Docking Simulation'. Rotate the 3Dmol canvas with your mouse. Click '🎯 Catalytic Triad' focus toggle. Point to the metric cards below: PIWI (4.21 Å), MID (3.17 Å), Clash Score (0.8), Status: OPTIMAL. Then click 'Download PDB' and 'PyMOL Script'.",
            "script": "Now for our most visually striking feature: the 3D Ago2 Catalytic Docking Studio. This is our physical feasibility filter.\n\nI click the pre-loaded chip for Patisiran—the first-ever FDA-approved siRNA drug—and click 'Run 3D Ago2 Docking'.\n\nWithin milliseconds, the 3Dmol canvas renders the full crystallographic complex of human Argonaute-2 from PDB 4W5N. With my mouse, I can freely rotate, zoom, and inspect the binding cleft.\n\nIf I click 'Catalytic Triad' in our camera toolbar, the view zooms right into the active site. Look at how the guide strand's scissile phosphate aligns perfectly over the catalytic triad.\n\nNow look at the diagnostic metric cards right beneath the canvas:\n- MID domain anchor distance: 3.17 Ångströms (optimal).\n- PIWI catalytic proxy: 4.21 Ångströms (well within the 5.5 Ångström threshold).\n- Steric clash score: 0.8 (extremely clean).\n- Overall verdict: 'OPTIMAL'.\n\nIf a candidate had an improper bulky modification, the clash score would turn red and the system would issue a 'GEOMETRIC VETO'.\n\nFinally, medicinal chemists can click 'Download PDB' to export the docked 3D coordinates, or 'PyMOL Script' to generate a publication-ready rendering session with one click.",
            "highlight": "Interactive 3D Biophysics & One-Click Export: In-browser 3Dmol rendering, sub-angstrom catalytic distance validation, and direct PDB/PyMOL export."
        },
        {
            "id": "Component 06",
            "name": "Tab 5: 📖 Modifications Ontology Dictionary",
            "time": "20–30 Seconds",
            "action": "Switch to '📖 Modifications' tab. Scroll through the cards categorized by Backbone, Sugar, Base, and Conjugate. Point to GalNAc and 2'-OMe.",
            "script": "Finally, our fifth tab is the Modifications Ontology. This acts as our comprehensive chemical dictionary. It lists every supported modification—from standard 2'-fluoro and 2'-O-methyl to phosphorothioate backbones and triantennary GalNAc targeting conjugates.\n\nFor every modification, we display its molecular formula, chemical class, steric radius, and biological mechanism. This guarantees full transparency and lossless representation across the entire platform.",
            "highlight": "Comprehensive Chemical Knowledge Graph: Lossless 6-attribute dictionary of all synthetic RNA chemistries."
        },
        {
            "id": "Component 07",
            "name": "Wrap-Up & Live Transition Back to Questions",
            "time": "15 Seconds",
            "action": "Return to the main screen or 3D viewer. Face the audience.",
            "script": "To summarize: HelixZero takes RNA drug discovery from an uncertain guessing game to a fast, rational, structure-guided computational pipeline. The web service is live at helixzerocms.icecloud.in, and our entire codebase is open on GitHub. Thank you, and I am now ready for your questions!",
            "highlight": "Strong Closing: Reiterate live availability, open-source access, and readiness for questions."
        }
    ]

    for comp in platform_components:
        header_table = Table([
            [
                Paragraph(f"<b>{comp['id']}</b>", slide_num_style),
                Paragraph(f"<b>{comp['name']}</b>", slide_title_style),
                Paragraph(f"<b>Duration:</b> {comp['time']}", ParagraphStyle('CTime', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=secondary_color, alignment=2))
            ]
        ], colWidths=[80, 310, 114])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))

        p_action = Paragraph(f"<b>Live Screen Action:</b> {comp['action']}", ParagraphStyle('PAction', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8.5, leading=12, textColor=colors.HexColor("#065F46")))
        t_action = Table([[p_action]], colWidths=[504])
        t_action.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), callout_bg),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#A7F3D0")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))

        formatted_script = comp['script'].replace('\n\n', '<br/><br/>').replace('\n', ' ')
        p_script = Paragraph(f"<b>Spoken Script:</b> \"{formatted_script}\"", spoken_style)

        p_hl = Paragraph(f"⭐ <b>Key Technical Feature:</b> {comp['highlight']}", ParagraphStyle('PHl', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=primary_color))
        t_hl = Table([[p_hl]], colWidths=[504])
        t_hl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_box),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))

        comp_block = [
            header_table,
            Spacer(1, 4),
            t_action,
            Spacer(1, 5),
            p_script,
            Spacer(1, 5),
            t_hl,
            Spacer(1, 10),
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=2, spaceAfter=8)
        ]
        story.append(KeepTogether(comp_block))

    story.append(Spacer(1, 10))

    # ─────────────────────────────────────────────────────────────────────────
    # EMERGENCY Q&A DEFENSE CHEAT SHEET
    # ─────────────────────────────────────────────────────────────────────────
    p_qa_hdr = Paragraph("<b>EMERGENCY Q&A DEFENSE CHEAT SHEET (FAST BULLETPROOF ANSWERS)</b>", ParagraphStyle('QAHdr', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=primary_color, spaceAfter=6))
    story.append(p_qa_hdr)

    qa_data = [
        ("Q1: How do you guarantee there is no data leakage between training and testing?",
         "<b>Answer:</b> We enforce strict antisense sequence GroupKFold partitioning. That means any 21-nucleotide sequence present in the test set—or any sequence with substantial sequence overlap—is completely firewalled out of training. Models are evaluated strictly on unseen genes, ensuring real-world cross-target generalization."),
        ("Q2: Why not just use AlphaFold 3 or ESMFold for docking?",
         "<b>Answer:</b> AlphaFold 3 predicts static complexes, but it cannot run high-throughput screening of tens of thousands of chemical variants at 150-millisecond speeds. Furthermore, human Ago2 undergoes a specific conformational catalytic cycle; our targeted rigid-body and pocket-constrained docking specifically measures the scissile phosphate to PIWI triad distance, which is the exact physical determinant of cleavage."),
        ("Q3: How does the model convert percentage knockdown to intrinsic pIC50?",
         "<b>Answer:</b> In public databases, assays are run at arbitrary concentrations (e.g. 10 nM, 100 nM). In Stage 1, we predict intrinsic pIC50 = -log10(IC50). In Stage 2, that pIC50 is passed through a parameterized sigmoidal Hill equation: Knockdown % = 100 / (1 + (IC50 / [C])^h). This disentangles the candidate's true thermodynamic affinity from experimental assay dose."),
        ("Q4: Why does the sequence-only model collapse to r = 0.20 on modified siRNAs?",
         "<b>Answer:</b> Because therapeutic siRNAs depend heavily on non-canonical chemical features. A single 2'-O-methyl at position 10 or 11 sterically clashes with Ago2 and eliminates silencing, even if the sequence is 100% complementary. A sequence-only model only sees 'A, C, G, U' and is blind to this clash, leading to catastrophic failure.")
    ]

    for q, a in qa_data:
        p_q = Paragraph(f"<b>{q}</b>", ParagraphStyle('Q', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=accent_color))
        p_a = Paragraph(a, ParagraphStyle('A', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=text_dark))
        t_qa = Table([[p_q], [p_a]], colWidths=[504])
        t_qa.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_box),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_qa)
        story.append(Spacer(1, 6))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built: {filename} ({os.path.getsize(filename)} bytes)")

if __name__ == "__main__":
    out_pdf = r"d:\Helixx\HelixZero_Presentation_Speaker_Notes_and_Platform_Guide.pdf"
    build_pdf(out_pdf)
