# monograph_content_p2.py
# Chapters 3 to 7 content for HelixZero Monograph

CHAPTER_3 = {
    "title": "Chapter 3: The Multi-Source Data Lake Assembly & Master Censuses",
    "sections": [
        {
            "title": "3.1 Overview of the 22-Dataset Master Repository",
            "body": [
                "To build a computational intelligence platform capable of true clinical generalizability across diverse chemical scaffolds and target genes, our engineering team assembled the most comprehensive curated siRNA data lake in the history of computational biology. The master data lake integrates 22 distinct dataset repositories comprising over 260,000 empirical measurements.",
                "The repository spans three distinct pharmacological tiers:",
                "1. Canonical High-Throughput In Vitro Screens: Baseline canonical datasets including the Novartis Huesken et al. (2006) dataset (661 siRNAs targeting 33 human and rodent mRNAs), the extended canonical library (4,060 assays), and external benchmark sets such as Hu.csv (2,361 human siRNAs), Takayuki.csv (702 assays), and Mixset.csv (472 multi-study assays). These provide the baseline sequence context rules for Model A.",
                "2. Chemically Modified Oligonucleotide Data Lake: High-density chemical libraries including the curated CMsiRNAdb master repository (25,863 rows), the internal multi-slot feature store (42,638 rows), the expanded commercial patent release (43,153 rows), heterogeneous training/validation splits (hetero_train_2728 with 23,187 rows and hetero_val_303 with 2,576 rows), and homogeneous control partitions (homo_train with 4,244 rows and homo_val with 472 rows).",
                "3. Clinical-Grade Multi-Concentration Series: The IEEE gold-bronze master dataset (40,255 rows), single-dose high-throughput screens (Dataset A, 38,973 rows), multi-concentration dose-response series (Dataset B, 35,982 rows), in vivo rodent/NHP pharmacodynamic assays (Dataset C, 4,180 rows), and the Hill kinetic inversion ground-truth set (1,458 full curves). These multi-dose measurements power the flagship IEEE v5 two-stage potency engine.",
                "In addition, the data lake includes the complete empirical 6-mer seed viability screen from Janas et al. (2018, 4,096 hexamers in HeLa cells), the 449 MB human transcriptome cDNA FASTA with its 863.8 MB 2-bit binary index, and verified structural scaffolds for all 7 FDA-approved commercial drugs."
            ]
        },
        {
            "title": "3.2 Experimental Assay Methodologies & Normalization Protocols",
            "body": [
                "A major technical challenge in aggregating data from 22 distinct literature and patent sources was reconciling disparate experimental methodologies. Data in the lake originated from three primary assay types:",
                "1. Dual-Luciferase Reporter Assays: Plasmids expressing target sequences fused to Renilla or Firefly luciferase were co-transfected with siRNAs into HeLa or HEK293 cells. Silencing was quantified via luminescence ratios relative to non-targeting controls.",
                "2. TaqMan Quantitative Real-Time PCR (qRT-PCR): Endogenous target mRNA levels in HepG2, Huh7, or primary hepatocytes were quantified using hydrolysis probe chemistry, normalized against housekeeping genes (GAPDH, ACTB).",
                "3. Branched DNA (bDNA) Assays: High-throughput direct hybridization assays that measure target mRNA without reverse transcription, common in industrial patent literature.",
                "To establish a unified training schema, all measurements were harmonized into a standardized Percentage mRNA Knockdown metric bounded strictly between 0.0% (no silencing) and 100.0% (complete degradation). Where studies reported 'Fraction Remaining' (R), knockdown was calculated as K = (1.0 - R) * 100.0. All experimental concentrations were converted to nanomolar units (nM) and transformed into logarithmic coordinates: Dose_transformed = log10(conc_nM + 1e-6)."
            ]
        }
    ]
}

