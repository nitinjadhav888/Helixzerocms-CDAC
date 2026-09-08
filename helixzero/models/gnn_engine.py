"""
helixzero.models.gnn_engine
===========================
Self-Contained Graph Neural Network (GNN) Engine for Stereochemical Molecular Graphs.
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from helixzero.ontology.tokenizer import CanonicalNucSlot
from helixzero.featurizers.graph_featurizer import DynamicMolecularGraphBuilder


class siRNA_GNN_Module(nn.Module):
    """
    Message-Passing Neural Network for siRNA duplex molecular graphs.
    """

    def __init__(self, in_dim: int = 32, hidden_dim: int = 64, num_layers: int = 3):
        super().__init__()
        self.node_proj = nn.Linear(in_dim, hidden_dim)
        
        # Message passing layers (Residual Graph Convolution)
        self.convs = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim) for _ in range(num_layers)
        ])
        self.norms = nn.ModuleList([
            nn.LayerNorm(hidden_dim) for _ in range(num_layers)
        ])

        # Global Attention Pooling & Readout
        self.attn = nn.Linear(hidden_dim, 1)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 1),
            nn.Sigmoid() # Outputs normalized efficacy [0.0, 1.0]
        )

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        h = F.relu(self.node_proj(x))
        src, dst = edge_index[0], edge_index[1]

        for conv, norm in zip(self.convs, self.norms):
            # Message aggregation: scatter mean
            msg = h[src]
            out = torch.zeros_like(h)
            out.index_add_(0, dst, msg)
            deg = torch.zeros(h.size(0), 1, device=h.device)
            deg.index_add_(0, dst, torch.ones(src.size(0), 1, device=h.device))
            deg = torch.clamp(deg, min=1.0)
            agg = out / deg
            h = norm(h + F.relu(conv(agg)))

        # Global Attention Pooling
        weights = F.softmax(self.attn(h), dim=0)
        pooled = torch.sum(weights * h, dim=0, keepdim=True)
        out = self.fc(pooled) * 100.0 # Scale to 0 - 100%
        return out


class GNNEngine:
    """
    Production PyTorch GNN Wrapper for molecular graph predictions.
    """

    def __init__(self, model_path: Optional[Path] = None):
        self.builder = DynamicMolecularGraphBuilder()
        self.device = torch.device("cpu")
        self.model = siRNA_GNN_Module(in_dim=32, hidden_dim=64, num_layers=3)
        self.model.to(self.device)
        self.model.eval()

        if model_path and Path(model_path).exists():
            try:
                ckpt = torch.load(model_path, map_location=self.device)
                if isinstance(ckpt, dict) and "state_dict" in ckpt:
                    self.model.load_state_dict(ckpt["state_dict"], strict=False)
                elif isinstance(ckpt, dict):
                    self.model.load_state_dict(ckpt, strict=False)
            except Exception:
                pass

    def predict_candidate(
        self,
        sense_slots: List[CanonicalNucSlot],
        anti_slots: List[CanonicalNucSlot]
    ) -> float:
        """
        Runs GNN forward pass on the dynamically generated duplex graph.
        """
        graph_data = self.builder.build_duplex_graph(sense_slots, anti_slots)
        x = graph_data["x"].to(self.device)
        edge_index = graph_data["edge_index"].to(self.device)

        with torch.no_grad():
            pred = float(self.model(x, edge_index)[0, 0].item())
        return float(np.clip(pred, 0.0, 100.0))
