"""
chem_alphabet.py -- Single Source of Truth for Chemical Modification Alphabet
=============================================================================
Unified canonical dictionary mapping single-letter modification codes to 
their exact sugar, backbone linkage, terminal 5', base modification, and 
conjugate chemistry properties across all modules.
"""

from typing import Dict, Any, FrozenSet

MODIFICATION_ALPHABET: Dict[str, Dict[str, Any]] = {
    'M': {'sugar': '2OMe', 'name': "2'-O-Methyl", 'type': 'sugar', 'b_factor': 80.0, 'tier': 0},
    'F': {'sugar': '2F', 'name': "2'-Fluoro", 'type': 'sugar', 'b_factor': 90.0, 'tier': 0},
    'D': {'sugar': 'deoxyribo', 'name': "2'-deoxy", 'type': 'sugar', 'b_factor': 0.0, 'tier': 0},
    'L': {'sugar': 'LNA', 'name': "Locked Nucleic Acid (LNA)", 'type': 'sugar', 'b_factor': 50.0, 'tier': 1},
    'E': {'sugar': '2MOE', 'name': "2'-O-Methoxyethyl (MOE)", 'type': 'sugar', 'b_factor': 60.0, 'tier': 1},
    'Y': {'sugar': 'ENA', 'name': "Ethylene-bridged Nucleic Acid (ENA)", 'type': 'sugar', 'b_factor': 55.0, 'tier': 1},
    'Q': {'sugar': 'abasic', 'name': "Abasic Site", 'type': 'sugar', 'b_factor': 0.0, 'tier': 2},
    'B': {'sugar': 'Benzyl', 'name': "2'-O-Benzyl", 'type': 'sugar', 'b_factor': 0.0, 'tier': 2},
    'I': {'sugar': 'FANA', 'name': "2'-F-ANA", 'type': 'sugar', 'b_factor': 0.0, 'tier': 2},
    'Z': {'sugar': '2OMe-4thio', 'name': "2'-OMe-4'-thio", 'type': 'sugar', 'b_factor': 0.0, 'tier': 2},
    'X': {'sugar': 'allyl', 'name': "2'-O-allyl", 'type': 'sugar', 'b_factor': 0.0, 'tier': 2},
    '6': {'sugar': 'UNA', 'name': "Unlocked Nucleic Acid (UNA)", 'type': 'sugar', 'b_factor': 0.0, 'tier': 2},
    '7': {'sugar': 'ANA', 'name': "Altritol Nucleic Acid (ANA)", 'type': 'sugar', 'b_factor': 0.0, 'tier': 2},
    '8': {'sugar': 'GNA', 'name': "Glycerol Nucleic Acid (GNA)", 'type': 'sugar', 'b_factor': 0.0, 'tier': 2},
    '9': {'sugar': 'TNA', 'name': "Threose Nucleic Acid (TNA)", 'type': 'sugar', 'b_factor': 0.0, 'tier': 2},

    'S': {'linkage_3p': 'PS', 'name': "Phosphorothioate (PS)", 'type': 'backbone', 'b_factor': 70.0, 'tier': 0},
    'P': {'linkage_3p': 'Boranophosphate', 'name': "Boranophosphate", 'type': 'backbone', 'b_factor': 0.0, 'tier': 2},
    'R': {'linkage_3p': 'Methylphosphonate', 'name': "Methylphosphonate", 'type': 'backbone', 'b_factor': 0.0, 'tier': 2},
    'H': {'linkage_3p': 'Phosphoramidate', 'name': "Phosphoramidate", 'type': 'backbone', 'b_factor': 0.0, 'tier': 2},
    '2': {'linkage_3p': '3P', 'name': "3'-Phosphate", 'type': 'backbone', 'b_factor': 0.0, 'tier': 0},

    '1': {'terminal_5p': '5P', 'name': "5'-Phosphate", 'type': 'terminus', 'b_factor': 0.0, 'tier': 0},
    '3': {'terminal_5p': '5OMe', 'name': "5'-OMe cap", 'type': 'terminus', 'b_factor': 0.0, 'tier': 0},

    '4': {'conjugate': 'GalNAc', 'name': "Trivalent GalNAc Conjugate", 'type': 'conjugate', 'b_factor': 0.0, 'tier': 0},
    '5': {'conjugate': 'PEG', 'name': "PEG Conjugate", 'type': 'conjugate', 'b_factor': 0.0, 'tier': 2},

    'J': {'base_mod': 'inosine', 'sugar': '2OMe', 'name': "Inosine", 'type': 'base', 'b_factor': 0.0, 'tier': 2},
    'V': {'base_mod': '5mC', 'name': "5-Methyl Cytidine", 'type': 'base', 'b_factor': 0.0, 'tier': 2},
    'W': {'base_mod': 'pseudouridine', 'name': "Pseudouridine", 'type': 'base', 'b_factor': 0.0, 'tier': 2},
    'K': {'base_mod': '2thioU', 'name': "2-thio Uridine", 'type': 'base', 'b_factor': 0.0, 'tier': 2},
    'O': {'base_mod': 'dihydrouridine', 'name': "Dihydrouridine", 'type': 'base', 'b_factor': 0.0, 'tier': 2},
}

MOD_2PRIME: FrozenSet[str] = frozenset(
    code for code, data in MODIFICATION_ALPHABET.items()
    if data.get('sugar') in ('2OMe', '2F', 'LNA', '2MOE', 'ENA', 'Benzyl', 'FANA', '2OMe-4thio', 'allyl', 'UNA', 'ANA', 'GNA', 'TNA')
)

TIER_0_FDA_CORE: FrozenSet[str] = frozenset(
    code for code, data in MODIFICATION_ALPHABET.items() if data.get('tier') == 0
) | frozenset("acgtuACGTU.")

TIER_1_PRECLINICAL: FrozenSet[str] = frozenset(
    code for code, data in MODIFICATION_ALPHABET.items() if data.get('tier') == 1
)


def get_mod_property(code: str, prop: str, default: Any = None) -> Any:
    """Helper to safely retrieve a modification property for a given code."""
    c = str(code).upper()
    if c in MODIFICATION_ALPHABET:
        return MODIFICATION_ALPHABET[c].get(prop, default)
    return default
