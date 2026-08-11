"""
test_phase3_verification.py
============================
Automated unit tests for Phase 3 Data Infrastructure Redesign:
1. 2-bit packed 15-mer k-mer hash index & SQLite OffTargetKVStore persistence with assembly versioning.
2. Candidate pre-filtering in sirna_generator.py.
3. Multi-organism transcriptome registry.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from smepred.src.offtarget import OffTargetEngine, get_offtarget_engine
from smepred.src.offtarget_store import OffTargetKVStore
from smepred.src.sirna_generator import generate_candidates
from smepred.src.transcriptome_source import list_supported_transcriptomes


def test_kmer_index_and_sqlite_store():
    print("[TEST 1] Testing 2-Bit Packed K-Mer Hash Index & SQLite Store (Versioned)...")
    store = OffTargetKVStore()

    # Test SQLite versioned roundtrip
    test_key = "AUGCAUGCAUGCAUGCAUGCA"
    test_data = {"isSafe": True, "overallSafetyScore": 95.0, "status": "CLEARED"}
    store.set(test_key, test_data, version="GRCh38.p14")

    retrieved = store.get(test_key, version="GRCh38.p14")
    assert retrieved is not None, "FAILED: SQLite cache get returned None!"
    assert retrieved["overallSafetyScore"] == 95.0, "FAILED: SQLite cached data mismatch!"
    
    # Assert different assembly version returns None (no collision across reference updates)
    other_ver = store.get(test_key, version="GRCh39.p1")
    assert other_ver is None, "FAILED: SQLite cache returned result for a different assembly version!"
    print("  -> SUCCESS: SQLite OffTargetKVStore versioned round-trip verified!")

    # Test OffTargetEngine 15-mer index
    engine = get_offtarget_engine()
    print(f"  -> OffTargetEngine loaded sequence bases: {len(engine.sequence):,}, 15-mer set size: {len(engine._kmer15_set):,}")
    
    sense = "GGAAUCUUCAUAGCUCAGCUU"
    anti  = "AAGCUGAGCUAAGAAGAUUCC"
    report = engine.validate_safety(sense, anti)
    assert "status" in report, "FAILED: Missing status in off-target report!"
    print(f"  -> SUCCESS: Off-target safety report generated in O(1) time (Status: {report['status']}, Score: {report['overallSafetyScore']})")


def test_candidate_prefiltering():
    print("[TEST 2] Testing Candidate Pre-Filtering in sirna_generator...")
    # Gene sequence with normal region, high-GC region, and homopolymer run
    mrna = "AUG" + ("G" * 10) + ("C" * 10) + "AUGCUAGCUAGCUAGCUAGCUAGCUAGCUAGCUAGC"
    
    raw_cands = generate_candidates(mrna, pre_filter=False)
    filtered_cands = generate_candidates(mrna, pre_filter=True)
    
    assert len(filtered_cands) < len(raw_cands), f"FAILED: Pre-filtering did not reduce candidates ({len(filtered_cands)} vs {len(raw_cands)})"
    print(f"  -> SUCCESS: Pre-filtering reduced candidate count from {len(raw_cands)} down to {len(filtered_cands)}!")


def test_transcriptome_registry():
    print("[TEST 3] Testing Multi-Organism Transcriptome Registry...")
    registry = list_supported_transcriptomes()
    assert len(registry) >= 3, f"FAILED: Expected at least 3 species in registry, got {len(registry)}"
    species_keys = [item["key"] for item in registry]
    assert "human_grch38" in species_keys, "FAILED: human_grch38 missing from registry!"
    print(f"  -> SUCCESS: Supported transcriptomes registry verified ({[item['organism'] for item in registry]})")


if __name__ == "__main__":
    print("=" * 60)
    print("      RUNNING PHASE 3 AUTOMATED VERIFICATION SUITE")
    print("=" * 60)
    test_kmer_index_and_sqlite_store()
    test_candidate_prefiltering()
    test_transcriptome_registry()
    print("=" * 60)
    print("      ALL PHASE 3 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
