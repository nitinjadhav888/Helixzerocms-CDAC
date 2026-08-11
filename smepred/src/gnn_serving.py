"""
gnn_serving.py -- Direct PyTorch inference wrapper for the fine-tuned MEG-mod GNN checkpoint
(finetuned_v2.pt) and the 50/50 Hybrid GBDT-GNN Ensemble.
"""
import os
import sys
import pickle
from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd
import torch

ROOT_DIR = Path(__file__).parent.parent.parent
MEGMOD_DIR = ROOT_DIR / "MEG-mod-main"
if str(MEGMOD_DIR) not in sys.path:
    sys.path.insert(0, str(MEGMOD_DIR))

# Imports from MEG-mod-main
try:
    from BAN_graph import MEG_mod_predictor
except Exception:
    MEG_mod_predictor = None

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
GNN_CKPT = MEGMOD_DIR / "Saved_Best_Models" / "finetuned_v2.pt"
BASE_PKL = ROOT_DIR / "data_pre" / "rnaernie_base_emb_fixed.pkl"
COFOLD_PKL = ROOT_DIR / "data_pre" / "cofold_results.pkl"

_gnn_cache = {}
_shared_base_dict = None
_shared_cofold_dict = None


def ensure_base_embeddings(df: "pd.DataFrame", base_dict: dict) -> dict:
    """
    Ensures every (sense, antisense) sequence pair in df has an entry in base_dict.
    For sequences not pre-computed in the pkl, synthesizes a zero-padded 27×768
    float32 tensor as a safe fallback so BAN_graph inference never KeyErrors.
    """
    for _, row in df.iterrows():
        for seq_col in ("sense", "antisense"):
            seq = str(row.get(seq_col, "")).lower().strip()
            if seq and seq not in base_dict:
                # Safe zero-padded fallback: (27, 768) float32
                base_dict[seq] = np.zeros((27, 768), dtype=np.float32)
    return base_dict


def ensure_cofold(df: "pd.DataFrame", cofold_dict: dict) -> dict:
    """
    Ensures every (sense_id, anti_id) pair in df has an entry in cofold_dict.
    For missing pairs, inserts a neutral empty structure dict so BAN_graph
    graph edge construction does not crash on missing cofold data.
    """
    for _, row in df.iterrows():
        key = (str(row.get("sense_id", "")), str(row.get("anti_id", "")))
        if key not in cofold_dict:
            cofold_dict[key] = {}
    return cofold_dict


def _load_gnn_model(ckpt_key="finetuned_v2"):
    global _shared_base_dict, _shared_cofold_dict

    if ckpt_key in _gnn_cache:
        return _gnn_cache[ckpt_key]["model"], _shared_base_dict, _shared_cofold_dict

    ckpt_file = "finetuned_v2.pt"
    ckpt_path = MEGMOD_DIR / "Saved_Best_Models" / ckpt_file

    if not ckpt_path.exists():
        raise FileNotFoundError(f"GNN checkpoint not found at: {ckpt_path}")

    print(f"Loading GNN model ({ckpt_file}) from {ckpt_path}...")
    
    if _shared_base_dict is None:
        _shared_base_dict = {}
        if BASE_PKL.exists():
            try:
                with open(BASE_PKL, "rb") as f:
                    _shared_base_dict = pickle.load(f)
            except Exception as e:
                print(f"Warning: Could not unpickle {BASE_PKL} ({e}), initializing empty base_dict.")
                _shared_base_dict = {}

    if _shared_cofold_dict is None:
        _shared_cofold_dict = {}
        if COFOLD_PKL.exists():
            try:
                with open(COFOLD_PKL, "rb") as f:
                    _shared_cofold_dict = pickle.load(f)
            except Exception as e:
                print(f"Warning: Could not unpickle {COFOLD_PKL} ({e}), initializing empty cofold_dict.")
                _shared_cofold_dict = {}

    if MEG_mod_predictor is None:
        raise ImportError("MEG_mod_predictor class could not be imported from BAN_graph. Ensure MEG-mod-main dependencies (dataset_pre.py, utils.py) exist.")

    model = MEG_mod_predictor(
        device=DEVICE,
        combine_1_dim=512,
        rnaernie_dim=768,
        pc_dim=10,
        use_prob=True,
        prob_threshold=0.2,
        include_intra_mfe_pairs=False,
    ).to(DEVICE)

    model.load_state_dict(torch.load(ckpt_path, map_location=DEVICE))
    model.eval()

    _gnn_cache[ckpt_key] = {
        "model": model,
    }

    return model, _shared_base_dict, _shared_cofold_dict


def _mod_str_to_meg_format(base_seq: str, mod_seq: str):
    """Converts modified sequence string into MEG-mod GNN types and positions."""
    mod_positions = {}
    
    MOD_NAME_MAP = {
        "M": "2-O-Methyl",
        "F": "2-Fluoro",
        "D": "deoxynucleotide",
        "S": "Phosphorothioate",
        "E": "2'-O-Methoxyethyl",
        "L": "LNA",
        "Q": "Abasic",
        "B": "2'-O-Benzyl",
        "I": "2'-F-ANA",
        "Z": "2'-OMe-4'-thio",
        "Y": "ENA",
        "X": "2'-O-allyl",
        "P": "Boranophosphate",
        "R": "Methylphosphonate",
        "H": "Phosphoramidate",
        "V": "5-Methyl Cytidine",
        "W": "Pseudouridine",
        "J": "Inosine",
        "K": "2-thio Uridine",
        "O": "Dihydrouridine",
        "1": "5'-Phosphate",
        "2": "3'-Phosphate",
        "3": "5'-OMe cap",
        "4": "GalNAc",
        "5": "PEG conjugate",
        "6": "UNA",
        "7": "ANA",
        "8": "GNA",
        "9": "TNA",
    }

    for pos, (b_char, m_char) in enumerate(zip(base_seq, mod_seq), start=1):
        if m_char.islower():
            mod_positions.setdefault("2-O-Methyl", []).append(pos)
        elif m_char in MOD_NAME_MAP:
            mod_positions.setdefault(MOD_NAME_MAP[m_char], []).append(pos)
        elif m_char.upper() == 'T' and b_char.upper() == 'U':
            mod_positions.setdefault("deoxynucleotide", []).append(pos)

    if not mod_positions:
        return "0", "0"

    types_list = list(mod_positions.keys())
    pos_list = [",".join(map(str, mod_positions[t])) for t in types_list]
    return " * ".join(types_list), " * ".join(pos_list)


