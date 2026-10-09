# 18. API & BACKEND MICROSERVICE ARCHITECTURE
## FastAPI Specification, Pydantic Schemas, and Endpoint Reference
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  
**Primary Source File:** `smepred/api/main.py`  

---

### 1. Microservice Specification & Startup Flow

The backend microservice is implemented in **FastAPI** (`v2.1.0`) running on **Uvicorn**:
- **Host / Port:** Default `0.0.0.0:8000`.
- **CORS Configuration:** Fully permissive middleware (`allow_origins=["*"]`) enabling seamless decoupled frontend interaction.
- **Startup Warm-up (`@app.on_event("startup")`):** Pre-warms `model_normal.txt` (Model A) and `unified_dose_catboost.cbm` (Model B) into system memory during server initialization in $< 0.5$ s, preventing cold-start latency spikes for user requests.
- **Lazy Index Loading:** The 863.8 MB human transcriptome binary index (`human_transcriptome.idx.pkl`) is loaded into memory on the first call to `/offtarget-scan`.

---

### 2. Complete Endpoint Reference

#### 2.1 `POST /rank` — Unmodified siRNA Scanning
- **Description:** Ingests raw target gene sequence, generates all candidate 21-mers, annotates biological transcript domains (5' UTR, CDS, 3' UTR), and scores sequences with Model A LightGBM.
- **Request Schema (`RankRequest`):**
  ```json
  {
    "sequence": "AUGUUGUCCUUUUUAUCUGAA...",
    "top_n": 20,
    "input_type": "gene",
    "conc_nM": 10.0
  }
  ```
- **Response Schema:**
  ```json
  {
    "total_candidates": 352,
    "input_type": "gene",
    "curated_leads": [ ... ],
    "results": [
      {
        "rank": 1,
        "position": 142,
        "sense": "CUACGAGACUGAUGACUAUTT",
        "antisense": "AUAGUCAUCAGUCUCGUAGTT",
        "efficacy_score": 84.25,
        "efficacy_label": "Very High",
        "toxicity_score": 88.5,
        "toxicity_label": "Low Risk",
        "func_ok": true,
        "domain": "CDS",
        "is_curated_lead": true,
        "asymmetry_ddg": 1.45
      }
    ]
  }
  ```

#### 2.2 `POST /single-mod` — Exhaustive Single-Modification Permutation Scanner
- **Description:** Systematically evaluates all 812 single-nucleotide chemical substitutions across both strands of a parent siRNA candidate.
- **Request Schema (`SingleModRequest`):**
  ```json
  {
    "sense": "CUACGAGACUGAUGACUAUTT",
    "antisense": "AUAGUCAUCAGUCUCGUAGTT",
    "model": "Unified_v5",
    "top_n": 50,
    "full_scan": true,
    "conc_nM": 10.0
  }
  ```

#### 2.3 `POST /multi-mod` — Custom Multi-Modification Evaluation
- **Description:** Evaluates a specific, user-defined combinatorial modification pattern.
- **Request Schema (`MultiModRequest`):**
  ```json
  {
    "sense": "CUACGAGACUGAUGACUAUTT",
    "antisense": "AUAGUCAUCAGUCUCGUAGTT",
    "sense_mods": "S,S,F,M,F,M,M,F",
    "sense_positions": "1,2,3,6,8,10,12,14",
    "antisense_mods": "S,S,F,F,F,F",
    "antisense_positions": "1,2,2,4,6,8",
    "model": "Unified_v5",
    "conc_nM": 10.0
  }
  ```
- **Response Fields:** Includes `efficacy_score`, `raw_efficacy_score`, `estimated_pIC50`, `estimated_IC50_nM`, `confidence_interval`, `penalties`, and `structural_properties`.

#### 2.4 `POST /multi-mod-scan` — Autonomous Combinatorial Beam Search
- **Description:** Launches a heuristic beam search ($W = 20$, depth 21) optimizing synergistic modifications and evaluating real-time biophysical guardrails.
- **Request Schema (`MultiModScanRequest`):**
  ```json
  {
    "sense": "CUACGAGACUGAUGACUAUTT",
    "antisense": "AUAGUCAUCAGUCUCGUAGTT",
    "max_mods": 21,
    "beam_width": 20,
    "fda_core_only": true,
    "conc_nM": 10.0
  }
  ```

#### 2.5 `POST /offtarget-scan` — Transcriptome-Wide Safety Firewall
- **Description:** Queries the 2-bit packed human transcriptome index to detect contiguous 15-mer slicer matches and seed match frequencies.
- **Request Schema (`OffTargetRequest`):**
  ```json
  {
    "sense": "CUACGAGACUGAUGACUAUTT",
    "antisense": "AUAGUCAUCAGUCUCGUAGTT",
    "antisense_mods": "S,S,M,F,M,F"
  }
  ```

#### 2.6 `GET /modifications` — Chemical Nomenclature Catalog
- **Description:** Emits the complete standardized JSON catalog of all 30 supported chemical modifications, chemical categories, and descriptions.

#### 2.7 `GET /health` — Liveness & Readiness Probe
- **Response:** `{"status": "ok", "version": "2.1.0", "service": "HelixZero-CMS"}`
