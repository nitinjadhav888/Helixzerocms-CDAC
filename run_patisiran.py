import sys
from pathlib import Path
sys.path.insert(0, r"d:\Helixx")
sys.path.insert(0, r"d:\Helixx\smepred")

from smepred.src.modification_engine import _apply_mod
from smepred.src.predictor import predict_modified

# Patisiran configuration
sense = "GUAACCAAGAGUAUUCCAUTT"
anti = "AUGGAAUACUCUUGGUUACTT"
sense_mods = ".M..MM......MMMM.M..."
anti_mods = "......M.........M...."

# Apply modifications
mod_sense = sense
for i, m in enumerate(sense_mods):
    if m != '.': mod_sense = _apply_mod(mod_sense, i, m)

mod_anti = anti
for i, m in enumerate(anti_mods):
    if m != '.': mod_anti = _apply_mod(mod_anti, i, m)

print("Parent Sense:", sense)
print("Parent Anti: ", anti)
print("Mod Sense:   ", mod_sense)
print("Mod Anti:    ", mod_anti)

res = predict_modified(
    sense=mod_sense,
    antisense=mod_anti,
    parent_sense=sense,
    parent_antisense=anti,
    mod_symbol="",
    mod_position=0,
    mod_positions="",
    mod_strand="",
    sense_mods=sense_mods,
    sense_positions="",
    antisense_mods=anti_mods,
    antisense_positions="",
    mode="multimod",
    top_n=10
)

import json
print(json.dumps(res["results"][0].to_dict(), indent=2))
print("Biophysics penalties:", res["results"][0].biophysics)
