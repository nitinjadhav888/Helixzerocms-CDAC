"""
generate_pristine_fig2_siRNA_anatomy.py
=======================================
Generates a biologically rigorous, publication-grade (300 DPI) schematic of:
1. Canonical Antiparallel Therapeutic siRNA Duplex Architecture (ESC/ESC+)
2. Human Argonaute-2 (Ago2) Functional Anatomy & mRNA Slicing Mechanism
3. Chemical Modification Taxonomy & Biophysical Rules
"""

import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle

ROOT_DIR = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT_DIR / "paper_figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']


def generate_pristine_fig2():
    fig = plt.figure(figsize=(16, 14.5), dpi=300)
    gs = fig.add_gridspec(3, 1, height_ratios=[4.0, 5.2, 2.3], hspace=0.32)

    # Color Scheme
    c_bg = '#f8fafc'
    c_card = '#ffffff'
    c_border = '#cbd5e1'
    c_title = '#0f2942'
    
    c_sense = '#1e3a8a'      # Deep Navy (Sense Strand)
    c_guide = '#0f766e'      # Deep Teal (Guide Strand)
    c_ome = '#f59e0b'        # Amber Gold (2'-OMe)
    c_fluoro = '#0284c7'     # Sky Blue (2'-F)
    c_gna = '#10b981'        # Emerald Green (GNA)
    c_ps = '#ef4444'         # Vivid Red (PS)
    c_vp = '#8b5cf6'         # Violet/Purple (5'-VP)
    c_galnac = '#ea580c'     # Orange (GalNAc)
    c_target = '#db2777'     # Magenta (Target mRNA)
    
    c_mid = '#f43f5e'        # Rose (Ago2 MID)
    c_piwi = '#d97706'       # Amber (Ago2 PIWI)
    c_paz = '#6366f1'        # Indigo (Ago2 PAZ)
    c_seed = '#2563eb'       # Seed Blue

    # =========================================================================
    # PANEL A: ANTIPARALLEL DUPLEX ARCHITECTURE & CHEMICAL MODIFICATIONS
    # =========================================================================
    ax1 = fig.add_subplot(gs[0])
    ax1.set_xlim(-5.2, 25.5)
    ax1.set_ylim(-1.5, 5.2)
    ax1.axis('off')

    # Card background
    ax1.add_patch(FancyBboxPatch((-5.0, -1.4), 30.2, 6.4, boxstyle="round,pad=0.03",
                                 facecolor=c_bg, edgecolor=c_border, lw=1.2, zorder=0))

    # Panel Title & Description
    ax1.text(-4.6, 4.75, 'A. Antiparallel Therapeutic siRNA Duplex Topology & Positional Chemical Architecture (ESC/ESC+)', 
             fontsize=11.5, fontweight='bold', color=c_title)
    ax1.text(-4.6, 4.30, 'Canonical 21-mer Duplex (19-bp Watson-Crick Hybridization Core + 2-nt 3\'-Overhangs) with Alternating 2\'-OMe / 2\'-F, GNA@7, and 3\'-GalNAc3', 
             fontsize=8.5, color='#475569', style='italic')

    # ---------------- SENSE (PASSENGER) STRAND (TOP): 5' -> 3' ----------------
    y_sense = 2.6
    ax1.text(-2.0, y_sense, 'Passenger (Sense)\n[ 5\' -> 3\' ]', ha='right', va='center', fontsize=8.2, fontweight='bold', color=c_sense)
    ax1.text(21.7, y_sense, "3'", ha='left', va='center', fontsize=9.5, fontweight='bold', color=c_galnac)

    # Sense Backbone Line
    ax1.plot([0.8, 21.2], [y_sense, y_sense], color='#94a3b8', lw=2.5, zorder=1)

    # Sense Modifications (Alnylam ESC design: alternating OMe / F)
    sense_mods = ['OMe', 'F', 'OMe', 'F', 'OMe', 'F', 'OMe', 'F', 'OMe', 'F', 'OMe', 'F', 'OMe', 'F', 'OMe', 'F', 'OMe', 'F', 'OMe', 'OMe', 'OMe']

    for i in range(1, 22):
        mod = sense_mods[i-1]
        col = c_ome if mod == 'OMe' else c_fluoro
        ax1.add_patch(FancyBboxPatch((i - 0.38, y_sense - 0.28), 0.76, 0.56, boxstyle='round,pad=0.03',
                                     facecolor=col, edgecolor='#1e293b', lw=0.9, zorder=3))
        ax1.text(i, y_sense, f's{i}', ha='center', va='center', fontsize=7.2, fontweight='bold', color='white', zorder=4)

    # Sense 5' PS linkages (s1-s2, s2-s3)
    ax1.plot(1.5, y_sense, marker='d', markersize=5.5, color=c_ps, zorder=5)
    ax1.plot(2.5, y_sense, marker='d', markersize=5.5, color=c_ps, zorder=5)

    # Sense 3' GalNAc Conjugate
    ax1.plot([21.4, 22.4], [y_sense, y_sense], color=c_galnac, lw=2.5, zorder=2)
    ax1.add_patch(FancyBboxPatch((22.4, y_sense - 0.35), 1.25, 0.70, boxstyle='round,pad=0.04',
                                 facecolor='#ffedd5', edgecolor=c_galnac, lw=1.3, zorder=3))
    ax1.text(23.02, y_sense, 'Triantennary\nGalNAc3 (L10)', ha='center', va='center', fontsize=6.8, fontweight='bold', color='#c2410c', zorder=4)

    # ---------------- GUIDE (ANTISENSE) STRAND (BOTTOM): 3' <- 5' ----------------
    y_guide = 0.9
    ax1.text(-2.0, y_guide, 'Guide (Antisense)\n[ 3\' <- 5\' ]', ha='right', va='center', fontsize=8.2, fontweight='bold', color=c_guide)
    ax1.text(20.3, y_guide, "5'", ha='left', va='center', fontsize=9.5, fontweight='bold', color=c_vp)

    # Guide Backbone Line
    ax1.plot([-1.2, 19.2], [y_guide, y_guide], color='#94a3b8', lw=2.5, zorder=1)

    guide_map = {}
    for g_idx in range(1, 22):
        x_pos = 20 - g_idx  # g1 -> x=19, g19 -> x=1, g20 -> x=0, g21 -> x=-1
        if g_idx == 7:
            mod = 'GNA'
        elif g_idx in [2, 4, 6, 10, 14, 16]:
            mod = 'F'
        else:
            mod = 'OMe'
        guide_map[g_idx] = (x_pos, mod)

    for g_idx, (x_pos, mod) in guide_map.items():
        if mod == 'GNA':
            col = c_gna
        elif mod == 'F':
            col = c_fluoro
        else:
            col = c_ome
        ax1.add_patch(FancyBboxPatch((x_pos - 0.38, y_guide - 0.28), 0.76, 0.56, boxstyle='round,pad=0.03',
                                     facecolor=col, edgecolor='#1e293b', lw=0.9, zorder=3))
        ax1.text(x_pos, y_guide, f'g{g_idx}', ha='center', va='center', fontsize=7.2, fontweight='bold', color='white', zorder=4)

    # Guide 5' 5'-VP / Monophosphate Cap at g1 (x=19)
    ax1.add_patch(Circle((19.7, y_guide), 0.28, facecolor='#ede9fe', edgecolor=c_vp, lw=1.3, zorder=3))
    ax1.text(19.7, y_guide, '5\'VP', ha='center', va='center', fontsize=6.2, fontweight='bold', color=c_vp, zorder=4)

    # Guide 5' PS linkages (between g1-g2 (x=18.5) and g2-g3 (x=17.5))
    ax1.plot(18.5, y_guide, marker='d', markersize=5.5, color=c_ps, zorder=5)
    ax1.plot(17.5, y_guide, marker='d', markersize=5.5, color=c_ps, zorder=5)

    # Guide 3' PS linkages (between g20-g21 (x=-0.5) and g19-g20 (x=0.5))
    ax1.plot(-0.5, y_guide, marker='d', markersize=5.5, color=c_ps, zorder=5)
    ax1.plot(0.5, y_guide, marker='d', markersize=5.5, color=c_ps, zorder=5)

    # Watson-Crick Base Pair Hydrogen Bonds (x = 1 to 19)
    for x in range(1, 20):
        ax1.plot([x, x], [y_guide + 0.32, y_sense - 0.32], color='#64748b', lw=1.1, linestyle='--', zorder=2)
        ax1.plot(x, (y_guide + y_sense)/2, marker='.', markersize=3.5, color='#94a3b8', zorder=2)

    # 19 bp Core Duplex Bracket (Top)
    ax1.annotate('', xy=(1, 3.45), xytext=(19, 3.45),
                 arrowprops=dict(arrowstyle='<->', color='#334155', lw=1.2))
    ax1.text(10, 3.62, '19-bp Watson-Crick Hybridization Core Duplex', ha='center', va='bottom', fontsize=8.2, fontweight='bold', color='#334155')

    # Overhang Indicators
    # Guide 3' overhang (x = -1, 0)
    ax1.add_patch(FancyBboxPatch((-1.45, y_guide - 0.42), 1.9, 0.84, boxstyle='round,pad=0.03',
                                 facecolor='none', edgecolor=c_guide, lw=1.1, linestyle=':', zorder=2))
    ax1.text(-0.5, y_guide - 0.62, "2-nt 3'-Overhang\n(g20-g21)", ha='center', va='top', fontsize=7.0, fontweight='bold', color=c_guide)

    # Sense 3' overhang (x = 20, 21)
    ax1.add_patch(FancyBboxPatch((19.55, y_sense - 0.42), 1.9, 0.84, boxstyle='round,pad=0.03',
                                 facecolor='none', edgecolor=c_sense, lw=1.1, linestyle=':', zorder=2))
    ax1.text(20.5, y_sense - 0.62, "2-nt 3'-Overhang\n(s20-s21)", ha='center', va='top', fontsize=7.0, fontweight='bold', color=c_sense)

    # =========================================================================
    # PANEL B: AGO2 FUNCTIONAL DOMAINS & MRNA SLICING DYNAMICS
    # =========================================================================
    ax2 = fig.add_subplot(gs[1])
    ax2.set_xlim(-5.2, 25.5)
    ax2.set_ylim(-2.0, 5.5)
    ax2.axis('off')

    ax2.add_patch(FancyBboxPatch((-5.0, -1.9), 30.2, 7.2, boxstyle="round,pad=0.03",
                                 facecolor=c_card, edgecolor=c_border, lw=1.2, zorder=0))

    # Panel Title & Description
    ax2.text(-4.6, 5.05, 'B. Human Argonaute-2 (Ago2) Structural Anatomy & Target mRNA Slicing Mechanism', 
             fontsize=11.5, fontweight='bold', color=c_title)
    ax2.text(-4.6, 4.65, 'Loaded Guide RNA in RISC (5\' -> 3\') Engaging Target mRNA with Ago2 MID, Seed, PIWI Catalytic Tetrad, and PAZ Domains', 
             fontsize=8.5, color='#475569', style='italic')

    y_risc_g = 1.6
    y_risc_t = 3.0

    ax2.text(-0.6, y_risc_t, 'Target mRNA\n[ 3\' <- 5\' ]', ha='right', va='center', fontsize=8.0, fontweight='bold', color=c_target)
    ax2.text(19.7, y_risc_t, "5'", ha='left', va='center', fontsize=9.5, fontweight='bold', color=c_target)

    ax2.text(-0.6, y_risc_g, 'Loaded Guide\n[ 5\' -> 3\' ]', ha='right', va='center', fontsize=8.0, fontweight='bold', color=c_guide)
    ax2.text(21.7, y_risc_g, "3'", ha='left', va='center', fontsize=9.5, fontweight='bold', color=c_paz)

    # Target mRNA Backbone Line (Scission at position 10-11)
    ax2.plot([0.8, 10.3], [y_risc_t, y_risc_t], color=c_target, lw=2.5, zorder=1)
    ax2.plot([10.7, 19.2], [y_risc_t, y_risc_t], color=c_target, lw=2.5, zorder=1)

    # Guide Backbone Line in RISC
    ax2.plot([0.8, 21.2], [y_risc_g, y_risc_g], color='#94a3b8', lw=2.5, zorder=1)

    # Draw Target mRNA Nucleotides (t1 opposite g19 ... t19 opposite g1)
    for g_idx in range(1, 20):
        x = g_idx
        t_idx = 20 - g_idx
        ax2.add_patch(FancyBboxPatch((x - 0.38, y_risc_t - 0.28), 0.76, 0.56, boxstyle='round,pad=0.03',
                                     facecolor='#fce7f3', edgecolor=c_target, lw=0.9, zorder=3))
        ax2.text(x, y_risc_t, f't{t_idx}', ha='center', va='center', fontsize=7.0, fontweight='bold', color='#9d174d', zorder=4)
        # Base-pairing lines
        ax2.plot([x, x], [y_risc_g + 0.32, y_risc_t - 0.32], color='#f472b6', lw=1.1, linestyle='--', zorder=2)

    # Draw Guide Nucleotides in RISC (g1 to g21)
    for g_idx in range(1, 22):
        x = g_idx
        if g_idx == 7:
            mod = 'GNA'
            col = c_gna
        elif g_idx in [2, 4, 6, 10, 14, 16]:
            mod = 'F'
            col = c_fluoro
        else:
            mod = 'OMe'
            col = c_ome
        ax2.add_patch(FancyBboxPatch((x - 0.38, y_risc_g - 0.28), 0.76, 0.56, boxstyle='round,pad=0.03',
                                     facecolor=col, edgecolor='#1e293b', lw=0.9, zorder=3))
        ax2.text(x, y_risc_g, f'g{g_idx}', ha='center', va='center', fontsize=7.2, fontweight='bold', color='white', zorder=4)

    # 5'-VP Cap at g1
    ax2.add_patch(Circle((0.25, y_risc_g), 0.28, facecolor='#ede9fe', edgecolor=c_vp, lw=1.3, zorder=3))
    ax2.text(0.25, y_risc_g, '5\'VP', ha='center', va='center', fontsize=6.2, fontweight='bold', color=c_vp, zorder=4)

    # Slicing Arrow & Annotation (Properly offset below title)
    ax2.annotate('⚡ Catalytic Slicing Point\n(Asp597, Glu638, Asp669, His807)', xy=(10.5, y_risc_t + 0.2), xytext=(10.5, 4.05),
                 ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#dc2626',
                 arrowprops=dict(facecolor='#dc2626', edgecolor='#dc2626', shrink=0.08, width=1.5, headwidth=5),
                 zorder=6)

    # --- AGO2 DOMAIN ANNOTATIONS (BOTTOM BOXES) ---
    # 1. Ago2 MID Pocket (g1)
    ax2.add_patch(FancyBboxPatch((0.45, y_risc_g - 1.15), 1.1, 0.75, boxstyle='round,pad=0.03',
                                 facecolor='#ffe4e6', edgecolor=c_mid, lw=1.3, zorder=2))
    ax2.text(1.0, y_risc_g - 0.78, "Ago2 MID\nDomain", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#be123c')
    ax2.text(1.0, y_risc_g - 1.45, "5'-VP / pU\nAnchor", ha='center', va='top', fontsize=6.5, color='#881337')

    # 2. Seed Region (g2 - g8)
    ax2.add_patch(FancyBboxPatch((1.65, y_risc_g - 1.15), 6.9, 0.75, boxstyle='round,pad=0.03',
                                 facecolor='#eff6ff', edgecolor=c_seed, lw=1.3, zorder=2))
    ax2.text(4.2, y_risc_g - 0.78, "Seed Region (Positions g2–g8)", ha='center', va='center', fontsize=7.6, fontweight='bold', color='#1d4ed8')
    ax2.text(5.1, y_risc_g - 1.45, "Pre-organized A-form; controls on-target &\nmicroRNA seed off-target binding", ha='center', va='top', fontsize=6.5, color='#1e3a8a', linespacing=1.2)

    # Highlight GNA@7 inside seed
    ax2.add_patch(FancyBboxPatch((6.8, y_risc_g - 1.05), 1.6, 0.55, boxstyle='round,pad=0.02',
                                 facecolor='#d1fae5', edgecolor=c_gna, lw=1.1, zorder=3))
    ax2.text(7.6, y_risc_g - 0.78, "★ GNA@7", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#047857', zorder=4)

    # 3. Ago2 PIWI Slicing Center (g10 - g11)
    ax2.add_patch(FancyBboxPatch((9.45, y_risc_g - 1.15), 2.1, 0.75, boxstyle='round,pad=0.03',
                                 facecolor='#fef3c7', edgecolor=c_piwi, lw=1.3, zorder=2))
    ax2.text(10.5, y_risc_g - 0.78, "PIWI Domain\nCatalytic Center", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#b45309')
    ax2.text(10.5, y_risc_g - 1.45, "Sterically sensitive\n(positions 10–11)", ha='center', va='top', fontsize=6.5, color='#78350f', linespacing=1.2)

    # 4. Supplementary / Tail (g12 - g18)
    ax2.add_patch(FancyBboxPatch((12.1, y_risc_g - 1.15), 6.8, 0.75, boxstyle='round,pad=0.03',
                                 facecolor='#f0fdf4', edgecolor=c_guide, lw=1.3, zorder=2))
    ax2.text(15.5, y_risc_g - 0.78, "Supplementary / Central Region (g12–g18)", ha='center', va='center', fontsize=7.4, fontweight='bold', color=c_guide)
    ax2.text(15.5, y_risc_g - 1.45, "Stabilizes guide:target duplex;\nhigh 2'-OMe / 2'-F tolerance", ha='center', va='top', fontsize=6.5, color='#14532d', linespacing=1.2)

    # 5. Ago2 PAZ Pocket (g20 - g21)
    ax2.add_patch(FancyBboxPatch((19.45, y_risc_g - 1.15), 2.1, 0.75, boxstyle='round,pad=0.03',
                                 facecolor='#e0e7ff', edgecolor=c_paz, lw=1.3, zorder=2))
    ax2.text(20.5, y_risc_g - 0.78, "Ago2 PAZ\nDomain", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#4338ca')
    ax2.text(20.5, y_risc_g - 1.45, "Clamps 3'\ndinucleotide", ha='center', va='top', fontsize=6.5, color='#312e81', linespacing=1.2)

    # =========================================================================
    # PANEL C: CHEMICAL TAXONOMY & BIOPHYSICAL PENALTY RULES
    # =========================================================================
    ax3 = fig.add_subplot(gs[2])
    ax3.set_xlim(-5.2, 25.5)
    ax3.set_ylim(-0.5, 2.5)
    ax3.axis('off')

    ax3.add_patch(FancyBboxPatch((-5.0, -0.4), 30.2, 2.8, boxstyle="round,pad=0.03",
                                 facecolor=c_bg, edgecolor=c_border, lw=1.2, zorder=0))

    ax3.text(-4.6, 2.1, 'C. Chemical Modification Classes, Biological Mechanism & HelixZero Deterministic Penalty Rules', 
             fontsize=11.0, fontweight='bold', color=c_title)

    # 5 Legend Cards with exact width and spacing
    card_width = 5.6
    cards = [
        ("2'-O-Methyl (2'-OMe)", c_ome, "• C3'-endo nuclease barrier\n• Suppresses TLR7/8 immune activation\n• Heavy placement at seed/PIWI penalized"),
        ("2'-Fluoro (2'-F)", c_fluoro, "• High binding affinity (+1.0°C Tm/mod)\n• Strict A-form helical locking\n• High content in seed & cleavage center"),
        ("Phosphorothioate (PS)", c_ps, "• Serum exonuclease shielding (3'/5')\n• Promotes plasma protein binding\n• Internal runs penalized (cytotoxicity)"),
        ("Glycol Nucleic Acid (GNA)", c_gna, "• Acyclic sugar; seed destabilizer (-5°C)\n• Abolishes microRNA-like off-target\n• ESC+ credit (-2.0 penalty at g7)"),
        ("Triantennary GalNAc / 5'-VP", c_galnac, "• High-affinity ASGPR liver targeting\n• 5'-VP locks into Ago2 MID pocket\n• Enables subcutaneous clinical dosing")
    ]

    for idx, (head, col, desc) in enumerate(cards):
        x_card = -4.6 + idx * (card_width + 0.35)
        ax3.add_patch(FancyBboxPatch((x_card, -0.25), card_width, 2.1, boxstyle="round,pad=0.03",
                                     facecolor='#ffffff', edgecolor=col, lw=1.3, zorder=1))
        # Top pill
        ax3.add_patch(FancyBboxPatch((x_card + 0.15, 1.45), card_width - 0.3, 0.35, boxstyle="round,pad=0.02",
                                     facecolor=col, edgecolor='none', zorder=2))
        ax3.text(x_card + card_width/2, 1.62, head, ha='center', va='center', fontsize=7.2, fontweight='bold', color='white', zorder=3)
        ax3.text(x_card + 0.25, 0.60, desc, ha='left', va='center', fontsize=6.6, color='#1e293b', zorder=2, linespacing=1.35)

    plt.tight_layout()
    p = FIG_DIR / "Fig2_siRNA_Functional_Anatomy.png"
    plt.savefig(p, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Successfully generated pristine figure: {p}")


if __name__ == '__main__':
    generate_pristine_fig2()
