"""
helixzero.structural_docking.ago2_receptor
==========================================
Receptor Model and Catalytic Pocket Geometry for Human Argonaute-2 (hAgo2).

Derived from the pristine 2.2 Å crystallographic structure of Human Argonaute-2
in complex with guide and target RNA (PDB ID: 4W5N).
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
from Bio.PDB import PDBParser, Structure, Model, Chain, Residue, Atom

PDB_4W5N_PATH = Path(__file__).parent / "data" / "4W5N.pdb"


class Ago2Receptor:
    """
    Human Argonaute-2 (hAgo2) structural receptor and active site pocket coordinate mapper.
    """

    def __init__(self, pdb_path: Optional[Path] = None):
        self.pdb_path = pdb_path or PDB_4W5N_PATH
        if not self.pdb_path.exists():
            raise FileNotFoundError(f"Ago2 crystal structure not found at {self.pdb_path}")
        
        self.parser = PDBParser(QUIET=True)
        self.structure = self.parser.get_structure("hAgo2", str(self.pdb_path))
        self.model = self.structure[0]
        self.protein_chain = self.model["A"]
        self.guide_chain = self.model["B"]

        # Cache key functional pocket coordinates
        self.mid_pocket_center = self._compute_pocket_center([529, 533])
        self.piwi_catalytic_center = self._compute_pocket_center([597, 637, 669, 807])
        self.paz_pocket_center = self._compute_pocket_center([294, 314])

    def _compute_pocket_center(self, residue_ids: List[int]) -> np.ndarray:
        """Calculates geometric center of functional coordinating sidechain atoms."""
        coords = []
        for res in self.protein_chain.get_residues():
            res_id = res.id[1]
            if res_id in residue_ids:
                if res_id == 529 and "OH" in res:
                    coords.append(res["OH"].get_coord())
                elif res_id == 533 and "NZ" in res:
                    coords.append(res["NZ"].get_coord())
                elif res_id in (597, 669) and "OD1" in res:
                    coords.append(res["OD1"].get_coord())
                elif res_id == 637 and "OE1" in res:
                    coords.append(res["OE1"].get_coord())
                elif res_id == 807 and "NE2" in res:
                    coords.append(res["NE2"].get_coord())
                elif res_id == 294 and "CZ" in res:
                    coords.append(res["CZ"].get_coord())
                elif res_id == 314 and "OD1" in res:
                    coords.append(res["OD1"].get_coord())
                else:
                    for atom in res.get_atoms():
                        if atom.name in ("OH", "NZ", "OD1", "OE1", "NE2", "CZ"):
                            coords.append(atom.get_coord())
        if coords:
            return np.mean(coords, axis=0)
        return np.zeros(3, dtype=np.float32)

    def get_native_guide_coordinates(self) -> List[Tuple[int, str, np.ndarray, np.ndarray]]:
        """
        Extracts native 4W5N guide RNA backbone phosphate and C1' ribose coordinates.
        Returns: list of (pos_1indexed, resname, P_coord, C1_coord)
        """
        guide_coords = []
        for i, res in enumerate(self.guide_chain.get_residues()):
            res_num = i + 1
            res_name = res.get_resname().strip()
            
            p_coord = res["P"].get_coord() if "P" in res else None
            c1_coord = res["C1'"].get_coord() if "C1'" in res else (res["C4'"].get_coord() if "C4'" in res else None)
            
            if p_coord is None and c1_coord is not None:
                p_coord = c1_coord + np.array([0.0, 0.0, 1.5], dtype=np.float32)
                
            guide_coords.append((res_num, res_name, p_coord, c1_coord))
        return guide_coords

    def compute_mid_pocket_distance(self, guide_5p_coord: np.ndarray) -> float:
        """Distance from guide 5'-phosphate to Tyr529/Lys533 MID pocket center."""
        return float(np.linalg.norm(guide_5p_coord - self.mid_pocket_center))

    def compute_piwi_cleavage_distance(self, guide_g10_g11_coord: np.ndarray) -> float:
        """Distance from scissile phosphate (between g10 and g11) to catalytic tetrad."""
        return float(np.linalg.norm(guide_g10_g11_coord - self.piwi_catalytic_center))

    def compute_paz_pocket_distance(self, guide_3p_coord: np.ndarray) -> float:
        """Distance from guide 3' dinucleotide to PAZ pocket center."""
        return float(np.linalg.norm(guide_3p_coord - self.paz_pocket_center))
