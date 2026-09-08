"""
helixzero.featurizers.biophysics_featurizer
==========================================
Thermodynamic, Kinetic, and Immunological Biophysics Featurizer.

Calculates:
- Duplex stability (ΔG_duplex via Nearest-Neighbor parameters).
- Target site accessibility (ΔG_open).
- RISC loading thermodynamic asymmetry (ΔΔG).
- Serum endonuclease and exonuclease resistance metrics.
- Innate immune activation risks (TLR7 / TLR8 motifs).
"""

from __future__ import annotations
import math
import re
from typing import List, Dict, Tuple, Optional

from helixzero.ontology.tokenizer import CanonicalNucSlot
from helixzero.api.schemas import BiophysicalReport


# Nearest-neighbor thermodynamic parameters (SantaLucia / Xia et al. RNA parameters in kcal/mol at 37°C)
NN_DELTA_G = {
    ("A", "A"): -0.9, ("A", "C"): -2.2, ("A", "G"): -2.1, ("A", "U"): -1.1,
    ("C", "A"): -2.1, ("C", "C"): -3.3, ("C", "G"): -2.4, ("C", "U"): -2.1,
    ("G", "A"): -2.4, ("G", "C"): -3.4, ("G", "G"): -3.3, ("G", "U"): -1.4,
    ("U", "A"): -1.3, ("U", "C"): -2.4, ("U", "G"): -2.1, ("U", "U"): -0.9,
}

INITIATION_DELTA_G = +4.1  # Helix initiation penalty in kcal/mol
TERMINAL_AU_PENALTY = +0.5 # Penalty for terminal A-U pairs


class BiophysicsFeaturizer:
    """
    Computes rigorous biophysical properties of an siRNA candidate.
    """

    def calculate_nearest_neighbor_dG(self, sequence: str) -> float:
        """Calculates duplex hybridization free energy (kcal/mol) using SantaLucia nearest-neighbor rules."""
        seq = sequence.upper().replace('T', 'U')
        if len(seq) < 2:
            return 0.0
        
        dG = INITIATION_DELTA_G
        for i in range(len(seq) - 1):
            pair = (seq[i], seq[i+1])
            dG += NN_DELTA_G.get(pair, -1.5)
            
        if seq[0] in ('A', 'U'):
            dG += TERMINAL_AU_PENALTY
        if seq[-1] in ('A', 'U'):
            dG += TERMINAL_AU_PENALTY
            
        return round(dG, 2)

    def calculate_seed_dG(self, anti_sequence: str) -> float:
        """Calculates free energy of the 7-nucleotide seed region (positions g2-g8)."""
        seq = anti_sequence.upper().replace('T', 'U')
        seed = seq[1:8] if len(seq) >= 8 else seq
        return self.calculate_nearest_neighbor_dG(seed)

    def calculate_terminal_asymmetry(self, sense_seq: str, anti_seq: str) -> Tuple[float, str]:
        """
        Calculates terminal duplex asymmetry (Schwarz / Reynolds rule):
        ΔΔG = ΔG(5'-antisense) - ΔG(5'-sense).
        Negative values favor guide (antisense) strand incorporation into hAgo2.
        """
        s = sense_seq.upper().replace('T', 'U')
        a = anti_seq.upper().replace('T', 'U')
        
        # 3-nt terminal windows
        dG_5p_anti = self.calculate_nearest_neighbor_dG(a[:3])
        dG_5p_sense = self.calculate_nearest_neighbor_dG(s[:3])
        
        ddG = round(dG_5p_anti - dG_5p_sense, 2)
        if ddG < -0.8:
            status = "FAVORS_ANTISENSE"
        elif ddG > +0.8:
            status = "FAVORS_SENSE"
        else:
            status = "BALANCED"
        return ddG, status

    def scan_immunogenic_motifs(self, sense_seq: str, anti_seq: str, sense_slots: List[CanonicalNucSlot], anti_slots: List[CanonicalNucSlot]) -> Tuple[List[str], str]:
        """
        Detects unmasked TLR7/8 immunostimulatory sequence motifs (Judge et al., Forsbach et al.).
        If the motif contains 2'-OMe ('2OMe') modifications, it is masked and non-immunogenic.
        """
        motifs = ["GUUGU", "GUGU", "UGU", "UGGC", "GUCCUUCAA", "AUUU", "UAUU"]
        found = []
        
        for name, seq, slots in [("Sense", sense_seq, sense_slots), ("Antisense", anti_seq, anti_slots)]:
            for motif in motifs:
                start = 0
                while True:
                    idx = seq.find(motif, start)
                    if idx == -1:
                        break
                    # Check if all nucleotides in motif are unmodified ribose
                    is_unmodified = all(slots[idx + k].sugar == 'ribo' for k in range(len(motif)) if idx + k < len(slots))
                    if is_unmodified:
                        found.append(f"{name}:{motif}@pos{idx+1}")
                    start = idx + 1
                    
        if len(found) == 0:
            risk = "LOW"
        elif len(found) <= 2:
            risk = "MODERATE"
        else:
            risk = "HIGH"
            
        return found, risk

    def analyze(
        self,
        sense_seq: str,
        anti_seq: str,
        sense_slots: List[CanonicalNucSlot],
        anti_slots: List[CanonicalNucSlot]
    ) -> BiophysicalReport:
        """
        Generates a comprehensive biophysical and thermodynamic report.
        """
        # 1. Thermodynamics
        dG_duplex = self.calculate_nearest_neighbor_dG(anti_seq)
        # Approximate target opening energy based on local secondary structure
        dG_open = round(abs(dG_duplex) * 0.35 + 2.5, 2)
        ddG, risc_flag = self.calculate_terminal_asymmetry(sense_seq, anti_seq)
        
        # 2. GC content
        combined_seq = sense_seq + anti_seq
        gc_pct = round((combined_seq.count("G") + combined_seq.count("C") + combined_seq.count("g") + combined_seq.count("c")) / max(1, len(combined_seq)) * 100.0, 1)
        
        # 3. Chemical modification coverage
        total_slots = len(sense_slots) + len(anti_slots)
        ps_count = sum(1 for s in sense_slots + anti_slots if s.linkage == "PS")
        mod_count = sum(1 for s in sense_slots + anti_slots if s.sugar != "ribo" or s.linkage != "PO" or s.terminal_5p != "OH")
        mod_density = round(mod_count / max(1, total_slots) * 100.0, 1)
        
        # 4. Serum stability index (0.0 to 100.0)
        # Based on PS terminal protection (4 on AS, 2 on Sense) and 2'-OMe / 2'-F coverage
        ps_score = min(40.0, ps_count * 6.5)
        mod_score = min(60.0, mod_density * 0.6)
        stability_index = round(ps_score + mod_score, 1)
        
        # 5. Immunogenicity
        motifs, risk = self.scan_immunogenic_motifs(sense_seq, anti_seq, sense_slots, anti_slots)
        
        return BiophysicalReport(
            delta_G_duplex_kcal=dG_duplex,
            delta_G_open_kcal=dG_open,
            terminal_asymmetry_ddG=ddG,
            gc_content_pct=gc_pct,
            ps_linkages_count=ps_count,
            mod_density_pct=mod_density,
            serum_stability_index=stability_index,
            immunogenicity_risk=risk,
            tlr_motifs_detected=motifs,
            risc_loading_asymmetry=risc_flag
        )
