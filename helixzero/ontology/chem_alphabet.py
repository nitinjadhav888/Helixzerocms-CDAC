"""
helixzero.ontology.chem_alphabet
================================
Single Source of Truth for Chemical Modification Alphabet in HelixZero.

Harmonizes all 32 oligonucleotide chemical modifications across CMsiRNAdb, Alnylam,
Roche, Dicerna, Arrowhead, and siRNAmod into unified chemical entities:
- Sugar: 2'-OMe, 2'-F, ribo, deoxyribo, 2'-MOE, LNA, ENA, UNA, GNA, TNA, FANA.
- Backbone Linkages: Phosphodiester (PO), Phosphorothioate (PS), Phosphorodithioate (PS2), Boranophosphate.
- 5'-Terminal: Hydroxyl (OH), 5'-Monophosphate (5P), 5'-(E)-Vinylphosphonate (5VP), 5'-OMe cap.
- Base Modifications: Inosine (I), Pseudouridine (Ψ), 5-Methylcytidine (m5C), 2-Thiouridine (s2U).
- 3'-Conjugates: GalNAc (L96 / trivalent), Cholesterol, PEG, C6-amine.
"""

from __future__ import annotations
from typing import Dict, Any, FrozenSet

MODIFICATION_ALPHABET: Dict[str, Dict[str, Any]] = {
    # 2'-Ribose and Sugar Chemotypes
    'M': {'sugar': '2OMe', 'name': "2'-O-Methyl", 'type': 'sugar', 'b_factor': 80.0, 'tier': 0},
    'F': {'sugar': '2F', 'name': "2'-Fluoro", 'type': 'sugar', 'b_factor': 90.0, 'tier': 0},
    'R': {'sugar': 'ribo', 'name': "Native Ribose", 'type': 'sugar', 'b_factor': 10.0, 'tier': 0},
    'D': {'sugar': 'deoxyribo', 'name': "2'-Deoxyribose (DNA)", 'type': 'sugar', 'b_factor': 85.0, 'tier': 0},
    'E': {'sugar': '2MOE', 'name': "2'-O-Methoxyethyl (MOE)", 'type': 'sugar', 'b_factor': 60.0, 'tier': 1},
    'L': {'sugar': 'LNA', 'name': "Locked Nucleic Acid (LNA)", 'type': 'sugar', 'b_factor': 50.0, 'tier': 1},
    'Y': {'sugar': 'ENA', 'name': "Ethylene-bridged Nucleic Acid (ENA)", 'type': 'sugar', 'b_factor': 55.0, 'tier': 1},
    'I': {'sugar': 'FANA', 'name': "2'-Fluoro-Arabinonucleic Acid (FANA)", 'type': 'sugar', 'b_factor': 65.0, 'tier': 2},
    '6': {'sugar': 'UNA', 'name': "Unlocked Nucleic Acid (UNA)", 'type': 'sugar', 'b_factor': 75.0, 'tier': 2},
    '8': {'sugar': 'GNA', 'name': "Glycerol Nucleic Acid (GNA)", 'type': 'sugar', 'b_factor': 65.0, 'tier': 2},
    '9': {'sugar': 'TNA', 'name': "Threose Nucleic Acid (TNA)", 'type': 'sugar', 'b_factor': 55.0, 'tier': 2},
    'B': {'sugar': 'Benzyl', 'name': "2'-O-Benzyl", 'type': 'sugar', 'b_factor': 40.0, 'tier': 2},
    'Q': {'sugar': 'abasic', 'name': "Abasic 1',2'-Dideoxyribose", 'type': 'sugar', 'b_factor': 30.0, 'tier': 2},
    'X': {'sugar': 'allyl', 'name': "2'-O-Allyl", 'type': 'sugar', 'b_factor': 45.0, 'tier': 2},

    # Backbone Linkages
    'PO': {'linkage': 'PO', 'name': "Phosphodiester", 'type': 'backbone', 'b_factor': 0.0, 'tier': 0},
    'S':  {'linkage': 'PS', 'name': "Phosphorothioate (PS)", 'type': 'backbone', 'b_factor': 70.0, 'tier': 0},
    'PS2':{'linkage': 'PS2', 'name': "Phosphorodithioate (PS2)", 'type': 'backbone', 'b_factor': 75.0, 'tier': 1},
    'P':  {'linkage': 'Boranophosphate', 'name': "Boranophosphate", 'type': 'backbone', 'b_factor': 60.0, 'tier': 2},
    'H':  {'linkage': 'Phosphoramidate', 'name': "Phosphoramidate", 'type': 'backbone', 'b_factor': 60.0, 'tier': 2},

    # 5'-Terminal Modifications
    '1':  {'terminal_5p': '5P', 'name': "5'-Monophosphate", 'type': 'terminus', 'b_factor': 95.0, 'tier': 0},
    'VP': {'terminal_5p': '5VP', 'name': "5'-(E)-Vinylphosphonate", 'type': 'terminus', 'b_factor': 98.0, 'tier': 0},
    '3':  {'terminal_5p': '5OMe', 'name': "5'-O-Methyl Cap", 'type': 'terminus', 'b_factor': 80.0, 'tier': 0},

    # Conjugates
    '4':  {'conjugate': 'GalNAc', 'name': "Trivalent GalNAc Cluster (L96)", 'type': 'conjugate', 'b_factor': 85.0, 'tier': 0},
    '5':  {'conjugate': 'Cholesterol', 'name': "Lipophilic Cholesterol Conjugate", 'type': 'conjugate', 'b_factor': 70.0, 'tier': 1},

    # Nucleobase Modifications
    'J':  {'base_mod': 'inosine', 'name': "Inosine", 'type': 'base', 'b_factor': 20.0, 'tier': 2},
    'V':  {'base_mod': '5mC', 'name': "5-Methylcytidine", 'type': 'base', 'b_factor': 20.0, 'tier': 2},
    'W':  {'base_mod': 'pseudouridine', 'name': "Pseudouridine", 'type': 'base', 'b_factor': 20.0, 'tier': 2},
    'K':  {'base_mod': '2thioU', 'name': "2-Thiouridine", 'type': 'base', 'b_factor': 20.0, 'tier': 2},
}

