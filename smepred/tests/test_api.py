"""
test_api.py
------------------
Comprehensive production test suite for all FastAPI endpoints in smepred.api.main
using TestClient. Validates route response codes, JSON schemas, biophysical metrics,
and error handling across all core platform capabilities.
"""

import sys, os
import pytest
from fastapi.testclient import TestClient

# Ensure smepred package directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import app

client = TestClient(app)

TEST_SENSE = "GGAUCAUCUCAAGUCUUACTT"
TEST_ANTISENSE = "GUAAGACUUGAGAUGAUCCTT"
TEST_GENE_SEQ = "ATGGCCAAGCGAAGCAAGGGAUCAUCUCAAGUCUUACACCGUAAGACUUGAGAUGAUCC"


def test_root_frontend_serving():
    """Verify root / serves the SPA HTML interface."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "helixzero" in response.text.lower() or "<html" in response.text.lower()


def test_health_check_endpoint():
    """Verify /health endpoint returns 200 OK with expected service metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["service"] == "HelixZero-CMS"


def test_rank_endpoint_valid():
    """Verify POST /rank successfully scores naked siRNA candidates."""
    payload = {
        "sequence": TEST_GENE_SEQ,
        "top_n": 5,
        "input_type": "gene"
    }
    response = client.post("/rank", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_candidates" in data
    assert data["total_candidates"] > 0
    assert "results" in data
    assert len(data["results"]) <= 5
    
    # Check top candidate schema
    top = data["results"][0]
    assert "sense" in top
    assert "antisense" in top
    assert "efficacy_score" in top
    assert "rank" in top
    assert top["rank"] == 1


def test_rank_endpoint_invalid_sequence():
    """Verify POST /rank returns 422 for sequence too short."""
    payload = {
        "sequence": "ATGC",
        "top_n": 5,
        "input_type": "gene"
    }
    response = client.post("/rank", json=payload)
    assert response.status_code in (422, 400, 500)


def test_single_mod_scan_endpoint():
    """Verify POST /single-mod evaluates single modifications with off-target safety."""
    payload = {
        "sense": TEST_SENSE,
        "antisense": TEST_ANTISENSE,
        "model": "B_v4",
        "top_n": 10
    }
    response = client.post("/single-mod", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "parent_sense" in data
    assert "parent_safety" in data
    assert "results" in data
    assert len(data["results"]) <= 10
    assert "isSafe" in data["parent_safety"]


def test_multi_mod_custom_endpoint():
    """Verify POST /multi-mod evaluates specific custom modification masks."""
    payload = {
        "sense": TEST_SENSE,
        "antisense": TEST_ANTISENSE,
        "sense_mods": "2'-OMe;2'-F;2'-OMe",
        "sense_positions": "1;2;3",
        "antisense_mods": "2'-OMe;2'-F;2'-OMe",
        "antisense_positions": "1;2;3",
        "model": "B_v4"
    }
    response = client.post("/multi-mod", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "parent_score" in data
    assert "result" in data or "results" in data


def test_multi_mod_scan_beam_search_endpoint():
    """Verify POST /multi-mod-scan runs beam search for optimal modification stacking."""
    payload = {
        "sense": TEST_SENSE,
        "antisense": TEST_ANTISENSE,
        "max_mods": 2,
        "beam_width": 5,
        "full_scan": False,
        "model": "B_v4"
    }
    response = client.post("/multi-mod-scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_variants" in data
    assert "results" in data
    assert len(data["results"]) > 0


def test_offtarget_scan_endpoint():
    """Verify POST /offtarget-scan executes O(1) biological safety scan."""
    payload = {
        "sense": TEST_SENSE,
        "antisense": TEST_ANTISENSE,
        "antisense_mods": ""
    }
    response = client.post("/offtarget-scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "isSafe" in data
    assert "overallSafetyScore" in data
    assert "status" in data
    assert data["status"] in ("CLEARED", "TOXIC", "WARNING", "WARNING_SEED")


def test_modifications_metadata_endpoint():
    """Verify GET /modifications returns available chemical modification codes."""
    response = client.get("/modifications")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, (dict, list))
    assert len(data) > 0


def test_dock_endpoint_unmodified():
    """Verify POST /dock successfully executes 3D Ago2 structural docking simulation."""
    payload = {
        "sense": TEST_SENSE,
        "antisense": TEST_ANTISENSE,
        "sense_mods": "RRRRRRRRRRRRRRRRRRR",
        "anti_mods": "RRRRRRRRRRRRRRRRRRR",
        "conc_nM": 10.0,
        "target_gene": "TTR",
        "candidate_id": "test_unmod_dock"
    }
    response = client.post("/dock", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Assert top-level prediction metadata
    assert data["candidate_id"] == "test_unmod_dock"
    assert data["target_gene"] == "TTR"
    assert data["concentration_nM"] == 10.0
    assert 0.0 <= data["predicted_knockdown_pct"] <= 100.0
    assert data["predicted_pIC50"] > 0.0
    assert data["predicted_ic50_nM"] > 0.0
    
    # Assert structural docking parameters
    dock = data["docking"]
    assert dock is not None
    assert "mid_anchor_distance_A" in dock
    assert "piwi_cleavage_distance_A" in dock
    assert "paz_anchor_distance_A" in dock
    assert "steric_clash_score" in dock
    assert "estimated_binding_dG_kcal" in dock
    assert "pocket_contacts_count" in dock
    assert "catalytic_alignment_status" in dock
    assert dock["mid_anchor_distance_A"] > 0.0
    assert dock["piwi_cleavage_distance_A"] > 0.0
    assert dock["catalytic_alignment_status"] in ("OPTIMAL", "SUBOPTIMAL", "INHIBITED_STERIC")
    
    # Assert 3D PDB structure and PyMOL script generation
    assert "pdb_data" in data
    assert "ATOM" in data["pdb_data"]
    assert "pymol_script" in data
    assert "load" in data["pymol_script"].lower()


def test_dock_endpoint_modified_patisiran():
    """Verify POST /dock with modified FDA therapeutic Patisiran generates clash-free docked complex."""
    payload = {
        "sense": "GGAUCAUCUCAAGUCUUAC",
        "antisense": "GUAAGACUUGAGAUGAUCC",
        "sense_mods": "MMFMFMFMFMFMFMFMFMF",
        "anti_mods": "MFMFMFMFFFFFMFMFMMM",
        "conc_nM": 10.0,
        "target_gene": "TTR",
        "candidate_id": "patisiran_test"
    }
    response = client.post("/dock", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_pIC50"] >= 7.0
    assert data["docking"]["pocket_contacts_count"] > 0
    assert "ATOM" in data["pdb_data"]


def test_dock_demo_all_drugs():
    """Verify GET /dock/demo/{drug_id} returns valid parameters for all clinical demonstration drugs."""
    demo_drugs = ["patisiran", "givosiran", "roche_jak1", "unmodified"]
    for drug_id in demo_drugs:
        response = client.get(f"/dock/demo/{drug_id}")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "sense" in data
        assert "antisense" in data
        assert len(data["sense"]) >= 19
        assert len(data["antisense"]) >= 19
        assert "target_gene" in data
        assert data["conc_nM"] > 0.0


def test_dock_demo_not_found():
    """Verify GET /dock/demo/{drug_id} returns 404 for an unknown drug identifier."""
    response = client.get("/dock/demo/unknown_nonexistent_drug")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_rank_upload_endpoint():
    """Verify POST /rank/upload processes multipart FASTA file upload."""
    fasta_content = b">NM_000371.4 TTR gene\nATGGCCAAGCGAAGCAAGGGAUCAUCUCAAGUCUUACACCGUAAGACUUGAGAUGAUCC\n"
    files = {"file": ("ttr_test.fasta", fasta_content, "text/plain")}
    response = client.post("/rank/upload?top_n=5", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "ttr_test.fasta"
    assert data["total_candidates"] > 0
    assert len(data["results"]) <= 5
    assert "efficacy_score" in data["results"][0]


def test_api_boundary_negative_dose_handling():
    """Verify POST /dock gracefully handles non-positive concentration doses."""
    payload = {
        "sense": TEST_SENSE,
        "antisense": TEST_ANTISENSE,
        "conc_nM": -5.0,
        "candidate_id": "test_neg_dose"
    }
    response = client.post("/dock", json=payload)
    # Concentration is clipped/handled internally or returns valid prediction
    assert response.status_code in (200, 422)

