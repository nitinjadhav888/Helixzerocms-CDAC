"""
features_v2.py -- Literature-grounded multi-slot feature extractor for Model B v2.

Root-cause fix: builds features directly from chem_schema.NucSlot (orthogonal
sugar / linkage_3p / base_mod / terminal_5p / conjugate), so phosphorothioate
(PS) backbone protection, chemistry-conjugate identity, and phosphate-mimic
status are ALWAYS available to the model simultaneously with sugar chemistry,
instead of forcing a single per-position category (the legacy bug).

Every design choice below is grounded in a specific published finding, cited
inline, and cross-checked against the empirical position-wise chemistry
distributions found in v2_multislot_dataset.csv (42,638 CMsiRNAdb rows):

  - Bramsen et al. 2009, NAR 37(9):2867-81            -> seed rigidity feature
  - Allerson et al. 2005, J Med Chem 48(4):901-4      -> overall 2-prime-mod density
  - Khvorova/Schwarz 2003, Cell 115                   -> 5-prime terminal asymmetry
  - Elmen et al. 2005 (already validated in repo)     -> AS pos1 LNA is fatal
  - Schirle & MacRae 2012, Science                    -> AS pos1 needs 5P/mimic
  - Parmar et al. 2016, ChemBioChem 17(11):985-9      -> 5-VP phosphate mimic
  - Behlke 2008, Oligonucleotides 18(4):305-19        -> terminal-vs-internal PS
  - Sakamuri et al. 2020 (already validated in repo)  -> AT3 PS pattern
  - Nair et al. 2014, JACS 136(49):16958-61           -> GalNAc conjugate identity
  - Weingaertner et al. 2020 (already validated repo) -> AS-conjugate is fatal
  - Reynolds et al. 2004, Nat Biotechnol 22(3):326-30 -> GC/terminal composition
"""
from __future__ import annotations
from typing import List
import numpy as np

from .chem_schema import NucSlot

MAX_LEN = 21  # canonical siRNA body length; extra tail (overhangs/conjugate
              # pseudo-positions) is summarized via aggregate features, not
              # positional one-hot, since its length varies 0-6nt across sources.

_BULKY_RIGID = {"LNA", "MOE", "ENA"}
_FLEXIBLE_EXOTIC = {"FANA", "UNA", "GNA", "TNA", "ANA", "4thio", "Benzyl", "Hexadecyl", "Allyl"}
_PHOSPHATE_MIMIC_5P = {"5P", "5VP", "5PhosRibose"}

_SUGAR_GROUPS = ["is_2F", "is_2OMe", "is_bulky_rigid", "is_flexible_exotic",
                 "is_unmod_ribo", "is_dna", "is_abasic_cap", "is_other_sugar"]
N_POS_FLAGS = len(_SUGAR_GROUPS) + 2  # + is_PS_linkage, is_base_mod  = 10
N_POS_TOTAL = N_POS_FLAGS * MAX_LEN * 2  # sense + antisense = 420

_N_ENGINEERED = 24


def _sugar_group(sugar: str) -> str:
    if sugar == "2F":
        return "is_2F"
    if sugar == "2OMe":
        return "is_2OMe"
    if sugar in _BULKY_RIGID:
        return "is_bulky_rigid"
    if sugar in _FLEXIBLE_EXOTIC:
        return "is_flexible_exotic"
    if sugar == "ribo":
        return "is_unmod_ribo"
    if sugar == "deoxyribo":
        return "is_dna"
    if sugar in ("Abasic", "InvAbasic", "THF"):
        return "is_abasic_cap"
    return "is_other_sugar"


def _positional_block(slots: List[NucSlot]) -> np.ndarray:
    arr = np.zeros((MAX_LEN, N_POS_FLAGS), dtype=np.float32)
    for i in range(min(len(slots), MAX_LEN)):
        s = slots[i]
        g = _sugar_group(s.sugar)
        arr[i, _SUGAR_GROUPS.index(g)] = 1.0
        arr[i, len(_SUGAR_GROUPS)] = 1.0 if s.linkage_3p == "PS" else 0.0
        arr[i, len(_SUGAR_GROUPS) + 1] = 1.0 if s.base_mod else 0.0
    return arr


def _gc(seq_bases: List[str]) -> float:
    if not seq_bases:
        return 0.5
    n = len(seq_bases)
    gc = sum(1 for b in seq_bases if b in "GC")
    return gc / n


