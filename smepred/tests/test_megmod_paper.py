import sys, os
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from src import predictor, modification_engine


def test_megmod_paper_case_study():
    sense = 'AAGGCCUUUCACUACUCCUAC'
    anti = 'GUAGGAGUAGUGAAAGGCCUU'

    # 1. Single Mod Scan
    single_res = predictor.predict_modified(sense, anti, mode='scan', model_key='B_v4')
    assert "parent_score" in single_res
    assert len(single_res['results']) > 0

    # 2. Multi-Mod Beam Search
    proxy_singles = [modification_engine.CmSiRNA(
        sense=sense, antisense=anti, mod_symbol=r.mod_symbol, mod_position=r.mod_position,
        mod_strand=r.mod_strand, parent_sense=sense, parent_antisense=anti, efficacy_score=r.efficacy_score
    ) for r in single_res['results']]

    mm_variants = modification_engine.multi_mod_scan(
        sense, anti, max_mods=2, beam_width=5, model_key='B_v4', single_results=proxy_singles, parent_score=single_res['parent_score']
    )
    assert len(mm_variants) > 0

