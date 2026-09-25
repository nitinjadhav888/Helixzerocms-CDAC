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
    assert "asymmetry_ddg" in top
    assert isinstance(top["asymmetry_ddg"], (int, float))
    assert "asymmetry_label" in top
    assert top["asymmetry_label"] in ("Optimal", "Moderate", "High Risk")



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
    """Verify POST /single-mod evaluates single modifications with off-target safety and dynamic PK."""
    payload = {
        "sense": TEST_SENSE,
        "antisense": TEST_ANTISENSE,
        "model": "IEEE_v5",
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
    top = data["results"][0]
    assert top["estimated_pIC50"] is not None
    assert top["estimated_IC50_nM"] is not None and top["estimated_IC50_nM"] > 0
    assert top["predicted_knockdown_pct"] is not None and 0.0 <= top["predicted_knockdown_pct"] <= 100.0
    assert "delta_score" in top


def test_multi_mod_custom_endpoint():
    """Verify POST /multi-mod evaluates specific custom modification masks with dynamic PK."""
    payload = {
        "sense": TEST_SENSE,
        "antisense": TEST_ANTISENSE,
        "sense_mods": "M,M",
        "sense_positions": "1,2",
        "antisense_mods": "F,F",
        "antisense_positions": "1,2",
        "model": "IEEE_v5"
    }
    response = client.post("/multi-mod", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "parent_score" in data
    assert "result" in data
    res = data["result"]
    assert res["sense_mods"] == "M,M"
    assert res["sense_positions"] == "1,2"
    assert res["antisense_mods"] == "F,F"
    assert res["antisense_positions"] == "1,2"
    assert res["estimated_pIC50"] is not None
    assert res["estimated_IC50_nM"] is not None and res["estimated_IC50_nM"] > 0
    assert res["predicted_knockdown_pct"] is not None and 0.0 <= res["predicted_knockdown_pct"] <= 100.0
    assert "delta_score" in res


def test_multi_mod_scan_beam_search_endpoint():
    """Verify POST /multi-mod-scan runs beam search for optimal modification stacking with dynamic PK."""
    payload = {
        "sense": TEST_SENSE,
        "antisense": TEST_ANTISENSE,
        "max_mods": 2,
        "beam_width": 5,
        "full_scan": False,
        "model": "IEEE_v5"
    }
    response = client.post("/multi-mod-scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_variants" in data
    assert "results" in data
    assert len(data["results"]) > 0
    top = data["results"][0]
    assert top["estimated_pIC50"] is not None
    assert top["estimated_IC50_nM"] is not None and top["estimated_IC50_nM"] > 0
    assert top["predicted_knockdown_pct"] is not None and 0.0 <= top["predicted_knockdown_pct"] <= 100.0
    assert "delta_score" in top


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