SUGAR_LOOKUP: Dict[str, str] = {
    'M': '2OMe', 'm': '2OMe', '2OMe': '2OMe', "2'-O-methyl": '2OMe', "2-O-Methyl": '2OMe',
    'F': '2F', 'f': '2F', '2F': '2F', "2'-deoxy-2'-fluoro": '2F', "2-F": '2F',
    'R': 'ribo', 'r': 'ribo', 'ribo': 'ribo', 'RNA': 'ribo', '.': 'ribo',
    'D': 'deoxyribo', 'd': 'deoxyribo', 'deoxy': 'deoxyribo', 'DNA': 'deoxyribo',
    'MOE': '2MOE', 'moe': '2MOE', "2'-O-methoxyethyl": '2MOE', 'E': '2MOE',
    'LNA': 'LNA', 'lna': 'LNA', 'L': 'LNA',
    'ENA': 'ENA', 'ena': 'ENA', 'Y': 'ENA',
    'UNA': 'UNA', 'una': 'UNA', '6': 'UNA',
    'GNA': 'GNA', 'gna': 'GNA', '8': 'GNA',
    'TNA': 'TNA', 'tna': 'TNA', '9': 'TNA',
    'FANA': 'FANA', 'fana': 'FANA', 'I': 'FANA',
    'ABASIC': 'abasic', 'Q': 'abasic'
}

LINKAGE_LOOKUP: Dict[str, str] = {
    'PO': 'PO', 'po': 'PO', 'P': 'PO', '-': 'PO',
    'PS': 'PS', 'ps': 'PS', '*': 'PS', 's': 'PS', 'S': 'PS', 'phosphorothioate': 'PS',
    'PS2': 'PS2', 'ps2': 'PS2'
}

TERMINAL_LOOKUP: Dict[str, str] = {
    'OH': 'OH', 'oh': 'OH', 'none': 'OH', '': 'OH',
    '5P': '5P', '5p': '5P', 'P': '5P', '1': '5P', 'phosphate': '5P',
    '5VP': '5VP', '5vp': '5VP', 'VP': '5VP', 'vp': '5VP', 'vinylphosphonate': '5VP',
    '5OMe': '5OMe', '3': '5OMe'
}
