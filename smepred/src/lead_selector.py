"""
lead_selector.py — Deterministic Multi-Criteria Decision Analysis (MCDA)
Ranks candidate siRNAs based on biophysical, thermodynamic, and safety criteria.
"""

from typing import List, Dict, Any

def score_and_rank_candidates(candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Ranks siRNA candidates via normalized multi-criteria weighting:
      1. Potency Score (Naked Model A or Modified Knockdown %) : Weight 0.35
      2. Seed Viability (Janas et al. cell viability %)        : Weight 0.25
      3. Thermodynamic Asymmetry (RISC loading delta delta G)  : Weight 0.15
      4. Off-target Safety (Human 3'-UTR hit penalty)          : Weight 0.15
      5. Structural / Biophysical Compatibility (Zero penalty)  : Weight 0.10

    Returns the top_k candidates enriched with composite rank scores and ranking rank.
    """
    if not candidates:
        return []

    scored_list = []
    for idx, c in enumerate(candidates):
        # 1. Potency / Knockdown (scale 0 to 100)
        eff = (
            c.get("efficacy_score")
            if c.get("efficacy_score") is not None
            else c.get("predicted_knockdown_pct")
            if c.get("predicted_knockdown_pct") is not None
            else c.get("knockdown")
            if c.get("knockdown") is not None
            else c.get("score")
            if c.get("score") is not None
            else c.get("pred_potency", 50.0)
        )
        try:
            eff = float(eff)
        except (ValueError, TypeError):
            eff = 50.0

        # 2. Seed Viability (Janas et al.)
        seed_tox = (
            c.get("toxicity_score")
            if c.get("toxicity_score") is not None
            else c.get("tox_score")
        )
        if seed_tox is None:
            # Check label
            lbl = str(c.get("toxicity_label", c.get("tox_label", ""))).lower()
            if "safe" in lbl or "mitigated" in lbl:
                seed_tox = 90.0
            elif "caution" in lbl:
                seed_tox = 65.0
            elif "toxic" in lbl:
                seed_tox = 35.0
            else:
                seed_tox = 80.0
        try:
            seed_tox = float(seed_tox)
        except (ValueError, TypeError):
            seed_tox = 80.0

        # 3. Off-target hits
        offtargets = c.get("offtarget_hits", c.get("transcriptome_hits", 0))
        try:
            offtargets = int(offtargets)
        except (ValueError, TypeError):
            offtargets = 0

        # 4. Thermodynamic Asymmetry (delta delta G, ideal >= 1.5 kcal/mol)
        asym = c.get("asymmetry_ddg", c.get("delta_delta_g", c.get("asymmetry", 1.5)))
        try:
            asym = float(asym)
        except (ValueError, TypeError):
            asym = 1.5

        # 5. Biophysical Penalty (0 is ideal, >0 is penalty)
        penalty = c.get("biophysical_penalty", c.get("total_penalty"))
        if penalty is None and isinstance(c.get("penalties"), dict):
            penalty = sum(c["penalties"].values())
        if penalty is None:
            penalty = 0.0
        try:
            penalty = float(penalty)
        except (ValueError, TypeError):
            penalty = 0.0

        # Normalized component scores [0.0 to 1.0]
        s_eff = min(max(eff / 100.0, 0.0), 1.0)
        s_seed = min(max(seed_tox / 100.0, 0.0), 1.0)
        # Asymmetry normalized: -2.0 to +4.0 kcal/mol mapped to [0, 1]
        s_asym = min(max((asym + 2.0) / 6.0, 0.0), 1.0)
        # Offtarget: 0 hits = 1.0, 1 hit = 0.5, >=2 hits = 0.1
        s_offtarget = 1.0 if offtargets == 0 else (0.5 if offtargets == 1 else 0.1)
        # Structural: penalty 0 = 1.0, down to 0
        s_struct = max(1.0 - (penalty / 30.0), 0.0)

        # Composite Score (0.0 to 100.0)
        composite = (
            0.35 * s_eff +
            0.25 * s_seed +
            0.15 * s_asym +
            0.15 * s_offtarget +
            0.10 * s_struct
        ) * 100.0

        # Heavy penalty if explicitly toxic or high off-targets
        if seed_tox < 50.0:
            composite *= 0.70
        if offtargets > 1:
            composite *= 0.60

        entry = dict(c)
        entry["composite_rank_score"] = round(composite, 2)
        entry["parsed_efficacy"] = round(eff, 2)
        entry["parsed_seed_viability"] = round(seed_tox, 1)
        entry["parsed_asymmetry_ddg"] = round(asym, 2)
        entry["parsed_offtargets"] = offtargets
        entry["parsed_penalty"] = round(penalty, 2)
        scored_list.append(entry)

    # Sort descending by composite rank score
    scored_list.sort(key=lambda x: x["composite_rank_score"], reverse=True)

    top_leads = scored_list[:top_k]
    for rank, lead in enumerate(top_leads, start=1):
        lead["lead_rank"] = rank

    return top_leads