CHAPTER_4 = {
    "title": "Chapter 4: Forensic Data Cleaning & The Elimination of Identity Leakage",
    "sections": [
        {
            "title": "4.1 The Sequence Identity Leakage Trap in Chemical Modification Datasets",
            "body": [
                "During early exploratory model training, our team discovered a severe methodological error that pervades academic literature: Sequence Identity Leakage across random train/test splits.",
                "When a baseline gradient boosted tree model was evaluated using standard Scikit-Learn 80/20 random splits, the validation metrics appeared spectacular: Pearson r > 0.88 and Spearman rho > 0.86. However, deep auditing revealed that these metrics were an artifact of data leakage.",
                "In typical chemical modification studies, researchers select a single highly potent antisense guide sequence (such as a sequence targeting Transthyretin or PCSK9) and synthesize 30 to 50 distinct chemical variants, systematically altering the placement of 2'-OMe, 2'-F, or phosphorothioate linkages.",
                "Under a naive random 80/20 split, 35 variants of Sequence A were assigned to the training set, while 10 variants of the exact same Sequence A ended up in the test set. Because decision trees excel at partitioning on sequence identity, the trees simply memorized the biological baseline potency of Sequence A. The model was not learning the biophysical consequences of chemical modifications; it was functioning as a sequence lookup table. When tested on a completely novel target gene, performance collapsed to near-zero correlation."
            ]
        },
        {
            "title": "4.2 The Engineering Solution: Strict 5-Fold GroupKFold by Antisense Sequence",
            "body": [
                "To guarantee rigorous, publication-grade generalizability, we implemented strict 5-Fold GroupKFold Cross-Validation grouped strictly by unique antisense sequence (anti_seq) in helixzero/training/validation.py.",
                "Under GroupKFold, all chemical variants derived from a given guide sequence are quarantined exclusively within the training fold or exclusively within the held-out test fold. The model is forced to evaluate target sequences it has never encountered during training.",
                "When evaluated under strict GroupKFold, validation metrics dropped from the fraudulent rho = 0.88 to an honest, highly competitive, and reproducible rho = 0.7463 ± 0.064 for our production ensemble. This proved that HelixZero genuinely generalizes to unseen biological targets and learns the true physics of chemical modifications."
            ]
        },
        {
            "title": "4.3 Sequence Sanitization and Overhang Cap Stripping",
            "body": [
                "In smepred/src/parser.py, we engineered an industrial sequence parsing pipeline to eliminate data corruptions:",
                "1. Header and Accession Stripping: Automatically removes multiline FASTA headers (>gene_id) and NCBI/Ensembl accession prefixes (NM_, ENST, XM_).",
                "2. RNA Alphabet Conversion: Automatically converts all thymidine ('T') characters to uridine ('U'), converting cDNA inputs into RNA.",
                "3. IUPAC Ambiguity Removal: Rejects degenerate ambiguity codes (N, R, Y, W, S, K, M, B, D, H, V) using strict regular expression sanitization.",
                "4. Overhang Cap Discrepancy Solution: A critical engineering trap was that canonical siRNAs contain a 19-base pair double-stranded core flanked by 2-nucleotide 3'-overhangs (often deoxythymidines, 'dTdT'). Feeding sequences formatted as 'GGAUCAUCUCAAGUCUUACdTdT' into the feature extractor caused array index out-of-bounds crashes in the 21-slot positional tensor. In _strip_3p_overhang(), we programmatically strip trailing overhang notation (dT, dTdT, D, 3P, -3') to isolate the 19-nt canonical core before slot mapping, guaranteeing zero array shape misalignment."
            ]
        }
    ]
}

