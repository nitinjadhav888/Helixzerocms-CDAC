import sys, os
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "smepred"))
import pandas as pd
import numpy as np
from smepred.src import model_b_v4, features_v4, biophysics, predictor
from smepred.src.chem_schema import promote_legacy_string
from helixzero_ieee_v5.predict_ieee_v5 import mod2_engine, mod3_engine

df = pd.read_csv(ROOT_DIR / "smepred" / "data" / "processed" / "helixzero_unified_master_ieee_dataset.csv")
print("Full shape:", df.shape)
df = df.sample(n=5000, random_state=42).reset_index(drop=True)
s_base_list = [str(r['sense']) for _, r in df.iterrows()]
a_base_list = [str(r['antisense']) for _, r in df.iterrows()]
s_mod_list = [str(r['sense_mods']) if pd.notnull(r.get('sense_mods')) else str(s_base_list[i]) for i, (_, r) in enumerate(df.iterrows())]
a_mod_list = [str(r['anti_mods']) if pd.notnull(r.get('anti_mods')) else str(a_base_list[i]) for i, (_, r) in enumerate(df.iterrows())]

print("Testing Model 2 predict...")
try:
    preds2 = model_b_v4.predict(s_mod_list, a_mod_list, s_base_list, a_base_list)
    print("Model 2 Success! Shape:", preds2.shape)
except Exception as e:
    import traceback
    traceback.print_exc()
