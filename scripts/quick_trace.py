import sys, os, traceback
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "smepred"))

import pandas as pd
import numpy as np

try:
    from smepred.src import model_b_v4, features, features_v4
    print("Imports OK!", flush=True)

    df = pd.read_csv(ROOT_DIR / "smepred" / "data" / "processed" / "helixzero_unified_master_ieee_dataset.csv", low_memory=False)
    print(f"Read {len(df)} rows", flush=True)
    df = df.sample(n=10, random_state=42).reset_index(drop=True)
    
    s_base = [str(r.get("canonical_sense_sequence", r.get("sense", "AUGCAUGCAUGCAUGCAUGCU"))).strip()[:21] for _, r in df.iterrows()]
    a_base = [str(r.get("canonical_antisense_sequence", r.get("antisense", "AUGCAUGCAUGCAUGCAUGCU"))).strip()[:21] for _, r in df.iterrows()]
    s_mod = [str(r.get("modified_sense_sequence", r.get("sense_mods", s_base[i])))[:21] for i, (_, r) in enumerate(df.iterrows())]
    a_mod = [str(r.get("modified_antisense_sequence", r.get("anti_mods", a_base[i])))[:21] for i, (_, r) in enumerate(df.iterrows())]

    print("Testing Model 1...", flush=True)
    feat1 = features.extract_batch_v4(s_base, a_base)
    print("Feat1 shape:", feat1.shape, flush=True)

    print("Testing Model 2...", flush=True)
    preds2 = model_b_v4.predict(s_mod, a_mod, s_base, a_base)
    print("Preds2 shape:", preds2.shape, "Values:", preds2[:3], flush=True)

except Exception as e:
    print(f"CRASH CAUGHT: {e}", flush=True)
    traceback.print_exc()