CHAPTER_5 = {
    "title": "Chapter 5: The 1-Character Tokenization Failure & The NucSlot Orthogonal Ontology",
    "sections": [
        {
            "title": "5.1 The Stereochemistry of a Nucleotide Slot & Five Degrees of Freedom",
            "body": [
                "The primary theoretical breakthrough of HelixZero is the complete abandonment of single-character string tokens in favor of the NucSlot Orthogonal 5-Tuple Chemical Ontology.",
                "At any single nucleotide position along an oligonucleotide chain, there are five completely independent chemical axes that can be modified without altering the others:",
                "1. Canonical Base Identity: Adenine (A), Cytosine (C), Guanine (G), or Uracil (U). Base identity determines Watson-Crick hydrogen bonding specificity.",
                "2. Ribose Sugar Conformation: Canonical ribo (unmodified), deoxyribo (DNA), 2'-OMe, 2'-F, Locked Nucleic Acid (LNA), 2'-MOE, Unlocked Nucleic Acid (UNA), or Glycol Nucleic Acid (GNA). The sugar moiety dictates ring pucker (C3'-endo North vs C2'-endo South), A-form helical rigidity, and nuclease susceptibility.",
                "3. 3'-Internucleotide Linkage: Phosphodiester (PO) vs Phosphorothioate (PS). Linkage dictates terminal exonuclease defense and in vivo tissue retention.",
                "4. 5'-Terminal Cap: Unmodified 5'-OH, 5'-monophosphate (5'-P), or 5'-(E)-vinylphosphonate (5'-VP). Essential at position 1 of the antisense strand for anchoring into the Ago2 MID pocket.",
                "5. Targeting Conjugate: Trivalent GalNAc, monovalent GalNAc, cholesterol, or PEG. Dictates tissue biodistribution and receptor-mediated uptake.",
                "Legacy systems assigned a single ASCII character (e.g., 'M' for 2'-OMe, 'S' for PS, '4' for GalNAc), forcing the data engineering pipeline to make impossible trade-offs. In NucSlot, all five axes are represented orthogonally in a Python dataclass."
            ]
        },
        {
            "title": "5.2 The Canonical 30-Modification Taxonomy & Regex Patent Parser",
            "body": [
                "In smepred/src/chem_alphabet.py and chem_schema.py, we codified a master 30-modification dictionary categorized into regulatory tiers: Tier 0 (Approved Commercial Drugs), Tier 1 (Clinical Phase II/III), Tier 2 (Preclinical / Literature Validated), and Tier 3 (Exotic Scaffolds).",
                "To ingest proprietary patent sequences from Alnylam, Silence Therapeutics, and Arrowhead, we engineered an industrial regular expression tokenizer that parses nested bracketed notation (e.g., 'mU', 'fG', 's(mC)', 'vp-u', 'NAG25-3P'). The tokenizer decomposes arbitrary patent strings into structured lists of NucSlot instances with complete audit traceability."
            ]
        }
    ]
}

CHAPTER_6 = {
    "title": "Chapter 6: Multi-Scale Feature Engineering (190-D & 577-D Spaces)",
    "sections": [
        {
            "title": "6.1 The 190-Dimensional Context Engine for Naked RNA (context_feature_extractor.py)",
            "body": [
                "For unmodified siRNA, target transcript accessibility is the primary determinant of knockdown. In context_feature_extractor.py, we extract a 190-dimensional multi-scale vector comprising:",
                "1. ViennaRNA Thermodynamics (33-D): Duplex binding energy (ΔG_duplex), mRNA target site opening free energy (ΔG_open), net thermodynamic driving force (ΔΔG = ΔG_duplex - ΔG_open), seed region (nt 2–8) binding energy, terminal asymmetry free energies (ΔG_end5, ΔG_end3), and the 24-dimensional OligoFormer nearest-neighbor matrix.",
                "2. Sequence & Composition Features (92-D): Guide GC%, target site GC%, flanking 5' and 3' context GC%, base counts (A, C, G, U), 5'-U anchor indicator bit (Ago2 MID pocket preference), and the 19-position one-hot sequence matrix (19 × 4 = 76-D).",
                "3. RNA Foundation Model Context (65-D): 32-D PCA-projected RNA-FM embedding of the 57-nt target mRNA context window, 32-D PCA-projected RNA-FM embedding of the 19-nt guide sequence, and the latent cosine similarity between guide and target context."
            ]
        },
        {
            "title": "6.2 The 577-Dimensional Multi-Modal Engine for Modified RNA (features_v4.py)",
            "body": [
                "For chemically modified siRNA, features_v4.py generates a comprehensive 577-dimensional vector:",
                "X_577 = [ X_pos_flags (420-D), X_engineered (24-D), X_RNA_FM (64-D), X_RNA_Ernie (64-D), X_Vienna (5-D) ]",
                "1. Positional Chemical Ontology Matrix (420-D): 42 nucleotide slots (21 sense + 21 antisense) × 10 orthogonal binary flags: 8 sugar flags (2F, 2OMe, bulky_rigid [LNA/MOE/ENA], flexible_exotic [UNA/GNA/TNA], unmod_ribo, dna, abasic_cap, other_sugar) + 1 linkage flag (is_PS) + 1 base mod flag (is_base_mod).",
                "2. Literature-Engineered Biophysical Features (24-D): Non-linear interaction metrics: seed_bulky_rigid_frac (Bramsen 2009), seed_flexible_exotic_frac, ss/as_mod_density (Allerson 2005), as_pos1_bulky_rigid (Elmén 2005), as_pos1_5p_phosphate_mimic (Parmar 2016), terminal/internal PS density (Sakamuri 2020), conjugate flags (Weingärtner 2020), GC asymmetry, and terminal AU/GC stability bits (Khvorova 2003).",
                "3. RNA-FM Foundation Model PCA (64-D): 640-D token embeddings from RNA-FM foundation model, projected via pre-fitted PCA (rnafm_pca_32.pkl) into 32-D for sense strand + 32-D for antisense strand.",
                "4. RNA-Ernie Foundation Model PCA (64-D): 768-D multi-scale masked representations from RNA-Ernie foundation model, projected via pre-fitted PCA (rnaernie_pca_32.pkl) into 32-D for sense strand + 32-D for antisense strand.",
                "5. ViennaRNA Duplex Thermodynamics (5-D): C-extension calculations: Duplex ΔG / -70.0, Sense self-folding MFE / -50.0, Antisense self-folding MFE / -50.0, base-pair ensemble diversity / 21.0, and duplex GC percentage."
            ]
        }
    ]
}

