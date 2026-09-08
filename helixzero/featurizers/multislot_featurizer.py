"""
helixzero.featurizers.multislot_featurizer
==========================================
Unified 577-dimensional Multi-Slot Chemotype Feature Extractor for HelixZero.

Encodes:
- Orthogonal positional multi-slot chemotypes (sugar, linkage, terminal 5', base, conjugate).
- Positional chemical interaction features (seed region, cleavage site, terminal overhangs).
- Pretrained RNA Foundation Model embeddings (RNA-FM PCA-32 + RNA-Ernie PCA-32).
- ViennaRNA thermodynamic parameters (MFE duplex, GC asymmetry).
"""

from __future__ import annotations
from typing import List, Tuple
import numpy as np

# Import underlying verified core features from smepred
from smepred.src import features_v4
from smepred.src.chem_schema import NucSlot
from helixzero.ontology.tokenizer import CanonicalNucSlot


def nucslot_to_v2_slot(slot: CanonicalNucSlot) -> NucSlot:
    """Converts a CanonicalNucSlot to the internal NucSlot format used by features_v4."""
    return NucSlot(
        base=slot.base,
        sugar=slot.sugar,
        linkage_3p=slot.linkage,
        terminal_5p=slot.terminal_5p if slot.terminal_5p != "OH" else None,
        base_mod=slot.basemod if slot.basemod != "none" else None,
        conjugate=slot.conjugate
    )


class MultiSlotFeaturizer:
    """
    Standardized multi-slot feature extractor returning 577-dimensional float32 arrays.
    """

    def __init__(self):
        self.feature_dim = 577

    def featurize(self, sense_slots: List[CanonicalNucSlot], anti_slots: List[CanonicalNucSlot]) -> np.ndarray:
        """
        Extracts a single 577-d feature vector for an siRNA candidate.
        """
        s_v2 = [nucslot_to_v2_slot(s) for s in sense_slots]
        a_v2 = [nucslot_to_v2_slot(a) for a in anti_slots]
        vec = features_v4.build_features_v4(s_v2, a_v2)
        return vec.astype(np.float32)

    def featurize_batch(
        self,
        batch_sense_slots: List[List[CanonicalNucSlot]],
        batch_anti_slots: List[List[CanonicalNucSlot]]
    ) -> np.ndarray:
        """
        Extracts an (N, 577) feature matrix for a batch of candidates.
        """
        s_v2_batch = [[nucslot_to_v2_slot(s) for s in s_list] for s_list in batch_sense_slots]
        a_v2_batch = [[nucslot_to_v2_slot(a) for a in a_list] for a_list in batch_anti_slots]
        mat = features_v4.batch_features_v4(s_v2_batch, a_v2_batch)
        return mat.astype(np.float32)
