"""
helixzero.featurizers.graph_featurizer
======================================
Dynamic Stereochemical Molecular Graph Builder for HelixZero GNN Engine.

Constructs self-contained PyTorch-compatible molecular graphs directly from
nucleotide sequence and chemical modification ontology (NucSlot), eliminating
static pickle caches and sequence-leakage pitfalls.
"""

from __future__ import annotations
from typing import List, Dict, Tuple, Optional
import numpy as np
import torch

from helixzero.ontology.tokenizer import CanonicalNucSlot


# Element and Atom Types for Nucleic Acids
ATOM_TYPES = ["C", "N", "O", "P", "S", "F", "H"]
SUGAR_TYPES = ['ribo', '2OMe', '2F', 'deoxyribo', '2MOE', 'LNA', 'GNA', 'UNA']


class DynamicMolecularGraphBuilder:
    """
    Constructs dynamic residue-level and atom-level graphs for siRNA duplexes.
    """

    def __init__(self):
        self.node_dim = 32  # 32-dimensional node feature vector

    def build_node_features(self, slots: List[CanonicalNucSlot], strand_id: int) -> torch.Tensor:
        """
        Builds a (L, 32) tensor of residue-level chemical features.
        """
        L = len(slots)
        features = np.zeros((L, self.node_dim), dtype=np.float32)

        for i, s in enumerate(slots):
            # 1. Nucleobase one-hot (5 bits: A, C, G, U, other)
            b = s.base.upper()
            if b == 'A': features[i, 0] = 1.0
            elif b == 'C': features[i, 1] = 1.0
            elif b == 'G': features[i, 2] = 1.0
            elif b in ('U', 'T'): features[i, 3] = 1.0
            else: features[i, 4] = 1.0

            # 2. Sugar modification one-hot (8 bits)
            sugar = s.sugar
            for k, sg in enumerate(SUGAR_TYPES):
                if sugar == sg:
                    features[i, 5 + k] = 1.0
                    break

            # 3. Backbone linkage (2 bits: PO vs PS)
            if s.linkage == 'PS':
                features[i, 13] = 1.0
            else:
                features[i, 14] = 1.0

            # 4. 5'-Terminal anchor (3 bits: OH, 5P, 5VP)
            if s.terminal_5p == '5P': features[i, 15] = 1.0
            elif s.terminal_5p == '5VP': features[i, 16] = 1.0
            else: features[i, 17] = 1.0

            # 5. Position along strand normalized (1 bit)
            features[i, 18] = float(i) / max(1.0, float(L - 1))

            # 6. Functional domain indicators (4 bits: Seed g2-g8, Cleavage g10-g11, Overhang, Strand)
            if 1 <= i <= 7: features[i, 19] = 1.0 # Seed region
            if 9 <= i <= 10: features[i, 20] = 1.0 # Catalytic cleavage site
            if i >= L - 2: features[i, 21] = 1.0 # 3' overhang
            features[i, 22] = float(strand_id) # 0 for Sense, 1 for Antisense

            # 7. Steric radius & molecular weight estimate (2 bits)
            if sugar == '2MOE': features[i, 23] = 1.2 # Bulky
            elif sugar == '2OMe': features[i, 23] = 0.8
            elif sugar == '2F': features[i, 23] = 0.4
            else: features[i, 23] = 0.6

        return torch.tensor(features, dtype=torch.float32)

    def build_edge_index_and_attributes(
        self,
        sense_len: int,
        anti_len: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Builds graph edges:
        - Backbone phosphodiester / phosphorothioate bonds (sequential edges).
        - Watson-Crick base-pairing hydrogen bonds (inter-strand antiparallel edges).
        """
        src = []
        dst = []
        edge_types = [] # 0: Backbone 5'->3', 1: Backbone 3'->5', 2: Base-pair

        # Sense strand backbone
        for i in range(sense_len - 1):
            src.extend([i, i + 1])
            dst.extend([i + 1, i])
            edge_types.extend([0, 1])

        # Antisense strand backbone (indices sense_len to sense_len + anti_len - 1)
        offset = sense_len
        for i in range(anti_len - 1):
            src.extend([offset + i, offset + i + 1])
            dst.extend([offset + i + 1, offset + i])
            edge_types.extend([0, 1])

        # Inter-strand base pairing (antiparallel alignment: Sense pos i <-> Anti pos (anti_len - 1 - i))
        overlap_len = min(sense_len, anti_len)
        for i in range(overlap_len):
            a_idx = offset + (anti_len - 1 - i)
            src.extend([i, a_idx])
            dst.extend([a_idx, i])
            edge_types.extend([2, 2])

        edge_index = torch.tensor([src, dst], dtype=torch.long)
        edge_attr = torch.tensor(edge_types, dtype=torch.long)
        return edge_index, edge_attr

    def build_duplex_graph(
        self,
        sense_slots: List[CanonicalNucSlot],
        anti_slots: List[CanonicalNucSlot]
    ) -> Dict[str, torch.Tensor]:
        """
        Constructs a complete duplex molecular graph dictionary ready for GNN forward pass.
        """
        x_sense = self.build_node_features(sense_slots, strand_id=0)
        x_anti = self.build_node_features(anti_slots, strand_id=1)
        x = torch.cat([x_sense, x_anti], dim=0)

        edge_index, edge_attr = self.build_edge_index_and_attributes(len(sense_slots), len(anti_slots))

        return {
            "x": x,
            "edge_index": edge_index,
            "edge_attr": edge_attr,
            "num_nodes": torch.tensor(len(x), dtype=torch.long)
        }
