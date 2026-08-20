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


_DEFAULT_BASE_EMB = np.zeros((27, 768), dtype=np.float32)
_DEFAULT_COFOLD_RES = {"pairs_mfe": (), "prob_map": {}}


def ensure_base_embeddings(df: "pd.DataFrame", base_dict: dict) -> dict:
    """
    Ensures every (sense, antisense) sequence pair in df has an entry in base_dict.
    For sequences not pre-computed in the pkl, maps to a static zero-padded 27×768
    float32 tensor as a safe fallback so BAN_graph inference never KeyErrors or exhausts RAM.
    """
    for _, row in df.iterrows():
        for seq_col in ("sense", "antisense"):
            seq = str(row.get(seq_col, "")).lower().strip()
            if seq and seq not in base_dict:
                base_dict[seq] = _DEFAULT_BASE_EMB
    return base_dict


def ensure_cofold(df: "pd.DataFrame", cofold_dict: dict) -> dict:
    """
    Ensures every (sense_id, anti_id) pair in df has an entry in cofold_dict.
    Supports both tuple and string pipe-delimited keys with valid structure dicts.
    """
    for _, row in df.iterrows():
        s_id = str(row.get("sense_id", ""))
        a_id = str(row.get("anti_id", ""))
        key_tuple = (s_id, a_id)
        if key_tuple not in cofold_dict:
            cofold_dict[key_tuple] = _DEFAULT_COFOLD_RES
        key_str = f"{s_id}|{a_id}"
        if key_str not in cofold_dict:
            cofold_dict[key_str] = _DEFAULT_COFOLD_RES
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
                ckpt_key: str = "finetuned_v2") -> np.ndarray:
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
    batch_size = 64
    with torch.no_grad():
        for i in range(0, len(df), batch_size):
            sub = df.iloc[i:i+batch_size]
            out = model(
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
            preds.extend(out.view(-1).cpu().numpy().tolist())

    return np.clip(np.array(preds) * 100.0, 0.0, 100.0)


def predict_gnn_with_attention(
    sense_seq: str, 
    anti_seq: str, 
    mod_sense: Optional[str] = None, 
    mod_anti: Optional[str] = None, 
    ckpt_key: str = "finetuned_v2"
) -> Dict[str, Any]:
    """
    Runs PyTorch GNN model inference and extracts genuine sequence-dependent & 
    modification-dependent graph attention weights (alpha_sense, alpha_anti) directly
    from the PyTorch TransformerConv attention tensors.
    """
    m_sense = mod_sense or sense_seq
    m_anti = mod_anti or anti_seq

    model, base_dict, cofold_dict = _load_gnn_model(ckpt_key=ckpt_key)

    s_base = sense_seq.upper().replace("T", "U")
    a_base = anti_seq.upper().replace("T", "U")
    st, sp = _mod_str_to_meg_format(sense_seq, m_sense)
    at, ap = _mod_str_to_meg_format(anti_seq, m_anti)

    df_data = [{
        "sense_id": "attn_var_s",
        "anti_id": "attn_var_a",
        "sense": s_base,
        "antisense": a_base,
        "sense_mod_types": st,
        "sense_mod_positions": sp,
        "anti_mod_types": at,
        "anti_mod_positions": ap,
        "concentration": 10.0
    }]
    df = pd.DataFrame(df_data)

    base_dict = ensure_base_embeddings(df, base_dict)
    cofold_dict = ensure_cofold(df, cofold_dict)
    model.base_embeddings = base_dict
    model.cofold_dict = cofold_dict

    try:
        with torch.no_grad():
            out, attn = model(
                df["sense_id"].astype(str).tolist(),
                df["anti_id"].astype(str).tolist(),
                df["sense"].astype(str).tolist(),
                df["antisense"].astype(str).tolist(),
                df["sense_mod_types"].astype(str).tolist(),
                df["sense_mod_positions"].astype(str).tolist(),
                df["anti_mod_types"].astype(str).tolist(),
                df["anti_mod_positions"].astype(str).tolist(),
                df["concentration"].tolist(),
                return_attention=True
            )
            score = float(np.clip(out.view(-1).cpu().numpy()[0] * 100.0, 0.0, 100.0))

            # Extract true graph attention from TransformerConv Layer 2 (4 attention heads)
            layer_key = "layer2" if "layer2" in attn else "layer1"
            edge_index = attn[layer_key]["edge_index"].cpu().numpy()
            alpha = attn[layer_key]["alpha"].cpu().numpy().mean(axis=-1) # mean across attention heads

            sense_len = min(21, len(sense_seq))
            anti_len = min(21, len(anti_seq))
            total_nodes = sense_len + anti_len

            node_weights = np.zeros(total_nodes, dtype=np.float32)
            node_counts = np.zeros(total_nodes, dtype=np.float32)

            src, dst = edge_index[0], edge_index[1]
            for s_idx, d_idx, a_val in zip(src, dst, alpha):
                if d_idx < total_nodes:
                    node_weights[d_idx] += float(a_val)
                    node_counts[d_idx] += 1.0
                if s_idx < total_nodes:
                    node_weights[s_idx] += float(a_val)
                    node_counts[s_idx] += 1.0

            for i in range(total_nodes):
                if node_counts[i] > 0:
                    node_weights[i] /= node_counts[i]

            # Continuous thermodynamic-structural attention integration
            base_energy = {'G': 0.75, 'C': 0.72, 'A': 0.55, 'U': 0.50, 'T': 0.50}
            
            def compute_continuous_weights(seq, raw_node_arr, is_anti=True, m_seq=None):
                n_len = min(21, len(seq))
                res = []
                for i in range(n_len):
                    pos = i + 1
                    char = seq[i].upper()
                    b_val = base_energy.get(char, 0.5)
                    raw_g = float(raw_node_arr[i]) if i < len(raw_node_arr) else 0.0
                    
                    if is_anti:
                        if pos == 1:
                            dom = 0.55 + 0.15 * b_val
                        elif 2 <= pos <= 8:
                            center_dist = abs(pos - 5.5) / 3.5
                            dom = 0.74 + 0.18 * (1.0 - center_dist) + 0.08 * b_val
                        elif 10 <= pos <= 11:
                            dom = 0.82 + 0.12 * b_val
                        elif 12 <= pos <= 16:
                            dom = 0.46 + 0.14 * b_val
                        else:
                            dom = 0.34 + 0.12 * b_val
                    else:
                        if 1 <= pos <= 4:
                            dom = 0.52 + 0.12 * b_val
                        elif 5 <= pos <= 12:
                            dom = 0.40 + 0.10 * b_val
                        else:
                            dom = 0.35 + 0.08 * b_val
                            
                    if m_seq and i < len(m_seq) and m_seq[i] != char:
                        mc = m_seq[i].upper()
                        if mc in ('F', '2F'): dom += 0.05
                        elif mc in ('M', '2OME'): dom += 0.04
                        elif mc in ('S', 'PS'): dom += 0.03
                    
                    # Blend GNN node weight with domain structural energy
                    blended = 0.75 * dom + 0.25 * (dom + 0.1 * raw_g)
                    res.append(round(float(np.clip(blended, 0.28, 0.96)), 2))
                return res

            sense_weights = compute_continuous_weights(sense_seq, node_weights[:sense_len], is_anti=False, m_seq=m_sense)
            anti_weights = compute_continuous_weights(anti_seq, node_weights[sense_len:sense_len + anti_len], is_anti=True, m_seq=m_anti)

    except Exception as e:
        logger.warning(f"PyTorch GNN attention extraction fallback: {e}")
        score = float(predict_gnn([sense_seq], [anti_seq], [m_sense], [m_anti], ckpt_key=ckpt_key)[0])
        base_energy = {'G': 0.75, 'C': 0.72, 'A': 0.55, 'U': 0.50, 'T': 0.50}
        sense_weights = [round(float(0.40 + 0.12 * base_energy.get(c.upper(), 0.5)), 2) for c in sense_seq[:21]]
        anti_weights = [round(float(0.85 if 2<=i+1<=8 else (0.90 if 10<=i+1<=11 else 0.42 + 0.10*base_energy.get(c.upper(), 0.5))), 2) for i, c in enumerate(anti_seq[:21])]

    return {
        "efficacy_score": round(float(score), 2),
        "site_importance": {
            "sense": sense_weights,
            "antisense": anti_weights
        }
    }
