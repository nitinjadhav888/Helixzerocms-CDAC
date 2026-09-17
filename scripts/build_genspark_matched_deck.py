"""
scripts/build_genspark_matched_deck.py
======================================
Replicates the exact layout, styling, and content of the user's Genspark slides 1-5.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

# Dark modern Genspark theme
BG_COLOR = RGBColor(7, 13, 23)          # Very deep midnight blue
CARD_BG = RGBColor(13, 22, 38)          # Card background
CARD_BORDER = RGBColor(30, 48, 77)      # Card border
CYAN = RGBColor(14, 165, 233)           # #0EA5E9
TEAL = RGBColor(20, 184, 166)          # #14B8A6
CORAL = RGBColor(244, 63, 94)          # #F43F5E
PURPLE = RGBColor(168, 85, 247)        # #A855F7
AMBER = RGBColor(245, 158, 11)         # #F59E0B
WHITE = RGBColor(248, 250, 252)
GRAY = RGBColor(148, 163, 184)
GRAY_LIGHT = RGBColor(203, 213, 225)


def add_bg(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_COLOR
    bg.line.fill.background()
    return bg


def add_pill_badge(slide, text, x, y, w, h=0.28, text_color=CYAN, border_color=CARD_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    tf = card.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = text_color
    p.alignment = PP_ALIGN.CENTER
    return card


# ==========================================
# SLIDE 1: Title Slide (Input_file_0)
# ==========================================
s1 = prs.slides.add_slide(blank)
add_bg(s1)

# Badge
add_pill_badge(s1, "IEEE TNNLS 2026 · MANUSCRIPT SUBMISSION", 0.8, 0.6, 3.2)

# Category text
tb_cat = s1.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(8), Inches(0.3))
p_cat = tb_cat.text_frame.paragraphs[0]
p_cat.text = "RNAI THERAPEUTICS · COMPUTATIONAL DESIGN · MACHINE LEARNING"
p_cat.font.size = Pt(10)
p_cat.font.bold = True
p_cat.font.color.rgb = GRAY

# Big Title "HelixZero"
tb_hz = s1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8), Inches(1.3))
p_hz = tb_hz.text_frame.paragraphs[0]
r1 = p_hz.add_run()
r1.text = "Helix"
r1.font.size = Pt(64)
r1.font.bold = True
r1.font.color.rgb = WHITE
r2 = p_hz.add_run()
r2.text = "Zero"
r2.font.size = Pt(64)
r2.font.bold = True
r2.font.color.rgb = CYAN

# Subtitle
tb_sub = s1.shapes.add_textbox(Inches(0.8), Inches(3.0), Inches(7.5), Inches(0.7))
p_sub = tb_sub.text_frame.paragraphs[0]
p_sub.text = "End-to-End Computational Screening and Structure-Guided Optimization of Therapeutic siRNAs"
p_sub.font.size = Pt(16)
p_sub.font.bold = True
p_sub.font.color.rgb = WHITE

# Description
tb_desc = s1.shapes.add_textbox(Inches(0.8), Inches(3.75), Inches(7.5), Inches(0.6))
p_desc = tb_desc.text_frame.paragraphs[0]
p_desc.text = "A tripartite ML framework combining multi-modal chemical ontologies, dose-aware potency prediction, and 3D Argonaute-2 structural validation."
p_desc.font.size = Pt(11)
p_desc.font.color.rgb = GRAY_LIGHT

# Author
tb_auth = s1.shapes.add_textbox(Inches(0.8), Inches(4.7), Inches(7.5), Inches(0.8))
p_a1 = tb_auth.text_frame.paragraphs[0]
p_a1.text = "Nitin Jadhav"
p_a1.font.size = Pt(14)
p_a1.font.bold = True
p_a1.font.color.rgb = WHITE
p_a2 = tb_auth.text_frame.add_paragraph()
p_a2.text = "CDAC, Pune · Independent Research"
p_a2.font.size = Pt(10.5)
p_a2.font.color.rgb = GRAY

# Bottom 3 Cards
cards_s1 = [
    ("SCOPE", "40,255 assays · 3,535 duplexes", 0.8, 3.5),
    ("VALIDATION", "FDA drugs · 0.83–2.24 nM potency", 4.6, 3.5),
    ("CODE", "nitinjadhav888/Helixzerocms-CDAC", 8.4, 4.1)
]
for lbl, val, cx, cw in cards_s1:
    c = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(cx), Inches(5.8), Inches(cw), Inches(0.9))
    c.fill.solid()
    c.fill.fore_color.rgb = CARD_BG
    c.line.color.rgb = CARD_BORDER
    tf = c.text_frame
    tf.margin_left = Inches(0.18)
    tf.margin_top = Inches(0.15)
    p1 = tf.paragraphs[0]
    p1.text = lbl
    p1.font.size = Pt(8.5)
    p1.font.bold = True
    p1.font.color.rgb = CYAN
    p2 = tf.add_paragraph()
    p2.text = val
    p2.font.size = Pt(11)
    p2.font.color.rgb = WHITE

# Right decorative circular element
circle = s1.shapes.add_shape(MSO_SHAPE.OVAL, Inches(8.5), Inches(1.6), Inches(4.2), Inches(4.2))
circle.fill.background()
circle.line.color.rgb = RGBColor(16, 35, 60)
circle.line.width = Pt(1.5)


# ==========================================
# SLIDE 2: Executive Overview (Input_file_1)
# ==========================================
s2 = prs.slides.add_slide(blank)
add_bg(s2)

# Top Tag
tb_tag2 = s2.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8), Inches(0.3))
p_t2 = tb_tag2.text_frame.paragraphs[0]
p_t2.text = "// EXECUTIVE OVERVIEW"
p_t2.font.size = Pt(10)
p_t2.font.bold = True
p_t2.font.color.rgb = CYAN

# Title
tb_tit2 = s2.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.8), Inches(0.8))
p_tit2 = tb_tit2.text_frame.paragraphs[0]
r_a = p_tit2.add_run()
r_a.text = "From naked sequence heuristics to a "
r_a.font.size = Pt(22)
r_a.font.bold = True
r_a.font.color.rgb = WHITE
r_b = p_tit2.add_run()
r_b.text = "chemistry-aware"
r_b.font.size = Pt(22)
r_b.font.bold = True
r_b.font.color.rgb = CYAN
r_c = p_tit2.add_run()
r_c.text = ", dose-aware framework"
r_c.font.size = Pt(22)
r_c.font.bold = True
r_c.font.color.rgb = WHITE

# Subtitle
tb_sub2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.8), Inches(0.4))
p_sub2 = tb_sub2.text_frame.paragraphs[0]
p_sub2.text = "Therapeutic siRNAs are 100% chemically modified. Sequence-only predictors collapse on modified duplexes. HelixZero rebuilds the problem around four orthogonal dimensions."
p_sub2.font.size = Pt(11)
p_sub2.font.color.rgb = GRAY_LIGHT

# 3 Columns
cols_s2 = [
    ("01 · CHALLENGE", "The chemistry blind-spot", CORAL,
     "100% of approved siRNAs are chemically modified (2'-F, 2'-OMe, PS, GalNAc). Sequence-only models reach r = 0.2070 on modified benchmarks — essentially guessing.",
     "A modification at position 14 may help. The same modification at position 9 sterilizes cleavage."),
    ("02 · SOLUTION", "A 577-D multi-modal framework", CYAN,
     "Orthogonal slot-based chemical ontology decouples sugar, linkage, base, and conjugate states. Combines positional chemistry, RNA foundation models, engineered biophysics, and thermodynamics.",
     "One representation per duplex. One pipeline. Two CatBoost stages. One GNN. One structural filter."),
    ("03 · IMPACT", "From blind heuristics to clinical predictions", TEAL,
     "40,255-assay master corpus. Pearson 0.8049 across 5 folds. Sub-nanomolar IC50 recovered on five FDA-approved drugs without fine-tuning.",
     "CAG-driven ANC. Steric filter pre-screens before wet-lab synthesis.")
]

for idx, (num, h_tit, col, body, foot) in enumerate(cols_s2):
    cx = 0.8 + idx * 3.95
    c = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(cx), Inches(2.0), Inches(3.8), Inches(2.9))
    c.fill.solid()
    c.fill.fore_color.rgb = CARD_BG
    c.line.color.rgb = col
    c.line.width = Pt(1.5)
    
    tf = c.text_frame
    tf.margin_left = Inches(0.2)
    tf.margin_top = Inches(0.18)
    tf.word_wrap = True
    
    p1 = tf.paragraphs[0]
    p1.text = num
    p1.font.size = Pt(8.5)
    p1.font.bold = True
    p1.font.color.rgb = col
    
    p2 = tf.add_paragraph()
    p2.text = h_tit
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.space_after = Pt(8)
    
    p3 = tf.add_paragraph()
    p3.text = body
    p3.font.size = Pt(9.5)
    p3.font.color.rgb = GRAY_LIGHT
    p3.space_after = Pt(10)
    
    p4 = tf.add_paragraph()
    p4.text = foot
    p4.font.size = Pt(8)
    p4.font.color.rgb = GRAY
    p4.font.italic = True

# Headline numbers bottom label
tb_hl = s2.shapes.add_textbox(Inches(0.8), Inches(5.1), Inches(8), Inches(0.25))
p_hl = tb_hl.text_frame.paragraphs[0]
p_hl.text = "HEADLINE NUMBERS"
p_hl.font.size = Pt(8.5)
p_hl.font.bold = True
p_hl.font.color.rgb = GRAY

# 4 KPI cards bottom
kpis_s2 = [
    ("5-FOLD PEARSON R", "0.8049", "across 37,946 measured assays", CYAN, 0.8, 2.8),
    ("MASTER CORPUS", "40,255", "assays · 3,535 unique duplexes", TEAL, 3.8, 2.8),
    ("FDA PANEL", "0.83–2.24 nM", "predicted potency, 5 approved drugs", PURPLE, 6.8, 2.8),
    ("STRUCTURAL FILTER", "PDB 4W5N", "Ago2 3D feasibility pre-screen", AMBER, 9.8, 2.733)
]
for lbl, num, sub, col, kx, kw in kpis_s2:
    kc = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(kx), Inches(5.4), Inches(kw), Inches(1.4))
    kc.fill.solid()
    kc.fill.fore_color.rgb = CARD_BG
    kc.line.color.rgb = CARD_BORDER
    
    tf = kc.text_frame
    tf.margin_left = Inches(0.18)
    tf.margin_top = Inches(0.15)
    
    p1 = tf.paragraphs[0]
    p1.text = lbl
    p1.font.size = Pt(8)
    p1.font.bold = True
    p1.font.color.rgb = GRAY
    
    p2 = tf.add_paragraph()
    p2.text = num
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = col
    
    p3 = tf.add_paragraph()
    p3.text = sub
    p3.font.size = Pt(8.5)
    p3.font.color.rgb = GRAY_LIGHT


# ==========================================
# SLIDE 3: Why This Is Hard (Input_file_2)
# ==========================================
s3 = prs.slides.add_slide(blank)
add_bg(s3)

tb_tag3 = s3.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8), Inches(0.3))
p_t3 = tb_tag3.text_frame.paragraphs[0]
p_t3.text = "// WHY THIS IS HARD"
p_t3.font.size = Pt(10)
p_t3.font.bold = True
p_t3.font.color.rgb = CORAL

tb_tit3 = s3.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.8), Inches(0.6))
p_tit3 = tb_tit3.text_frame.paragraphs[0]
r_a3 = p_tit3.add_run()
r_a3.text = "Therapeutic siRNAs are "
r_a3.font.size = Pt(24)
r_a3.font.bold = True
r_a3.font.color.rgb = WHITE
r_b3 = p_tit3.add_run()
r_b3.text = "not"
r_b3.font.size = Pt(24)
r_b3.font.bold = True
r_b3.font.color.rgb = CORAL
r_c3 = p_tit3.add_run()
r_c3.text = " naked RNA"
r_c3.font.size = Pt(24)
r_c3.font.bold = True
r_c3.font.color.rgb = WHITE

tb_sub3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.8), Inches(0.4))
p_sub3 = tb_sub3.text_frame.paragraphs[0]
p_sub3.text = "Clinical drugs look nothing like the synthetic 21-mers used to train older algorithms. RNA interference has more knobs to turn than target complementarity."
p_sub3.font.size = Pt(11)
p_sub3.font.color.rgb = GRAY_LIGHT

# Left Column (3 cards)
left_cards_s3 = [
    ("1 · 100% of approved siRNAs carry chemical mods",
     "Without 2'-F, 2'-OMe sugar mods and PS backbone linkages, naked RNA is digested in minutes by serum nucleases and triggers innate immune sensors. Clinical drugs lean on these mods to survive dosing schedules.", 1.8),
    ("2 · Modification rules are positional, not binary",
     "A 2'-F at position 14 boosts cleavage. The same substituent at position 9 collides with the Ago2 catalytic triad. One string-of-letters per nucleotide can't capture this.", 3.5),
    ("3 · Dose is not potency",
     "A mediocre siRNA at 100 nM gives 90% knockdown. A potent drug at 0.1 nM gives 50%. Without pIC50, benchmarks conflate exposure with molecular quality.", 5.2)
]
for h_tit, body, cy in left_cards_s3:
    c = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(cy), Inches(5.8), Inches(1.5))
    c.fill.solid()
    c.fill.fore_color.rgb = CARD_BG
    c.line.color.rgb = CARD_BORDER
    tf = c.text_frame
    tf.margin_left = Inches(0.2)
    tf.margin_top = Inches(0.15)
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = h_tit
    p1.font.size = Pt(11)
    p1.font.bold = True
    p1.font.color.rgb = CYAN
    p2 = tf.add_paragraph()
    p2.text = body
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = GRAY_LIGHT

# Right Card: Where chemistry actually matters
c_rt = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.8), Inches(5.633), Inches(4.9))
c_rt.fill.solid()
c_rt.fill.fore_color.rgb = CARD_BG
c_rt.line.color.rgb = CARD_BORDER

tf_rt = c_rt.text_frame
tf_rt.margin_left = Inches(0.25)
tf_rt.margin_top = Inches(0.2)
tf_rt.word_wrap = True

p_r1 = tf_rt.paragraphs[0]
p_r1.text = "A 21-NT DUPLEX · FOUR FUNCTIONAL REGIONS"
p_r1.font.size = Pt(8.5)
p_r1.font.bold = True
p_r1.font.color.rgb = GRAY

p_r2 = tf_rt.add_paragraph()
p_r2.text = "Where the chemistry actually matters"
p_r2.font.size = Pt(14)
p_r2.font.bold = True
p_r2.font.color.rgb = WHITE
p_r2.space_after = Pt(16)

# Embed visual schematic or draw regions
p_r3 = tf_rt.add_paragraph()
p_r3.text = "• Position 1 (5'-Monophosphate): Anchors the Ago2 MID pocket (≤4.5 Å) — without it, silencing is abolished."
p_r3.font.size = Pt(10)
p_r3.font.color.rgb = CYAN
p_r3.space_after = Pt(8)

p_r4 = tf_rt.add_paragraph()
p_r4.text = "• Positions 2–7 (Seed Region): Rigidification with alternating 2'-OMe and 2'-F enhances target mRNA unzipping."
p_r4.font.size = Pt(10)
p_r4.font.color.rgb = TEAL
p_r4.space_after = Pt(8)

p_r5 = tf_rt.add_paragraph()
p_r5.text = "• Positions 9–11 (Cleavage Center): Restrict bulky substituents to preserve catalytic cleavage (Asp669/Glu635/His807)."
p_r5.font.size = Pt(10)
p_r5.font.color.rgb = CORAL
p_r5.space_after = Pt(8)

p_r6 = tf_rt.add_paragraph()
p_r6.text = "• 3'-Overhangs: Phosphorothioate (PS) linkages protect against circulating exonucleases."
p_r6.font.size = Pt(10)
p_r6.font.color.rgb = AMBER
p_r6.space_after = Pt(16)

p_r7 = tf_rt.add_paragraph()
p_r7.text = "Designing clinical siRNAs means reasoning about chemistry, position, dose, and 3D pocket geometry simultaneously."
p_r7.font.size = Pt(10)
p_r7.font.italic = True
p_r7.font.color.rgb = GRAY


# ==========================================
# SLIDE 4: Methodology & Pillars (Input_file_3)
# ==========================================
s4 = prs.slides.add_slide(blank)
add_bg(s4)

tb_tag4 = s4.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8), Inches(0.3))
p_t4 = tb_tag4.text_frame.paragraphs[0]
p_t4.text = "// METHODOLOGY & PILLARS"
p_t4.font.size = Pt(10)
p_t4.font.bold = True
p_t4.font.color.rgb = TEAL

tb_tit4 = s4.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.8), Inches(0.6))
p_tit4 = tb_tit4.text_frame.paragraphs[0]
r_a4 = p_tit4.add_run()
r_a4.text = "Four "
r_a4.font.size = Pt(24)
r_a4.font.bold = True
r_a4.font.color.rgb = WHITE
r_b4 = p_tit4.add_run()
r_b4.text = "co-optimized"
r_b4.font.size = Pt(24)
r_b4.font.bold = True
r_b4.font.color.rgb = CYAN
r_c4 = p_tit4.add_run()
r_c4.text = " dimensions of siRNA efficacy"
r_c4.font.size = Pt(24)
r_c4.font.bold = True
r_c4.font.color.rgb = WHITE

tb_sub4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.8), Inches(0.4))
p_sub4 = tb_sub4.text_frame.paragraphs[0]
p_sub4.text = "HelixZero decouples the problem into four orthogonal engineering pillars. Each does one distinct, verifiable biological job."
p_sub4.font.size = Pt(11)
p_sub4.font.color.rgb = GRAY_LIGHT

# 4 Pillars
pillars_data = [
    ("PILLAR 01", "Sequence screening", CYAN,
     "Target mRNA alignment and isoform specificity across the open reading frame",
     ["• Thermodynamic asymmetry ΔG_5' - ΔG_3' < 0", "• Seed fluidity (positions 2–7)", "• GC clamp balance", "• Off-target seed cytotoxicity filter (4,096 hexamers)"],
     "WHERE IT WORKS", "Naked siRNA triage & fast LightGBM ranking"),
    ("PILLAR 02", "Chemical ontology", TEAL,
     "Six-attribute slot per nucleotide — sugar, linkage, base, terminal, conjugate",
     ["• 2'-F, 2'-OMe, MOE, LNA coexisting", "• Phosphorothioate (PS) backbone linkage", "• Cleavage-sparing central rule (pos 9–11)", "• Triantennary GalNAc liver targeting"],
     "WHERE IT WORKS", "Modified siRNA scoring for clinical chemistry"),
    ("PILLAR 03", "Dose-potency curve", PURPLE,
     "Two-stage hierarchical regressor: intrinsic pIC50 followed by Hill response",
     ["• Predicts pIC50 = -log10 IC50", "• Hill fit across 68 doses (0.00017–1000 nM)", "• Standardized 10 nM clinical benchmark", "• N = 8,159 guide partition test"],
     "WHERE IT WORKS", "Multi-dose clinical translation & guidance"),
    ("PILLAR 04", "Ago2 3D docking", AMBER,
     "Human Argonaute-2 crystal coordinates (PDB 4W5N, 2.90 Å) as geometric veto",
     ["• MID pocket ≤ 4.5 Å", "• PAZ 3'-overhang 12–15 Å", "• PIWI catalytic ≤ 5.5 Å", "• Steric clash detection (≤ 4 clean)"],
     "WHERE IT WORKS", "Pre-synth structural feasibility filter")
]

for idx, (p_num, p_name, col, p_desc, bullets, w_lbl, w_val) in enumerate(pillars_data):
    px = 0.8 + idx * 2.95
    c = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(px), Inches(1.8), Inches(2.8), Inches(4.9))
    c.fill.solid()
    c.fill.fore_color.rgb = CARD_BG
    c.line.color.rgb = CARD_BORDER
    
    tf = c.text_frame
    tf.margin_left = Inches(0.18)
    tf.margin_top = Inches(0.15)
    tf.word_wrap = True
    
    p1 = tf.paragraphs[0]
    p1.text = p_num
    p1.font.size = Pt(8.5)
    p1.font.bold = True
    p1.font.color.rgb = col
    
    p2 = tf.add_paragraph()
    p2.text = p_name
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.space_after = Pt(4)
    
    p3 = tf.add_paragraph()
    p3.text = p_desc
    p3.font.size = Pt(8.5)
    p3.font.color.rgb = GRAY_LIGHT
    p3.space_after = Pt(8)
    
    for b in bullets:
        pb = tf.add_paragraph()
        pb.text = b
        pb.font.size = Pt(8.2)
        pb.font.color.rgb = GRAY_LIGHT
        pb.space_after = Pt(2)
        
    p_w1 = tf.add_paragraph()
    p_w1.space_before = Pt(14)
    p_w1.text = w_lbl
    p_w1.font.size = Pt(8)
    p_w1.font.bold = True
    p_w1.font.color.rgb = col
    
    p_w2 = tf.add_paragraph()
    p_w2.text = w_val
    p_w2.font.size = Pt(8.5)
    p_w2.font.color.rgb = WHITE


# ==========================================
# SLIDE 5: Ten Public Resources (Input_file_4)
# ==========================================
s5 = prs.slides.add_slide(blank)
add_bg(s5)

tb_tag5 = s5.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8), Inches(0.3))
p_t5 = tb_tag5.text_frame.paragraphs[0]
p_t5.text = "// DATA ENGINEERING"
p_t5.font.size = Pt(10)
p_t5.font.bold = True
p_t5.font.color.rgb = CYAN

tb_tit5 = s5.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.8), Inches(0.6))
p_tit5 = tb_tit5.text_frame.paragraphs[0]
r_a5 = p_tit5.add_run()
r_a5.text = "Ten public resources, "
r_a5.font.size = Pt(24)
r_a5.font.bold = True
r_a5.font.color.rgb = WHITE
r_b5 = p_tit5.add_run()
r_b5.text = "four"
r_b5.font.size = Pt(24)
r_b5.font.bold = True
r_b5.font.color.rgb = CYAN
r_c5 = p_tit5.add_run()
r_c5.text = " functional clusters"
r_c5.font.size = Pt(24)
r_c5.font.bold = True
r_c5.font.color.rgb = WHITE

tb_sub5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.8), Inches(0.4))
p_sub5 = tb_sub5.text_frame.paragraphs[0]
p_sub5.text = "40,255 measured assays · 3,535 canonical duplexes · 549 patent/clinical compounds · human Ago2 coordinates"
p_sub5.font.size = Pt(11)
p_sub5.font.color.rgb = GRAY_LIGHT

# 4 Quadrants
quads_data = [
    ("CLUSTER 01", "Canonical sequence benchmarks", CYAN, [
        ("Huesken Gold Standard", "N = 2,361 siRNAs across 34 genes; Novartis Nature Biotech 2005; r = 0.8044"),
        ("Takayuki / siDirect", "N = 702 siRNAs; Katoh & Suzuki, NAR 2007; r = 0.8788"),
        ("Seven-Study Canonical Mixset", "N = 472 siRNAs across Reynolds, Ui-Tei, Amarzguioui, Vickers collections; r = 0.8291")
    ], 0.8, 1.8),
    ("CLUSTER 02", "Multi-dose + chemistry corpus", TEAL, [
        ("CMsiRNAdb master", "40,255 records; 37,946 BRONZE assays at 68 doses + 2,309 GOLD Hill curves; r = 0.8049"),
        ("Foster GalNAc panel", "N = 15 siRNAs; ESC/ESC+ chemistries, Mol Therapy 2018; r = 0.9120"),
        ("CMsiRNAdb 10 nM subset", "N = 472 siRNAs at the standardized 10 nM dose. The same-drug-comparison benchmark.")
    ], 6.8, 1.8),
    ("CLUSTER 03", "Patent & clinical translation", PURPLE, [
        ("FENNEC patent panels", "N = 534 (APP N=343, JAK1 N=191); Alnylam WO2020132227A2 & WO2024256707A1."),
        ("Heterogeneous multi-patent", "N = 2,576 siRNAs across 90 patent disclosures; r = 0.6217"),
        ("FDA-approved commercial", "Patisiran · Givosiran · Inclisiran · Lumasiran · Vutrisiran. Five reference drugs as the clinical yardstick.")
    ], 0.8, 4.4),
    ("CLUSTER 04", "Structural & genomic safety", AMBER, [
        ("Human Ago2 crystal", "PDB 4W5N at 2.90 Å; Schirle & MacRae, Science 2014"),
        ("Reference transcriptome", "863 MB GRCh38 2-bit packed > 40M 30-mer off-target index"),
        ("OligoFormer seed viability", "4,096 hexamers; positions 2–7 miRNA-like seed toxicity pre-filter.")
    ], 6.8, 4.4)
]

for c_tag, c_name, col, items, qx, qy in quads_data:
    qc = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(qx), Inches(qy), Inches(5.733), Inches(2.4))
    qc.fill.solid()
    qc.fill.fore_color.rgb = CARD_BG
    qc.line.color.rgb = CARD_BORDER
    
    tf = qc.text_frame
    tf.margin_left = Inches(0.2)
    tf.margin_top = Inches(0.15)
    tf.word_wrap = True
    
    p1 = tf.paragraphs[0]
    p1.text = c_tag
    p1.font.size = Pt(8)
    p1.font.bold = True
    p1.font.color.rgb = col
    
    p2 = tf.add_paragraph()
    p2.text = c_name
    p2.font.size = Pt(12.5)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.space_after = Pt(6)
    
    for iname, idesc in items:
        pi = tf.add_paragraph()
        r_n = pi.add_run()
        r_n.text = f"{iname}: "
        r_n.font.size = Pt(8.5)
        r_n.font.bold = True
        r_n.font.color.rgb = col
        r_d = pi.add_run()
        r_d.text = idesc
        r_d.font.size = Pt(8)
        r_d.font.color.rgb = GRAY_LIGHT
        pi.space_after = Pt(2)

# Save
out_pptx = Path("d:/Helixx/HelixZero_Genspark_Collaged_Presentation.pptx")
prs.save(out_pptx)
print(f"Collaged deck created at: {out_pptx}")
