import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.predictor import generate_sirna_pdb, extract_structural_properties, predict_modified

TEST_SENSE = "CAGAAAGAGUGUCUCAUCUUA"
TEST_ANTISENSE = "UAAGAUGAGACACUCUUUCUG"

def test_3d_pdb_single_mod_highlight():
    """Verify single mod on antisense strand pos 6 produces non-zero B-factor in PDB ATOM records."""
    pdb_str = generate_sirna_pdb(
        TEST_SENSE, TEST_ANTISENSE,
        mod_symbol="2'-Fluoro",
        mod_position=6,
        mod_strand="antisense"
    )
    assert pdb_str is not None
    lines = [l for l in pdb_str.split("\n") if l.startswith("ATOM")]
    assert len(lines) > 0
    highlighted = [l for l in lines if float(l[60:66]) == 90.0]
    assert len(highlighted) > 0, "Expected 2'-F atoms to have B-factor 90.0"

def test_3d_pdb_single_mod_sense_highlight():
    """Verify single mod on sense strand pos 1 produces 2'-OMe B-factor 80.0."""
    pdb_str = generate_sirna_pdb(
        TEST_SENSE, TEST_ANTISENSE,
        mod_symbol="2'-O-Methyl",
        mod_position=1,
        mod_strand="sense"
    )
    assert pdb_str is not None
    lines = [l for l in pdb_str.split("\n") if l.startswith("ATOM")]
    highlighted = [l for l in lines if float(l[60:66]) == 80.0]
    assert len(highlighted) > 0, "Expected 2'-OMe atoms to have B-factor 80.0"

def test_3d_pdb_multimod_highlight():
    """Verify multi-mod explicit parameters produce multiple highlighted positions."""
    pdb_str = generate_sirna_pdb(
        TEST_SENSE, TEST_ANTISENSE,
        sense_mods="F,M",
        sense_positions="2,5",
        antisense_mods="M,S",
        antisense_positions="6,21"
    )
    assert pdb_str is not None
    lines = [l for l in pdb_str.split("\n") if l.startswith("ATOM")]
    b_factors = {float(l[60:66]) for l in lines}
    assert 90.0 in b_factors # 2'-F
    assert 80.0 in b_factors # 2'-OMe
    assert 70.0 in b_factors # PS

def test_predict_modified_multimod_with_single_mod_args():
    """Verify predict_modified in multimod mode correctly accepts single-mod arguments."""
    res = predict_modified(
        TEST_SENSE, TEST_ANTISENSE,
        mode="multimod",
        mod_symbol="2'-Fluoro",
        mod_position=6,
        mod_strand="antisense"
    )
    assert "results" in res
    assert len(res["results"]) == 1
    v = res["results"][0]
    assert v.antisense[5] == "F" # 1-based pos 6 is index 5
    assert "structural_properties" in res
    pdb = res["structural_properties"]["pdb_data"]
    lines = [l for l in pdb.split("\n") if l.startswith("ATOM") and float(l[60:66]) == 90.0]
    assert len(lines) > 0
