"""
helixzero.ontology.tokenizer
============================
Standardized Sequence and Multi-Slot Chemical Ontology Tokenizer.

Converts any siRNA specification (plain string, legacy CMsiRNAdb string, Alnylam format,
or position maps) into a sequence of immutable CanonicalNucSlot objects.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any

from .chem_alphabet import SUGAR_LOOKUP, LINKAGE_LOOKUP, TERMINAL_LOOKUP


@dataclass(frozen=True)
class CanonicalNucSlot:
    """
    Immutable representation of a single nucleotide position in a therapeutic siRNA duplex.
    """
    base: str           # Standard Base: A, C, G, U, T, I, W
    sugar: str          # 2OMe, 2F, ribo, deoxyribo, 2MOE, LNA, GNA, UNA, etc.
    linkage: str        # PO, PS, PS2
    terminal_5p: str    # OH, 5P, 5VP, 5OMe
    basemod: str        # none, 5mC, 2thioU, inosine, pseudouridine
    conjugate: Optional[str] = None # GalNAc, Cholesterol, None

    @property
    def linkage_3p(self) -> str:
        return self.linkage

    @property
    def base_mod(self) -> Optional[str]:
        return self.basemod if self.basemod != 'none' else None

    def to_one_hot_vector(self) -> List[float]:
        """Encodes slot attributes into a 24-bit binary vector."""
        vec = []
        # Base (5 bits: A, C, G, U, T)
        bases = ['A', 'C', 'G', 'U', 'T']
        vec.extend([1.0 if self.base == b else 0.0 for b in bases])
        
        # Sugar (8 bits: 2OMe, 2F, ribo, deoxyribo, 2MOE, LNA, GNA, UNA)
        sugars = ['2OMe', '2F', 'ribo', 'deoxyribo', '2MOE', 'LNA', 'GNA', 'UNA']
        vec.extend([1.0 if self.sugar == s else 0.0 for s in sugars])
        
        # Linkage (3 bits: PO, PS, PS2)
        linkages = ['PO', 'PS', 'PS2']
        vec.extend([1.0 if self.linkage == l else 0.0 for l in linkages])
        
        # Terminal 5' (4 bits: OH, 5P, 5VP, 5OMe)
        terms = ['OH', '5P', '5VP', '5OMe']
        vec.extend([1.0 if self.terminal_5p == t else 0.0 for t in terms])
        
        # Basemod (4 bits: none, 5mC, inosine, pseudouridine)
        mods = ['none', '5mC', 'inosine', 'pseudouridine']
        vec.extend([1.0 if self.basemod == m else 0.0 for m in mods])
        
        return vec


def parse_sirna_sequence(
    sequence: str,
    mods_str: str = "",
    positions_str: str = "",
    terminal_5p: str = "OH",
    default_sugar: str = "ribo",
    default_linkage: str = "PO"
) -> List[CanonicalNucSlot]:
    """
    Parses any nucleotide sequence and chemical annotation into a list of CanonicalNucSlot objects.
    
    Handles:
    - Clean plain RNA: "GGAUCAUCUCAAGUCUUAC"
    - Legacy single-letter format: "MMFMFMFMFMFMFMFMFMFMF"
    - Position map format: "2OMe:1,3,5; 2F:2,4,6; PS:1,2,20,21"
    - Alnylam tokenized format: "mG*fG*a*u*c..."
    """
    clean_seq = sequence.upper().replace('T', 'U').replace(' ', '').strip()
    n = len(clean_seq)
    if n == 0:
        return []

    sugars = [default_sugar] * n
    linkages = [default_linkage] * n
    terms = ["OH"] * n
    basemods = ["none"] * n
    terms[0] = TERMINAL_LOOKUP.get(terminal_5p.upper(), "OH")

    # 1. Parse position maps if provided: e.g., "2OMe:0,2,4; 2F:1,3,5"
    if positions_str and ":" in positions_str:
        entries = positions_str.split(";")
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            if ":" in entry:
                mod_name, pos_list = entry.split(":", 1)
                mod_clean = mod_name.strip()
                try:
                    positions = [int(p.strip()) for p in pos_list.split(",") if p.strip()]
                except ValueError:
                    continue
                
                # Check if it's sugar, linkage, or terminal
                sugar_val = SUGAR_LOOKUP.get(mod_clean, SUGAR_LOOKUP.get(mod_clean.upper()))
                linkage_val = LINKAGE_LOOKUP.get(mod_clean, LINKAGE_LOOKUP.get(mod_clean.upper()))
                term_val = TERMINAL_LOOKUP.get(mod_clean, TERMINAL_LOOKUP.get(mod_clean.upper()))
                
                for pos in positions:
                    idx = pos - 1 if min(positions) >= 1 else pos
                    if 0 <= idx < n:
                        if sugar_val:
                            sugars[idx] = sugar_val
                        if linkage_val:
                            linkages[idx] = linkage_val
                        if term_val and idx == 0:
                            terms[0] = term_val

    # 2. Parse mods_str if provided (position-aligned characters, comma-separated, or Alnylam format)
    if mods_str:
        clean_mods = mods_str.strip()
        # Case A1: Comma-separated format (e.g. "m,m,f,f,m,s,...")
        if ',' in clean_mods:
            tokens = [t.strip() for t in clean_mods.split(',') if t.strip()]
            for i in range(min(n, len(tokens))):
                tok = tokens[i]
                if tok in SUGAR_LOOKUP:
                    sugars[i] = SUGAR_LOOKUP[tok]
                elif tok.upper() in SUGAR_LOOKUP:
                    sugars[i] = SUGAR_LOOKUP[tok.upper()]
                if tok.upper() in ('PS', 'S'):
                    linkages[i] = 'PS'
                if tok.upper() in ('1', 'P', '5P'):
                    terms[0] = '5P'
                if tok.upper() in ('V', 'VP', '5VP'):
                    terms[0] = '5VP'
        # Case A2: Single-letter string matching or exceeding sequence length
        elif len(clean_mods) >= n:
            for i in range(n):
                c = clean_mods[i]
                if c in SUGAR_LOOKUP:
                    sugars[i] = SUGAR_LOOKUP[c]
                elif c.upper() in SUGAR_LOOKUP:
                    sugars[i] = SUGAR_LOOKUP[c.upper()]
                if c.upper() == 'S':
                    linkages[i] = 'PS'
                if c in ('1', 'P'):
                    terms[0] = '5P'
                if c in ('V', 'VP'):
                    terms[0] = '5VP'
        # Case B: Asterisks for phosphorothioate (e.g. mG*fG*a*u)
        elif '*' in clean_mods:
            ps_indices = set()
            seq_idx = 0
            for char in clean_mods:
                if char == '*':
                    if seq_idx > 0:
                        ps_indices.add(seq_idx - 1)
                elif char.isalpha():
                    seq_idx += 1
            for idx in ps_indices:
                if 0 <= idx < n:
                    linkages[idx] = 'PS'

    # Build Canonical Slots
    slots = []
    for i in range(n):
        slot = CanonicalNucSlot(
            base=clean_seq[i],
            sugar=sugars[i],
            linkage=linkages[i],
            terminal_5p=terms[i],
            basemod=basemods[i]
        )
        slots.append(slot)
    return slots
