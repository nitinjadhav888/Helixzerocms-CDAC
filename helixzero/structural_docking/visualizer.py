"""
helixzero.structural_docking.visualizer
=======================================
3D Structural Visualization and Rendering Script Generator for PyMOL and 3Dmol.js.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional


class DockingVisualizer:
    """
    Generates automated PyMOL scripts and interactive 3Dmol.js visualizations.
    """

    @staticmethod
    def generate_pymol_script(pdb_filename: str, output_pml_path: Path) -> str:
        """
        Emits a publication-ready PyMOL macro script for rendering the docked hAgo2 complex.
        """
        script = f"""# PyMOL Rendering Script for HelixZero hAgo2 Docked siRNA Complex
load {pdb_filename}, ago2_complex

# Styling
hide everything, ago2_complex
show cartoon, chain A
color gray80, chain A

# Highlight Active Site Pockets
select mid_pocket, chain A and resi 526+529+533+545+570
show surface, mid_pocket
color marine, mid_pocket

select piwi_catalytic, chain A and resi 597+637+669+807
show surface, piwi_catalytic
color firebrick, piwi_catalytic

select paz_pocket, chain A and resi 294+314+336
show surface, paz_pocket
color forest, paz_pocket

# Guide (Antisense) Strand
show sticks, chain A_guide or chain B
color cyan, chain A_guide or chain B

# Passenger (Sense) Strand
show sticks, chain S
color orange, chain S

# Set View & Lighting
bg_color white
set ray_shadows, 1
set cartoon_transparency, 0.4, chain A
zoom chain A_guide or chain B, 5
"""
        with open(output_pml_path, "w", encoding="utf-8") as f:
            f.write(script)
        return script

    @staticmethod
    def generate_3dmol_html(pdb_content: str) -> str:
        """
        Emits a standalone responsive HTML snippet containing interactive 3Dmol.js viewer.
        """
        escaped_pdb = pdb_content.replace("`", "\\`").replace("$", "\\$")
        html = f"""<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.4/3Dmol-min.js"></script>
    <style>
        .mol-container {{ width: 100%; height: 500px; position: relative; background: #0f172a; border-radius: 12px; }}
    </style>
</head>
<body>
    <div id="ago2_viewer" class="mol-container"></div>
    <script>
        let viewer = $3Dmol.createViewer("ago2_viewer", {{ defaultcolors: $3Dmol.rasmolElementColors }});
        let pdbData = `{escaped_pdb}`;
        viewer.addModel(pdbData, "pdb");
        viewer.setStyle({{chain: 'A'}}, {{cartoon: {{color: 'lightgray', opacity: 0.7}}}});
        viewer.setStyle({{chain: 'A', resi: [526, 529, 533, 545, 570]}}, {{surface: {{color: 'blue', opacity: 0.5}}}});
        viewer.setStyle({{chain: 'A', resi: [597, 637, 669, 807]}}, {{surface: {{color: 'red', opacity: 0.5}}}});
        viewer.setStyle({{chain: 'B'}}, {{stick: {{colorscheme: 'cyanCarbon'}}}});
        viewer.setStyle({{chain: 'S'}}, {{stick: {{colorscheme: 'orangeCarbon'}}}});
        viewer.zoomTo();
        viewer.render();
    </script>
</body>
</html>
"""
        return html
