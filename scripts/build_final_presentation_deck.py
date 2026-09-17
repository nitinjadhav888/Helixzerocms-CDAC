"""
scripts/build_final_presentation_deck.py
========================================
Generates a comprehensive 18-slide executive-ready presentation deck
for the HelixZero project based on HZ.pdf (IEEE TNNLS 2026).
"""

import sys
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation in 16:9 Widescreen
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Color Palette Constants
BG_DARK = RGBColor(10, 15, 29)         # Deepest Navy Slate
CARD_BG = RGBColor(17, 24, 39)         # Dark Charcoal Panel
CARD_BG_ALT = RGBColor(24, 35, 54)     # Elevated Card Panel
CARD_BORDER = RGBColor(40, 53, 75)     # Subtle Slate Border
CYAN = RGBColor(14, 165, 233)          # Electric Cyan
TEAL = RGBColor(20, 184, 166)          # Emerald Teal
PURPLE = RGBColor(168, 85, 247)        # Royal Purple
AMBER = RGBColor(245, 158, 11)         # Bright Amber
ROSE = RGBColor(244, 63, 94)           # Coral Rose
TEXT_WHITE = RGBColor(248, 250, 252)   # Pure Bright White
TEXT_MUTED = RGBColor(148, 163, 184)   # Soft Gray Slate
TEXT_SUB = RGBColor(203, 213, 225)     # Readable Subtext

FIGURES_DIR = Path("d:/Helixx/paper_figures")


def add_base_slide(tag: str, title: str, subtitle: str = ""):
    """Creates a standardized dark-themed slide with consistent header hierarchy."""
    slide = prs.slides.add_slide(blank_layout)
    
    # Background fill
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_DARK
    bg.line.fill.background()
    
    # Top accent line
    top_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.08))
    top_line.fill.solid()
    top_line.fill.fore_color.rgb = CYAN
    top_line.line.fill.background()
    
    # Category Tag / Badge
    if tag:
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.3))
        tf = tag_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f"// {tag.upper()}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN
        
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.8), Inches(0.55))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    
    # Subtitle
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.22), Inches(11.8), Inches(0.4))
        tf_s = sub_box.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle
        p_s.font.size = Pt(12)
        p_s.font.color.rgb = TEXT_MUTED

    # Footer
    footer = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.8), Inches(0.3))
    tf_f = footer.text_frame
    tf_f.margin_left = tf_f.margin_top = tf_f.margin_right = tf_f.margin_bottom = 0
    p_f = tf_f.paragraphs[0]
    p_f.text = "HelixZero: End-to-End Computational Screening & Structure-Guided siRNA Optimization | IEEE TNNLS 2026"
    p_f.font.size = Pt(9)
    p_f.font.color.rgb = RGBColor(71, 85, 105)
    
    return slide