def _engineered(sense: List[NucSlot], anti: List[NucSlot]) -> List[float]:
    feats: List[float] = []
    sense_b = [s.base for s in sense]
    anti_b = [s.base for s in anti]

    # --- Bramsen 2009: seed (AS pos 2-8) rigidity load ---
    seed = anti[1:8]
    seed_bulky = sum(1 for s in seed if s.sugar in _BULKY_RIGID)
    feats.append(seed_bulky / max(1, len(seed)))
    seed_flex = sum(1 for s in seed if s.sugar in _FLEXIBLE_EXOTIC)
    feats.append(seed_flex / max(1, len(seed)))

    # --- Allerson 2005: overall 2-prime modification density per strand ---
    for strand in (sense, anti):
        n_mod = sum(1 for s in strand if s.sugar not in ("ribo", "n/a"))
        feats.append(n_mod / max(1, len(strand)))

    # --- Elmen 2005 / Schirle 2012 / Bramsen 2009: AS 5-prime anchor (pos1) state ---
    if anti:
        p1 = anti[0]
        feats.append(1.0 if p1.sugar in _BULKY_RIGID else 0.0)   # fatal-rigidity flag
        feats.append(1.0 if p1.sugar == "2F" else 0.0)
        feats.append(1.0 if p1.sugar == "2OMe" else 0.0)
    else:
        feats.extend([0.0, 0.0, 0.0])
    # Phosphate-mimic requirement for RISC loading (Parmar 2016 / Schirle 2012)
    has_5p_mimic = any(s.terminal_5p in _PHOSPHATE_MIMIC_5P for s in anti[:1])
    feats.append(1.0 if has_5p_mimic else 0.0)

    # --- Behlke 2008 / Sakamuri 2020: terminal vs internal PS density ---
    def ps_frac(strand, idxs):
        idxs = [i for i in idxs if i < len(strand)]
        if not idxs:
            return 0.0
        return sum(1 for i in idxs if strand[i].linkage_3p == "PS") / len(idxs)

    feats.append(ps_frac(anti, [0, 1]))                              # AS 5-prime terminal PS
    feats.append(ps_frac(anti, range(len(anti) - 2, len(anti))))       # AS 3-prime terminal PS
    feats.append(ps_frac(anti, range(2, max(2, len(anti) - 2))))       # AS internal PS (should be LOW)
    feats.append(ps_frac(sense, [0, 1]))                              # SS 5-prime terminal PS
    feats.append(ps_frac(sense, range(len(sense) - 2, len(sense))))     # SS 3-prime terminal PS

    # --- Nair 2014 / Weingaertner 2020: conjugate identity + fatal AS-conjugate ---
    sense_conj = any(s.conjugate for s in sense)
    anti_conj = any(s.conjugate for s in anti)
    feats.append(1.0 if sense_conj else 0.0)
    feats.append(1.0 if anti_conj else 0.0)          # literature says this should be ~fatal
    sense_galnac_3p = any(s.conjugate == "GalNAc" for s in sense[-3:]) if len(sense) >= 3 else False
    feats.append(1.0 if sense_galnac_3p else 0.0)     # canonical 3-prime GalNAc position

    # --- Reynolds 2004: sequence-composition covariates (unmodified base identity) ---
    feats.append(_gc(sense_b))
    feats.append(_gc(anti_b))
    feats.append(abs(_gc(sense_b) - _gc(anti_b)))
    feats.append(1.0 if anti_b and anti_b[0] in "AU" else 0.0)   # weak 5-prime AS end (Khvorova 2003 asymmetry)
    feats.append(1.0 if sense_b and sense_b[0] in "GC" else 0.0)
    tail = anti_b[-2:] if len(anti_b) >= 2 else anti_b
    feats.append(sum(1 for b in tail if b in "GC") / max(1, len(tail)))

    # --- lengths (design variants: 19-mer vs 21-mer vs 23-mer blunt/tiled) ---
    feats.append(len(sense) / 27.0)
    feats.append(len(anti) / 27.0)

    return feats


FEATURE_NAMES: List[str] = (
    [f"{strand}_pos{p+1}_{flag}" for strand in ("ss", "as") for p in range(MAX_LEN) for flag in _SUGAR_GROUPS + ["is_PS", "is_base_mod"]]
    + [
        "seed_bulky_rigid_frac", "seed_flexible_exotic_frac",
        "ss_mod_density", "as_mod_density",
        "as_pos1_bulky_rigid", "as_pos1_2F", "as_pos1_2OMe", "as_pos1_5p_phosphate_mimic",
        "as_5p_terminal_PS_frac", "as_3p_terminal_PS_frac", "as_internal_PS_frac",
        "ss_5p_terminal_PS_frac", "ss_3p_terminal_PS_frac",
        "sense_has_conjugate", "antisense_has_conjugate_FATAL_FLAG", "sense_3p_galnac",
        "sense_gc", "antisense_gc", "gc_asymmetry",
        "as_5p_weak_end_AU", "ss_5p_strong_end_GC", "as_3p_gc_clamp",
        "sense_len_norm", "anti_len_norm",
    ]
)
assert len(FEATURE_NAMES) == N_POS_TOTAL + _N_ENGINEERED, (len(FEATURE_NAMES), N_POS_TOTAL + _N_ENGINEERED)
N_FEATURES = len(FEATURE_NAMES)


def build_features_v2(sense_slots: List[NucSlot], anti_slots: List[NucSlot]) -> np.ndarray:
    ss_block = _positional_block(sense_slots).flatten()
    as_block = _positional_block(anti_slots).flatten()
    eng = np.array(_engineered(sense_slots, anti_slots), dtype=np.float32)
    return np.concatenate([ss_block, as_block, eng])


def batch_features_v2(sense_slots_list, anti_slots_list) -> np.ndarray:
    return np.stack([
        build_features_v2(ss, as_)
        for ss, as_ in zip(sense_slots_list, anti_slots_list)
    ])
