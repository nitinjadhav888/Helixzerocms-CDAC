import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT_DIR / "paper_figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# -------------------------------------------------------------
# FIG 1: System Architecture Diagram (IEEE Hierarchical Multi-Model)
# -------------------------------------------------------------
def generate_fig1():
    fig, ax = plt.subplots(figsize=(10, 6.8), dpi=300)
    ax.axis('off')
    
    # Background card
    ax.add_patch(patches.Rectangle((0.02, 0.02), 0.96, 0.96, transform=ax.transAxes,
                                   facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.5, zorder=0))
    
    # Header box
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.88), 0.90, 0.08, boxstyle="round,pad=0.01",
                                        facecolor='#0f2942', edgecolor='none', transform=ax.transAxes))
    ax.text(0.5, 0.92, "HelixZero IEEE: Multi-Stage Hierarchical Biophysical ML Architecture", 
            ha='center', va='center', color='white', fontsize=12, fontweight='bold', transform=ax.transAxes)
    
    # Input box
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.75), 0.90, 0.08, boxstyle="round,pad=0.01",
                                        facecolor='#e2e8f0', edgecolor='#94a3b8', transform=ax.transAxes))
    ax.text(0.5, 0.79, "Input mRNA / FASTA Sequence & Multi-Slot NucSlot Dissection (2'-OMe, 2'-F, PS, GNA, GalNAc)",
            ha='center', va='center', color='#0f172a', fontsize=9.5, fontweight='bold', transform=ax.transAxes)
    
    # Left Column: Canonical Naked Branch
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.40), 0.38, 0.30, boxstyle="round,pad=0.01",
                                        facecolor='#eff6ff', edgecolor='#3b82f6', linewidth=1.5, transform=ax.transAxes))
    ax.text(0.24, 0.66, "Canonical Naked RNA Branch", ha='center', va='center', color='#1e3a8a', fontsize=9.5, fontweight='bold', transform=ax.transAxes)
    ax.text(0.24, 0.58, "214-dim Sequence Descriptors\n(One-Hot + TNC + GC + Nearest-NN)", ha='center', va='center', color='#1e293b', fontsize=8.2, transform=ax.transAxes)
    ax.text(0.24, 0.47, "Model 1: Naked LightGBM\n(r = 0.8788 on Takayuki,\nr = 0.8044 on Huesken)", ha='center', va='center', color='#1d4ed8', fontsize=8.2, fontweight='bold', transform=ax.transAxes)

    # Right Column: HelixZero IEEE Multi-Stage Stack
    ax.add_patch(patches.FancyBboxPatch((0.47, 0.40), 0.48, 0.30, boxstyle="round,pad=0.01",
                                        facecolor='#f0fdf4', edgecolor='#22c55e', linewidth=1.5, transform=ax.transAxes))
    ax.text(0.71, 0.66, "HelixZero IEEE Hierarchical Stack", ha='center', va='center', color='#14532d', fontsize=9.5, fontweight='bold', transform=ax.transAxes)
    ax.text(0.71, 0.58, "Stage 1 (Mod 2): Intrinsic pIC50 Engine (CatBoost)\nStage 2 (Mod 3): Dose-Aware Knockdown % (CatBoost)\n3D GNN (Mod 4): PyG MEG-mod TransformerConv", ha='center', va='center', color='#1e293b', fontsize=8.0, transform=ax.transAxes)
    ax.text(0.71, 0.47, "Multi-Slot CatBoost v4 (r = 0.7401, AUC = 0.8745)\n577-dim Vector: 444d Chem + 128d FM/Ernie + 5d VR", ha='center', va='center', color='#15803d', fontsize=8.0, fontweight='bold', transform=ax.transAxes)

    # Middle biophysical layer
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.19), 0.90, 0.16, boxstyle="round,pad=0.01",
                                        facecolor='#fffbeb', edgecolor='#f59e0b', linewidth=1.5, transform=ax.transAxes))
    ax.text(0.5, 0.30, "5-Domain Biophysical Adjustment & Calibration Engine (Score_adj = Score_ML - 0.70 * Sum(P_d))", 
            ha='center', va='center', color='#78350f', fontsize=9.2, fontweight='bold', transform=ax.transAxes)
    ax.text(0.5, 0.23, "• Nuclease Protection (0-16)  • Innate Immuno Suppression (0-20)  • RISC/Ago2 Cleavage + GNA@7 Bonus (-10 to 60)\n• Thermodynamic Asymmetry (0-20)  • Serum Exonuclease Persistence (0-17)",
            ha='center', va='center', color='#92400e', fontsize=8.0, transform=ax.transAxes)

    # Output bottom box
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.04), 0.90, 0.11, boxstyle="round,pad=0.01",
                                        facecolor='#0f2942', edgecolor='none', transform=ax.transAxes))
    ax.text(0.5, 0.095, "Outputs: Intrinsic pIC50 | Dose-Dependent % Knockdown | Combinatorial Multi-Mod Leads | Safety Labels",
            ha='center', va='center', color='white', fontsize=9.5, fontweight='bold', transform=ax.transAxes)

    plt.tight_layout()
    p = FIG_DIR / "Fig1_System_Architecture.png"
    plt.savefig(p, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated {p}")

# -------------------------------------------------------------
# FIG 2: Structural siRNA Duplex Anatomy
# -------------------------------------------------------------
def generate_fig2():
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.set_xlim(0, 23)
    ax.set_ylim(0, 7)
    ax.axis('off')

    ax.text(11.5, 6.3, "Structural Functional Anatomy of Clinical siRNA Duplex Architecture", 
            ha='center', va='center', fontsize=11, fontweight='bold', color='#0f2942')

    # Guide strand (Antisense) 5' -> 3'
    ax.text(0.5, 4.5, "5'-End\n(5'-VP Cap)", ha='center', va='center', fontsize=8, fontweight='bold', color='#c026d3')
    ax.plot([1.5, 21.5], [4.5, 4.5], color='#475569', lw=4, zorder=1)
    
    # Passenger strand (Sense) 3' <- 5'
    ax.plot([1.5, 21.5], [2.5, 2.5], color='#475569', lw=4, zorder=1)
    ax.text(22.2, 2.5, "3'-End\n(GalNAc)", ha='center', va='center', fontsize=8, fontweight='bold', color='#d97706')

    # Base pairs
    for i in range(2, 21):
        ax.plot([i, i], [2.6, 4.4], color='#94a3b8', lw=1.5, linestyle=':')

    # Pos 1: Ago2 MID Anchor
    ax.add_patch(patches.Rectangle((1.6, 4.1), 0.8, 0.8, facecolor='#f43f5e', alpha=0.3, edgecolor='#e11d48', lw=1.5))
    ax.text(2.0, 5.3, "Pos 1\nAgo2 MID Anchor", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#be123c')

    # Pos 2-8: Seed Region
    ax.add_patch(patches.Rectangle((2.6, 4.1), 6.8, 0.8, facecolor='#3b82f6', alpha=0.25, edgecolor='#2563eb', lw=1.5))
    ax.text(6.0, 5.3, "Positions 2–8: Seed Region (Target 3'-UTR Binding)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1d4ed8')

    # Pos 7: GNA@7 Modification
    ax.add_patch(patches.Circle((7.0, 4.5), 0.35, facecolor='#10b981', edgecolor='#047857', lw=1.5))
    ax.text(7.0, 3.5, "GNA@7\n(ESC+ Bonus)", ha='center', va='center', fontsize=7, fontweight='bold', color='#047857')

    # Pos 10-11: Catalytic Cleavage Site
    ax.add_patch(patches.Rectangle((10.6, 4.1), 1.8, 0.8, facecolor='#eab308', alpha=0.3, edgecolor='#ca8a04', lw=1.5))
    ax.text(11.5, 5.3, "Pos 10–11\nAgo2 Slicing Site", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#a16207')

    # Terminal PS linkages
    ax.text(2.0, 1.6, "Terminal Phosphorothioates (PS)\n(Exonuclease Shielding)", ha='center', va='center', fontsize=7.5, color='#475569')
    ax.text(20.0, 1.6, "3'-Overhangs (2 nt)\n(Dicer Recognition)", ha='center', va='center', fontsize=7.5, color='#475569')

    plt.tight_layout()
    p = FIG_DIR / "Fig2_siRNA_Functional_Anatomy.png"
    plt.savefig(p, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated {p}")

# -------------------------------------------------------------
# FIG 3: Feature Architecture Breakdown
# -------------------------------------------------------------
def generate_fig3():
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    
    categories = ['Multi-Slot Chemical\nPositional Flags', 'Domain-Engineered\nBiophysical Feats', 'RNA-FM 650M\nPCA Embeddings', 'RNA-Ernie Transformer\nPCA Embeddings', 'ViennaRNA\nThermodynamics']
    dimensions = [420, 24, 64, 64, 5]
    colors_list = ['#3b82f6', '#60a5fa', '#10b981', '#34d399', '#f59e0b']

    bars = ax.barh(categories, dimensions, color=colors_list, edgecolor='#334155', height=0.6)
    ax.set_xlabel('Feature Dimensionality (Total: 577 Dimensions)', fontsize=9.5, fontweight='bold', color='#0f2942')
    ax.set_title('HelixZero IEEE 577-Dimensional Hybrid Feature Architecture', fontsize=11, fontweight='bold', color='#0f2942')
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    for bar, d in zip(bars, dimensions):
        ax.text(bar.get_width() + 8, bar.get_y() + bar.get_height()/2, f"{d} dims ({d/577*100:.1f}%)", 
                va='center', ha='left', fontsize=8.5, fontweight='bold', color='#1e293b')

    ax.set_xlim(0, 480)
    plt.tight_layout()
    p = FIG_DIR / "Fig3_Feature_Architecture.png"
    plt.savefig(p, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated {p}")

# -------------------------------------------------------------
# FIG 4: Empirical Benchmark Summary Across 7 Datasets
# -------------------------------------------------------------
def generate_fig4():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

    # Left: Canonical Naked RNA Datasets (Model 1)
    datasets_naked = ['Huesken Gold\n(N=2,361)', 'Takayuki Transfer\n(N=702)', 'Mixset 7-Study\n(N=472)']
    r_naked = [0.8044, 0.8788, 0.8291]
    auc_naked = [0.9099, 0.9275, 0.9456]

    x = np.arange(len(datasets_naked))
    width = 0.35

    ax1.bar(x - width/2, r_naked, width, label='Pearson r', color='#2563eb')
    ax1.bar(x + width/2, auc_naked, width, label='ROC-AUC', color='#60a5fa')
    ax1.set_title('Canonical Unmodified RNA (Model 1 GBDT)', fontsize=9.5, fontweight='bold', color='#0f2942')
    ax1.set_xticks(x)
    ax1.set_xticklabels(datasets_naked, fontsize=8)
    ax1.set_ylim(0.5, 1.0)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    ax1.legend(loc='lower right', fontsize=8)

    # Right: Chemically Modified RNA Datasets (Model 2 CatBoost v4)
    datasets_mod = ['CMsiRNAdb Homo\n(N=472)', 'CMsiRNAdb Hetero\n(N=2,576)', 'CMsiRNAdb Full\n(N=5,000)']
    r_mod = [0.7401, 0.6217, 0.6341]
    auc_mod = [0.8745, 0.8077, 0.8045]

    x2 = np.arange(len(datasets_mod))
    ax2.bar(x2 - width/2, r_mod, width, label='Pearson r', color='#059669')
    ax2.bar(x2 + width/2, auc_mod, width, label='ROC-AUC', color='#34d399')
    ax2.set_title('Chemically Modified RNA (Model 2 CatBoost v4)', fontsize=9.5, fontweight='bold', color='#0f2942')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(datasets_mod, fontsize=8)
    ax2.set_ylim(0.5, 1.0)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    ax2.legend(loc='lower right', fontsize=8)

    plt.tight_layout()
    p = FIG_DIR / "Fig4_Empirical_Benchmarks.png"
    plt.savefig(p, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated {p}")

if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
    generate_fig4()
    print("All figures generated successfully in paper_figures/!")
