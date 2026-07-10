"""
multislot_designer.py -- Generates clinically-realistic, fully multi-slot
siRNA modification patterns (independent sugar + PS backbone + 5' phosphate
mimic + 3' conjugate at every position simultaneously) and ranks them with
Model B v2 + the existing biophysics penalty engine.

This is the direct fix for the candidate-generation half of the root-cause
bug: modification_engine.py's single_mod_scan/multimod_gen still can't
express "2'-F sugar AND phosphorothioate linkage at the same position"
because its candidates are one-char-per-position strings. Here, candidates
are built natively as chem_schema.NucSlot lists, so every combination the
literature says matters can actually be represented and scored.

Design axes, each grounded in a specific study already used to validate
this pipeline (see docs/validations/model_b_v2_multislot_ablation.md):
  - sugar alternation phase (2'-F / 2'-OMe)         Allerson 2005; Bramsen 2009
  - terminal phosphorothioate (Sakamuri AT3 pattern) Behlke 2008; Sakamuri 2020
  - antisense 5' phosphate mimic (5'-VP)            Parmar 2016; Schirle 2012
  - sense 3'-GalNAc conjugate                        Nair 2014; Weingärtner 2020
Antisense conjugation is never generated (confirmed fatal, see H2 audit).
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import List

from .chem_schema import NucSlot
from .biophysics import calculate_adjusted_efficacy
from . import model_b_v2


@dataclass
class MultiSlotDesign:
    sense_slots: List[NucSlot]
    anti_slots: List[NucSlot]
    label: str
    raw_score: float = 0.0
    adjusted_score: float = 0.0
    penalties: dict = None

    @property
    def sense_annotated(self) -> List[dict]:
        return [_slot_summary(s) for s in self.sense_slots]

    @property
    def antisense_annotated(self) -> List[dict]:
        return [_slot_summary(s) for s in self.anti_slots]


def _slot_summary(s: NucSlot) -> dict:
    return {"base": s.base, "sugar": s.sugar, "linkage_3p": s.linkage_3p,
            "base_mod": s.base_mod, "terminal_5p": s.terminal_5p, "conjugate": s.conjugate}


_SUGAR_TO_LEGACY = {"2F": "F", "2OMe": "M", "LNA": "L", "MOE": "E", "deoxyribo": "D"}


def _slots_to_biophysics_view(slots: List[NucSlot]) -> str:
    """Legacy-alphabet projection FOR THE BIOPHYSICS PENALTY ENGINE specifically
    (different priority than chem_schema.slots_to_legacy_string, which is
    calibrated to replicate historical *training-data* loss for the ablation).
    biophysics.py's nuclease/serum checks key off 'S' and '1' explicitly, so
    those take priority here; this under-counts 2'-mod density by one slot
    when PS and a sugar mod truly co-occur -- an accepted, documented
    approximation of the single-char rule engine, not a claim of full fidelity."""
    chars = []
    for s in slots:
        if s.terminal_5p in {"5P", "5VP", "5PhosRibose"}:
            chars.append("1")
        elif s.conjugate:
            chars.append("4")
        elif s.linkage_3p == "PS":
            chars.append("S")
        elif s.sugar in _SUGAR_TO_LEGACY:
            chars.append(_SUGAR_TO_LEGACY[s.sugar])
        else:
            chars.append(s.base if s.base and s.base not in ("-", "Q") else ".")
    return "".join(chars)


def _sugar_pattern(length: int, start_with_f: bool) -> List[str]:
    return ["2F" if (i % 2 == 0) == start_with_f else "2OMe" for i in range(length)]


def _apply_terminal_ps(slots: List[NucSlot], five_prime: bool, three_prime: bool) -> None:
    if five_prime and len(slots) > 1:
        slots[0].linkage_3p = slots[1].linkage_3p = "PS"
    if three_prime and len(slots) > 1:
        slots[-2].linkage_3p = slots[-1].linkage_3p = "PS"


def generate_esc_plus_candidates(base_sense: str, base_antisense: str) -> List[MultiSlotDesign]:
    """16 clinically-motivated multi-slot variants (2 alt-phase x 2 PS x 2
    5'-mimic x 2 conjugate), each internally consistent (real chemistry, no
    single-slot conflation)."""
    designs = []
    for alt_phase, ps_on, mimic_on, conj_on in product([False, True], repeat=4):
        ss_sugars = _sugar_pattern(len(base_sense), alt_phase)
        as_sugars = _sugar_pattern(len(base_antisense), not alt_phase)
        # Literature-grounded guardrail: keep AS pos1 as 2'-OMe/ribo, never rigid/2'-F
        # extreme (H1 audit: 79% of real, effective designs use 2'-OMe here).
        if as_sugars:
            as_sugars[0] = "2OMe"

        sense_slots = [NucSlot(base=b, sugar=s) for b, s in zip(base_sense, ss_sugars)]
        anti_slots = [NucSlot(base=b, sugar=s) for b, s in zip(base_antisense, as_sugars)]

        _apply_terminal_ps(sense_slots, five_prime=ps_on, three_prime=False)
        _apply_terminal_ps(anti_slots, five_prime=ps_on, three_prime=ps_on)

        if mimic_on and anti_slots:
            anti_slots[0].terminal_5p = "5VP"
        if conj_on and sense_slots:
            # Anchored at the terminal 3' nucleotide (not appended as an extra
            # position) so legacy-string length stays == len(base_sense) for
            # the biophysics bridge below.
            sense_slots[-1].conjugate = "GalNAc"

        label = (f"{'F-start' if alt_phase else 'OMe-start'} alt-sugar, "
                 f"PS={'termini' if ps_on else 'none'}, "
                 f"5'mimic={'VP' if mimic_on else 'none'}, "
                 f"3'GalNAc={'yes' if conj_on else 'no'}")
        designs.append(MultiSlotDesign(sense_slots, anti_slots, label))
    return designs


def rank_esc_plus_designs(base_sense: str, base_antisense: str) -> List[MultiSlotDesign]:
    """Generates, scores (Model B v2, true multi-slot fidelity), applies
    biophysics penalties, and returns designs ranked best-first."""
    designs = generate_esc_plus_candidates(base_sense, base_antisense)
    raw_scores = model_b_v2.predict_from_slots(
        [d.sense_slots for d in designs], [d.anti_slots for d in designs]
    )
    for d, raw in zip(designs, raw_scores):
        d.raw_score = float(raw)
        legacy_sense = _slots_to_biophysics_view(d.sense_slots)
        legacy_anti = _slots_to_biophysics_view(d.anti_slots)
        d.adjusted_score, d.penalties, _ = calculate_adjusted_efficacy(
            d.raw_score, legacy_sense, legacy_anti, base_sense, base_antisense
        )
    designs.sort(key=lambda d: d.adjusted_score, reverse=True)
    return designs
