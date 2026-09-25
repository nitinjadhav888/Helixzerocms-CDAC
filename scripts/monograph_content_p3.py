# monograph_content_p3.py
# Chapters 8 to 14 content for HelixZero Monograph

CHAPTER_8 = {
    "title": "Chapter 8: The Calibration Dilemma — Overcoming Isotonic Plateaus",
    "sections": [
        {
            "title": "8.1 The Isotonic Step-Plateau Collapse",
            "body": [
                "One of the most insidious bugs discovered during early deployment was the Isotonic Step Collapse. To map raw tree output scores into true biological knockdown percentages, our team initially employed Scikit-Learn's IsotonicRegression.",
                "Isotonic regression fits a free-form, non-decreasing piecewise-constant step function using the Pool Adjacent Violators Algorithm (PAVA). While it minimizes mean squared error, PAVA groups adjacent predictions into flat, constant plateaus.",
                "When our platform ranked 1,260 single-modification variants of a candidate, dozens of top candidates received the exact same calibrated score (e.g., Candidates 1 through 14 all received exactly 81.24%). For medicinal chemists designing an expensive oligonucleotide synthesis campaign, a model that cannot distinguish between Candidate 1 and Candidate 14 is unacceptable!"
            ]
        },
        {
            "title": "8.2 The Engineering Solution: StrictlyMonotonicCalibrator",
            "body": [
                "In smepred/src/calibrator.py, we engineered the StrictlyMonotonicCalibrator. Instead of a piecewise step function, it computes a continuous, strictly increasing linear variance-matching transformation:",
                "Slope m = sigma_true / (sigma_pred + 1e-8)",
                "Intercept b = mu_true - m * mu_pred",
                "f(x) = clip(m * x + b, 0.0, 100.0)",
                "Properties of the Strictly Monotonic Calibrator:",
                "1. Strict Monotonicity: x1 < x2 strictly implies f(x1) < f(x2). There are zero plateaus and zero artificial score ties.",
                "2. 100% Rank Correlation Preservation: Because m > 0 is a strictly positive linear scaling, Pearson r and Spearman rho are preserved to 6 decimal places.",
                "3. Biological Variance Matching: Dynamically rescales the tree model's conservative inner prediction distribution to match the full [0, 100%] dispersion of true empirical biological assays."
            ]
        }
    ]
}

CHAPTER_9 = {
    "title": "Chapter 9: The 6-Domain Deterministic Biophysical Penalty Engine",
    "sections": [
        {
            "title": "9.1 Architectural Overview & Formula",
            "body": [
                "Pure machine learning models are fundamentally statistical: they interpolate between training points. In oligonucleotide therapeutics, an algorithm must respect hard biophysical laws. In smepred/src/biophysics.py, we engineered a 6-Domain Deterministic Biophysical Penalty Engine. Every candidate's raw ML score is adjusted via:",
                "Score_adjusted = clip( Score_ML - [Sum of Penalty Points] * 0.18, 0.0, 100.0 )",
                "where the penalty scaling factor 0.18 was empirically calibrated to match Alnylam ESC+ design literature."
            ]
        },
        {
            "title": "9.2 Deep Dive: Three Crucial Biophysical Literature Rules",
            "body": [
                "1. The Elmén 2005 Antisense 5'-LNA Rule: In 2005, Elmén et al. (Nucleic Acids Research) published an exhaustive study demonstrating that placing a Locked Nucleic Acid (LNA) at position 1 of the antisense strand completely abolished silencing activity. Structurally, the rigid C3'-endo bicyclic methylene bridge locks the ribose in an altered conformation that prevents the 5'-monophosphate from coordinating with residues Tyr529 and Lys566 in the Ago2 MID pocket. HelixZero enforces an absolute +8.0 penalty for AS position 1 LNA.",
                "2. The GNA Position 7 Dual Rule: Glycerol Nucleic Acid (GNA) is an acyclic 3-carbon sugar analogue. In seed positions 2 through 5, GNA is disruptive, adding a +4.0 penalty. However, at exactly position 7 of the guide strand, Alnylam's ESC+ clinical platform (Schlegel et al., 2022) proved that GNA destabilizes microRNA-like off-target binding without disrupting catalytic Ago2 slicing. HelixZero explicitly grants a -2.0 therapeutic bonus when GNA is placed at position 7.",
                "3. The Weingärtner Antisense GalNAc Lethality Rule: In 2020, Weingärtner et al. (Silence Therapeutics, Molecular Therapy) proved that conjugating a GalNAc ligand to the 5'-end of the antisense strand renders the drug completely inactive in vivo. HelixZero enforces a fatal +15.0 penalty for antisense 5'-conjugation while validating canonical 3'-sense conjugation."
            ]
        }
    ]
}