def add_card(slide, x, y, w, h, title="", border_color=CARD_BORDER, bg_color=CARD_BG):
    """Adds a stylish rounded card container with optional header."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)
    
    if title:
        tb = slide.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.15), Inches(w - 0.4), Inches(0.35))
        tf = tb.text_frame
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = CYAN
    return card


def add_kpi_card(slide, x, y, w, h, number: str, label: str, subtext: str = "", accent_color=CYAN):
    """Creates a high-impact numerical metric KPI callout box."""
    add_card(slide, x, y, w, h, border_color=accent_color, bg_color=CARD_BG_ALT)
    
    # Number
    tb_num = slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 0.15), Inches(w - 0.3), Inches(0.55))
    tf_num = tb_num.text_frame
    tf_num.margin_left = tf_num.margin_top = tf_num.margin_right = tf_num.margin_bottom = 0
    p_num = tf_num.paragraphs[0]
    p_num.text = number
    p_num.font.size = Pt(28)
    p_num.font.bold = True
    p_num.font.color.rgb = accent_color
    
    # Label
    tb_lbl = slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 0.72), Inches(w - 0.3), Inches(0.3))
    tf_lbl = tb_lbl.text_frame
    tf_lbl.margin_left = tf_lbl.margin_top = tf_lbl.margin_right = tf_lbl.margin_bottom = 0
    p_lbl = tf_lbl.paragraphs[0]
    p_lbl.text = label
    p_lbl.font.size = Pt(11)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = TEXT_WHITE
    
    # Subtext
    if subtext:
        tb_sub = slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 1.05), Inches(w - 0.3), Inches(0.5))
        tf_sub = tb_sub.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtext
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = TEXT_MUTED


# ==============================================================================
# SLIDE 1: TITLE SLIDE (HERO)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = BG_DARK
bg1.line.fill.background()

# Glowing accent strip
glow = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(0.12), Inches(4.5))
glow.fill.solid()
glow.fill.fore_color.rgb = CYAN
glow.line.fill.background()

# Title text frame
tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.4), Inches(11.2), Inches(4.8))
tf1 = tb1.text_frame
tf1.word_wrap = True

# Badge
p_badge = tf1.paragraphs[0]
p_badge.text = "IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS (IEEE TNNLS 2026)"
p_badge.font.size = Pt(11)
p_badge.font.bold = True
p_badge.font.color.rgb = CYAN
p_badge.space_after = Pt(14)

# Main Title
p_title = tf1.add_paragraph()
p_title.text = "HELIXZERO: END-TO-END COMPUTATIONAL SCREENING AND STRUCTURE-GUIDED SIRNA OPTIMIZATION"
p_title.font.size = Pt(30)
p_title.font.bold = True
p_title.font.color.rgb = TEXT_WHITE
p_title.space_after = Pt(12)

# Subtitle
p_sub = tf1.add_paragraph()
p_sub.text = "A Tripartite Machine Learning, Multi-Modal Chemical Ontology, and 3D Argonaute-2 Structural Framework for Next-Generation RNAi Therapeutics"
p_sub.font.size = Pt(15)
p_sub.font.color.rgb = TEXT_SUB
p_sub.space_after = Pt(32)

# Author info
p_auth = tf1.add_paragraph()
p_auth.text = "Lead Author: Nitin Jadhav  |  Affiliation: CDAC / Independent Research"
p_auth.font.size = Pt(13)
p_auth.font.bold = True
p_auth.font.color.rgb = TEXT_WHITE

p_det = tf1.add_paragraph()
p_det.text = "Codebase: nitinjadhav888/Helixzerocms-CDAC  |  Empirical Scope: 40,255 Measured Assays  |  PDB: 4W5N"
p_det.font.size = Pt(11)
p_det.font.color.rgb = TEXT_MUTED


# ==============================================================================
# SLIDE 2: EXECUTIVE SUMMARY & CORE PARADIGM
# ==============================================================================
s2 = add_base_slide(
    "Executive Overview",
    "Transforming RNAi Drug Discovery with Multi-Modal Intelligence",
    "From naked sequence heuristics to modern chemistry-aware, dose-conditioned, and structure-validated siRNA engineering"
)

# 3 Pillar Cards
card_data_s2 = [
    {
        "title": "The Chemical Complexity Challenge",
        "color": ROSE,
        "bullets": [
            "Modern therapeutic siRNAs are NOT naked RNA: 100% of commercial drugs have full chemical modifications (2'-F, 2'-OMe, PS linkages, GalNAc conjugates).",
            "Naked sequence models collapse on modified duplexes (Pearson r = 0.2070 on CMsiRNAdb modified benchmarks).",
            "Modification effects are strictly non-additive: a single 2'-F at guide position 14 can boost cleavage 10-fold, while at position 9 it sterically clashes."
        ]
    },
    {
        "title": "The HelixZero Tripartite Solution",
        "color": CYAN,
        "bullets": [
            "Orthogonal Multi-Modal Chemical Ontologies: Uncoupling sugar chemistry, phosphate linkage, nucleobase modification, and terminal conjugates.",
            "577-Dimensional Hybrid Feature Vector: Fusing explicit positional flags, RNA foundation models (RNA-FM, RNAErnie), and thermodynamics.",
            "Hierarchical Potency-Response Architecture: Jointly predicting intrinsic potency (pIC50) and concentration-dependent knockdown curves."
        ]
    },
    {
        "title": "Empirical & Clinical Proof",
        "color": TEAL,
        "bullets": [
            "40,255-Assay Master Corpus: 5-fold cross-validation achieves Pearson r = 0.8049, Spearman ρ = 0.8018, R² = 0.6410.",
            "FDA Commercial Therapeutics Panel: Accurately predicts clinical potency across Givosiran, Patisiran, Inclisiran, and Lumasiran (0.83–2.24 nM).",
            "3D Ago2 Structural Docking: Human Ago2 (PDB 4W5N) template modeling flags steric clashes and confirms active-site geometric compatibility."
        ]
    }
]

for i, cd in enumerate(card_data_s2):
    cx = 0.8 + i * 4.0
    add_card(s2, cx, 1.8, 3.8, 4.9, cd["title"], border_color=cd["color"])
    tb = s2.shapes.add_textbox(Inches(cx + 0.2), Inches(2.4), Inches(3.4), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    for b_idx, b in enumerate(cd["bullets"]):
        p = tf.paragraphs[0] if b_idx == 0 else tf.add_paragraph()
        p.text = f"• {b}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_SUB
        p.space_after = Pt(12)


# ==============================================================================
# SLIDE 3: THE FOUR ORTHOGONAL PILLARS OF HELIXZERO
# ==============================================================================
s3 = add_base_slide(
    "Methodology & Pillars",
    "The Four Co-Optimized Dimensions of siRNA Efficacy",
    "Activity is governed by the non-linear interplay of sequence, chemistry, dose, and receptor geometry"
)

pillars = [
    {
        "p": "PILLAR 1", "title": "Sequence Screening", "color": CYAN,
        "points": ["Target mRNA transcript alignment", "Thermodynamic terminal asymmetry (ΔΔG)", "GC-clamp & seed fluidity (pos 2–7)", "Off-target seed cytotoxicity filtering"]
    },
    {
        "p": "PILLAR 2", "title": "Chemical Ontology", "color": TEAL,
        "points": ["Orthogonal 6-attribute slot model", "2'-OMe, 2'-F, 2'-MOE, LNA sugars", "Phosphorothioate (PS) stereochemistry", "Triantennary GalNAc targeting ligands"]
    },
    {
        "p": "PILLAR 3", "title": "Dose Potency Curve", "color": PURPLE,
        "points": ["Hierarchical pIC50 regressor", "4-parameter Hill concentration response", "Standardized 10 nM clinical benchmarking", "Multi-dose guide partition (N=8,159)"]
    },
    {
        "p": "PILLAR 4", "title": "3D Ago2 Docking", "color": AMBER,
        "points": ["Human Ago2 crystal reference (4W5N)", "MID pocket 5'-phosphate anchoring (≤4.5 Å)", "PAZ domain 3'-overhang fit (12–15 Å)", "PIWI catalytic proxy distance & clash filtering"]
    }
]

for i, pil in enumerate(pillars):
    px = 0.8 + i * 3.0
    add_card(s3, px, 1.8, 2.85, 4.9, pil["p"], border_color=pil["color"])
    
    # Subhead
    tb_h = s3.shapes.add_textbox(Inches(px + 0.18), Inches(2.25), Inches(2.5), Inches(0.4))
    p_h = tb_h.text_frame.paragraphs[0]
    p_h.text = pil["title"]
    p_h.font.size = Pt(13)
    p_h.font.bold = True
    p_h.font.color.rgb = TEXT_WHITE
    
    # Bullet points
    tb_b = s3.shapes.add_textbox(Inches(px + 0.18), Inches(2.8), Inches(2.5), Inches(3.6))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    for p_idx, pt in enumerate(pil["points"]):
        p = tf_b.paragraphs[0] if p_idx == 0 else tf_b.add_paragraph()
        p.text = f"✔ {pt}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_SUB
        p.space_after = Pt(10)


# ==============================================================================
# SLIDE 4: COMPREHENSIVE 10-RESOURCE DATASET TAXONOMY (IMAGE EMBED)
# ==============================================================================
s4 = add_base_slide(
    "Data Engineering",
    "Comprehensive Ten-Resource Public-Data Taxonomy",
    "Curating 40,255 measured records, 3,535 canonical duplexes, 549 patent/clinical compounds, and human Ago2 coordinates"
)

# Embed the generated 16:9 taxonomy graphic
tax_img = FIGURES_DIR / "helixzero_10_resource_dataset_taxonomy.png"
if tax_img.exists():
    s4.shapes.add_picture(str(tax_img), Inches(0.8), Inches(1.8), width=Inches(11.733), height=Inches(5.0))


# ==============================================================================
# SLIDE 5: MULTI-MODAL CHEMICAL ONTOLOGIES & SLOT ARCHITECTURE
# ==============================================================================
s5 = add_base_slide(
    "Chemical Representation",
    "Orthogonal Slot-Based Chemical Ontologies",
    "Resolving positional chemistry conflicts by decoupling sugar, linkage, base, and conjugate states"
)

add_card(s5, 0.8, 1.8, 5.8, 4.9, "The Slot-Based Nucleotide Model", border_color=CYAN)
tb_s5 = s5.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.4), Inches(4.1))
tf_s5 = tb_s5.text_frame
tf_s5.word_wrap = True
s5_text = [
    ("Mathematical Formulation", "Every nucleotide is formalized as a 6-attribute tuple: s_i = (b_i, q_i, l_i, m_i, t_i, c_i), where b=base, q=sugar, l=linkage, m=base mod, t=terminal state, c=conjugate."),
    ("Resolving Competing Notations", "Legacy strings collapse 2'-F and PS linkages into a single character, creating ambiguity. The slot model represents both independently without loss of chemical state."),
    ("Biophysical Rule Preservation", "Directly encodes critical structural constraints: seed region rigidification (pos 2–8), cleavage-sparing central core (pos 9–11), and terminal thermodynamic asymmetry."),
    ("GalNAc Conjugate Integration", "Seamlessly models multi-valent triantennary GalNAc targeting moieties at sense 3'/5' termini for liver asialoglycoprotein receptor (ASGPR) uptake.")
]
for head, desc in s5_text:
    p = tf_s5.add_paragraph() if tf_s5.paragraphs[0].text else tf_s5.paragraphs[0]
    p.text = f"■ {head}: "
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = CYAN
    p_sub = tf_s5.add_paragraph()
    p_sub.text = desc
    p_sub.font.size = Pt(10)
    p_sub.font.color.rgb = TEXT_SUB
    p_sub.space_after = Pt(8)

# Right side: Embed Functional Anatomy figure
anat_img = FIGURES_DIR / "Fig2_siRNA_Functional_Anatomy.png"
if anat_img.exists():
    s5.shapes.add_picture(str(anat_img), Inches(6.9), Inches(1.8), width=Inches(5.6), height=Inches(4.9))


# ==============================================================================
# SLIDE 6: 577-DIMENSIONAL HYBRID FEATURE ARCHITECTURE
# ==============================================================================
s6 = add_base_slide(
    "Feature Engineering",
    "577-Dimensional Multi-Modal Feature Architecture",
    "Integrating explicit positional chemistry flags, foundation-model representations, and thermodynamic calculations"
)

feat_blocks = [
    ("Positional Chemistry", "420 Features", CYAN, "Ten explicit binary flags at each of 21 nucleotide positions on both strands (8 sugar states, PS linkages, base modifications)."),
    ("RNA Foundation Models", "128 Features", TEAL, "Pre-trained deep biological representations: RNA-FM (64 PCA components) + RNAErnie (64 PCA components) capturing contextual sequence semantics."),
    ("Engineered Biophysics", "24 Features", PURPLE, "Seed-region rigidity indices, strand modification density, terminal phosphorothioate distribution, ASGPR conjugate indicators, and sequence composition."),
    ("Thermodynamics & GC", "5 Features", AMBER, "Nearest-neighbor Gibbs free energy (ΔG), terminal 5'-/3'-asymmetry (ΔΔG), GC content, and secondary structure melting profiles.")
]

for i, (fname, fdim, fcol, fdesc) in enumerate(feat_blocks):
    fx = 0.8 + i * 2.95
    add_card(s6, fx, 1.8, 2.8, 2.2, fname, border_color=fcol)
    
    tb_dim = s6.shapes.add_textbox(Inches(fx + 0.15), Inches(2.25), Inches(2.5), Inches(0.35))
    p_d = tb_dim.text_frame.paragraphs[0]
    p_d.text = fdim
    p_d.font.size = Pt(15)
    p_d.font.bold = True
    p_d.font.color.rgb = fcol
    
    tb_ds = s6.shapes.add_textbox(Inches(fx + 0.15), Inches(2.65), Inches(2.5), Inches(1.2))
    tf_ds = tb_ds.text_frame
    tf_ds.word_wrap = True
    p_ds = tf_ds.paragraphs[0]
    p_ds.text = fdesc
    p_ds.font.size = Pt(9.5)
    p_ds.font.color.rgb = TEXT_SUB

# Bottom: Feature architecture diagram
feat_img = FIGURES_DIR / "Fig3_Feature_Architecture.png"
if feat_img.exists():
    s6.shapes.add_picture(str(feat_img), Inches(0.8), Inches(4.2), width=Inches(11.733), height=Inches(2.65))


# ==============================================================================
# SLIDE 7: MACHINE LEARNING PIPELINE & MODEL PORTFOLIO
# ==============================================================================
s7 = add_base_slide(
    "Machine Learning Pipeline",
    "Tripartite Strategy & Domain-Specific Model Routing",
    "Aligning model complexity with chemical modification state to avoid negative cross-domain transfer"
)

models_s7 = [
    {
        "name": "Model 1: LightGBM Canonical",
        "domain": "Canonical / Unmodified Sequences",
        "color": CYAN,
        "metrics": "Huesken: r = 0.8044 | Takayuki: r = 0.8788",
        "desc": "Ultra-fast gradient boosted decision tree optimized on sequence kmers and thermodynamic asymmetry. Dominates canonical screening but intentionally lacks chemical awareness."
    },
    {
        "name": "Model 2: CatBoost v4 Chemistry-Aware",
        "domain": "Modified Duplex Regressions",
        "color": TEAL,
        "metrics": "CMsiRNAdb: r = 0.7401 | AUC = 0.8745",
        "desc": "Trains on full 577-D feature vectors. Leverages symmetric trees to prevent overfitting across sparse chemical modification patterns. Solves the modified-duplex failure of naked models."
    },
    {
        "name": "Model 3: Duplex Graph Network (GNN)",
        "domain": "Inter-Strand Topology & Geometry",
        "color": PURPLE,
        "metrics": "Topology-Aware Sequence Context",
        "desc": "Bidirectional graph neural network modeling Watson-Crick and wobble pairing interactions across strands, capturing spatial chemical context and helix stability."
    },
    {
        "name": "Model 4: Hierarchical Potency Engine",
        "domain": "Dose-Dependent Hill Response",
        "color": AMBER,
        "metrics": "5-Fold CV: r = 0.8049 | r_s = 0.8018",
        "desc": "Two-stage regressor predicting intrinsic pIC50 potency followed by concentration-conditioned sigmoidal knockdown response across 68 dose levels (0.00017–1000 nM)."
    }
]

for i, m in enumerate(models_s7):
    mx = 0.8 + i * 2.95
    add_card(s7, mx, 1.8, 2.8, 4.9, m["name"], border_color=m["color"])
    
    tb_dom = s7.shapes.add_textbox(Inches(mx + 0.15), Inches(2.25), Inches(2.5), Inches(0.3))
    p_dom = tb_dom.text_frame.paragraphs[0]
    p_dom.text = m["domain"]
    p_dom.font.size = Pt(10)
    p_dom.font.bold = True
    p_dom.font.color.rgb = m["color"]
    
    tb_met = s7.shapes.add_textbox(Inches(mx + 0.15), Inches(2.6), Inches(2.5), Inches(0.4))
    p_met = tb_met.text_frame.paragraphs[0]
    p_met.text = m["metrics"]
    p_met.font.size = Pt(10)
    p_met.font.bold = True
    p_met.font.color.rgb = TEXT_WHITE
    
    tb_dsc = s7.shapes.add_textbox(Inches(mx + 0.15), Inches(3.1), Inches(2.5), Inches(3.4))
    tf_dsc = tb_dsc.text_frame
    tf_dsc.word_wrap = True
    p_dsc = tf_dsc.paragraphs[0]
    p_dsc.text = m["desc"]
    p_dsc.font.size = Pt(10)
    p_dsc.font.color.rgb = TEXT_SUB


# ==============================================================================
# SLIDE 8: HIERARCHICAL POTENCY-RESPONSE ENGINE
# ==============================================================================
s8 = add_base_slide(
    "Potency Modeling",
    "Hierarchical Potency–Response Prediction Engine",
    "Disentangling sequence–chemistry intrinsic affinity (pIC50) from experimental assay concentration"
)

# Left column: KPI cards
add_kpi_card(s8, 0.8, 1.8, 2.7, 1.5, "r = 0.8049", "Pearson Correlation", "5-Partition Guide Evaluation", CYAN)
add_kpi_card(s8, 0.8, 3.5, 2.7, 1.5, "ρ = 0.8018", "Spearman Rank Correlation", "Strict monotonic preservation", TEAL)
add_kpi_card(s8, 0.8, 5.2, 2.7, 1.5, "R² = 0.6410", "Coefficient of Determination", "RMSE = 18.63 pp across 68 doses", PURPLE)

# Middle/Right: Detailed Mechanism Card
add_card(s8, 3.8, 1.8, 8.7, 4.9, "Two-Stage Sigmoidal Response Architecture", border_color=CYAN)
tb_s8 = s8.shapes.add_textbox(Inches(4.1), Inches(2.4), Inches(8.1), Inches(4.1))
tf_s8 = tb_s8.text_frame
tf_s8.word_wrap = True

s8_bullets = [
    ("Stage 1: Intrinsic Potency Regressor", "CatBoost regressor maps the 577-D feature vector to intrinsic duplex potency pIC50 = -log10(IC50 in M). Trained on 2,309 multi-dose curves with R² ≥ 0.75."),
    ("Stage 2: Concentration-Conditioned Knockdown", "Second regressor takes predicted pIC50 alongside assay concentration C (nM) and thermodynamic descriptors to compute predicted % knockdown: KD = 100 / (1 + 10^(h * (pIC50 - pC)))."),
    ("Solving Concentration Bias", "Standard models conflate high dose with high potency. A poor siRNA at 100 nM can match an ultra-potent siRNA at 0.1 nM. HelixZero cleanly uncouples affinity from dosage."),
    ("Multi-Dose Guide Partition (N = 8,159)", "Tested on an independent guide partition across 37,946 assays: Pearson r = 0.8365, Spearman ρ = 0.8335, MAE = 13.82 pp, RMSE = 17.12 pp, ROC-AUC = 0.9331.")
]

for title, desc in s8_bullets:
    p = tf_s8.add_paragraph() if tf_s8.paragraphs[0].text else tf_s8.paragraphs[0]
    p.text = f"✔ {title}: "
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = CYAN
    p_b = tf_s8.add_paragraph()
    p_b.text = desc
    p_b.font.size = Pt(10.5)
    p_b.font.color.rgb = TEXT_SUB
    p_b.space_after = Pt(10)


# ==============================================================================
# SLIDE 9: CANONICAL SEQUENCE BENCHMARKS (N = 3,535)
# ==============================================================================
s9 = add_base_slide(
    "Canonical Benchmarks",
    "Rigorous Validation on Unmodified siRNAs (N = 3,535)",
    "State-of-the-art performance across historical benchmark collections"
)

# Table VI data for canonical sets
table_shape = s9.shapes.add_table(5, 7, Inches(0.8), Inches(1.8), Inches(11.733), Inches(2.5))
table = table_shape.table

# Set Column Widths
col_widths = [Inches(2.5), Inches(2.0), Inches(1.2), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.533)]
for idx, w in enumerate(col_widths):
    table.columns[idx].width = w

headers = ["Benchmark Dataset", "Evaluated Model", "Sample N", "Pearson r", "Spearman ρ", "R² Score", "ROC-AUC"]
for c_idx, h in enumerate(headers):
    cell = table.cell(0, c_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = CARD_BG_ALT
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = CYAN

rows_s9 = [
    ["Huesken Gold Standard", "LightGBM Canonical", "2,361", "0.8044", "0.8065", "0.6252", "0.9099"],
    ["Takayuki / siDirect Alias", "LightGBM Canonical", "702", "0.8788", "0.8734", "0.6525", "0.9275"],
    ["Seven-Study Canonical Mixset", "LightGBM Canonical", "472", "0.8291", "0.8093", "0.4605", "0.9456"],
    ["Multi-Study Pooled Average", "HelixZero Pipeline", "3,535", "0.8374", "0.8297", "0.5794", "0.9277"]
]

for r_idx, row in enumerate(rows_s9):
    for c_idx, val in enumerate(row):
        cell = table.cell(r_idx + 1, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 0 else CARD_BG_ALT
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_WHITE if c_idx == 0 else (CYAN if c_idx in [3, 4] else TEXT_SUB)

# Bottom Takeaways
add_card(s9, 0.8, 4.6, 11.733, 2.1, "Key Scientific Findings", border_color=TEAL)
tb_s9_b = s9.shapes.add_textbox(Inches(1.0), Inches(5.1), Inches(11.3), Inches(1.5))
tf_s9_b = tb_s9_b.text_frame
tf_s9_b.word_wrap = True
s9_bullets = [
    "Near-Perfect Sequence Generalization: LightGBM achieves r = 0.8788 on Takayuki and r = 0.8044 on Huesken without relying on computationally expensive LLMs during inference.",
    "Strict Negative Controls: When CatBoost v4 (chemistry-trained) is evaluated on Huesken without modifications, it yields r = -0.0421, confirming domain-specific routing is necessary.",
    "AUC > 0.90 Across All Sets: Reliable discrimination of highly functional siRNAs (>70% knockdown threshold) for high-throughput therapeutic candidate shortlisting."
]
for b in s9_bullets:
    p = tf_s9_b.add_paragraph() if tf_s9_b.paragraphs[0].text else tf_s9_b.paragraphs[0]
    p.text = f"• {b}"
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_SUB
    p.space_after = Pt(4)


# ==============================================================================
# SLIDE 10: MODIFIED-DUPLEX & CROSS-DOMAIN GENERALIZATION (N = 5,000+)
# ==============================================================================
s10 = add_base_slide(
    "Modified Duplex Benchmarks",
    "Chemically Modified Generalization (N = 5,000+)",
    "CatBoost v4 rescues predictive efficacy where canonical models completely collapse"
)

# Left Column: Table of Modified Sets
table_shape_10 = s10.shapes.add_table(4, 6, Inches(0.8), Inches(1.8), Inches(7.5), Inches(2.2))
table10 = table_shape_10.table
for idx, w in enumerate([Inches(2.5), Inches(1.3), Inches(0.9), Inches(1.0), Inches(1.0), Inches(0.8)]):
    table10.columns[idx].width = w

headers10 = ["Modified Dataset", "Model", "N", "Pearson r", "Spearman ρ", "AUC"]
for c_idx, h in enumerate(headers10):
    cell = table10.cell(0, c_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = CARD_BG_ALT
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = CYAN

rows_s10 = [
    ["CMsiRNAdb Homogeneous (10 nM)", "CatBoost v4", "472", "0.7401", "0.7540", "0.8745"],
    ["CMsiRNAdb Homogeneous (10 nM)", "LightGBM (Naked)", "472", "0.2070", "0.1885", "0.5841"],
    ["CMsiRNAdb Heterogeneous Master", "CatBoost v4", "2,576", "0.6217", "0.6049", "0.8077"]
]
for r_idx, row in enumerate(rows_s10):
    for c_idx, val in enumerate(row):
        cell = table10.cell(r_idx + 1, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 0 else CARD_BG_ALT
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.size = Pt(9.5)
        p.font.color.rgb = ROSE if (r_idx == 1 and c_idx == 3) else (CYAN if c_idx == 3 else TEXT_WHITE)

# Right Column: Big Comparison Card
add_card(s10, 8.6, 1.8, 3.933, 4.9, "The Canonical Collapse Paradox", border_color=ROSE)
tb_s10_r = s10.shapes.add_textbox(Inches(8.8), Inches(2.4), Inches(3.5), Inches(4.1))
tf_s10_r = tb_s10_r.text_frame
tf_s10_r.word_wrap = True
s10_insights = [
    ("Naked Models Fail", "On CMsiRNAdb homogeneous modified assays, LightGBM drops from r = 0.88 to r = 0.2070. Sequence-only features cannot account for modified ribonucleotide chemistry."),
    ("CatBoost v4 Rescues Activity", "Adding the 420 positional chemistry flags drives Pearson r to 0.7401 and ROC-AUC to 0.8745 (+0.533 correlation gain)."),
    ("Chemical Heterogeneity Penalty", "In the 2,576-duplex multi-patent set, correlation moderates to r = 0.6217 (RMSE = 22.74 pp), reflecting diverse assay protocols and vendor chemistry variations.")
]
for h, d in s10_insights:
    p = tf_s10_r.add_paragraph() if tf_s10_r.paragraphs[0].text else tf_s10_r.paragraphs[0]
    p.text = f"■ {h}: "
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ROSE if "Fail" in h else CYAN
    p_d = tf_s10_r.add_paragraph()
    p_d.text = d
    p_d.font.size = Pt(9.5)
    p_d.font.color.rgb = TEXT_SUB
    p_d.space_after = Pt(8)

# Bottom Left: Embed Fig4 empirical benchmarks
bench_img = FIGURES_DIR / "Fig4_Empirical_Benchmarks.png"
if bench_img.exists():
    s10.shapes.add_picture(str(bench_img), Inches(0.8), Inches(4.2), width=Inches(7.5), height=Inches(2.5))


# ==============================================================================
# SLIDE 11: FEATURE ABLATION & CHEMICAL FAMILY STRATIFICATION
# ==============================================================================
s11 = add_base_slide(
    "Model Interpretability",
    "Feature Ablation & Chemical Family Stratification",
    "Positional chemistry is the primary determinant of modified siRNA knockdown"
)

# Left Side: Ablation Table
add_card(s11, 0.8, 1.8, 5.6, 4.9, "Component Ablation Study", border_color=CYAN)
tb_abl = s11.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.1))
tf_abl = tb_abl.text_frame
tf_abl.word_wrap = True
ablations = [
    ("Full 577-Feature Model", "Pearson r = 0.7401", CYAN, "All 5 feature blocks active (positional, engineered, RNA-FM, RNAErnie, thermodynamics)."),
    ("Without Positional Chemistry", "Pearson r = 0.4120 (-0.3281)", ROSE, "Largest performance drop. Proves explicit modification state is essential."),
    ("Without Foundation Models", "Pearson r = 0.6912 (-0.0489)", AMBER, "RNA-FM and RNAErnie provide useful evolutionary semantic context."),
    ("Without Thermodynamics", "Pearson r = 0.7210 (-0.0191)", TEXT_MUTED, "Nearest-neighbor ΔΔG features contribute minor complementary stability information."),
    ("Legacy Sequence Baseline", "Pearson r = 0.2450 (-0.4951)", ROSE, "Legacy kmer encoding completely fails on modified oligonucleotides.")
]
for name, drop, col, desc in ablations:
    p = tf_abl.add_paragraph() if tf_abl.paragraphs[0].text else tf_abl.paragraphs[0]
    p.text = f"• {name} → {drop}"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = col
    p_sub = tf_abl.add_paragraph()
    p_sub.text = desc
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = TEXT_SUB
    p_sub.space_after = Pt(6)

# Right Side: Embed Chemical Stratification & Ablation figures
abl_img = FIGURES_DIR / "Fig4_Feature_Ablation.png"
if abl_img.exists():
    s11.shapes.add_picture(str(abl_img), Inches(6.8), Inches(1.8), width=Inches(5.733), height=Inches(4.9))


# ==============================================================================
# SLIDE 12: REAL-WORLD PATENT & GALNAC BENCHMARKS
# ==============================================================================
s12 = add_base_slide(
    "External Validation",
    "Real-World Patent & GalNAc Delivery Panels",
    "Validating generalization on commercial patent disclosures and liver-targeting conjugates"
)

panels_s12 = [
    {
        "name": "FENNEC APP Patent Panel",
        "patent": "WO2020132227A2 (Alnylam)",
        "scope": "N = 343 siRNAs (Amyloid Precursor Protein)",
        "color": CYAN,
        "metrics": "Pearson r = 0.7182 | Spearman ρ = 0.7095 | AUC = 0.8410",
        "bullets": [
            "Evaluated on real-world commercial patent screening data for neurodegenerative targets.",
            "Consensus v4/v5 ensemble achieves MAE = 15.22 pp, RMSE = 19.84 pp.",
            "Demonstrates zero-shot transfer across complex proprietary chemical architectures."
        ]
    },
    {
        "name": "FENNEC JAK1 Patent Panel",
        "patent": "WO2024256707A1 (Janus Kinase 1)",
        "scope": "N = 191 siRNAs (Immunology & Oncology)",
        "color": TEAL,
        "metrics": "Pearson r = 0.6945 | Spearman ρ = 0.6880 | AUC = 0.8250",
        "bullets": [
            "Independent target mRNA gene with distinct GC composition and secondary structure.",
            "Confirms high ranking accuracy across multi-site modified chemical patterns.",
            "Consensus ensemble achieves MAE = 16.10 pp, RMSE = 20.45 pp."
        ]
    },
    {
        "name": "Foster GalNAc Delivery Panel",
        "patent": "Molecular Therapy (2018)",
        "scope": "N = 15 siRNAs (ESC/ESC+ Chemistries)",
        "color": PURPLE,
        "metrics": "Pearson r = 0.9120 | Spearman ρ = 0.8940 | R² = 0.7920",
        "bullets": [
            "Advanced Enhanced Stabilization Chemistry (ESC/ESC+) with triantennary GalNAc.",
            "Near-perfect rank preservation (ρ = 0.8940, MAE = 7.45 pp, RMSE = 9.80 pp).",
            "Validates multi-slot designer's ability to prioritize liver-targeted clinical candidates."
        ]
    }
]

for i, pnl in enumerate(panels_s12):
    px = 0.8 + i * 4.0
    add_card(s12, px, 1.8, 3.8, 4.9, pnl["name"], border_color=pnl["color"])
    
    tb_p = s12.shapes.add_textbox(Inches(px + 0.2), Inches(2.3), Inches(3.4), Inches(0.4))
    p_pat = tb_p.text_frame.paragraphs[0]
    p_pat.text = f"{pnl['patent']}\n{pnl['scope']}"
    p_pat.font.size = Pt(9.5)
    p_pat.font.color.rgb = TEXT_MUTED
    
    tb_m = s12.shapes.add_textbox(Inches(px + 0.2), Inches(2.85), Inches(3.4), Inches(0.5))
    p_m = tb_m.text_frame.paragraphs[0]
    p_m.text = pnl["metrics"]
    p_m.font.size = Pt(10)
    p_m.font.bold = True
    p_m.font.color.rgb = pnl["color"]
    
    tb_bl = s12.shapes.add_textbox(Inches(px + 0.2), Inches(3.45), Inches(3.4), Inches(3.1))
    tf_bl = tb_bl.text_frame
    tf_bl.word_wrap = True
    for b in pnl["bullets"]:
        p = tf_bl.add_paragraph() if tf_bl.paragraphs[0].text else tf_bl.paragraphs[0]
        p.text = f"• {b}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_SUB
        p.space_after = Pt(8)


# ==============================================================================
# SLIDE 13: CLINICAL TRANSLATION & FDA-APPROVED THERAPEUTIC PANEL
# ==============================================================================
s13 = add_base_slide(
    "Clinical Translation",
    "Validation on FDA-Approved Commercial siRNA Therapeutics",
    "Demonstrating sub-nanomolar potency prediction across commercial clinical drugs"
)

# Table VII Paired Therapeutics Table
table_shape_13 = s13.shapes.add_table(5, 7, Inches(0.8), Inches(1.8), Inches(11.733), Inches(2.6))
table13 = table_shape_13.table
for idx, w in enumerate([Inches(2.4), Inches(1.1), Inches(2.6), Inches(1.3), Inches(1.4), Inches(1.4), Inches(1.533)]):
    table13.columns[idx].width = w

headers13 = ["Commercial Drug", "Target", "Clinical Trial Reduction", "pIC50", "Potency (IC50)", "Pred KD (10 nM)", "Anchor Exemption"]
for c_idx, h in enumerate(headers13):
    cell = table13.cell(0, c_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = CARD_BG_ALT
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = CYAN

rows_s13 = [
    ["Givosiran (AD-62846, 2019)", "ALAS1", "88.0%–93.0% (Mid: 90.5%)", "9.0811", "0.83 nM", "92.3%", "0.0 pts (Verified)"],
    ["Patisiran (AD-18328, 2018)", "TTR", "84.0%–90.0% (Mid: 87.0%)", "8.8709", "1.35 nM", "88.1%", "0.0 pts (Verified)"],
    ["Inclisiran (AD-63025, 2021)", "PCSK9", "80.0%–86.0% (Mid: 83.0%)", "8.8747", "1.33 nM", "88.2%", "0.0 pts (Verified)"],
    ["Lumasiran (AD-67379, 2020)", "HAO1", "80.0%–85.0% (Mid: 82.5%)", "8.6577", "2.20 nM", "82.0%", "0.0 pts (Verified)"]
]

for r_idx, row in enumerate(rows_s13):
    for c_idx, val in enumerate(row):
        cell = table13.cell(r_idx + 1, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 0 else CARD_BG_ALT
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.size = Pt(9.5)
        p.font.color.rgb = CYAN if c_idx == 4 else TEXT_WHITE

# 3 Callout Cards Bottom
add_kpi_card(s13, 0.8, 4.7, 3.7, 2.0, "0.83–2.24 nM", "Corrected Potency Conversion", "Matches FDA nanomolar clinical therapeutic window exactly (IC50 = 10^(9 - pIC50)).", CYAN)
add_kpi_card(s13, 4.8, 4.7, 3.7, 2.0, "r_s = 0.8000", "Untied Spearman Rank Correlation", "Reflects exact discrete rank correlation with single adjacent transposition (Σ d_i² = 2).", TEAL)
add_kpi_card(s13, 8.8, 4.7, 3.733, 2.0, "0.0 Penalty Exemption", "Biophysical Exemption Verified", "All 5 FDA drugs pass without spurious steric/charge rule deductions.", PURPLE)


# ==============================================================================
# SLIDE 14: STRUCTURE-GUIDED 3D AGO2 DOCKING & MOLECULAR MECHANICS
# ==============================================================================
s14 = add_base_slide(
    "Structural Biology",
    "Argonaute-2 (Ago2) Guided 3D Docking & Pocket Geometry",
    "Integrating PDB 4W5N coordinates to filter steric clashes before downstream synthesis"
)

# Left: 3D Image Embed
dock_img = FIGURES_DIR / "patisiran_3d_pocket_docking.png"
if not dock_img.exists():
    dock_img = FIGURES_DIR / "ago2_3d_docking_complex.png"
if dock_img.exists():
    s14.shapes.add_picture(str(dock_img), Inches(0.8), Inches(1.8), width=Inches(5.6), height=Inches(4.9))

# Right: Metrics Table VIII
add_card(s14, 6.7, 1.8, 5.833, 4.9, "Ago2 Pocket Compatibility (Table VIII)", border_color=CYAN)
table_shape_14 = s14.shapes.add_table(6, 4, Inches(6.9), Inches(2.4), Inches(5.4), Inches(2.4))
table14 = table_shape_14.table
for idx, w in enumerate([Inches(2.2), Inches(1.0), Inches(1.1), Inches(1.1)]):
    table14.columns[idx].width = w

headers14 = ["Geometric Descriptor", "Patisiran", "Clashed Duplex", "Screening Rule"]
for c_idx, h in enumerate(headers14):
    cell = table14.cell(0, c_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = CARD_BG_ALT
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = CYAN

rows_s14 = [
    ["MID Distance (Å)", "3.17", "3.17", "≤ 4.5 Å"],
    ["PIWI Distance (Å)", "4.21", "10.42", "≤ 5.5 Å"],
    ["PAZ Distance (Å)", "13.98", "13.98", "12–15 Å"],
    ["Clash Score", "0.8", "24.8", "≤ 4 (Flag > 12)"],
    ["Structural Score", "-15.2", "-5.6", "-16.5 to -14.0"]
]
for r_idx, row in enumerate(rows_s14):
    for c_idx, val in enumerate(row):
        cell = table14.cell(r_idx + 1, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 0 else CARD_BG_ALT
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.size = Pt(9)
        p.font.color.rgb = ROSE if (r_idx in [1, 3] and c_idx == 2) else TEXT_WHITE

tb_s14_b = s14.shapes.add_textbox(Inches(6.9), Inches(5.0), Inches(5.4), Inches(1.5))
tf_s14_b = tb_s14_b.text_frame
tf_s14_b.word_wrap = True
s14_points = [
    "MID Domain 5'-Anchoring: Confirms guide 5'-monophosphate is buried in the MID pocket coordinating Lys278, Gln545, and Tyr529 (3.17 Å ≤ 4.5 Å tolerance).",
    "PIWI Catalytic Pocket: Impaired comparator displaces the scissile phosphate to 10.42 Å (clash score 24.8), flagging steric obstruction to catalytic Asp669/Glu635/His807 cleavage."
]
for pt in s14_points:
    p = tf_s14_b.add_paragraph() if tf_s14_b.paragraphs[0].text else tf_s14_b.paragraphs[0]
    p.text = f"• {pt}"
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_SUB
    p.space_after = Pt(4)


# ==============================================================================
# SLIDE 15: SCIENTIFIC RIGOR & PEER REVIEW AUDITING
# ==============================================================================
s15 = add_base_slide(
    "Scientific Skepticism",
    "Peer-Review Auditing & Mathematical Rigor",
    "Stringent validation standards satisfying IEEE TNNLS and Nature Biotechnology directives"
)

audit_pillars = [
    {
        "title": "Strict Zero-Leakage GroupKFold",
        "color": CYAN,
        "bullets": [
            "All cross-validation splits are grouped strictly by antisense sequence/target mRNA.",
            "Zero sequence overlap between train and test folds prevents synthetic data leakage and memorization.",
            "Validates genuine out-of-distribution generalizability across novel therapeutic targets."
        ]
    },
    {
        "title": "Mathematical Spearman ρ Resolution",
        "color": TEAL,
        "bullets": [
            "Addressed review query regarding flagged ρ = 0.9480 on N=4 therapeutic panel.",
            "Proven that untied 4-pair rank correlation is mathematically restricted to {1.0, 0.8, 0.6, ...}.",
            "Traced 0.9480 to empirical Hill slope parameter (h = 0.94809); corrected exact untied rank correlation is strictly ρ = 0.8000."
        ]
    },
    {
        "title": "Differentiating Docking from Binding ΔG",
        "color": AMBER,
        "bullets": [
            "Explicitly avoids conflating rigid-receptor docking scores with experimental thermodynamic binding free energies.",
            "Structural metrics serve as binary/geometric feasibility filters, not quantitative affinity predictors.",
            "Preserves complete scientific honesty regarding template placement limitations."
        ]
    }
]

for i, aud in enumerate(audit_pillars):
    ax_pos = 0.8 + i * 4.0
    add_card(s15, ax_pos, 1.8, 3.8, 4.9, aud["title"], border_color=aud["color"])
    tb = s15.shapes.add_textbox(Inches(ax_pos + 0.2), Inches(2.4), Inches(3.4), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    for b in aud["bullets"]:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        p.text = f"✔ {b}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_SUB
        p.space_after = Pt(12)


# ==============================================================================
# SLIDE 16: PRODUCTION PLATFORM ARCHITECTURE & SERVING
# ==============================================================================
s16 = add_base_slide(
    "Platform Architecture",
    "Production-Grade Web Application & Serving Pipeline",
    "End-to-end containerized microservices supporting real-time oligonucleotide design and optimization"
)

# Left: System Architecture Image Embed
sys_img = FIGURES_DIR / "Fig1_System_Architecture.png"
if sys_img.exists():
    s16.shapes.add_picture(str(sys_img), Inches(0.8), Inches(1.8), width=Inches(6.2), height=Inches(4.9))

# Right: Technical Stack Cards
add_card(s16, 7.3, 1.8, 5.233, 4.9, "Production Serving Stack", border_color=CYAN)
tb_s16_r = s16.shapes.add_textbox(Inches(7.5), Inches(2.4), Inches(4.8), Inches(4.1))
tf_s16_r = tb_s16_r.text_frame
tf_s16_r.word_wrap = True

stack_items = [
    ("Backend API Engine", "FastAPI microservice executing inference pipelines in <150 ms per duplex with pre-loaded LightGBM, CatBoost, and GNN model weights."),
    ("Interactive UI Dashboard", "Streamlit front-end providing interactive duplex visualization, 3D molecular inspection, and automated patent design generation."),
    ("Human Transcriptome Index", "863 MB 2-bit packed GRCh38 transcriptome serving genome-wide specificity queries across 40M+ 30-mers."),
    ("Automated CI/CD & Testing", "GitHub Actions pipeline with 3 rigorous test suites covering unit regression, biophysics literature verification, and full-stack integration.")
]
for h, d in stack_items:
    p = tf_s16_r.add_paragraph() if tf_s16_r.paragraphs[0].text else tf_s16_r.paragraphs[0]
    p.text = f"■ {h}: "
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = CYAN
    p_d = tf_s16_r.add_paragraph()
    p_d.text = d
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = TEXT_SUB
    p_d.space_after = Pt(10)


# ==============================================================================
# SLIDE 17: SUMMARY, CONCLUSIONS & FUTURE HORIZONS
# ==============================================================================
s17 = add_base_slide(
    "Conclusions & Roadmap",
    "Key Achievements & Future Horizons for HelixZero",
    "Establishing a new benchmark in chemistry-aware, structure-guided RNAi therapeutics"
)

# 4 Quadrant Summary Cards
quads = [
    ("1. Solved Chemical Blindspot", CYAN, "Replaced brittle naked sequence models with a 577-D multi-modal ontology that natively handles 2'-F, 2'-OMe, PS, and GalNAc conjugates."),
    ("2. Unified Potency & Dose", TEAL, "Disentangled intrinsic sequence affinity (pIC50) from assay concentration, achieving Pearson r = 0.8049 across 37,946 multi-dose assays."),
    ("3. Structural Pre-Filtering", PURPLE, "Integrated human Ago2 (PDB 4W5N) crystallographic constraints to detect steric clashes and eliminate inactive candidates before in vitro synthesis."),
    ("4. Validated on Clinical Drugs", AMBER, "Directly confirmed against FDA-approved therapeutics (Givosiran, Patisiran, Inclisiran, Lumasiran), predicting clinical potency within 0.83–2.24 nM.")
]

for idx, (qtitle, qcol, qdesc) in enumerate(quads):
    qx = 0.8 + (idx % 2) * 6.0
    qy = 1.8 + (idx // 2) * 2.5
    add_card(s17, qx, qy, 5.733, 2.3, qtitle, border_color=qcol)
    tb_q = s17.shapes.add_textbox(Inches(qx + 0.2), Inches(qy + 0.6), Inches(5.3), Inches(1.5))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    p_q = tf_q.paragraphs[0]
    p_q.text = qdesc
    p_q.font.size = Pt(11)
    p_q.font.color.rgb = TEXT_SUB


# ==============================================================================
# SLIDE 18: CLOSING / Q&A SLIDE
# ==============================================================================
s18 = prs.slides.add_slide(blank_layout)
bg18 = s18.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg18.fill.solid()
bg18.fill.fore_color.rgb = BG_DARK
bg18.line.fill.background()

top_line18 = s18.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.08))
top_line18.fill.solid()
top_line18.fill.fore_color.rgb = CYAN
top_line18.line.fill.background()

tb18 = s18.shapes.add_textbox(Inches(1.5), Inches(2.0), Inches(10.333), Inches(4.0))
tf18 = tb18.text_frame
tf18.word_wrap = True

p_c1 = tf18.paragraphs[0]
p_c1.text = "THANK YOU"
p_c1.font.size = Pt(44)
p_c1.font.bold = True
p_c1.font.color.rgb = TEXT_WHITE
p_c1.alignment = PP_ALIGN.CENTER
p_c1.space_after = Pt(16)

p_c2 = tf18.add_paragraph()
p_c2.text = "HelixZero: End-to-End Computational Screening & Structure-Guided Chemical Optimization of Therapeutic siRNAs"
p_c2.font.size = Pt(16)
p_c2.font.color.rgb = CYAN
p_c2.alignment = PP_ALIGN.CENTER
p_c2.space_after = Pt(24)

p_c3 = tf18.add_paragraph()
p_c3.text = "Author: Nitin Jadhav  |  Target Journal: IEEE TNNLS 2026\nOpen-Source Codebase: https://github.com/nitinjadhav888/Helixzerocms-CDAC\nQuestions & Scientific Discussion Welcome"
p_c3.font.size = Pt(13)
p_c3.font.color.rgb = TEXT_SUB
p_c3.alignment = PP_ALIGN.CENTER

# Save presentation
out_pptx = Path("d:/Helixx/HelixZero_Final_Presentation_Deck.pptx")
prs.save(out_pptx)
print(f"🎉 Presentation successfully created at: {out_pptx} ({out_pptx.stat().st_size / 1024:.1f} KB)")
