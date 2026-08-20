import sys
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(".")))
sys.path.insert(0, str(Path("./smepred")))

from smepred.src import predictor

payloads = [
    # Case 0: Normal single mod
    {"sense": "GUAACCAAGAGUAUUCCAUTT", "antisense": "AUGGAAUACUCUUGGUUACTT", "mode": "multimod", "mod_symbol": "M", "mod_position": "3", "mod_strand": "antisense"},
    # Case 1: Multi mod comma list
    {"sense": "GUAACCAAGAGUAUUCCAUTT", "antisense": "AUGGAAUACUCUUGGUUACTT", "mode": "multimod", "sense_mods": "M,F", "sense_positions": "1,2", "antisense_mods": "M,F", "antisense_positions": "1,2"},
    # Case 2: Full 21-char mask string
    {"sense": "GUAACCAAGAGUAUUCCAUTT", "antisense": "AUGGAAUACUCUUGGUUACTT", "mode": "multimod", "sense_mods": "MMMMMMMMMMMMMMMMMMMMM", "antisense_mods": "FFFFFFFFFFFFFFFFFFFFF"},
    # Case 3: mod_symbol as string name e.g. 2'-OMe
    {"sense": "GUAACCAAGAGUAUUCCAUTT", "antisense": "AUGGAAUACUCUUGGUUACTT", "mode": "multimod", "mod_symbol": "2'-OMe", "mod_position": "5", "mod_strand": "antisense"},
    # Case 4: mod_positions as '+' separated
    {"sense": "GUAACCAAGAGUAUUCCAUTT", "antisense": "AUGGAAUACUCUUGGUUACTT", "mode": "multimod", "mod_symbol": "M+F", "mod_positions": "2+6", "mod_strand": "antisense"},
    # Case 5: 19-mer sequences
    {"sense": "GUAACCAAGAGUAUUCCAU", "antisense": "AUGGAAUACUCUUGGUUAC", "mode": "multimod", "mod_symbol": "M", "mod_position": "20", "mod_strand": "antisense"},
    # Case 6: Out of bound position
    {"sense": "GUAACCAAGAGUAUUCCAU", "antisense": "AUGGAAUACUCUUGGUUAC", "mode": "multimod", "sense_mods": "M", "sense_positions": "1, 2, 3"},
    # Case 7: 23-mer vs 21-mer (e.g. Vutrisiran, Givosiran)
    {"sense": "CAGUCAACUUGCCUGCUUAUU", "antisense": "UAAGCAGGCAAGUUGACUGUUUU", "mode": "multimod", "mod_symbol": "M", "mod_position": "2", "mod_strand": "antisense"},
    # Case 8: Click on 3D in UI with already-modified sequences in sense/antisense inputs
    {"sense": "GUAACCAAGAGUAUUCCAUTT", "antisense": "AUGGAAUACUCUUGGUUACTT", "mode": "multimod", "mod_symbol": "", "mod_position": "", "mod_strand": "", "sense_mods": "", "sense_positions": "", "antisense_mods": "", "antisense_positions": ""},
    # Case 9: Empty sense_positions with non-empty sense_mods that is NOT length of sense
    {"sense": "GUAACCAAGAGUAUUCCAUTT", "antisense": "AUGGAAUACUCUUGGUUACTT", "mode": "multimod", "sense_mods": "M", "sense_positions": "", "antisense_mods": "F", "antisense_positions": ""}
]

for idx, p in enumerate(payloads):
    try:
        res = predictor.predict_modified(**p)
        print(f"Payload {idx}: PASSED")
    except Exception as e:
        print(f"Payload {idx} FAILED: {e}")
        traceback.print_exc()