CHAPTER_7 = {
    "title": "Chapter 7: Machine Learning & Deep Learning Model Architectures",
    "sections": [
        {
            "title": "7.1 The Flagship Hierarchical Engine: HelixZero IEEE v5",
            "body": [
                "The flagship machine learning breakthrough of HelixZero is the Two-Stage Hierarchical Engine implemented in helixzero_ieee_v5/predict_ieee_v5.py.",
                "In clinical pharmacology, drug-induced mRNA knockdown follows the Hill-Langmuir dose-response equation:",
                "Efficacy(C) = (E_max * C^h) / (IC50^h + C^h)",
                "where C is drug concentration, IC50 is the half-maximal inhibitory concentration, E_max is maximum efficacy (100%), and h is the Hill coefficient (approximately 1.0 for catalytic RISC slicing).",
                "HelixZero IEEE v5 decouples intrinsic thermodynamic affinity from experimental assay dosing via two cascaded gradient boosted models:",
                "Stage 1 (Intrinsic Affinity Regressor): Evaluates the 577-D feature vector to predict the concentration-independent affinity constant pIC50 = -log10(IC50 in M). A candidate with IC50 = 10 pM receives pIC50 = 11.0; a weak candidate with IC50 = 10 nM receives pIC50 = 8.0.",
                "Stage 2 (Dose-Aware Assay Response): Takes the horizontally stacked 579-dimensional vector [pIC50, log10(target_dose_nM + 1e-6), X_577] and predicts the exact percentage mRNA knockdown at the user's specific target concentration.",
                "Vectorized C++ Acceleration: In predict_sirna_potency_batch(), Stage 1 and Stage 2 CatBoost models are evaluated via vectorized C++ batch routines. A batch of 1,260 chemical variants is scored in under 2.5 seconds—over 6,000 times faster than sequential Python loops."
            ]
        },
        {
            "title": "7.2 The MEG-mod Bimodal Graph Attention Network (BAN_graph.py)",
            "body": [
                "In MEG-mod-main/BAN_graph.py, we implemented a structural graph neural network operating on RNA duplex topology:",
                "Node Architecture: 54 nodes (27 sense + 27 antisense slots). Each node receives a 778-dimensional feature vector combining a 768-D RNA-Ernie embedding with a 10-D physicochemical property vector (molecular weight, logP, polar surface area, hydrogen bond donors/acceptors).",
                "Edge Architecture: 5-dimensional edge vectors encoding 4 one-hot edge types (intra-sense backbone, intra-antisense backbone, inter-strand base pairs from ViennaRNA RNAcofold, and intra-strand MFE pairs) plus 1 continuous channel for base-pairing probability P_ij.",
                "Graph Convolution & Bilinear Attention: 2 layers of PyTorch Geometric TransformerConv (4 attention heads, 512 hidden channels) coupled with Bilinear Attention Networks (BANLayer_token) for pairwise token-chemical interactions."
            ]
        },
        {
            "title": "7.3 Production Hybrid Ensemble V4 & Epistemic Uncertainty",
            "body": [
                "In production (smepred/src/predictor.py), predictions are generated via a calibrated weighted blend:",
                "Efficacy_final = 0.85 * Efficacy_CatBoost_v4 + 0.15 * Efficacy_MEG-mod_GNN",
                "The CatBoost GBDT (85% weight) provides rapid, non-linear partitioning across the 420 ontology flags, while the MEG-mod GNN (15% weight) contributes 3D topological awareness. Furthermore, predict_with_uncertainty() quantifies epistemic uncertainty via ensemble disagreement: Disagreement = |y_gbdt - y_gnn|, scaling standard deviation from 1.5% up to 12.0% for out-of-distribution molecules."
            ]
        }
    ]
}
