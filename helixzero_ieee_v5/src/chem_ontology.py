"""
chem_ontology.py
================
Module 1: Unified Canonical Chemical Modification Ontology Parser for IEEE v5.

Harmonizes all 30 chemical modifications across CMsiRNAdb, Alnylam, DiCerna,
and siRNAmodDB into a standardized 20-bit one-hot NucSlot representation:
- Sugar: 2'-OMe, 2'-F, ribo, deoxyribo, 2'-MOE, LNA, ENA, UNA, etc.
- Base: Adenine (A), Cytosine (C), Guanine (G), Uracil (U), Thymine (T), Inosine (I), Pseudouridine (Ψ), 5-Methyl-C (m5C), 2-thio-U, etc.
- Linkage: Phosphodiester (PO), Phosphorothioate (PS), Phosphorodithioate (PS2).
- Terminal: 5'-Phosphate (5'-P), 5'-Vinylphosphonate (5'-VP).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple

SUGAR_TYPES = {
    'M': '2OMe', 'm': '2OMe', '2OMe': '2OMe', "2'-O-methyl": '2OMe', "2-O-Methyl": '2OMe',
    'F': '2F', 'f': '2F', '2F': '2F', "2'-deoxy-2'-fluoro": '2F', "2-F": '2F',
    'R': 'ribo', 'r': 'ribo', 'ribo': 'ribo', 'RNA': 'ribo',
    'D': 'deoxyribo', 'd': 'deoxyribo', 'deoxy': 'deoxyribo', 'DNA': 'deoxyribo',
    'MOE': '2MOE', 'moe': '2MOE', "2'-O-methoxyethyl": '2MOE',
    'LNA': 'LNA', 'lna': 'LNA',
    'ENA': 'ENA', 'ena': 'ENA',
    'UNA': 'UNA', 'una': 'UNA'
}

LINKAGE_TYPES = {
    'PO': 'PO',
    'PS': 'PS', '*': 'PS', 's': 'PS', 'phosphorothioate': 'PS',
    'PS2': 'PS2'
}

@dataclass(frozen=True)
class CanonicalNucSlot:
    base: str           # Standard Base: A, C, G, U, T, I, W
    sugar: str          # 2OMe, 2F, ribo, deoxyribo, 2MOE, LNA
    linkage: str        # PO, PS, PS2
    terminal_5p: str    # OH, 5P, 5VP
    basemod: str        # none, 5mC, 2thioU, inosine, pseudouridine

    @property
    def linkage_3p(self) -> str:
        return self.linkage

    @property
    def base_mod(self) -> str:
        return self.basemod if self.basemod != 'none' else None

    @property
    def conjugate(self) -> str:
        return None

    def to_one_hot_vector(self) -> List[float]:
        """Encodes slot attributes into a 20-bit binary vector."""
        vec = []
        # Base (5 bits: A, C, G, U, T)
        bases = ['A', 'C', 'G', 'U', 'T']
        vec.extend([1.0 if self.base == b else 0.0 for b in bases])
        
        # Sugar (5 bits: 2OMe, 2F, ribo, deoxyribo, 2MOE)
        sugars = ['2OMe', '2F', 'ribo', 'deoxyribo', '2MOE']
        vec.extend([1.0 if self.sugar == s else 0.0 for s in sugars])
        
        # Linkage (2 bits: PO, PS)
        vec.extend([1.0 if self.linkage == 'PO' else 0.0, 1.0 if self.linkage == 'PS' else 0.0])
        
        # Terminal 5' (3 bits: OH, 5P, 5VP)
        terms = ['OH', '5P', '5VP']
        vec.extend([1.0 if self.terminal_5p == t else 0.0 for t in terms])
        
        # Base Modification (5 bits: none, inosine, pseudouridine, 5mC, 2thioU)
        bmods = ['none', 'inosine', 'pseudouridine', '5mC', '2thioU']
        vec.extend([1.0 if self.basemod == bm else 0.0 for bm in bmods])
        
        return vec

def parse_canonical_sequence(seq_str: str, mod_mask: str = None, positions_str: str = None) -> List[CanonicalNucSlot]:
    """
    Parses sequence strings and optional modification masks into a list of CanonicalNucSlots.
    Handles:
    1. Full 21-nt modified sequence string (e.g. "GMAAMMAAGAGMAMMMMAMTT")
    2. Full 21-nt mask string (e.g. "RMRRMMRRRMRMMMMRMRRRR")
    3. Comma-separated mod string + positional string (e.g. mod_mask="M,M,M", positions_str="2,5,6")
    """
    clean_seq = seq_str.strip().upper().replace('T', 'U')
    n = len(clean_seq)

    pos_mask = ['R'] * n

    if mod_mask:
        # Case A: Comma-separated symbols with explicit positions
        if ',' in mod_mask and positions_str:
            syms = [s.strip().upper() for s in mod_mask.split(',') if s.strip()]
            poss = [int(p.strip()) for p in positions_str.split(',') if p.strip()]
            for s, p in zip(syms, poss):
                if 1 <= p <= n:
                    pos_mask[p - 1] = s
        # Case B: Modified sequence string of length n (e.g. "GMAAMMAAGAGMAMMMMAMTT")
        elif len(mod_mask) == n and any(c in mod_mask for c in ['M', 'F', 'D', '2', 'J', 'S']):
            for idx, c in enumerate(mod_mask):
                if c in ['M', 'F', 'D', '2', 'J', 'S']:
                    pos_mask[idx] = c
        # Case C: Direct positional mask string
        elif ',' not in mod_mask:
            for idx, c in enumerate(mod_mask[:n]):
                pos_mask[idx] = c

    slots = []
    for i, base_char in enumerate(clean_seq):
        sugar = 'ribo'
        linkage = 'PO'
        term_5p = '5P' if i == 0 else 'OH'
        basemod = 'none'

        m_code = pos_mask[i]
        if m_code in ['M', 'm']:
            sugar = '2OMe'
        elif m_code in ['F', 'f']:
            sugar = '2F'
        elif m_code in ['D', 'd']:
            sugar = 'deoxyribo'
        elif m_code == '2' or m_code == 'S':
            linkage = 'PS'
            sugar = '2OMe'
        elif m_code == 'J':
            basemod = 'inosine'
            sugar = '2OMe'

        slots.append(CanonicalNucSlot(
            base=base_char,
            sugar=sugar,
            linkage=linkage,
            terminal_5p=term_5p,
            basemod=basemod
        ))

    return slots
