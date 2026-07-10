"""
patent_sources.py -- Reproducible ingestion of every real (non-synthetic)
Model B training source, each parsed with the notation THAT source actually
uses (conflating notations across sources silently corrupts chemistry --
see model_b_v2_multislot_ablation.md for the confirmed bugs this guards
against).

Sources
-------
1. CMsiRNAdb (CMsiRNA_data_update.tsv) -- compositional English modification
   names, parsed by src.chem_schema.parse_position_string.
2. US10240152B2, Table 2/4/8 -- compact lowercase(2'-OMe)/uppercase(RNA)/
   dT(DNA overhang) notation. 32/140 duplexes have a real measured IC50 and
   are held out from ALL training as the external test.
3. US10240152B2, Table 13/14 (tiled duplexes) -- the original extraction
   dropped the antisense strand for rows whose duplex ID wasn't repeated in
   the source text (parser only anchored on lines starting with "AD-").
   7/39 duplexes are recoverable by re-joining through Table 2/4 on oligo ID;
   the remaining 32 need the raw patent text (unavailable this session) and
   are excluded, not fabricated.
4. US11697812B2 (Dicerna TTR), Table 2 -- 25/27nt asymmetric DsiRNA. Lowercase
   here means DNA (2nt 3' overhang), NOT 2'-OMe -- a different convention
   from source 2/3, requiring its own parser.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from smepred.src.chem_schema import parse_position_string, NucSlot

PATENT_DIR = "smepred/data/patent_data"
CMS_TSV = "smepred/data/processed/CMsiRNA_data_update.tsv"


def parse_alnylam_compact(modified: str) -> list[NucSlot]:
    """lowercase=2'-OMe, uppercase=RNA, 'dX'=DNA overhang (US10240152B2 notation)."""
    slots, i, n = [], 0, len(modified)
    while i < n:
        c = modified[i]
        if c == 'd' and i + 1 < n and modified[i + 1].upper() in 'ATCGU':
            base = modified[i + 1].upper()
            slots.append(NucSlot(base='U' if base == 'T' else base, sugar="deoxyribo"))
            i += 2
        elif c.isalpha():
            slots.append(NucSlot(base=c.upper(), sugar="2OMe" if c.islower() else "ribo"))
            i += 1
        else:
            i += 1
    return slots


def parse_dicerna(sense: str, antisense: str) -> tuple[list[NucSlot], list[NucSlot]]:
    """US11697812B2 25/27 DsiRNA: lowercase = DNA (3' overhang), not 2'-OMe."""
    s_slots = [NucSlot(base=c.upper(), sugar="deoxyribo" if c.islower() else "ribo") for c in sense]
    a_slots = [NucSlot(base=c.upper(), sugar="ribo") for c in antisense]
    return s_slots, a_slots


class Row:
    __slots__ = ("sense_slots", "anti_slots", "efficacy", "group_key", "source")

    def __init__(self, sense_slots, anti_slots, efficacy, group_key, source):
        self.sense_slots, self.anti_slots = sense_slots, anti_slots
        self.efficacy, self.group_key, self.source = efficacy, group_key, source


def load_cmsirnadb() -> list[Row]:
    df = pd.read_csv(CMS_TSV, sep="\t", low_memory=False)
    df["Inhibition"] = pd.to_numeric(df["Inhibition"], errors="coerce")
    df = df[df["Inhibition"].between(-50, 150) & df["Sense_seqence"].notna() & df["Antisense_seqence"].notna()]
    df = df[(df["Sense_seqence"].str.len() <= 27) & (df["Antisense_seqence"].str.len() <= 27)]
    df["Inhibition"] = df["Inhibition"].clip(0, 100)

    rows = []
    for _, r in df.iterrows():
        ss, as_ = r["Sense_seqence"], r["Antisense_seqence"]
        s_slots = parse_position_string(r.get("Modification_Types_Sense_strand"), ss) or [NucSlot(base=b) for b in ss]
        a_slots = parse_position_string(r.get("Modification_Types_Antisense_strand"), as_) or [NucSlot(base=b) for b in as_]
        rows.append(Row(s_slots, a_slots, float(r["Inhibition"]), as_, "cmsirnadb"))
    return rows


def _load_alnylam_tables():
    t2 = pd.read_csv(f"{PATENT_DIR}/patent_table2_duplex_map.csv")
    t4 = pd.read_csv(f"{PATENT_DIR}/patent_table4_sequences.csv")
    t8 = pd.read_csv(f"{PATENT_DIR}/patent_table8_ic50.csv")
    return t2, t4, t8, dict(zip(t4["oligo"], t4["sequence"]))