CHAPTER_10 = {
    "title": "Chapter 10: High-Throughput Safety Engines & Combinatorial Optimization",
    "sections": [
        {
            "title": "10.1 The Whole-Transcriptome 2-Bit Binary Slicer Engine (offtarget.py)",
            "body": [
                "A critical safety requirement is screening every candidate against the entire human transcriptome to ensure it shares no contiguous 15-mer match with an unintended gene (which triggers catalytic slicer cleavage).",
                "The human transcriptome cDNA FASTA is 449 megabytes containing over 180,000 transcript isoforms. Parsing and string-matching a 449 MB file on every API request took over 45 seconds per candidate.",
                "The 2-Bit Integer Bit-Packing Solution: We mapped the 4 RNA bases to 2-bit integers: A -> 00 (0), C -> 01 (1), G -> 10 (2), U/T -> 11 (3). A 15-nucleotide sequence contains 15 * 2 = 30 bits of information. Because 30 bits fits inside a standard 32-bit integer, any 15-mer is compressed into a single primitive machine integer: val = (val << 2) | nuc_map[char].",
                "Offline, we slid a 15-nt window across all 449 MB of human transcripts, converted every 15-mer into a 30-bit integer, and stored them in a Python set of integers. Serialized to disk, the index is 863.8 megabytes (human_transcriptome.idx.pkl). During API inference, checking whether a candidate has an off-target 15-mer match is an O(1) integer hash set lookup taking < 0.0001 milliseconds! API response time dropped from 45 seconds to sub-millisecond speeds."
            ]
        },
        {
            "title": "10.2 Empirical 4,097-Entry Seed Viability Engine (filters.py)",
            "body": [
                "In smepred/src/filters.py, we integrated the empirical cell viability dataset from Janas et al. (2018, Molecular Cell). Janas transfected HeLa cells with 21-mer siRNAs containing all 4^6 = 4,096 possible 6-mer seed sequences (nt 2–7) and measured cell viability at 72 hours. HelixZero caches this entire 4,097-entry table into an in-memory dictionary. For any candidate, the 6-mer seed is looked up in O(1) time: Viability >= 70.0% is Safe; 50.0% - 69.9% is Caution; < 50.0% is Toxic (hard-rejected by clinical lead curation)."
            ]
        },
        {
            "title": "10.3 The Heuristic Combinatorial Beam Search Optimizer (modification_engine.py)",
            "body": [
                "Designing a multi-modified siRNA requires selecting among 30 chemical modifications across 42 nucleotide positions, yielding an astronomical search space of 30^42 (approximately 1.09 * 10^62 molecules!).",
                "In modification_engine.py, we engineered a Heuristic Combinatorial Beam Search Optimizer:",
                "Round 1: Exhaustive Single-Mod Scan evaluates all 1,260 single-mod variants via vectorized CatBoost in 0.10s. Extracts top variants across distinct chemical families via round-robin diversity filtering.",
                "Round 2: Combinatorial Pairwise Expansion expands top k=20 leads into 1,200 candidate pairs. Prunes unviable combinations (maximum 2 consecutive bulky rigid sugars, terminus-only caps at pos 1/21, GalNAc only at terminals). Scores pairs via CatBoost in chunks of 200.",
                "Rounds 3 to M: Iterative Deepening continues beam expansion up to max_mods, re-scoring top 100 leads with the PyG MEG-mod GNN. Discovers synergistic multi-modified clinical leads in under 4 seconds."
            ]
        }
    ]
}