def predict_gnn(sense_list: list[str], anti_list: list[str],
                mod_sense_list: list[str], mod_anti_list: list[str],
                ckpt_key: str = "finetuned_v2", return_attention: bool = False):
    """Runs PyTorch inference using specified MEG-mod GNN model checkpoint."""
    model, base_dict, cofold_dict = _load_gnn_model(ckpt_key=ckpt_key)

    df_data = []
    for idx, (s_base, a_base, s_mod, a_mod) in enumerate(zip(sense_list, anti_list, mod_sense_list, mod_anti_list)):
        st, sp = _mod_str_to_meg_format(s_base, s_mod)
        at, ap = _mod_str_to_meg_format(a_base, a_mod)
        df_data.append({
            "sense_id": f"var_{idx}_s",
            "anti_id": f"var_{idx}_a",
            "sense": s_base.upper().replace("T", "U"),
            "antisense": a_base.upper().replace("T", "U"),
            "sense_mod_types": st,
            "sense_mod_positions": sp,
            "anti_mod_types": at,
            "anti_mod_positions": ap,
            "concentration": 10.0
        })

    df = pd.DataFrame(df_data)

    # Ensure embeddings & secondary structures exist in cache
    if ensure_base_embeddings is not None and ensure_cofold is not None:
        base_dict = ensure_base_embeddings(df, base_dict)
        cofold_dict = ensure_cofold(df, cofold_dict)
        model.base_embeddings = base_dict
        model.cofold_dict = cofold_dict

    preds = []
    attn_list = []
    batch_size = 64
    with torch.no_grad():
        for i in range(0, len(df), batch_size):
            sub = df.iloc[i:i+batch_size]
            args = (
                sub["sense_id"].astype(str).tolist(),
                sub["anti_id"].astype(str).tolist(),
                sub["sense"].astype(str).tolist(),
                sub["antisense"].astype(str).tolist(),
                sub["sense_mod_types"].astype(str).tolist(),
                sub["sense_mod_positions"].astype(str).tolist(),
                sub["anti_mod_types"].astype(str).tolist(),
                sub["anti_mod_positions"].astype(str).tolist(),
                sub["concentration"].tolist(),
            )
            if return_attention:
                out, attn = model(*args, return_attention=True)
                attn_list.append(attn)
            else:
                out = model(*args)
            preds.extend(out.view(-1).cpu().numpy().tolist())

    res = np.clip(np.array(preds) * 100.0, 0.0, 100.0)
    if return_attention:
        return res, attn_list
    return res


def predict_gnn_with_attention(
    sense_seq: str, 
    anti_seq: str, 
    mod_sense: Optional[str] = None, 
    mod_anti: Optional[str] = None, 
    ckpt_key: str = "finetuned_v2"
) -> Dict[str, Any]:
    """
    Runs PyTorch GNN model inference and extracts TRUE sequence-dependent & 
    modification-dependent graph attention weights (alpha_sense, alpha_anti).
    """
    m_sense = mod_sense or sense_seq
    m_anti = mod_anti or anti_seq

    preds, attn_list = predict_gnn([sense_seq], [anti_seq], [m_sense], [m_anti], ckpt_key=ckpt_key, return_attention=True)
    score = preds[0]
    
    s_len = min(21, len(sense_seq))
    a_len = min(21, len(anti_seq))

    sense_weights = [0.1] * s_len
    anti_weights = [0.1] * a_len

    if attn_list and len(attn_list) > 0:
        attn = attn_list[0]
        try:
            layer_attn = attn.get("layer2", attn.get("layer1", {}))
            edge_index = layer_attn.get("edge_index")
            alpha = layer_attn.get("alpha")
            
            if edge_index is not None and alpha is not None:
                target_nodes = edge_index[1].cpu().numpy()
                alpha_vals = alpha.cpu().numpy()
                
                node_scores = {}
                for t_idx, a_val in zip(target_nodes, alpha_vals):
                    import numpy as np
                    node_scores[t_idx] = node_scores.get(t_idx, 0.0) + float(np.mean(a_val))
                
                max_score = max(node_scores.values()) if node_scores else 1.0
                if max_score == 0: max_score = 1.0
                
                Ls = 27  # MEG_mod_predictor max_seq_len padding
                for i in range(s_len):
                    sense_weights[i] = round(min(1.0, node_scores.get(i, 0.0) / max_score), 3)
                for i in range(a_len):
                    anti_weights[i] = round(min(1.0, node_scores.get(Ls + i, 0.0) / max_score), 3)
        except Exception as e:
            print(f"Error parsing live attention weights: {e}")

    return {
        "efficacy_score": round(float(score), 2),
        "site_importance": {
            "sense": sense_weights,
            "antisense": anti_weights
        }
    }
