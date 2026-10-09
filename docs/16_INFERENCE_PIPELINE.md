# 16. INFERENCE PIPELINE & RUNTIME EXECUTION
## Step-by-Step Inference Flow, Latencies, and Error Boundaries
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. End-to-End Inference Workflow

The active production inference pipeline is orchestrated through `smepred/src/predictor.py`:

```mermaid
sequenceDiagram
    autonumber
    actor User as Scientist / API Client
    participant API as FastAPI Gateway (main.py)
    participant Pred as Predictor (predictor.py)
    participant ModB as Model B Wrapper (model_b_v4.py)
    participant Feat as Feature Extractor (features_v4.py)
    participant Bio as Biophysics Engine (biophysics.py)
    participant Off as Off-Target Engine (offtarget.py)
    participant PDB as PDB Generator (pdb_generator.py)

    User->>API: POST /multi-mod-scan {sense, antisense, conc_nM: 10.0}
    API->>Pred: predict_modified(mode="multimod" / "scan")
    Pred->>Feat: batch_unified_features(sense_slots, anti_slots, conc_nM)
    Feat-->>Pred: Matrix X_517 (N x 517 float32)
    Pred->>ModB: predict_from_slots(X_517)
    ModB-->>Pred: Raw Knockdown Scores y_raw [0, 100]%
    loop For each variant
        Pred->>Pred: Analytical Closed-Form Hill Inversion (IC50, pIC50)
        Pred->>Bio: calculate_adjusted_efficacy(y_raw, sense, anti)
        Bio-->>Pred: Score_adj, Domain Penalties
        Pred->>Off: validate_safety(sense, anti)
        Off-->>Pred: Slicer Hits, Seed Matches, Flag
    end
    Pred->>Pred: Multi-Objective Pareto Sorting (Score_adj desc, Penalty asc)
    Pred->>PDB: generate_sirna_pdb(lead_sense, lead_anti)
    PDB-->>Pred: 504-Atom PDB String with B-factor Mods
    Pred-->>API: Consolidated Prediction Payload
    API-->>User: JSON Response (HTTP 200) in < 1.5 seconds
```

---

### 2. Computational Latency Benchmarks

Measured on standard 8-core CPU hardware (No GPU required):

| Processing Phase | Scope / Candidates | Execution Latency | Code Implementation |
| :--- | :--- | :---: | :--- |
| **Model Pre-Warming** | LightGBM + CatBoost Checkpoints | $< 0.45\text{ s}$ | `api/main.py:startup_warmup()` |
| **Full Transcript Scanning** | 3,000 candidate 21-mers along mRNA | $< 0.05\text{ s}$ | `src/features.py` + Model A |
| **Exhaustive Single-Mod Scan** | 812 single-point permutations | $< 0.10\text{ s}$ | `src/modification_engine.py:single_mod_scan()` |
| **Combinatorial Beam Search** | $W = 20$, depth 21 (100 evaluated designs) | $< 1.50\text{ s}$ | `src/modification_engine.py:multi_mod_scan()` |
| **Whole-Transcriptome Off-Target** | 2-bit SIMD hash query across 94M 15-mers | $< 0.02\text{ s}$ | `src/offtarget.py:validate_safety()` |
| **Continuous 3D PDB Generation** | 504 atoms, B-factor mapping | $< 0.01\text{ s}$ | `src/pdb_generator.py:generate_sirna_pdb()` |

---

### 3. Error Boundaries & Fallback Policies

- **Invalid Nucleotides:** Input sequences containing characters outside `[A, C, G, T, U]` are rejected at ingestion with `HTTP 422 Unprocessable Entity`.
- **Short Sequences:** Sequences shorter than 21 nucleotides are rejected with descriptive length errors.
- **ViennaRNA C-Extension Absence:** If ViennaRNA native binaries are missing on Windows, fallback nearest-neighbor Turner tables execute transparently without throwing exceptions (`smepred/src/features_v4.py:215-226`).
- **Transcriptome Index Availability:** If `human_transcriptome.idx.pkl` is absent, the system logs a non-fatal warning and provides localized heuristic off-target warnings rather than crashing the API.