def load_external_ic50_holdout() -> pd.DataFrame:
    """32 duplexes with a real measured IC50 -- held out from ALL training."""
    t2, t4, t8, seq_by_oligo = _load_alnylam_tables()
    valid = t8[t8["ic50_hepg2_qpcr_nM"].notna() & (t8["ic50_hepg2_qpcr_nM"] != "ND")].merge(t2, on="duplex")
    valid = valid[valid["sense_oligo"].map(seq_by_oligo).notna() & valid["antisense_oligo"].map(seq_by_oligo).notna()]
    return pd.DataFrame({
        "duplex": valid["duplex"],
        "sense_compact": valid["sense_oligo"].map(seq_by_oligo),
        "anti_compact": valid["antisense_oligo"].map(seq_by_oligo),
        "ic50_nM": valid["ic50_hepg2_qpcr_nM"].astype(float),
    })


def load_alnylam_10240152(exclude_duplexes: set) -> list[Row]:
    t2, t4, t8, seq_by_oligo = _load_alnylam_tables()
    rows = []
    for _, d in t2.iterrows():
        dup = d["duplex"]
        if dup in exclude_duplexes or d["sense_oligo"] not in seq_by_oligo or d["antisense_oligo"] not in seq_by_oligo:
            continue
        ic8 = t8[t8["duplex"] == dup]
        if ic8.empty or pd.isna(ic8.iloc[0]["singledose_hepg2_qpcr"]):
            continue
        efficacy = float(np.clip(100.0 - float(ic8.iloc[0]["singledose_hepg2_qpcr"]), 0, 100))
        s_slots = parse_alnylam_compact(seq_by_oligo[d["sense_oligo"]])
        a_slots = parse_alnylam_compact(seq_by_oligo[d["antisense_oligo"]])
        rows.append(Row(s_slots, a_slots, efficacy, "".join(s.base for s in a_slots), "alnylam_10240152_t2t4t8"))
    return rows


def load_alnylam_10240152_tiled_recovered() -> list[Row]:
    """7/39 Table 13 duplexes recoverable by re-joining Table 2/4 (see module docstring)."""
    t2, t4, _, seq_by_oligo = _load_alnylam_tables()
    t13 = pd.read_csv(f"{PATENT_DIR}/patent_table13_tiled_sequences.csv")
    t14 = pd.read_csv(f"{PATENT_DIR}/patent_table14_knockdown.csv")
    merged = t13.merge(t2, on="duplex", how="left").merge(t14, on="duplex", how="left")
    merged["anti_seq"] = merged["antisense_oligo"].map(seq_by_oligo)
    merged = merged[merged["anti_seq"].notna() & merged["pct_remaining_10nM"].notna()]

    rows = []
    for _, r in merged.iterrows():
        efficacy = float(np.clip(100.0 - float(r["pct_remaining_10nM"]), 0, 100))
        s_slots, a_slots = parse_alnylam_compact(r["sequence"]), parse_alnylam_compact(r["anti_seq"])
        rows.append(Row(s_slots, a_slots, efficacy, "".join(s.base for s in a_slots), "alnylam_10240152_t13_recovered"))
    return rows


def load_dicerna_11697812() -> list[Row]:
    df = pd.read_csv(f"{PATENT_DIR}/dicerna_merged.csv").dropna(subset=["sense_seq", "antisense_seq", "huh7_pct_amplicon1"])
    rows = []
    for _, r in df.iterrows():
        pct = float(np.nanmean([r.get("huh7_pct_amplicon1"), r.get("huh7_pct_amplicon2")]))
        efficacy = float(np.clip(100.0 - pct, 0, 100))
        s_slots, a_slots = parse_dicerna(r["sense_seq"], r["antisense_seq"])
        rows.append(Row(s_slots, a_slots, efficacy, r["antisense_seq"], "dicerna_11697812"))
    return rows


def load_all_real_sources() -> tuple[list[Row], pd.DataFrame]:
    """All 4 real (non-synthetic) sources + the disjoint external IC50 test set."""
    external = load_external_ic50_holdout()
    t8 = pd.read_csv(f"{PATENT_DIR}/patent_table8_ic50.csv")
    exclude = set(t8[t8["ic50_hepg2_qpcr_nM"].notna() & (t8["ic50_hepg2_qpcr_nM"] != "ND")]["duplex"])
    rows = (load_cmsirnadb() + load_alnylam_10240152(exclude)
            + load_alnylam_10240152_tiled_recovered() + load_dicerna_11697812())
    return rows, external
