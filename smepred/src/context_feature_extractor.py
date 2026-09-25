"""
context_feature_extractor.py — Target mRNA Context-Aware Feature Extractor

Extracts joint biophysical, thermodynamic, sequence-engineering, and RNA-FM foundation
embeddings for siRNA guide sequences coupled with 57-nt target mRNA context windows.

Feature Groups:
1. ViennaRNA Thermodynamics (33-D):
   - dg_open (mRNA target unfolding free energy penalty, kcal/mol)
   - dg_duplex (siRNA-mRNA hybridization free energy, kcal/mol)
   - ddg (net thermodynamic driving force = dg_duplex - dg_open, kcal/mol)
   - seed_dg_duplex (seed region nt 2-8 hybridization free energy, kcal/mol)
   - dg_end5, dg_end3, end_diff (terminal thermodynamic asymmetry, kcal/mol)
   - mfe_target_local, mfe_guide_local (hairpin / secondary structure propensities)
   - td_0 to td_23 (24-D OligoFormer nearest-neighbor thermodynamic parameters)

2. Sequence & Context Engineering (92-D):
   - GC contents: guide_gc, target_gc, flank5_gc, flank3_gc, seed_gc
   - Nucleotide counts: guide U/A/G/C, target U/A/G/C
   - Terminal determinants: has_5p_u (Ago2 MID pocket preference), has_3p_a
   - Positional one-hot encoding across 19-nt guide sequence (19 x 4 = 76-D)

3. RNA-FM Foundation Model Embeddings (65-D with PCA-32):
   - PCA-32 projected mRNA context representation (capturing global secondary structure & accessibility)
   - PCA-32 projected siRNA guide representation
   - Cosine similarity between guide and target site latent representations
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import pandas as pd
import joblib

try:
    import RNA
except ImportError:
    RNA = None

try:
    import torch
    import fm
except ImportError:
    torch = None
    fm = None

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models"
PCA_CACHE_PATH = MODELS_DIR / "context_rnafm_pca_32.joblib"

NUC_MAP = {"A": 0, "C": 1, "G": 2, "U": 3}
COMPLEMENT = str.maketrans("ACGU", "UGCA")


def _clean_rna(seq: str) -> str:
    """Normalizes sequence to uppercase RNA alphabet."""
    return seq.strip().upper().replace("T", "U")


def compute_viennarna_features(siRNA: str, mRNA: str) -> Dict[str, float]:
    """
    Computes rigorous biophysical accessibility and hybridization metrics
    using the official ViennaRNA 2.7+ package.
    """
    if RNA is None:
        return {
            "dg_open": 0.0, "dg_duplex": -20.0, "ddg": -20.0,
            "seed_dg_duplex": -7.0, "dg_end5": -2.0, "dg_end3": -2.0,
            "end_diff": 0.0, "mfe_target_local": 0.0, "mfe_guide_local": 0.0,
        }

    clean_guide = _clean_rna(siRNA)
    clean_mrna = _clean_rna(mRNA).replace("X", "A")
    target_site = clean_mrna[19:38] if len(clean_mrna) >= 38 else clean_mrna

    # 1. mRNA Free MFE vs Target Constrained MFE -> dg_open
    s_free, mfe_free = RNA.fold(clean_mrna)
    constraint = "." * 19 + "x" * 19 + "." * (len(clean_mrna) - 38)
    md = RNA.md()
    fc = RNA.fold_compound(clean_mrna, md)
    fc.hc_add_from_db(constraint)
    s_cons, mfe_cons = fc.mfe()
    dg_open = max(0.0, float(mfe_cons - mfe_free))

    # 2. Duplex hybridization free energy -> dg_duplex
    dup_res = RNA.duplexfold(clean_guide, target_site)
    dg_duplex = float(dup_res.energy)

    # 3. Net driving force -> ddg
    ddg = float(dg_duplex - dg_open)

    # 4. Seed hybridization (guide nt 2-8, target complement)
    seed_guide = clean_guide[1:8] if len(clean_guide) >= 8 else clean_guide
    seed_target = target_site[-8:-1] if len(target_site) >= 8 else target_site
    seed_res = RNA.duplexfold(seed_guide, seed_target)
    seed_dg_duplex = float(seed_res.energy)

    # 5. Terminal end stabilities (first 2 nt vs last 2 nt)
    end5_res = RNA.duplexfold(clean_guide[:2], target_site[-2:])
    end3_res = RNA.duplexfold(clean_guide[-2:], target_site[:2])
    dg_end5 = float(end5_res.energy)
    dg_end3 = float(end3_res.energy)
    end_diff = float(dg_end5 - dg_end3)  # Negative means guide 5' is more loosely bound (desirable)

    # 6. Local hairpins / self-structure
    _, mfe_guide = RNA.fold(clean_guide)
    _, mfe_target = RNA.fold(target_site)

    return {
        "dg_open": dg_open,
        "dg_duplex": dg_duplex,
        "ddg": ddg,
        "seed_dg_duplex": seed_dg_duplex,
        "dg_end5": dg_end5,
        "dg_end3": dg_end3,
        "end_diff": end_diff,
        "mfe_target_local": float(mfe_target),
        "mfe_guide_local": float(mfe_guide),
    }


def compute_sequence_features(siRNA: str, mRNA: str) -> np.ndarray:
    """
    Extracts sequence composition, GC contents, terminal motifs,
    and 19-position one-hot features. Returns 92-D float array.
    """
    clean_guide = _clean_rna(siRNA)
    clean_mrna = _clean_rna(mRNA).replace("X", "A")
    target_site = clean_mrna[19:38] if len(clean_mrna) >= 38 else clean_mrna
    flank5 = clean_mrna[:19]
    flank3 = clean_mrna[38:57]
    seed = clean_guide[1:8]

    def _gc(s: str) -> float:
        return sum(1 for c in s if c in "GC") / max(1, len(s))

    guide_gc = _gc(clean_guide)
    target_gc = _gc(target_site)
    flank5_gc = _gc(flank5)
    flank3_gc = _gc(flank3)
    seed_gc = _gc(seed)

    has_5p_u = 1.0 if clean_guide.startswith("U") else 0.0
    has_3p_a = 1.0 if clean_guide.endswith("A") else 0.0

    counts = [
        clean_guide.count("U") / len(clean_guide),
        clean_guide.count("A") / len(clean_guide),
        clean_guide.count("G") / len(clean_guide),
        clean_guide.count("C") / len(clean_guide),
        target_site.count("U") / len(target_site),
        target_site.count("A") / len(target_site),
        target_site.count("G") / len(target_site),
        target_site.count("C") / len(target_site),
    ]

    base_stats = [
        guide_gc, target_gc, flank5_gc, flank3_gc, seed_gc,
        target_gc - guide_gc, has_5p_u, has_3p_a,
    ] + counts

    # Positional one-hot for 19 nt guide
    onehot = np.zeros((19, 4), dtype=np.float32)
    for i, c in enumerate(clean_guide[:19]):
        if c in NUC_MAP:
            onehot[i, NUC_MAP[c]] = 1.0

    return np.hstack([np.array(base_stats, dtype=np.float32), onehot.flatten()])


class ContextFeatureExtractor:
    """
    Unified feature extractor combining:
    - ViennaRNA accessibility & thermodynamics
    - Sequence engineering
    - Pretrained RNA-FM representations with fitted PCA projection
    """

    def __init__(self, use_rna_fm: bool = True, pca_dim: int = 32):
        self.use_rna_fm = use_rna_fm and (fm is not None) and (torch is not None)
        self.pca_dim = pca_dim
        self.rna_fm_model = None
        self.rna_fm_alphabet = None
        self.batch_converter = None
        self.mrna_pca = None
        self.guide_pca = None

    def _init_rna_fm(self):
        if self.use_rna_fm and self.rna_fm_model is None:
            logger.info("Loading pretrained RNA-FM model (rna_fm_t12)...")
            self.rna_fm_model, self.rna_fm_alphabet = fm.pretrained.rna_fm_t12()
            self.rna_fm_model.eval()
            self.batch_converter = self.rna_fm_alphabet.get_batch_converter()
            logger.info("RNA-FM model loaded successfully.")

    def extract_rna_fm_raw(self, sequences: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Extracts 640-D mean token embeddings from RNA-FM layer 12 in batches.
        """
        self._init_rna_fm()
        if not self.use_rna_fm:
            return np.zeros((len(sequences), 640), dtype=np.float32)

        all_embeddings = []
        for i in range(0, len(sequences), batch_size):
            batch_seqs = sequences[i:i + batch_size]
            data = [(f"seq_{idx}", seq.replace("X", "A")) for idx, seq in enumerate(batch_seqs)]
            _, _, batch_tokens = self.batch_converter(data)

            with torch.no_grad():
                results = self.rna_fm_model(batch_tokens, repr_layers=[12])
            token_reps = results["representations"][12]  # [B, L, 640]
            # Mean pool over sequence tokens (exclude BOS token at 0)
            seq_lens = [len(s) for s in batch_seqs]
            for b_idx, s_len in enumerate(seq_lens):
                rep = token_reps[b_idx, 1:s_len + 1].mean(dim=0).cpu().numpy()
                all_embeddings.append(rep)

        return np.vstack(all_embeddings).astype(np.float32)

    def extract_features_from_df(
        self,
        df: pd.DataFrame,
        batch_size: int = 32,
        fit_pca: bool = False,
    ) -> np.ndarray:
        """
        Extracts complete 189-D feature matrix from prepared dataset DataFrame.
        """
        logger.info(f"Extracting context-aware features for {len(df)} samples...")

        # 1. ViennaRNA features (9-D)
        vienna_list = []
        for _, row in df.iterrows():
            vienna_list.append(list(compute_viennarna_features(row["siRNA"], row["mRNA"]).values()))
        X_vienna = np.array(vienna_list, dtype=np.float32)

        # 2. OligoFormer td features (24-D)
        td_cols = [f"td_{i}" for i in range(24)]
        if all(c in df.columns for c in td_cols):
            X_td = df[td_cols].values.astype(np.float32)
        else:
            X_td = np.zeros((len(df), 24), dtype=np.float32)

        # 3. Sequence engineering features (92-D)
        seq_list = []
        for _, row in df.iterrows():
            seq_list.append(compute_sequence_features(row["siRNA"], row["mRNA"]))
        X_seq = np.vstack(seq_list).astype(np.float32)

        # 4. RNA-FM foundation embeddings (65-D)
        if self.use_rna_fm:
            from sklearn.decomposition import PCA
            logger.info("Extracting RNA-FM embeddings for mRNA target windows...")
            mrna_seqs = df["mRNA"].str.replace("X", "A").tolist()
            guide_seqs = df["siRNA"].tolist()

            raw_mrna_emb = self.extract_rna_fm_raw(mrna_seqs, batch_size=batch_size)
            raw_guide_emb = self.extract_rna_fm_raw(guide_seqs, batch_size=batch_size)

            # Cosine similarity
            norm_m = np.linalg.norm(raw_mrna_emb, axis=1, keepdims=True) + 1e-8
            norm_g = np.linalg.norm(raw_guide_emb, axis=1, keepdims=True) + 1e-8
            cos_sim = np.sum((raw_mrna_emb / norm_m) * (raw_guide_emb / norm_g), axis=1, keepdims=True)

            if not fit_pca and self.mrna_pca is None and PCA_CACHE_PATH.exists():
                try:
                    cached = joblib.load(PCA_CACHE_PATH)
                    self.mrna_pca = cached.get("mrna_pca")
                    self.guide_pca = cached.get("guide_pca")
                except Exception as e:
                    logger.warning(f"Could not load cached PCA: {e}")

            if fit_pca or self.mrna_pca is None:
                actual_pca_dim = min(self.pca_dim, raw_mrna_emb.shape[0])
                logger.info(f"Fitting PCA ({actual_pca_dim} components) on RNA-FM embeddings...")
                self.mrna_pca = PCA(n_components=actual_pca_dim, random_state=42)
                self.guide_pca = PCA(n_components=actual_pca_dim, random_state=42)
                mrna_proj = self.mrna_pca.fit_transform(raw_mrna_emb)
                guide_proj = self.guide_pca.fit_transform(raw_guide_emb)
                joblib.dump({"mrna_pca": self.mrna_pca, "guide_pca": self.guide_pca}, PCA_CACHE_PATH)
            else:
                mrna_proj = self.mrna_pca.transform(raw_mrna_emb)
                guide_proj = self.guide_pca.transform(raw_guide_emb)

            X_fm = np.hstack([mrna_proj, guide_proj, cos_sim]).astype(np.float32)
        else:
            X_fm = np.zeros((len(df), self.pca_dim * 2 + 1), dtype=np.float32)

        X_full = np.hstack([X_vienna, X_td, X_seq, X_fm])
        logger.info(f"Feature extraction complete. Matrix shape: {X_full.shape}")
        return X_full

    def extract_for_candidates(
        self,
        candidates: List[Any],
        mrna_sequence: str,
        batch_size: int = 32,
    ) -> np.ndarray:
        """
        Extracts 190-D context-aware features directly for a list of candidate siRNAs
        and their parent mRNA sequence.
        """
        clean_mrna = _clean_rna(mrna_sequence)
        df_rows = []
        for c in candidates:
            # Candidate position is a 1-based biological coordinate (1 to L)
            pos_1based = getattr(c, "position", 1)
            pos = max(0, pos_1based - 1)
            target = clean_mrna[pos : pos + 19]
            if len(target) < 19:
                target = target + "A" * (19 - len(target))

            # 19-nt upstream flank
            if pos >= 19:
                up = clean_mrna[pos - 19 : pos]
            else:
                up = "A" * (19 - pos) + clean_mrna[:pos]

            # 19-nt downstream flank
            down_end = min(len(clean_mrna), pos + 38)
            down = clean_mrna[pos + 19 : down_end]
            if len(down) < 19:
                down = down + "A" * (19 - len(down))

            context_57nt = up + target + down
            guide_19nt = _clean_rna(getattr(c, "antisense", ""))[:19]
            if len(guide_19nt) < 19:
                guide_19nt = guide_19nt + "A" * (19 - len(guide_19nt))

            df_rows.append({"siRNA": guide_19nt, "mRNA": context_57nt})

        df = pd.DataFrame(df_rows)
        return self.extract_features_from_df(df, batch_size=batch_size, fit_pca=False)