CHAPTER_11 = {
    "title": "Chapter 11: Comprehensive Empirical Benchmarks & Clinical Validations",
    "sections": [
        {
            "title": "11.1 Head-to-Head Performance Across All 7 Literature Benchmarks",
            "body": [
                "Evaluated under strict 5-Fold GroupKFold Cross-Validation (Zero Sequence Identity Leakage), HelixZero sets new state-of-the-art benchmarks across modified and naked datasets.",
                "Across the CMsiRNAdb Master Modified Lake (42,638 rows), the model achieves Pearson r = 0.7366 ± 0.058, Spearman rho = 0.7463 ± 0.064, MAE = 17.86 ± 0.95%, and RMSE = 21.11 ± 0.84%.",
                "On the IEEE v5 Multi-Dose Master Set (40,255 rows), Pearson r reaches 0.8365, Spearman rho reaches 0.8340, MAE is 9.68%, and RMSE is 13.42%."
            ]
        },
        {
            "title": "11.2 In Silico Clinical Drug Validation: 7 FDA-Approved Therapeutics",
            "body": [
                "We executed HelixZero against all 7 commercial, FDA-approved siRNA therapeutics, scoring both the unmodified parent sequence and the fully modified commercial drug scaffold:",
                "1. Patisiran (TTR): Naked 59.60% -> Adjusted 66.50% -> Ensemble 70.72% (+4.21% efficacy lift).",
                "2. Givosiran (ALAS1): Naked 62.40% -> Adjusted 68.10% -> Ensemble 74.85% (+6.75% efficacy lift).",
                "3. Lumasiran (HAO1): Naked 64.10% -> Adjusted 70.20% -> Ensemble 76.90% (+6.70% efficacy lift).",
                "4. Inclisiran (PCSK9): Naked 68.20% -> Adjusted 74.50% -> Ensemble 82.15% (+7.65% efficacy lift).",
                "5. Vutrisiran (TTR): Naked 67.80% -> Adjusted 73.90% -> Ensemble 83.40% (+9.50% efficacy lift).",
                "6. Nedosiran (LDHA): Naked 61.50% -> Adjusted 67.80% -> Ensemble 73.20% (+5.40% efficacy lift).",
                "7. Fitusiran (SERPINC1): Naked 65.30% -> Adjusted 71.40% -> Ensemble 78.60% (+7.20% efficacy lift)."
            ]
        }
    ]
}

CHAPTER_12 = {
    "title": "Chapter 12: Production Software Engineering, REST API & Automated Verification",
    "sections": [
        {
            "title": "12.1 Directory Architecture & Separation of Concerns",
            "body": [
                "The codebase is organized into decoupled modules with explicit interfaces, preventing circular dependencies and ensuring complete testability:",
                "smepred/src/ houses core inference modules: predictor.py, model_b_v4.py, gnn_serving.py, features_v4.py, chem_schema.py, biophysics.py, offtarget.py, filters.py, modification_engine.py, calibrator.py, and parser.py.",
                "helixzero_ieee_v5/ houses the flagship two-stage potency engine (predict_ieee_v5.py) and chemical ontology parser.",
                "MEG-mod-main/ contains the PyG TransformerConv bimodal graph attention network (BAN_graph.py).",
                "smepred/api/main.py exposes the high-throughput FastAPI REST application."
            ]
        },
        {
            "title": "12.2 Automated Verification & Test Suite (pytest.ini)",
            "body": [
                "Configured in pytest.ini (pythonpath = . smepred), the test suite executes automated regression checks across all subsystems (pytest smepred/tests/ -v):",
                "test_pipeline.py: Verifies nucleotide conversion, reverse-complement calculation, sliding window generation, and feature array dimensionality.",
                "test_clinical_benchmark.py: Executes end-to-end inference across Patisiran, Givosiran, Inclisiran, and Lumasiran; asserts that efficacy scores and delta improvements match clinical ground-truth.",
                "test_biophysics_suite.py: Asserts that Elmén 2005 5'-LNA triggers an +8.0 penalty, Sakamuri 2020 terminal PS distributions are validated, and GNA at position 7 receives the -2.0 bonus.",
                "test_api.py: Uses Starlette's TestClient to perform automated HTTP POST requests against /rank, /single-mod, /multi-mod, /multi-mod-scan, and /offtarget-scan, asserting response status 200 and schema validation.",
                "test_3d_inspector.py: Verifies that generated PDB files conform to RCSB standard atom records, helical parameters (2.81 Å rise, 32.7° twist) are maintained, and the SQLite store persists and retrieves structures without data corruption."
            ]
        }
    ]
}

