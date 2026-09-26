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


def normalize_mod_code(mod_char: str) -> str:
    """
    Normalizes any modification code, symbol, or verbose chemical name 
    to its canonical single-letter chemical alphabet symbol.
    """
    c = str(mod_char or '').strip().upper()
    if not c:
        return ""
    if c in MODIFICATION_ALPHABET:
        return c
    if any(k in c for k in ('2OME', 'METHYL', "2'-OME", 'OMET')): return 'M'
    if any(k in c for k in ('2F', 'FLUORO', "2'-F")): return 'F'
    if any(k in c for k in ('PS', 'PHOSPHOROTHIOATE', 'THIO')): return 'S'
    if any(k in c for k in ('MOE', 'METHOXYETHYL')): return 'E'
    if any(k in c for k in ('LNA', 'LOCKED')): return 'L'
    if any(k in c for k in ('DEOXY', 'DNA')): return 'D'
    if any(k in c for k in ('UNA', 'UNLOCKED')): return '6'
    if any(k in c for k in ('GNA', 'GLYCOL')): return '8'
    if any(k in c for k in ('TNA', 'THREOSE')): return '9'
    if any(k in c for k in ('ENA', 'ETHYLENE')): return 'Y'
    if any(k in c for k in ('ABASIC',)): return 'Q'
    if any(k in c for k in ('BENZYL',)): return 'B'
    if any(k in c for k in ('FANA',)): return 'I'
    if any(k in c for k in ('INOSINE',)): return 'J'
    return c[0] if c else ""


# Empirical thermodynamic perturbation increments (ΔΔG°37 in kcal/mol per modification)
# Relative to unmodified ribonucleotide (Xia & Turner 1998, SantaLucia 1998, Egli & Manoharan 2023, Alnylam ESC/ESC+ data)
# Negative values stabilize duplex hybridization (lower ΔG); positive values destabilize.
MOD_DELTA_DG: Dict[str, float] = {
    'F': -0.85,   # 2'-Fluoro: C3'-endo gauche effect, pre-organizes A-form, strongly stabilizing (~ +1.2°C Tm)
    'M': -0.45,   # 2'-O-Methyl: C3'-endo preference, minor groove hydration, stabilizing (~ +0.7°C Tm)
    'L': -3.50,   # LNA: Locked C3'-endo ribose, massive thermal stabilization (~ +4.5°C Tm)
    'E': -0.75,   # 2'-MOE: 2'-O-methoxyethyl, stabilizes A-form duplex (~ +1.1°C Tm)
    'Y': -2.50,   # ENA: Ethylene-bridged nucleic acid, high thermal stability (~ +3.0°C Tm)
    'I': -0.30,   # 2'-F-ANA: Arabino-fluoro, moderate stabilization
    'V': -0.40,   # 5-Methyl Cytidine: Enhanced base stacking (~ +0.5°C Tm)
    'W': -0.50,   # Pseudouridine: Additional H-bonding via N1-H (~ +0.6°C Tm)
    'K': -0.60,   # 2-thio Uridine: Enhanced stacking and C3'-endo preference
    'Z': -0.20,   # 2'-OMe-4'-thio: Favorable duplex hybridization
    '7': -0.40,   # ANA: Altritol nucleic acid, stabilizes A-form
    
    'S': +0.40,   # Phosphorothioate (PS): Chiral relaxation & sulfur radius destabilizes (~ -0.5°C Tm/linkage)
    'D': +0.70,   # 2'-deoxy / DNA: C2'-endo B-form preference disrupts A-form helix (~ -1.2°C Tm)
    '6': +4.00,   # UNA: Acyclic unlocked ribose, huge entropic penalty (~ -6.0°C Tm)
    '8': +2.80,   # GNA: Acyclic glycol backbone, strong duplex destabilization (~ -4.0°C Tm)
    'Q': +4.50,   # Abasic site: Missing nucleobase, loss of H-bonding & stacking (~ -8.0°C Tm)
    'B': +1.80,   # 2'-O-Benzyl: Bulky aromatic steric clash in duplex minor groove
    'X': +0.60,   # 2'-O-allyl: Bulky alkyl side chain
    'J': +1.20,   # Inosine: Hypoxanthine pairs with C via 2 H-bonds instead of 3 (loss of 1 H-bond)
    'O': +1.50,   # Dihydrouridine: Non-planar ring disrupts aromatic stacking
    '9': +2.20,   # TNA: Threose backbone isomerism disrupts helical pitch
    
    'P': +0.30,   # Boranophosphate: Neutral backbone modification
    'R': +0.50,   # Methylphosphonate: Non-ionic backbone
    'H': +0.30,   # Phosphoramidate
    '1':  0.00,   # 5'-Phosphate: Terminal anchor
    '2':  0.00,   # 3'-Phosphate: Terminal
    '3': -0.10,   # 5'-OMe cap: Terminal
    '4': +0.20,   # GalNAc conjugate: Terminal ligand attachment
    '5': +0.20,   # PEG conjugate: Terminal conjugate
}


def get_mod_delta_dg(mod_code_or_name: str) -> float:
    """
    Retrieves empirical thermodynamic ΔΔG°37 increment (kcal/mol) for any chemical modification.
    """
    norm = normalize_mod_code(mod_code_or_name)
    return MOD_DELTA_DG.get(norm, 0.0)

