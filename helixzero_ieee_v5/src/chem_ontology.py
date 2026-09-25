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

_VERBOSE_MOD_MAP = {
    "2'-FLUORO": 'F', "2-FLUORO": 'F', "2'-F": 'F', "2-F": 'F',
    "2'-O-METHYL": 'M', "2-O-METHYL": 'M', "2'-OME": 'M', "2-OME": 'M',
    "PHOSPHOROTHIOATE": 'S', "PS": 'S',
    "2'-DEOXY": 'D', "DNA": 'D',
    "5'-VINYL PHOSPHONATE": '1', "5'-VP": '1', "5VP": '1',
    "LOCKED NUCLEIC ACID": 'L', "LNA": 'L',
    "2'-O-METHOXYETHYL": 'E', "2'-MOE": 'E', "MOE": 'E',
    "ETHYLENE-BRIDGED NUCLEIC ACID": 'Y', "ENA": 'Y',
    "UNLOCKED NUCLEIC ACID": '6', "UNA": '6',
    "ARABINONUCLEIC ACID": '7', "ANA": '7',
    "GLYCOL NUCLEIC ACID": '8', "GNA": '8',
    "THREOSE NUCLEIC ACID": '9', "TNA": '9',
    "INOSINE": 'J', "PSEUDOURIDINE": 'W', "5-METHYLCYTOSINE": 'V', "2-THIOURIDINE": 'K',
}

_CHAR_TO_SLOT_ATTRS = {
    'M': {'sugar': '2OMe'},
    'm': {'sugar': '2OMe'},
    'F': {'sugar': '2F'},
    'f': {'sugar': '2F'},
    'D': {'sugar': 'deoxyribo'},
    'd': {'sugar': 'deoxyribo'},
    'L': {'sugar': 'LNA'},
    'l': {'sugar': 'LNA'},
    'E': {'sugar': 'MOE'},
    'e': {'sugar': 'MOE'},
    'Y': {'sugar': 'ENA'},
    'y': {'sugar': 'ENA'},
    '6': {'sugar': 'UNA'},
    '7': {'sugar': 'ANA'},
    '8': {'sugar': 'GNA'},
    '9': {'sugar': 'TNA'},
    'I': {'sugar': 'FANA'},
    'N': {'sugar': '4thio'},
    'B': {'sugar': 'Benzyl'},
    'Q': {'sugar': 'Abasic'},
    '2': {'sugar': '2OMe', 'linkage': 'PS'},
    '3': {'sugar': '2F', 'linkage': 'PS'},
    'S': {'linkage': 'PS'},
    's': {'linkage': 'PS'},
    '1': {'terminal_5p': '5VP'},
    'J': {'basemod': 'inosine'},
    'j': {'basemod': 'inosine'},
    '5': {'basemod': 'inosine'},
    'V': {'basemod': '5mC'},
    'v': {'basemod': '5mC'},
    'W': {'basemod': 'pseudouridine'},
    'w': {'basemod': 'pseudouridine'},
    'K': {'basemod': '2thioU'},
    'k': {'basemod': '2thioU'},
}

def parse_canonical_sequence(seq_str: str, mod_mask: str = None, positions_str: str = None, parent_seq: str = None) -> List[CanonicalNucSlot]:
    """
    Parses sequence strings and optional modification masks into a list of CanonicalNucSlots.
    Handles:
    1. Full 21-nt modified sequence string (e.g. "GMAAMMAAGAGMAMMMMAMTT" or "1ANSASGSSSSSHSUCDKAFS")
    2. Full 21-nt mask string (e.g. "RMRRMMRRRMRMMMMRMRRRR")
    3. Comma-separated mod string + positional string (e.g. mod_mask="M,M,M", positions_str="2,5,6")
    4. Multi-modification accumulation at a single position (e.g. 5'-VP + 2'-OMe + PS at pos 1)
    """
    clean_seq = seq_str.strip().upper().replace('T', 'U')
    n = len(clean_seq)
    p_seq = parent_seq.strip().upper().replace('T', 'U') if parent_seq else None

    # Track slot attributes orthogonally per nucleotide position
    pos_attrs = [{} for _ in range(n)]

    if mod_mask:
        # Case A: Symbols with explicit positions (e.g. "M,F,S" at "1,2,3" or "1,M,S" at "1,1,1")
        if positions_str:
            syms = [_VERBOSE_MOD_MAP.get(s.strip().upper(), s.strip().upper()) for s in mod_mask.split(',') if s.strip()]
            poss = [int(p.strip()) for p in positions_str.split(',') if p.strip()]
            for s, p in zip(syms, poss):
                if 1 <= p <= n:
                    if s in _CHAR_TO_SLOT_ATTRS:
                        pos_attrs[p - 1].update(_CHAR_TO_SLOT_ATTRS[s])
        # Case B: Modified sequence string of length n (e.g. "GMAAMMAAGAGMAMMMMAMTT")
        elif len(mod_mask) == n and any(c not in ['A', 'C', 'G', 'U', 'T', 'R', '.'] for c in mod_mask):
            for idx, c in enumerate(mod_mask):
                if c in _CHAR_TO_SLOT_ATTRS:
                    pos_attrs[idx].update(_CHAR_TO_SLOT_ATTRS[c])
        # Case C: Direct positional mask string of length n (e.g. "RMRRMMRRRMRMMMMRMRRRR")
        elif ',' not in mod_mask:
            for idx, c in enumerate(mod_mask[:n]):
                if c in _CHAR_TO_SLOT_ATTRS:
                    pos_attrs[idx].update(_CHAR_TO_SLOT_ATTRS[c])
    else:
        # If no explicit mod_mask provided, check if clean_seq itself contains embedded modification codes
        if any(c not in ['A', 'C', 'G', 'U', 'N', '.'] for c in clean_seq):
            for idx, c in enumerate(clean_seq):
                if c in _CHAR_TO_SLOT_ATTRS:
                    pos_attrs[idx].update(_CHAR_TO_SLOT_ATTRS[c])

    slots = []
    for i in range(n):
        base_char = clean_seq[i]
        # Resolve true biological base: if base_char was replaced by a modification code (e.g. '1', 'S', 'M', 'F')
        if p_seq and i < len(p_seq):
            base_char = p_seq[i]
        elif base_char not in ['A', 'C', 'G', 'U']:
            # Fallback biological base inference for common modification codes
            if base_char in ['V', 'C', 'c']:
                base_char = 'C'
            elif base_char in ['W', 'K', 'U', 'u', 'T', 't']:
                base_char = 'U'
            elif base_char in ['J', 'G', 'g']:
                base_char = 'G'
            else:
                base_char = 'A'

        sugar = 'ribo'
        linkage = 'PO'
        term_5p = '5P' if i == 0 else 'OH'
        basemod = 'none'

        attrs = pos_attrs[i]
        if 'sugar' in attrs:
            sugar = attrs['sugar']
        if 'linkage' in attrs:
            linkage = attrs['linkage']
        if 'terminal_5p' in attrs:
            term_5p = attrs['terminal_5p']
        if 'basemod' in attrs:
            basemod = attrs['basemod']

        slots.append(CanonicalNucSlot(
            base=base_char,
            sugar=sugar,
            linkage=linkage,
            terminal_5p=term_5p,
            basemod=basemod
        ))

    return slots
