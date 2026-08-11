"""
test_phase5_verification.py
============================
Automated unit tests for Phase 5 Real 3D Structure Implementation Path:
1. Residue-accurate 3D PDB atom geometry generation with nucleobase ring splicing (A, U, G, C).
2. Modification fragment templates (2'-OMe, 2'-F, PS backbone, LNA bridges, 2'-MOE, Abasic site).
3. SQLite persistent 3D structure caching with WAL mode.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from smepred.src.structure_minimization import generate_residue_accurate_pdb, StructureKVStore
from smepred.src import predictor


def test_residue_accurate_pdb_generation():
    print("[TEST 1] Testing Residue-Accurate 3D PDB Structure Generation & Ring Atom Splicing...")
    sense = "GGAAUCUUCAUAGCUCAGCUU"
    anti  = "AAGCUGAGCUAAGAAGAUUCC"
    
    pdb_str = generate_residue_accurate_pdb(
        sense, anti, 
        sense_mods="M2M2M2M2M2M2M2M2M2M2M", 
        antisense_mods="F3F3F3F3F3F3F3F3F3F3F"
    )
    
    assert "HEADER    RESIDUE-ACCURATE SIRNA DUPLEX" in pdb_str, "FAILED: Missing residue-accurate header!"
    assert "ATOM" in pdb_str, "FAILED: No ATOM lines generated!"
    assert "C2M" in pdb_str, "FAILED: Missing 2'-OMe fragment template atoms!"
    assert "F2'" in pdb_str, "FAILED: Missing 2'-F fragment template atoms!"
    assert "N9 " in pdb_str and "C8 " in pdb_str and "C6 " in pdb_str, "FAILED: Missing purine/pyrimidine nucleobase ring atoms!"
    print("  -> SUCCESS: Residue-accurate PDB with nucleobase ring geometry, 2'-OMe and 2'-F fragment templates generated!")


def test_moe_and_abasic_templates():
    print("[TEST 2] Testing MOE ('E') Substituent & Abasic ('Q') Site Templates...")
    sense = "GGAAUCUUCAUAGCUCAGCUU"
    anti  = "AAGCUGAGCUAAGAAGAUUCC"
    
    # Candidate with MOE at pos 1 on sense (chain A) and Abasic at pos 1 on antisense (chain B)
    pdb_moe = generate_residue_accurate_pdb(
        sense, anti,
        sense_mods="E....................",
        antisense_mods="Q...................."
    )
    
    assert "C1E" in pdb_moe and "C2E" in pdb_moe and "O3E" in pdb_moe, "FAILED: Missing 2'-MOE fragment atoms (C1E, C2E, O3E)!"
    
    # Verify Abasic ('Q') site at pos 1 on antisense (chain B) has sugar backbone but NO nucleobase ring atoms
    b1_lines = [l for l in pdb_moe.splitlines() if l.startswith("ATOM") and " B   1 " in l]
    b1_atoms = [l[12:16].strip() for l in b1_lines]
    assert not any(n in ("N9", "N1", "C8", "C6", "N7", "N6", "O6") for n in b1_atoms), f"FAILED: Abasic site (Q) at B1 should omit base ring atoms, found: {b1_atoms}"
    print("  -> SUCCESS: MOE fragment (2'-O-CH2-CH2-O-CH3) and Abasic site base-omission verified!")


def test_structure_sqlite_store():
    print("[TEST 3] Testing SQLite 3D Structure Cache (WAL Mode)...")
    store = StructureKVStore()
    
    # Verify WAL journal_mode is active
    with store._get_connection() as conn:
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert journal_mode.lower() == "wal", f"FAILED: Expected SQLite journal_mode WAL, got '{journal_mode}'"
    
    key = "TEST_SENSE|TEST_ANTI|MOD1|MOD2"
    pdb_sample = "HEADER TEST PDB MODEL\nATOM 1 P A 1 ...\nEND"
    
    store.set(key, pdb_sample)
    retrieved = store.get(key)
    
    assert retrieved is not None, "FAILED: 3D structure SQLite store get returned None!"
    assert "HEADER TEST PDB MODEL" in retrieved, "FAILED: 3D structure content mismatch!"
    print("  -> SUCCESS: SQLite 3D Structure Cache (verified PRAGMA journal_mode=WAL) round-trip verified!")


def test_predictor_pdb_integration():
    print("[TEST 4] Testing Predictor PDB Endpoint & Explicit Single-Mod Params Integration...")
    sense = "GGAAUCUUCAUAGCUCAGCUU"
    anti  = "AAGCUGAGCUAAGAAGAUUCC"
    
    pdb_out = predictor.generate_sirna_pdb(
        sense, anti,
        mod_symbol="F",
        mod_position=2,
        mod_strand="antisense"
    )
    assert "ATOM" in pdb_out, "FAILED: Predictor PDB generation returned empty/invalid output!"
    assert "F2'" in pdb_out, "FAILED: Explicit single-mod param F not reflected in 3D PDB output!"
    print("  -> SUCCESS: Predictor PDB integration and explicit single-mod params verified!")


if __name__ == "__main__":
    print("=" * 60)
    print("      RUNNING PHASE 5 AUTOMATED VERIFICATION SUITE")
    print("=" * 60)
    test_residue_accurate_pdb_generation()
    test_moe_and_abasic_templates()
    test_structure_sqlite_store()
    test_predictor_pdb_integration()
    print("=" * 60)
    print("      ALL PHASE 5 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