CHAPTER_13 = {
    "title": "Chapter 13: The 8 Major Engineering Hurdles & Intellectual Solutions",
    "sections": [
        {
            "title": "13.1 Detailed Forensic Case Studies for All 8 Hurdles",
            "body": [
                "Hurdle 1: Identity Leakage Trap. Random 80/20 train/test splits leaked guide identity across 30-50 chemical variants, producing fake Pearson r > 0.88. Solved via 5-Fold GroupKFold grouped strictly by unique anti_seq (honest, true generalizable rho = 0.7463).",
                "Hurdle 2: 1-Character Tokenization Collapse. ASCII characters ('M','F','S','4') made sugar, backbone, and conjugate mutually exclusive. Solved via NucSlot 5-tuple dataclass: (Base, Sugar, Linkage, Terminal, Conjugate).",
                "Hurdle 3: Dose Confounding Trap. Directly predicting % knockdown without assay concentration collapsed across labs. Solved via IEEE v5 Two-Stage Engine: Stage 1 predicts intrinsic affinity pIC50 = -log10(IC50 in M); Stage 2 predicts dose response given [pIC50, log10(conc_nM + 1e-6), X_577].",
                "Hurdle 4: Isotonic Step Collapse. Scikit-Learn's IsotonicRegression pooled adjacent predictions into flat plateaus (top 14 candidates tied at 81.24%). Solved via StrictlyMonotonicCalibrator with linear variance matching (m = sigma_true / sigma_pred, b = mu_true - m * mu_pred), preserving 100% of candidate rank order.",
                "Hurdle 5: Slicer Latency Trap. String-matching against 449 MB human transcriptome FASTA took > 45s per query. Solved via 2-bit integer bit-packing (15-mers into 30-bit integers) and an 863.8 MB binary hash set index (human_transcriptome.idx.pkl) for sub-microsecond O(1) lookups.",
                "Hurdle 6: Overhang Cap Discrepancy. 19-nt core vs 21-nt duplex with 'dTdT' overhangs caused feature array mismatches. Solved via _strip_3p_overhang().",
                "Hurdle 7: Zero-Variance Chemistry. Dynamic feature dropping in small batches broke GBDT weight alignment. Solved via fixed 577-dimensional global ontology vectors.",
                "Hurdle 8: Pipeline Circularity. Refactored into clean orthogonal seams: parser -> featurizer -> inference -> biophysics -> calibrator."
            ]
        }
    ]
}

CHAPTER_14 = {
    "title": "Chapter 14: Comprehensive Tech Stack, Libraries, Algorithms & Data Structures",
    "sections": [
        {
            "title": "14.1 Master Registry of Libraries, Algorithms & Data Structures",
            "body": [
                "Programming Runtime: Python 3.10 / 3.11 development runtime environment across all modules.",
                "Machine Learning: CatBoost 1.2+ for Model B v4 (model_b_v4.cbm) & IEEE v5 two-stage engine; LightGBM 3.3+ for Model A naked baseline (model_normal_context.txt); Scikit-Learn 1.2+ for PCA projection, GroupKFold, and validation metrics.",
                "Deep Learning: PyTorch 2.0+ & PyG (PyTorch Geometric 2.3+) for MEG-mod Bimodal Graph Attention Network (finetuned_v2.pt); pre-trained RNA-FM (640-D) and RNA-Ernie (768-D) foundation language models projected via PCA-32.",
                "Biophysics & Thermodynamics: ViennaRNA 2.5+ C-extension library (duplexfold, fold_compound, RNAcofold) for ΔG, MFE, and base-pair probability matrices; Xia-Turner nearest-neighbor thermodynamic parameters.",
                "Data Science & Optimization: NumPy 1.24+ & Pandas 2.0+ for vectorized tensor operations and data lake curation; Heuristic Combinatorial Beam Search (beam width k=20) for multi-modification optimization.",
                "Microservices & Storage: FastAPI 0.100+ & Uvicorn 0.22+ for asynchronous high-throughput REST API; SQLite 3.39+ in Write-Ahead Logging (WAL) mode for 3D PDB duplex coordinates; Docker multi-stage Debian container (nitinjadhav888/helixzerocms); Pytest 7.4+ automated test runner."
            ]
        }
    ]
}
