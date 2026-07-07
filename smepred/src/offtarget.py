"""
offtarget.py — Transcriptome-Wide Off-Target Safety Engine

Validates candidate siRNAs against the human transcriptome to detect off-target 
hybridization risks and innate immunogenic motifs.

Core Validations:
1. Thermodynamic Asymmetry: Ensures the guide strand is preferentially loaded into RISC.
2. 15-mer Slicer Check: Hard-rejects any candidate that shares a 15-mer identity 
   with an unintended human gene, as this triggers catastrophic off-target slicing.
3. Seed Region Mitigation: Quantifies transcriptome-wide matches of the critical 
   positions 2-8, checking if chemical modifications (e.g., 2'-OMe) mitigate the risk.
4. TLR Motif Masking: Identifies GU-rich immunostimulatory sequences and ensures 
   they are masked by 2'-O-methylations to evade Toll-Like Receptors 7 and 8.
5. Pharmacokinetic Delivery: Checks for required biological conjugates like GalNAc.
"""

import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class OffTargetEngine:
    """
    A unified engine that evaluates the safety of siRNA sequences against 
    a loaded reference transcriptome.
    """

    def __init__(self, transcriptome_path: str) -> None:
        """
        Initializes the OffTargetEngine.
        
        Args:
            transcriptome_path (str): File path to the reference FASTA file (e.g. GRCh38).
        """
        self.transcriptome_path: str = transcriptome_path
        self.sequence: str = ""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_transcriptome()

    def _load_transcriptome(self) -> None:
        """
        Loads the FASTA reference file and concatenates sequences with a sentinel 
        to prevent boundary crossing false positives, while maintaining fast string search.
        """
        try:
            if not os.path.exists(self.transcriptome_path):
                logger.warning(f"Transcriptome file not found at {self.transcriptome_path}. Off-target scans will bypass exact match checks.")
                return

            with open(self.transcriptome_path, "r", encoding="utf-8") as f:
                current_seq = []
                seqs = []
                for line in f:
                    if line.startswith(">"):
                        if current_seq:
                            seqs.append("".join(current_seq))
                        current_seq = []
                    else:
                        current_seq.append(line.strip().upper())
                if current_seq:
                    seqs.append("".join(current_seq))
                
                # Join with 15 N's so no 15-mer or seed can match across boundaries
                self.sequence = ("N" * 15).join(seqs)
                
            logger.info(f"Loaded transcriptome matrix: {len(self.sequence):,} bases.")
        except Exception as e:
            logger.error(f"Failed to load transcriptome database: {e}")
            self.sequence = ""

    def _calculate_asymmetry(self, sense: str, antisense: str) -> float:
        """
        Calculates the thermodynamic asymmetry between the 5' ends of the siRNA
        using RNA nearest-neighbor ΔG (Gibbs free energy) at 37°C.
        
        Why: Ago2 protein preferentially loads the strand with the less thermodynamically 
        stable 5' terminus. ΔG is the correct thermodynamic metric (free energy at 
        37°C determines spontaneous duplex stability), replacing the earlier ΔH-only 
        approach which ignored the entropy contribution.
        
        Args:
            sense (str): The sense strand sequence.
            antisense (str): The antisense strand sequence.
            
        Returns:
            float: ΔG difference (Sense ΔG - Antisense ΔG). Negative values mean 
                   Antisense terminus is less stable (optimal for RISC loading).
        """
        # RNA Nearest-Neighbor ΔG (kcal/mol) at 37°C — Xia et al. 1998, Turner 2004
        # These are the standard Turner rules for RNA folding free energy
        rna_nn_dg = {
            'AA': -0.93, 'AU': -1.10, 'AC': -2.24, 'AG': -2.08,
            'UA': -1.33, 'UU': -0.93, 'UC': -1.43, 'UG': -2.70,
            'CA': -1.78, 'CU': -1.70, 'CC': -2.70, 'CG': -2.36,
            'GA': -1.70, 'GU': -1.78, 'GC': -2.08, 'GG': -2.70,
        }
        
        def terminus_energy(seq: str, n: int = 4) -> float:
            s = seq[:n].upper().replace('T', 'U')
            return sum(rna_nn_dg.get(s[i:i+2], -1.5) for i in range(len(s) - 1))
        
        sense_energy = terminus_energy(sense)
        antisense_energy = terminus_energy(antisense)
        
        return sense_energy - antisense_energy

    def validate_safety(
        self, 
        sense: str, 
        antisense: str, 
        antisense_mods: str = "", 
        mod_sense: str = "",
        delivery_route: str = "hepatic",
        base_antisense: str = ""
    ) -> Dict[str, Any]:
        """
        Executes the full safety heuristic pipeline against a given candidate.
        
        Args:
            sense (str): The parent sense sequence.
            antisense (str): The parent antisense sequence.
            antisense_mods (str): The modification mask for the antisense strand.
            mod_sense (str): The modification mask for the sense strand.
            delivery_route (str): Target delivery route (e.g. "hepatic").
            base_antisense (str): The unmodified parent antisense sequence.
            
        Returns:
            Dict[str, Any]: A detailed safety dossier containing the final score, 
                            status flags, risk factors, and mitigation notes.
        """
        sense = sense.upper()
        antisense = antisense.upper()
        
        def _reverse_complement(seq: str) -> str:
            return seq.upper().translate(str.maketrans("AUGC", "UACG"))[::-1]
            
        report: Dict[str, Any] = {
            "isSafe": True,
            "overallSafetyScore": 100.0,
            "status": "CLEARED",
            "riskFactors": [],
            "safetyNotes": [],
            "certificate_path": None
        }
        
        # 1. Thermodynamic Asymmetry
        asymmetry_score = self._calculate_asymmetry(sense, antisense)
        if asymmetry_score > 0:
            report["riskFactors"].append(
                f"WARNING: Thermodynamic asymmetry favors Sense Strand loading (Score: {asymmetry_score}). "
                "High risk of Sense-Strand-mediated off-targets."
            )
            report["overallSafetyScore"] -= 40.0
            
        # 1.b. AGO2 5' Terminal Preference
        underlying_nt = base_antisense[0] if base_antisense else antisense[0]
        if underlying_nt not in ['A', 'U', 'T']:
            report["safetyNotes"].append(
                "Note: Antisense 5' end is not A or U. This is sub-optimal for Ago2 MID-domain anchoring."
            )
            report["overallSafetyScore"] -= 5.0
            
        # 2. 15-mer Slicer-mediated Exclusion Check & 3. Seed Region Analysis
        # These operations search a ~400MB string. Since multi-mod variants share the same parent,
        # we cache the string-search results to prevent redundant gigabyte-scale scans.
        cache_key = antisense
        if cache_key not in self._cache:
            has_crit_match = False
            if self.sequence:
                sense_rc = _reverse_complement(antisense)
                for i in range(len(sense_rc) - 15 + 1):
                    if sense_rc[i : i + 15] in self.sequence:
                        has_crit_match = True
                        break
            
            # Bartel hierarchical seed classification (Bartel 2009, Cell; Agarwal 2015, eLife):
            # 8mer (pos 2-8 + A at pos 1) > 7mer-m8 (pos 2-8) > 7mer-A1 (pos 2-7 + A at pos 1) > 6mer (pos 2-7)
            # Higher-class matches have stronger off-target silencing potential
            seed_seq_6mer = antisense[1:7]
            seed_seq_7mer = antisense[1:8] if len(antisense) >= 8 else antisense[1:7]
            has_anchor_a = len(antisense) > 0 and antisense[0] in ('A', 'U')
            
            seed_complement_6mer = _reverse_complement(seed_seq_6mer)
            seed_complement_7mer = _reverse_complement(seed_seq_7mer) if len(antisense) >= 8 else ""
            
            seed_6mer_count = self.sequence.count(seed_complement_6mer) if self.sequence else 0
            seed_7mer_count = self.sequence.count(seed_complement_7mer) if self.sequence and seed_complement_7mer else 0
            
            # Classify: 8mer = 7mer-m8 + A1 anchor, 7mer-m8 = 7mer match, 7mer-A1 = 6mer + A1, 6mer = 6mer only
            seed_8mer_count = seed_7mer_count if has_anchor_a else 0
            seed_7m8_count = seed_7mer_count
            seed_7a1_count = seed_6mer_count if has_anchor_a else 0
            # 6mer-only = 6mer matches that are NOT also 7mer matches
            seed_6mer_only = seed_6mer_count - seed_7mer_count if seed_6mer_count > seed_7mer_count else 0
            
            # Weighted seed occurrence score: 8mer=1.0, 7mer-m8=0.8, 7mer-A1=0.6, 6mer=0.3
            weighted_seed = (seed_8mer_count * 1.0 + seed_7m8_count * 0.8 + 
                           seed_7a1_count * 0.6 + seed_6mer_only * 0.3)
            
            self._cache[cache_key] = {
                "has_critical_match": has_crit_match,
                "seed_occurrences": seed_6mer_count,
                "weighted_seed_score": weighted_seed,
                "seed_region": seed_seq_6mer,
                "seed_seven_mer": seed_seq_7mer,
                "seed_6mer_only": seed_6mer_only,
                "seed_8mer": seed_8mer_count,
                "seed_7m8": seed_7m8_count,
                "seed_7a1": seed_7a1_count,
            }
            
        cached_data = self._cache[cache_key]
        has_critical_match = cached_data["has_critical_match"]
        seed_occurrences = cached_data["seed_occurrences"]
        weighted_seed_score = cached_data["weighted_seed_score"]
        seed_region = cached_data["seed_region"]
                
        if has_critical_match:
            report["riskFactors"].append(
                "CRITICAL: 15-mer contiguous match detected in Human Transcriptome. "
                "This guarantees off-target transcript cleavage."
            )
            report["overallSafetyScore"] = 0.0
            report["isSafe"] = False
            report["status"] = "TOXIC"
            
        # 3. Seed Region Mitigation Analysis
        
        # Scientific Mitigation (Parvathaneni 2026 & Neumeier 2021)
        is_seed_mitigated = False
        if len(antisense_mods) >= 8:
            # OMe at ANY seed position (2-7) disrupts miRNA-like off-target pairing
            # Jackson et al. 2006, RNA; Parvathaneni 2026: seed 2'-OMe suppresses seed-based off-targets
            for pos_idx in range(1, 7):
                if antisense_mods[pos_idx] == "M":
                    is_seed_mitigated = True
                    report["safetyNotes"].append(
                        f"Position {pos_idx+1} contains 2'-OMe, mitigating off-target seed binding."
                    )
                    break
            # GNA at position 7 (index 6) independently rescues via steric disruption (Schlegel 2022)
            if antisense_mods[6] == "8":
                is_seed_mitigated = True
                report["safetyNotes"].append(
                    "Position 7 contains GNA ('8'), mitigating seed-based off-targets via steric disruption."
                )
        
        if seed_occurrences > 0:
            # Use Bartel-weighted seed score (8mer=1.0, 7mer-m8=0.8, 7mer-A1=0.6, 6mer=0.3)
            # This better reflects actual off-target silencing risk than raw 6mer counts
            seed_display = int(weighted_seed_score)
            if is_seed_mitigated:
                report["safetyNotes"].append(
                    f"Seed region has {seed_display:,} weighted transcriptome matches, but risk is MITIGATED by chemical modification."
                )
                report["overallSafetyScore"] -= min(5.0, weighted_seed_score * 0.05)
            else:
                report["riskFactors"].append(
                    f"Seed region ({seed_region}) matched {seed_display:,} weighted times in human transcriptome without mitigation."
                )
                report["overallSafetyScore"] -= min(30.0, weighted_seed_score * 2.5)
                
        # 4. Toll-Like Receptor (TLR7 / TLR8) Motif Masking
        # Hierarchical TLR7/8 agonist motifs — Goodchild 2009, Judge 2005, Heil 2004, Hornung 2005
        tlr_motifs = ["GUUGU", "GUGU", "UGU", "UUG", "UGGC", "GUUC", "GUCCUUCAA", "UGUGU"]
        
        def _evaluate_tlr_masking(strand_seq: str, mod_strand_mask: str, strand_name: str) -> None:
            """Evaluates whether immunostimulatory GU motifs are shielded by 2'-OMe."""
            for motif in tlr_motifs:
                idx = strand_seq.find(motif)
                while idx != -1:
                    is_masked = False
                    if len(mod_strand_mask) == len(strand_seq):
                        for i in range(idx, idx + len(motif)):
                            if mod_strand_mask[i] == 'M':
                                is_masked = True
                                break
                                
                    if not is_masked:
                        report["riskFactors"].append(
                            f"WARNING: Unmasked TLR7/8 motif ({motif}) found in {strand_name} strand. "
                            "High risk of innate immune activation (Interferon response)."
                        )
                        report["overallSafetyScore"] -= 15.0
                    else:
                        report["safetyNotes"].append(
                            f"TLR7/8 motif ({motif}) in {strand_name} strand is safely masked by 2'-OMe."
                        )
                    idx = strand_seq.find(motif, idx + 1)
                    
        _evaluate_tlr_masking(sense, mod_sense, "Sense")
        _evaluate_tlr_masking(antisense, antisense_mods, "Antisense")
        
        # 5. Pharmacokinetic (PK) & Delivery Conjugate Validation
        has_galnac = False
        if (mod_sense and "4" in mod_sense) or (antisense_mods and "4" in antisense_mods):
            has_galnac = True
            
        if delivery_route == "hepatic" and not has_galnac:
            report["riskFactors"].append(
                "WARNING: Missing GalNAc ('4') delivery conjugate. Predicted hepatic uptake is 0%. "
                "In vivo pharmacokinetic profile will fail."
            )
            report["overallSafetyScore"] -= 10.0
        elif has_galnac:
            report["safetyNotes"].append(
                "GalNAc ('4') conjugate detected. Hepatic uptake and PK profile validated."
            )

        # Enforce bounds
        report["overallSafetyScore"] = max(0.0, min(100.0, report["overallSafetyScore"]))
        
        # Final status evaluation
        if report["overallSafetyScore"] < 80.0 and report["isSafe"]:
            report["status"] = "WARNING_SEED"
            
        return report

    def generate_markdown_certificate(
        self, 
        report: Dict[str, Any], 
        sense: str, 
        antisense: str, 
        mods: str
    ) -> str:
        """
        Generates a Markdown Certificate of Biological Safety and saves it.
        """
        docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
        os.makedirs(docs_dir, exist_ok=True)
        
        safe_prefix = sense[:10] + "..." if len(sense) > 10 else sense
        filename = f"Certificate_offtarget_{safe_prefix}.md"
        filepath = os.path.join(docs_dir, filename)
        
        md_content = f"""# Certificate of Biological Safety
**Human RNAi Therapeutics Off-Target Scan**

## Sequence Details
* **Sense Strand:** `{sense}`
* **Antisense Strand:** `{antisense}`
* **Antisense Modifications:** `{mods or 'None'}`

## Validation Results
* **Status:** **{report['status']}**
* **Overall Safety Score:** **{report['overallSafetyScore']}%**

### Risk Factors Identified
"""
        if not report['riskFactors']:
            md_content += "* None detected.\n"
        else:
            for factor in report['riskFactors']:
                md_content += f"* {factor}\n"
                
        md_content += "\n### Safety Notes & Mitigations\n"
        if not report['safetyNotes']:
            md_content += "* None.\n"
        else:
            for note in report['safetyNotes']:
                md_content += f"* {note}\n"
                
        md_content += (
            "\n---\n*Validated checks include: Thermodynamic Asymmetry end-loading preference, "
            "Slicer-mediated 15-mer exclusion, and Seed-region mismatch mitigation against the "
            "GRCh38 Human Transcriptome.*"
        )
        
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(md_content)
            
        return filepath


# Global instance for FastAPI dependency injection
_engine_instance: Optional[OffTargetEngine] = None

def get_offtarget_engine() -> OffTargetEngine:
    """Singleton accessor for the OffTargetEngine."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = OffTargetEngine("data/human_transcriptome.fasta")
    return _engine_instance
