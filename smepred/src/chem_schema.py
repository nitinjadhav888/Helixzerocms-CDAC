"""
chem_schema.py -- Multi-slot chemical modification schema (v2)
================================================================
Fixes the root-cause data-model bug identified in HelixZero-CMS v1:
the old schema used ONE character per nucleotide position, forcing
sugar modification, backbone linkage, base modification, and terminal
conjugates to be mutually exclusive. Real ESC/ESC+ chemistry requires
ALL of these simultaneously at a single position (e.g. 2'-F sugar +
phosphorothioate linkage + being part of a GalNAc-conjugated 3' end).

This module represents each nucleotide as an orthogonal set of
independent chemical slots, and parses the compositional English
modification names found in patent-mined data (e.g. CMsiRNAdb) into
this schema WITHOUT discarding any chemistry.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional, List


# --- Controlled vocabularies for each independent slot ---------------------

SUGAR_CODES = {
    "ribo": "Ribose (unmodified RNA)",
    "deoxyribo": "Deoxyribose (unmodified DNA)",
    "2F": "2'-Fluoro",
    "2OMe": "2'-O-Methyl",
    "MOE": "2'-O-Methoxyethyl (MOE)",
    "LNA": "Locked Nucleic Acid",
    "ENA": "Ethylene-bridged NA (ENA)",
    "UNA": "Unlocked Nucleic Acid",
    "GNA": "Glycol Nucleic Acid",
    "TNA": "Threose Nucleic Acid",
    "FANA": "2'-F-arabino NA",
    "ANA": "Arabino Nucleic Acid",
    "EGNA": "Ethylene Glycol Nucleic Acid (thiophosphate variant)",
    "Benzyl": "2'-O-Benzyl",
    "Hexadecyl": "2'-O-hexadecyl (lipophilic)",
    "Allyl": "2'-O-allyl",
    "4thio": "4'-thio",
    "Abasic": "Abasic site",
    "InvAbasic": "Inverted abasic (3' cap, reversed orientation)",
    "THF": "Tetrahydrofuran abasic-like spacer",
    "unknown": "Unclassified/unparsed sugar chemistry",
}

LINKAGE_CODES = {
    "PO": "Phosphodiester (natural)",
    "PS": "Phosphorothioate",
    "PS2": "Phosphorodithioate",
    "Boranophosphate": "Boranophosphate",
    "Methylphosphonate": "Methylphosphonate",
    "Phosphoramidate": "Phosphoramidate",
    "CyclopropylPhosphonate": "Cyclopropyl phosphonate",
    "MethylenePhosphonate": "4'-O-methylene phosphonate",
}

BASE_MOD_CODES = {
    None: "Canonical base",
    "m5C": "5-Methylcytidine",
    "pseudoU": "Pseudouridine",
    "inosine": "Inosine",
    "2thioU": "2-thiouridine",
    "dihydroU": "Dihydrouridine",
    "2aminoA": "2'-amino-adenosine variant",
}

TERMINAL_5P_CODES = {
    None: "None (free 5'-OH or default)",
    "5P": "Natural 5'-Phosphate",
    "5VP": "5'-(E)-Vinylphosphonate (clinically stable 5'-P mimic)",
    "5OMeCap": "5'-O-Methyl cap (blocks 5'-phosphorylation)",
    "5PhosRibose": "5'-Phosphate-ribose linked sugar (Dicerna-style)",
}

CONJUGATE_CATEGORIES = {
    None: "None",
    "GalNAc": "N-Acetylgalactosamine (hepatocyte ASGPR ligand)",
    "Cholesterol": "Cholesterol / lipid conjugate",
    "PEG": "Polyethylene glycol",
    "Ligand_L_series": "Proprietary 'L'-series extrahepatic ligand",
    "Ligand_H_series": "Proprietary 'H'-series extrahepatic ligand",
    "Ligand_MVIP_series": "Proprietary MVIP-series ligand",
    "Ligand_C7NH_series": "C7NH-linked ligand series (peptide/receptor-targeting)",
    "Unclassified": "Unclassified conjugate/ligand (raw code preserved)",
}


@dataclass
class NucSlot:
    """Orthogonal chemical description of ONE nucleotide position."""
    base: str                              # A, C, G, U, T (never lost)
    sugar: str = "ribo"
    linkage_3p: str = "PO"                 # linkage connecting THIS nt to the NEXT (3') nt
    base_mod: Optional[str] = None
    terminal_5p: Optional[str] = None      # only meaningful at position 1
    conjugate: Optional[str] = None        # only meaningful at terminal positions
    conjugate_raw: Optional[str] = None    # raw ligand code, e.g. "NAG25", "L14"
    raw_name: str = ""                     # original compositional string, always preserved
    parsed_ok: bool = True                 # False if we fell back to "unknown"


# --- Compositional-name parser ----------------------------------------------

_BASE_WORD_TO_LETTER = {
    "adenosine": "A", "cytidine": "C", "guanosine": "G",
    "uridine": "U", "thymidine": "T", "adenine": "A",
    "uracil": "U", "cytosine": "C", "guanine": "G",
}

# Sugar chemistry keyword -> code, ORDER MATTERS (most specific first)
_SUGAR_PATTERNS = [
    (r"2'-o-methyl-4'-o-methylene phosphonate", "2OMe"),
    (r"2'-o-methyl-2'-amino", "2OMe"),
    (r"2'-o-methylinosine", "2OMe"),
    (r"2'-o-methyl", "2OMe"),
    (r"2'-methoxyethyl", "MOE"),
    (r"2'-methoxy(?!ethyl)", "2OMe"),   # VP nomenclature shorthand, e.g. "2'-methoxyadenosine"
    (r"2'-deoxy-2'-fluoro-4'-thio", "4thio"),
    (r"2'-fluoro", "2F"),
    (r"2'-deoxy", "deoxyribo"),
    (r"2'-o-hexadecyl", "Hexadecyl"),
    (r"2'-o-benzyl", "Benzyl"),
    (r"2'-o-allyl", "Allyl"),
    (r"2'-o-n-methylacetamide", "2OMe"),
    (r"2'-f-ana|2'-fluoroarabino|fana", "FANA"),
    (r"arabino", "ANA"),
    (r"glycol nucleic acid|-glycol nucleic acid|threofuranosyl", "GNA"),
    (r"threose nucleic acid", "TNA"),
    (r"unlocked nucleic acid", "UNA"),
    (r"locked nucleic acid", "LNA"),
    (r"ethylene glycol nucleic acid", "EGNA"),
    (r"4'-thio", "4thio"),
    (r"tetrahydrofuran", "THF"),
    (r"^abasic$|^abasic", "Abasic"),
    (r"inverted abasic", "InvAbasic"),
]

# Linkage keyword -> code
_LINKAGE_PATTERNS = [
    (r"phosphorodithioate", "PS2"),
    (r"phosphorothioate", "PS"),
    (r"boranophosphate", "Boranophosphate"),
    (r"methylphosphonate", "Methylphosphonate"),
    (r"phosphoramidate", "Phosphoramidate"),
    (r"cyclopropyl phosphonate", "CyclopropylPhosphonate"),
    (r"methylene phosphonate", "MethylenePhosphonate"),
]

_BASE_MOD_PATTERNS = [
    (r"methylcytidine|5-methylcytidine", "m5C"),
    (r"pseudouridine", "pseudoU"),
    (r"inosine", "inosine"),
    (r"2-thio.?uridine", "2thioU"),
    (r"dihydrouridine", "dihydroU"),
    (r"2'-amino", "2aminoA"),
]

# Known proprietary ligand/conjugate short codes (not decomposable by rule)
_LIGAND_CODE_RE = re.compile(
    r"^(NAG\d+[a-z]?|L\d+|H\d+[a-z]?|Hd|MVIP\d+|C7NH-L\d+|C6NH-L\d+U|"
    r"SA\d+SA\d+SA\d+|Y1|n001[RS]|Mod\d+L\d+)"
)


def _classify_ligand_code(code: str) -> str:
    c = code.upper()
    if "NAG" in c or "GALNAC" in c or "ACETYLGALACTOSAMINE" in c or "GAL-" in c or re.search(r"GA.?NAC", c):
        return "GalNAc"
    if "CHOL" in c:
        return "Cholesterol"
    if "PEG" in c or "POLYETHYLENE GLYCOL" in c:
        return "PEG"
    if re.match(r"^L\d+$", code) or code in ("L-shaped ligand", "S-shaped ligand"):
        return "Ligand_L_series"
    if re.match(r"^H\d+", code) or code == "Hd":
        return "Ligand_H_series"
    if code.startswith("MVIP"):
        return "Ligand_MVIP_series"
    if "C7NH" in code or "C6NH" in code:
        return "Ligand_C7NH_series"
    if "C12" in code or "PAZ" in code:
        return "Ligand_L_series"  # lipophilic tail / peptide-anchor-domain linker
    return "Unclassified"


def _strip_wrapping_punct(s: str) -> str:
    """Strips outer parens/prefixes like 'IB(...)' seen in OCR-mined ligand codes."""
    t = s.strip()
    if t.startswith("IB(") and t.endswith(")"):
        t = t[3:-1]
    t = t.strip("()")
    return t


def parse_modification_name(raw: str, position_base_hint: Optional[str] = None) -> NucSlot:
    """
    Decomposes a compositional modification-name string (as found in
    CMsiRNAdb-style patent-mined data) into an orthogonal NucSlot.

    Never silently discards chemistry: unrecognized fragments are kept
    in `raw_name` and `parsed_ok` is set to False so downstream code can
    flag/exclude low-confidence rows instead of pretending certainty.
    """
    original = raw.strip()
    text = original.lower().replace("’", "'")

    slot = NucSlot(base=position_base_hint or "N", raw_name=original)

    # -- Known non-chemistry scraping artifacts (protein domain names etc
    #    that leaked into the modification-type column during OCR/table
    #    extraction). Explicitly flagged, never guessed at. --
    _JUNK_ARTIFACTS = {"piwi/argonaute/zwille domain"}
    if text in _JUNK_ARTIFACTS:
        slot.sugar = "unknown"
        slot.parsed_ok = False
        return slot

    # -- Reverse-oriented deoxy caps (3'-3' or 5'-5' inverted linkage) --
    m_rev = re.match(r"^reverse deoxy(adenosine|cytidine|guanosine|thymidine|uridine)$", text)
    if m_rev:
        slot.base = _BASE_WORD_TO_LETTER[m_rev.group(1)]
        slot.sugar = "deoxyribo"
        slot.base_mod = "reverse_linkage"
        return slot

    # -- Bare canonical base (A, C, G, U, T) possibly with trailing -3'-PS --
    m = re.match(r"^([acgut])(-3'-phosphorothioate)?$", text)
    if m:
        slot.base = m.group(1).upper()
        slot.sugar = "deoxyribo" if slot.base == "T" else "ribo"
        if m.group(2):
            slot.linkage_3p = "PS"
        return slot

    # -- Vinylphosphonate 5' terminal modifications --
    if "vinyl phosphonate" in text or "vinyl-(e)-phosphonate" in text:
        slot.terminal_5p = "5VP"
        text = re.sub(r"vinyl[- ]?\(?e?\)?-?phosphonate-?", "", text).strip("- ")

    # -- 5'-Phosphate-ribose prefix (Dicerna-style annotation) --
    if text.startswith("5'-phosphate ribose"):
        slot.terminal_5p = "5PhosRibose"
        text = text.replace("5'-phosphate ribose-", "").replace("5'-phosphate ribose", "").strip("- ")

    # -- Standalone 5'-phosphate / 5'-OMe cap --
    if re.match(r"^5'-phosphate$", text):
        slot.terminal_5p = "5P"
        slot.sugar = "ribo"
        return slot

    # -- Inverted abasic prefix (chain-terminating cap, may carry its own sugar mod) --
    if text.startswith("inverted abasic"):
        slot.sugar = "InvAbasic"
        remainder = text[len("inverted abasic"):].lstrip("- ")
        if remainder:
            sub = parse_modification_name(remainder.strip(), position_base_hint)
            slot.linkage_3p = sub.linkage_3p
            slot.terminal_5p = slot.terminal_5p or sub.terminal_5p
            slot.base = sub.base if sub.base != "N" else "Q"
        else:
            slot.base = "Q"
        return slot

    if text == "abasic":
        slot.sugar = "Abasic"
        slot.base = "Q"
        return slot

    # -- Cholesterol / TEG conjugate, possibly with a PS-linkage prefix --
    if "cholesterol" in text or "triethylene glycol" in text or text == "chol-teg":
        if "phosphorothioate" in text:
            slot.linkage_3p = "PS"
        slot.base = "-"
        slot.sugar = "n/a"
        slot.conjugate_raw = original
        slot.conjugate = "Cholesterol"
        return slot

    # -- Ligand/conjugate proprietary short codes (incl. parenthesized OCR forms) --
    _stripped = _strip_wrapping_punct(original)
    if (_LIGAND_CODE_RE.match(original) or _LIGAND_CODE_RE.match(_stripped)
        or original in (
            "Chol-TEG", "Cholesterol-Triethylene Glycol", "L-shaped ligand",
            "S-shaped ligand", "N-acetyl-galactosamine",
            "C11-Polyethylene Glycol Tri-N-Acetylglucosamine",
            "Lipophilic Linker-025 Dimer", "C6-SS-Alkyl-Methyl",
        )
        or "galnac" in text or "acetylgalactosamine" in text or "nag" in text
        or re.match(r"^\(?gal-\d+\)?", text) or "(c12)" in text or "(paz)" in text
        or re.search(r"ga.?nac", text)):
        slot.base = "-"
        slot.sugar = "n/a"
        slot.conjugate_raw = original
        slot.conjugate = _classify_ligand_code(_stripped)
        return slot

    # -- Rare backbone/sugar isomer: 2'-phosphate (distinct from 3'-phosphate) --
    m2p = re.match(r"^2'-phosphate (adenosine|cytidine|guanosine|uridine|thymidine)$", text)
    if m2p:
        slot.base = _BASE_WORD_TO_LETTER[m2p.group(1)]
        slot.sugar = "2Phos"
        return slot

    # -- Rare: 3'-O-methyl with 2'-5' linked phosphate (non-standard backbone isomer) --
    if "2'-5' linked phosphate" in text:
        base_found = next((L for w, L in _BASE_WORD_TO_LETTER.items() if w in text), position_base_hint or "N")
        slot.base = base_found
        slot.sugar = "3OMe_25linked"
        return slot

    # -- Extract linkage (search anywhere in string) --
    for pat, code in _LINKAGE_PATTERNS:
        if re.search(pat, text):
            slot.linkage_3p = code
            break

    # -- Extract base_mod --
    for pat, code in _BASE_MOD_PATTERNS:
        if re.search(pat, text):
            slot.base_mod = code
            break

    # -- Extract sugar chemistry --
    matched_sugar = False
    for pat, code in _SUGAR_PATTERNS:
        if re.search(pat, text):
            slot.sugar = code
            matched_sugar = True
            break

    # -- Extract base identity (last nucleobase word found) --
    base_found = None
    for word, letter in _BASE_WORD_TO_LETTER.items():
        if word in text:
            base_found = letter
    if base_found:
        slot.base = base_found
    elif position_base_hint:
        slot.base = position_base_hint

    if (not matched_sugar and slot.base_mod is None and slot.terminal_5p is None
            and slot.linkage_3p == "PO"):
        slot.parsed_ok = False
        slot.sugar = "unknown"

    return slot


def parse_position_string(mod_types_field: str, base_seq: str) -> List[NucSlot]:
    """
    Parses a full `Modification_Types_*_strand` field
    (format: "1*<name> || 2*<name> || ...") into an ordered list of NucSlot.
    `base_seq` (canonical bases) is used as a fallback base hint per index.
    """
    slots: List[NucSlot] = []
    if not isinstance(mod_types_field, str) or not mod_types_field.strip():
        return slots
    parts = [p.strip() for p in mod_types_field.split("||") if p.strip()]
    for part in parts:
        if "*" in part:
            idx_str, name = part.split("*", 1)
        else:
            idx_str, name = str(len(slots) + 1), part
        try:
            idx = int(idx_str.strip())
        except ValueError:
            idx = len(slots) + 1
        base_hint = base_seq[idx - 1] if base_seq and 0 < idx <= len(base_seq) else None
        slots.append(parse_modification_name(name.strip(), base_hint))
    return slots


# --- Inference-time bridge from legacy single-char candidates ---------------
# modification_engine.py still generates candidates in the legacy one-char/
# position alphabet (features._MODIFICATION_MAP). This promotes those chars
# to NucSlot so Model B v2 can score them today. NOTE: the legacy alphabet
# still can't express independent sugar+PS co-occurrence at a position (that
# is the root-cause bug this schema fixes for *data*) -- generating truly
# multi-slot candidates requires upgrading modification_engine.py, tracked
# as follow-up work, not done here.
_LEGACY_CHAR_TO_SUGAR = {
    'F': '2F', 'M': '2OMe', 'L': 'LNA', 'D': 'deoxyribo', 'E': 'MOE',
    'B': 'Benzyl', 'N': '4thio', 'I': 'FANA', 'Y': 'ENA',
    '6': 'UNA', '7': 'ANA', '8': 'GNA', '9': 'TNA', 'Q': 'Abasic',
}
_LEGACY_CHAR_TO_BASEMOD = {'V': 'm5C', 'W': 'pseudoU', 'J': 'inosine', 'K': '2thioU', 'O': 'dihydroU'}


def promote_legacy_string(modified: str, base_seq: str) -> List[NucSlot]:
    """Legacy per-position char string -> NucSlot list, for scoring existing candidates."""
    slots = []
    for i, c in enumerate(modified):
        base = base_seq[i] if i < len(base_seq) else 'N'
        if c == 'S':
            slots.append(NucSlot(base=base, sugar="ribo", linkage_3p="PS"))
        elif c in _LEGACY_CHAR_TO_SUGAR:
            slots.append(NucSlot(base=base, sugar=_LEGACY_CHAR_TO_SUGAR[c]))
        elif c in _LEGACY_CHAR_TO_BASEMOD:
            slots.append(NucSlot(base=base, sugar="ribo", base_mod=_LEGACY_CHAR_TO_BASEMOD[c]))
        elif c == '1':
            slots.append(NucSlot(base=base, sugar="ribo", terminal_5p="5P"))
        elif c == '4':
            slots.append(NucSlot(base=base, sugar="n/a", conjugate="Unclassified"))
        else:
            slots.append(NucSlot(base=base, sugar="ribo"))
    return slots


# --- Down-projection to the legacy single-char alphabet ----------------------
# Used to (a) reproduce the historical single-slot representation for
# controlled ablations, and (b) as one component of the production blend
# (see scripts/train_model_b_v2.py). Priority: conjugate > base_mod > sugar
# > bare-PS > unmodified base -- calibrated to match the ~0.03-0.1% PS-symbol
# density empirically observed in the legacy training CSVs.
_SUGAR_TO_LEGACY = {
    "2F": "F", "2OMe": "M", "LNA": "L", "MOE": "E", "deoxyribo": "D",
    "Benzyl": "B", "4thio": "N", "FANA": "I", "ENA": "Y", "UNA": "6",
    "ANA": "7", "GNA": "8", "TNA": "9", "Abasic": "Q", "InvAbasic": "Q", "THF": "Q",
}
_BASEMOD_TO_LEGACY = {"m5C": "V", "pseudoU": "W", "inosine": "J", "2thioU": "K", "dihydroU": "O"}


_PHOSPHATE_MIMIC_5P = {"5P", "5VP", "5PhosRibose"}


def slots_to_legacy_string(slots: List[NucSlot]) -> str:
    chars = []
    for s in slots:
        if s.terminal_5p in _PHOSPHATE_MIMIC_5P:
            chars.append("1")  # RISC 5'-phosphate anchor (natural or stable mimic)
        elif s.conjugate:
            chars.append("4")
        elif s.base_mod in _BASEMOD_TO_LEGACY:
            chars.append(_BASEMOD_TO_LEGACY[s.base_mod])
        elif s.sugar in _SUGAR_TO_LEGACY:
            chars.append(_SUGAR_TO_LEGACY[s.sugar])
        elif s.sugar == "ribo" and s.linkage_3p == "PS":
            chars.append("S")
        else:
            chars.append(s.base if s.base and s.base not in ("-", "Q") else ".")
    return "".join(chars)
