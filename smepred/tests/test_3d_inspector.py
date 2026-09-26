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


def test_duplex_binding_energy_varies_with_modifications():
    """Verify duplex binding energy dynamically responds to stabilizing and destabilizing chemistries."""
    # 1. Unmodified parent baseline
    naked = extract_structural_properties(TEST_SENSE, TEST_ANTISENSE)
    g_naked = naked["duplex_mfe_kcal"]
    assert naked["delta_duplex_dg"] == 0.0

    # 2. 2'-Fluoro (stabilizing: ΔΔG ≈ -0.85 kcal/mol)
    mod_2f = extract_structural_properties(
        TEST_SENSE, TEST_ANTISENSE,
        mod_symbol="2'-Fluoro", mod_position=6, mod_strand="antisense"
    )
    assert mod_2f["duplex_mfe_kcal"] < g_naked
    assert round(mod_2f["duplex_mfe_kcal"] - g_naked, 2) == -0.85
    assert mod_2f["delta_duplex_dg"] == -0.85

    # 3. LNA (Locked Nucleic Acid, strongly stabilizing: ΔΔG ≈ -3.50 kcal/mol)
    mod_lna = extract_structural_properties(
        TEST_SENSE, TEST_ANTISENSE,
        mod_symbol="L", mod_position=6, mod_strand="antisense"
    )
    assert mod_lna["duplex_mfe_kcal"] < mod_2f["duplex_mfe_kcal"]
    assert round(mod_lna["duplex_mfe_kcal"] - g_naked, 2) == -3.50
    assert mod_lna["delta_duplex_dg"] == -3.50

    # 4. 2'-Deoxy / DNA (destabilizing: ΔΔG ≈ +0.70 kcal/mol)
    mod_dna = extract_structural_properties(
        TEST_SENSE, TEST_ANTISENSE,
        mod_symbol="D", mod_position=6, mod_strand="antisense"
    )
    assert mod_dna["duplex_mfe_kcal"] > g_naked
    assert round(mod_dna["duplex_mfe_kcal"] - g_naked, 2) == 0.70
    assert mod_dna["delta_duplex_dg"] == 0.70

    # 5. UNA (Unlocked Nucleic Acid, strongly destabilizing: ΔΔG ≈ +4.00 kcal/mol)
    mod_una = extract_structural_properties(
        TEST_SENSE, TEST_ANTISENSE,
        mod_symbol="6", mod_position=6, mod_strand="antisense"
    )
    assert mod_una["duplex_mfe_kcal"] > mod_dna["duplex_mfe_kcal"]
    assert round(mod_una["duplex_mfe_kcal"] - g_naked, 2) == 4.00
    assert mod_una["delta_duplex_dg"] == 4.00


def test_single_mod_scan_variants_have_distinct_duplex_dg():
    """Verify single-mod scan returns distinct, chemistry-specific duplex binding energies across candidates."""
    res = predict_modified(TEST_SENSE, TEST_ANTISENSE, mode="scan", full_scan=False)
    results = res["results"]
    assert len(results) > 0

    duplex_energies = {r.duplex_mfe_kcal for r in results if r.duplex_mfe_kcal is not None}
    delta_dgs = {r.delta_duplex_dg for r in results if r.delta_duplex_dg is not None}

    # Different modification types (E, D, Q, L) must have different duplex binding energies
    assert len(duplex_energies) > 1, f"Expected distinct duplex energies across variants, got only {duplex_energies}"
    assert len(delta_dgs) > 1, f"Expected distinct delta dG values, got only {delta_dgs}"
    
    # Check that LNA candidates have negative delta dG (stabilizing) and DNA has positive delta dG (destabilizing)
    lna_variants = [r for r in results if r.mod_symbol == 'L']
    dna_variants = [r for r in results if r.mod_symbol == 'D']
    if lna_variants:
        assert lna_variants[0].delta_duplex_dg < 0, "LNA must be stabilizing (delta dG < 0)"
    if dna_variants:
        assert dna_variants[0].delta_duplex_dg > 0, "DNA must be destabilizing (delta dG > 0)"

