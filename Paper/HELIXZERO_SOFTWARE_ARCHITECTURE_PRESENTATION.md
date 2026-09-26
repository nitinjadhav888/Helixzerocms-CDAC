# HELIXZERO: PRODUCTION SOFTWARE ARCHITECTURE & ML ENGINEERING DECK
## An End-to-End Software, Feature Engineering, and Machine Learning Systems Deep-Dive (18 Slides)

**Presenter**: Nitin Jadhav  
**Affiliation**: High Performance Computing – Medical & Bioinformatics Applications (HPC-M&BA) Group, C-DAC Pune  
**Project**: HelixZero (Production siRNA Screening, Optimization & Potency Engine)  
**Target Audience**: Dr. Uddhavesh Sonavane (HOD), Dr. Vinod Jani (Mentor), Mallikarjunachari V. N. Uppuladinne (Mentor)  
**Audience Focus**: Software Architecture, Data Pipelines, 577-D Feature Engineering, Model Training, Hyperparameters, and Empirical Benchmarks  

---

## SLIDE 1: HelixZero-CMS: Production siRNA and RNAi Design Platform

### Slide Metadata
* **Category / Eyebrow**: EXECUTIVE OVERVIEW - PLATFORM ARCHITECTURE
* **Title**: HelixZero-CMS: Production siRNA and RNAi Design Platform
* **Subtitle**: FastAPI Microservice, 577-D Multi-Modal Feature Extraction, and Hierarchical Machine Learning
* **Badges**: PRODUCTION ACTIVE, RNAi / siRNA THERAPEUTICS, C-DAC PUNE HPC-M&BA

### Slide Content
#### Core Platform Scope and Engineering
* **Target Biological Modality:** Specifically engineered for **double-stranded RNAi / siRNA therapeutics** (21-mer duplexes acting through the cellular RISC / Argonaute-2 pathway), strictly distinguished from single-stranded antisense oligonucleotides (ASOs).
* **Production Software Stack:** Python 3.11 with a modular FastAPI microservice architecture, designed for rapid whole-transcriptome scanning and real-time combinatorial optimization.
* **Hierarchical Design Workflow:** mRNA sequence ingestion -> 21-mer sliding window -> 577-D multi-modal vectorization -> Hierarchical ML potency prediction -> 2-bit packed safety audit -> Pareto-TOPSIS candidate ranking.
* **Current Operational Scope:** High-throughput inference operates without real-time 3D Ago2 atomic docking; structural compatibility is maintained via calibrated biophysical rules and spatial clearances.

#### Key Platform Performance Metrics
* **Multi-Modal Feature Vector**: `577-D` (Positional + Deep Embeddings + Physics)
* **Model Inference Latency**: `< 25 ms` (CatBoost Symmetric Oblivious Trees)
* **Screening Throughput**: `~3,700` (Candidate siRNAs Evaluated / Second)
* **Held-Out Potency Accuracy**: `r = 0.8187` (Zero-Leakage Test Split (N=7,674, R² = 0.6655))

### Spoken Talk Track (Presenter Notes)
> "Good morning everyone. Today, I am honored to present the software architecture and machine learning engineering behind HelixZero. HelixZero is a production-grade software platform specifically designed for the discovery, screening, and chemical optimization of therapeutic small interfering RNAs—or siRNAs—operating through the RNA interference (RNAi) pathway. Unlike single-stranded antisense oligonucleotides (ASOs), our system focuses strictly on double-stranded 21-mer siRNA therapeutics that load into the cellular RISC complex. Built on Python 3.11 with a high-performance FastAPI microservice backend, HelixZero screens thousands of candidate siRNAs per second, extracts a 577-dimensional multi-modal feature vector, and uses hierarchical machine learning to predict intrinsic potency and dose response."

---

## SLIDE 2: The Biophysical and Computational Bottlenecks of siRNA Design

### Slide Metadata
* **Category / Eyebrow**: PROBLEM SPACE - BIOPHYSICAL CONSTRAINTS
* **Title**: The Biophysical and Computational Bottlenecks of siRNA Design
* **Subtitle**: Why Traditional Bioinformatics and Standard Machine Learning Fail on Modified RNAi Drugs
* **Badges**: BIOLOGICAL REALITY, COMBINATORIAL EXPLOSION, CONCENTRATION CONFOUNDING

### Slide Content
#### Biological Realities vs. Software Constraints
* **Exhaustive 21-Mer Requirement:** Human Argonaute-2 sterically demands a 21-nucleotide duplex with 2-nucleotide 3-prime overhangs. Software must evaluate every overlapping 21-mer across full-length mRNA transcripts (up to 10,000+ nucleotides).
* **Chemical Discontinuity:** Commercial siRNAs are **100% chemically modified** (2'-OMe, 2'-F, phosphorothioate backbones, GalNAc conjugates). Naked sequence algorithms suffer complete failure on modified duplexes (**r = 0.1771, R² = -0.0901**).
* **The Concentration Confounder:** Biological assays measure percentage knockdown at arbitrary doses (from 0.001 nM to 100 nM). Single-label regression conflates intrinsic molecular potency with exposure dose.
* **Combinatorial Explosion:** A 21-mer duplex with 42 nucleotide slots and 30 chemistries represents **30^42 (approximately 10^62)** possible states, requiring intelligent guided search.

#### Mentor Literature Touchpoint - Oligonucleotide Biophysics
> **CDAC Mentor Research Alignment**: Dr. Uddhavesh Sonavane (HOD) & Mallikarjunachari V. N. Uppuladinne (Mentor)  
> *Citation*: J. Biomol. Struct. Dyn. (2019) 37(18): 4739–4750  
In their 2019 JBSD paper on antisense gapmer-RNA duplexes, Sonavane sir and Mallikarjunachari sir demonstrated that chemical substitutions (such as LNA, MOE, and phosphorothioate linkages) fundamentally remodel duplex hydration shells, backbone dihedral angles, and thermal stability (Tm), while requiring strict preservation of central catalytic cleavage geometry.
<p style='margin-top:8px;'>**Engineering Translation to RNAi:** While single-stranded ASOs recruit RNase H and siRNAs recruit Argonaute-2, the underlying physical chemistry is shared: chemical modifications alter A-form helical geometry and steric clearance. A software model that treats RNA as a naive 4-letter alphabet cannot generalize to chemically engineered siRNA therapeutics.

### Spoken Talk Track (Presenter Notes)
> "Here we confront the core problem in RNA therapeutics: naked sequence models fail catastrophically when applied to chemically modified siRNAs, showing negative R-squared. Every commercial siRNA drug today is heavily modified. In their 2019 paper on antisense gapmers, Sonavane sir and Mallikarjunachari sir showed that modifications like LNA, MOE, and phosphorothioates remodel hydration shells and backbone flexibility. While ASOs recruit RNase H and siRNAs recruit Argonaute-2, both demand strict preservation of catalytic geometry. A model without chemical awareness is completely blind to these effects."

---

## SLIDE 3: System Topology: The 5-Tier Hierarchical Engineering Pipeline

### Slide Metadata
* **Category / Eyebrow**: SYSTEM TOPOLOGY - 5-TIER PIPELINE
* **Title**: System Topology: The 5-Tier Hierarchical Engineering Pipeline
* **Subtitle**: End-to-End Modular Decoupling of Ingestion, Vectorization, ML Inference, and Safety
* **Badges**: MODULAR DECOUPLING, FAST INFERENCE, MULTI-TIERED PIPELINE

### Slide Content
#### 5-Tier Pipeline Walkthrough
> * **Tier 1 - High-Speed Ingestion & Sliding Window:** <code>sirna_generator.py</code> slides a 21-mer window across mRNA, computing antisense duplexes with O(1) translation.
> * **Tier 2 - 577-D Feature Extraction Engine:** <code>features_v4.py</code> vectorizes positional chemistry (444-D), RNA foundation embeddings (128-D), and ViennaRNA thermodynamics (5-D).
> * **Tier 3 - Multi-Engine Machine Learning Suite:** Model A (LightGBM, 214-D), Model B v4 (CatBoost, 577-D), and IEEE v5 Hierarchical Potency & Hill Sigmoid Regressors.
> * **Tier 4 - Biophysical Guardrails & Safety Engine:** 7 penalty modules (nuclease, TLR7/8, RISC asymmetry) + 2-bit packed transcriptome off-target search.
> * **Tier 5 - Combinatorial Optimization & Ranking:** Multi-slot beam search (Width = 20) + Pareto-TOPSIS multi-criteria decision making.

#### Design Principle: Avoid Monolithic Collapse
* **Decoupled Responsibilities:** Whole-transcriptome sequence filtering (< 1 ms) is completely decoupled from heavy chemical potency evaluation and dose-response modeling.
* **Independent Auditing:** Each tier can be unit-tested and calibrated against biological gold standards independently.
* **Pluggable Model Backends:** Fast switching between CatBoost, GNN, Ensemble, and IEEE v5 via the central model registry.

### Spoken Talk Track (Presenter Notes)
> "Slide 3 presents the overall system topology. Instead of a monolithic black-box neural net that tries to predict everything at once, HelixZero decouples the software into five distinct tiers: Tier 1 handles sequence ingestion and sliding window; Tier 2 extracts our 577-D multi-modal signature; Tier 3 runs our gradient-boosted machine learning engines; Tier 4 enforces biophysical and safety guardrails; and Tier 5 performs combinatorial beam search and Pareto-TOPSIS ranking."

---

## SLIDE 4: Tier 1 - Ingestion: Exhaustive 21-Mer Sliding Window and O(1) Translation

### Slide Metadata
* **Category / Eyebrow**: TIER 1 - INGESTION - SLIDING WINDOW ENGINE
* **Title**: Tier 1 - Ingestion: Exhaustive 21-Mer Sliding Window and O(1) Translation
* **Subtitle**: Generating Thousands of Therapeutic Candidates in Milliseconds via Compiled C Translation
* **Badges**: O(1) REVERSE COMPLEMENT, DSIRNA PROCESSING, ZERO HEAP OVERHEAD

### Slide Content
#### Sliding Window Complexity & O(1) Translation
* **Exhaustive Sliding Window:** For an mRNA of length L, the engine generates (L - 21 + 1) overlapping 21-mer candidates. For a 3,000-nucleotide mRNA, 2,980 candidates are created in **under 5 milliseconds**.
* **The Reverse Complement Bottleneck:** Naive string loops or dictionary lookups trigger Python heap memory churn. HelixZero uses compiled C-level translation tables:
```python
_RNA_COMPLEMENT = str.maketrans("AUGC", "UACG")
def _calculate_reverse_complement(sequence: str) -> str:
# Zero intermediate heap allocations; runs at native C speed
return sequence.translate(_RNA_COMPLEMENT)[::-1]
```

#### DsiRNA (Dicer-Substrate 27-Mer) Cleavage Emulation
* **Biomimetic DsiRNA Cleavage:** Dicer substrates (27-mers) are cleaved endogenously by human Dicer to yield mature 21-mer duplexes (*Kim et al., Nature Biotechnology 2005*).
* **Deterministic Terminal Rule:** Dicer anchors at the 2-nucleotide 3-prime overhang of the sense strand and cleaves 21 nucleotides inward:
```python
def generate_dsirna_candidate(dsirna_sequence: str):
# Extracts the exact mature 21-mer therapeutic drug product
sense_strand = dsirna_sequence[-21:]
return SiRNACandidate(sense=sense_strand, ...)
```

### Spoken Talk Track (Presenter Notes)
> "In Tier 1, sliding window generation is the first computational bottleneck. A single long transcript like TTR or PCSK9 generates thousands of candidates. Using Python's str.maketrans at the compiled C-level, we compute reverse complements with zero heap allocation in under 5 milliseconds. We also handle 27-mer Dicer-substrate duplexes by deterministic 21-mer terminal cleavage mapping."

---

## SLIDE 5: Data Governance: 10-Resource Taxonomy and Zero-Leakage GroupKFold Protocol

### Slide Metadata
* **Category / Eyebrow**: DATA GOVERNANCE - TAXONOMY & SPLITTING
* **Title**: Data Governance: 10-Resource Taxonomy and Zero-Leakage GroupKFold Protocol
* **Subtitle**: Curating 40,255 Assays with Strict Sequence-Identity Partitioning to Prevent Model Hallucination
* **Badges**: N = 40,255 ASSAYS, ZERO-LEAKAGE GKF, STRICT PEER-REVIEW STANDARDS

### Slide Content
#### 10-Resource Dataset Taxonomy
| **Dataset** | **Sample Count** | **Type** | **Provenance & Role**
| **CMsiRNAdb Master** | 40,255 | Mixed | 37,946 BRONZE (68 doses) + 2,309 GOLD Hill curves
| **Huesken Held-Out** | 2,361 | Naked | Canonical gold standard across 34 mRNAs (Nat Biotechnol)
| **Takayuki Screen** | 702 | Naked | Unmodified validation screen across multi-target mRNAs
| **Mixset 7-Studies** | 472 | Naked | Multi-lab consolidated unmodified benchmark
| **CMsiRNAdb Homogeneous** | 472 | Modified | Uniform chemical backbones (held-out test)
| **CMsiRNAdb Heterogeneous** | 2,576 | Modified | Complex clinical modifications (alternating 2'-F/2'-OMe)

#### The Zero-Leakage GroupKFold Protocol
* **The Sequence Leakage Trap:** Standard random train/test splits leak identical or 1-nucleotide shifted antisense sequences, artificially boosting correlation to r > 0.90.
* **Rigorous GroupKFold Partitioning:** Folds are partitioned strictly on **unique core antisense sequence**. No test sequence or chemical analog ever appears in training:
```python
# Programmatic assertion in all training loops
val_seqs = set(groups[val_idx])
tr_seqs = set(groups[tr_idx])
assert len(val_seqs.intersection(tr_seqs)) == 0, "Leakage detected!"
```

### Spoken Talk Track (Presenter Notes)
> "Slide 5 covers our training data and strict validation protocol. We consolidated 10 datasets totaling over 40,000 biological assays. The most critical software standard here is zero sequence leakage. If you split randomly, identical sequences end up in train and test, inflating accuracy. We enforce GroupKFold grouped strictly on the core antisense sequence, programmatically verifying zero sequence overlap between folds."

---

## SLIDE 6: Data Schema: Multi-Slot Chemical Schema and Orthogonal NucSlot Dataclass

### Slide Metadata
* **Category / Eyebrow**: DATA SCHEMA - ORTHOGONAL CHEMICAL ONTOLOGY
* **Title**: Data Schema: Multi-Slot Chemical Schema and Orthogonal NucSlot Dataclass
* **Subtitle**: Fixing the Broken Legacy 1-Character Serialization with Typed 6-Attribute Nucleotide Slots
* **Badges**: CHEM_SCHEMA.PY, 6-ATTRIBUTE SLOTS, 50+ REGEX PARSERS

### Slide Content
#### The Broken 1-Char String Flaw vs. NucSlot Fix
* **Legacy Serialization Bug:** Legacy databases used single ASCII characters (M = 2'-OMe, F = 2'-F, S = phosphorothioate). Sugar, linkage, and base became mutually exclusive. A nucleotide could not have a 2'-F sugar *and* a phosphorothioate linkage!
* **The Orthogonal 6-Attribute Schema (chem_schema.py):**
```python
@dataclass
class NucSlot:
base: str                         # A, C, G, U (base never lost)
sugar: str = "ribo"               # ribo, 2F, 2OMe, LNA, MOE, deoxyribo
linkage_3p: str = "PO"            # PO, PS, PS2, Boranophosphate
base_mod: Optional[str] = None    # m5C, pseudouridine, inosine
terminal_5p: Optional[str] = None # 5P, 5VP (vinylphosphonate), 5OMeCap
conjugate: Optional[str] = None   # GalNAc, Cholesterol, PEG
raw_name: str = ""                # Preserves original IUPAC string
```

#### Mentor Literature Touchpoint - Sugar Pucker & Conformation
> **CDAC Mentor Research Alignment**: Mallikarjunachari V. N. Uppuladinne (Mentor)  
> *Citation*: Quantum Chemical Studies of 2'-4' Conformationally Restricted Monomers  
Mallikarjunachari sir's quantum chemical research proved that 2'-substituents (e.g., 2'-F vs. 2'-OMe) dictate whether the furanose adopts a rigid **C3'-endo (North)** or **C2'-endo (South)** conformation, altering A-form geometry and van der Waals envelopes independently from phosphate linkages.
<p style='margin-top:8px;'>**Engineering Translation:** Our NucSlot dataclass explicitly decouples sugar puckering from internucleotide phosphate linkages, allowing HelixZero to accurately model coexisting 2'-F sugars and phosphorothioate backbones.

### Spoken Talk Track (Presenter Notes)
> "Slide 6 explains a major software refactoring. Historical databases stored modifications as a single string of letters like 'M' or 'F', making sugar and linkage mutually exclusive. As Mallikarjunachari sir's quantum chemical research demonstrated, sugar pucker and internucleotide linkages are independent physical variables. Our NucSlot dataclass decouples base, sugar, linkage, base modifications, terminal caps, and delivery conjugates into orthogonal attributes."

---

## SLIDE 7: Feature Engineering: The 577-Dimensional Multi-Modal Signature

### Slide Metadata
* **Category / Eyebrow**: FEATURE ENGINEERING - 577-DIMENSIONAL VECTOR
* **Title**: Feature Engineering: The 577-Dimensional Multi-Modal Signature
* **Subtitle**: Vectorizing Positional Stereochemistry, Pretrained Foundation Models, and Thermodynamics
* **Badges**: 577-D SIGNATURE, FEATURES_V4.PY, MULTI-MODAL FUSION

### Slide Content
#### Exact 577-D Mathematical Breakdown
> * **Feature Vector Composition (577 Total Dimensions):**<br>
444-D Positional Chemistry + 64-D RNA-FM Embeddings + 64-D RNA-Ernie Embeddings + 5-D ViennaRNA Physics
| **Feature Block** | **Dims** | **Source Engine** | **Biological & Physical Meaning**
| **Positional v2 (Slots)** | **420** | Multi-slot encoding | 42 slots × 10 attributes: base, sugar (2F/2OMe/LNA), linkage (PO/PS), caps
| **Global Chemistry** | **24** | Descriptor engine | Total 2'-F/2'-OMe ratio, terminal PS count, total charge, duplex GC%
| **RNA-FM Foundation** | **64** | 12-layer Transformer (PCA) | 32-D sense + 32-D antisense evolutionary and structural representations
| **RNA-Ernie Context** | **64** | Structural Transformer (PCA) | 32-D sense + 32-D antisense secondary structure awareness embeddings
| **ViennaRNA Physics** | **5** | ViennaRNA C-API | Sense MFE, Antisense MFE, Duplex ΔG, Ensemble Diversity, GC fraction

#### ViennaRNA Real Biophysics (5 Dimensions)
* **Real Physical Folding:** Evaluates Turner nearest-neighbor free energy parameters via compiled C bindings (RNA.fold, RNA.duplexfold):
* 1. Sense strand Minimum Free Energy (MFE, normalized between -50 and 0 kcal/mol).
* 2. Antisense strand MFE (normalized between -50 and 0 kcal/mol).
* 3. Duplex hybridization binding energy (normalized between -70 and 0 kcal/mol).
* 4. Ensemble structural diversity metric (base-pair distance / 21).
* 5. Combined duplex GC content fraction.

### Spoken Talk Track (Presenter Notes)
> "Slide 7 shows our exact 577-dimensional feature stack in features_v4.py. We have 444 dimensions of positional and global chemistry, 128 dimensions from pre-trained RNA foundation models—RNA-FM and RNA-Ernie—compressed via PCA, and 5 dimensions of physical folding thermodynamics from the ViennaRNA C-API."

---

## SLIDE 8: Feature Pipeline: Batch Vectorization and ViennaRNA Integration

### Slide Metadata
* **Category / Eyebrow**: FEATURE PIPELINE - BATCH EXTRACTION & FAULT TOLERANCE
* **Title**: Feature Pipeline: Batch Vectorization and ViennaRNA Integration
* **Subtitle**: High-Performance Vector Assembly at ~8,400 Candidates/Second with Graceful Fallbacks
* **Badges**: BATCH NUMPY ARRAYS, C-EXTENSION INTEGRATION, FAULT TOLERANCE

### Slide Content
#### Code Implementation: features_v4.py
```python
# smepred/src/features_v4.py
def build_features_v4(sense_slots, anti_slots) -> np.ndarray:
v2    = build_features_v2(sense_slots, anti_slots)      # 444-D
fm    = _rnafm_features(sense_slots, anti_slots)        # 64-D
ernie = _rnaernie_features(sense_slots, anti_slots)     # 64-D
vr    = _vienna_features(sense_slots, anti_slots)       # 5-D
return np.concatenate([v2, fm, ernie, vr])             # 577-D Float32
def batch_features_v4(sense_list, anti_list) -> np.ndarray:
# Pre-allocates contiguous C-ordered array: shape (N, 577)
X = np.zeros((len(sense_list), 577), dtype=np.float32)
for i, (s, a) in enumerate(zip(sense_list, anti_list)):
X[i] = build_features_v4(s, a)
return X
```

#### Throughput & Resilience Engineering
* **Memory-Efficient Vectorization:** Pre-allocating contiguous float32 arrays avoids memory fragmentation, achieving **~8,400 candidate vectors/second**.
* **Graceful C-Extension Fallback:** If ViennaRNA shared libraries are missing in a lightweight execution environment, the engine switches to vectorized nearest-neighbor GC-proxy thermodynamics without pipeline crashing.
* **PCA Projection Caching:** Pre-computed orthogonal projection matrices allow instantaneous 640-D to 32-D dimensionality reduction for foundation model embeddings.

### Spoken Talk Track (Presenter Notes)
> "Slide 8 shows how features are built in code. Pre-allocating contiguous C-ordered float32 NumPy arrays gives us a throughput of ~8,400 feature vectors per second on CPU. If the ViennaRNA C-extension is missing in a minimal Docker image, the code doesn't crash; it smoothly falls back to vectorized nearest-neighbor thermodynamics."

---

## SLIDE 9: The 3-Card Framework: Model A (Naked), Model B v4 (Chemistry), and Card 3 (Biophysics)

### Slide Metadata
* **Category / Eyebrow**: THE 3-CARD FRAMEWORK - ML SPECIALIZATION
* **Title**: The 3-Card Framework: Model A (Naked), Model B v4 (Chemistry), and Card 3 (Biophysics)
* **Subtitle**: Decoupling Sequence Screening, Chemical Potency, and Clinical Biophysical Gating
* **Badges**: MODEL A (LIGHTGBM), MODEL B V4 (CATBOOST), CARD 3 (BIOPHYSICS)

### Slide Content
#### The 3-Card Functional Topology
| **Card Layer** | **Engine** | **Features** | **Target Objective & Performance**
| **CARD 1: Naked Screen** | **Model A (LightGBM)** | 214 Descriptors | Fast sequence screening (< 1 ms). **r = 0.8788** (Takayuki), **r = 0.8044** (Huesken).
| **CARD 2: Chemical Potency** | **Model B v4 (CatBoost)** | 577-D Vector | Chemistry-aware regression (< 25 ms). **r = 0.7401** (Homog), **r = 0.6217** (Heterog).
| **CARD 3: Biophysics & Lift** | **Biophysics Rule Engine** | 7 Penalty Engines | Calibrated 0.12 scaling deducting for nuclease, immune, and synthesis liabilities.

#### Mentor Literature Touchpoint - Stacked Descriptors & Ensembles
> **CDAC Mentor Research Alignment**: Dr. Vinod Jani & Dr. Uddhavesh Sonavane  
> *Citation*: MolToxPred: Small Molecule Toxicity Prediction, RSC Advances (2024) 14: 2197–2207  
In *MolToxPred*, Vinod sir and Sonavane sir demonstrated that a stacked model combining LightGBM, Random Forest, and MLP on structured physicochemical descriptors outperformed monolithic architectures (achieving AUROC >88%).
<p style='margin-top:8px;'>**Engineering Translation:** HelixZero adopts this exact philosophy: rather than forcing a single network to learn sequence and chemical rules simultaneously, we decouple sequence screening (LightGBM) from chemical potency (CatBoost), preventing feature dominance.

### Spoken Talk Track (Presenter Notes)
> "Slide 9 presents our 3-Card Framework. Taking inspiration from Vinod sir and Sonavane sir's MolToxPred paper where stacked tree models on structured descriptors proved superior to monolithic deep networks, we separate sequence screening (Model A) from chemical potency (Model B v4) and biophysical penalties. This functional separation guarantees that sequence-level rules don't overwrite chemical modification signals."

---

## SLIDE 10: Algorithm Selection: Why LightGBM and CatBoost Dominate Tabular Biology

### Slide Metadata
* **Category / Eyebrow**: ALGORITHM SELECTION - GBDT EFFICIENCY
* **Title**: Algorithm Selection: Why LightGBM and CatBoost Dominate Tabular Biology
* **Subtitle**: Oblivious Trees, Histogram Binning, Deterministic Latency, and Tabular Generalization
* **Badges**: HISTOGRAM GBDT, OBLIVIOUS TREES, ZERO OVERFITTING

### Slide Content
#### Why LightGBM for Model A (Sequence Screening)?
* **Histogram Binning:** Discretizes 214 continuous sequence and thermodynamic features into 256 bins, enabling whole-transcriptome inference at **>3,700 candidates/second** on standard CPU.
* **Leaf-Wise Splitting:** Explores asymmetric, high-order sequence motif interactions (e.g., Reynolds position 1 A/U paired with position 19 GC-clamp).
* **Failure Mode:** Collapses on chemically modified duplexes (**r = 0.1771**) because naked models assume standard unmodified ribose geometry.

#### Why CatBoost for Model B v4 & IEEE v5 (Chemical Potency)?
* **Symmetric (Oblivious) Trees:** CatBoost applies identical split conditions across entire tree levels, compiling to single-pass cache-friendly memory lookups with latency **under 25 milliseconds**.
* **Ordered Boosting:** Eliminates target leakage during gradient estimation, essential when dealing with clustered pharmacological modification datasets.
* **Deep Net Failure on Modified RNA:** End-to-end graph neural networks (e.g., MEG-mod TransformerConv) overfit severely (**r = 0.0631**) due to dataset sparsity in chemical combinations.

### Spoken Talk Track (Presenter Notes)
> "Why did we choose LightGBM and CatBoost instead of deep neural networks? Because biological tabular datasets feature sparse, clustered combinations. CatBoost's oblivious symmetric trees evaluate splits simultaneously in hardware cache with deterministic latency under 25 milliseconds, while GNNs overfit severely with an r of 0.06."

---

## SLIDE 11: Model Training: Audited Hyperparameter Configurations and Loss Objectives

### Slide Metadata
* **Category / Eyebrow**: MODEL TRAINING - HYPERPARAMETERS & OBJECTIVES
* **Title**: Model Training: Audited Hyperparameter Configurations and Loss Objectives
* **Subtitle**: Exact Hyperparameter Specifications Across All Production GBDT and GNN Models
* **Badges**: AUDITED HYPERPARAMETERS, EARLY STOPPING, RMSE OBJECTIVE

### Slide Content
#### Production Hyperparameter Matrix
| **Hyperparameter** | **Model A (LightGBM)** | **Model B v4 (CatBoost)** | **Module 2 Potency** | **Module 3 Dose Response** | **MEG-mod GNN**
| **Objective / Loss** | MSE (L2 Loss) | RMSE | RMSE | RMSE | Smooth L1 Loss
| **Input Dims** | 214 Features | 577 Features | 577 Features | **579 Features** | 54-node Graph
| **Iterations / Trees** | 500 | 1,500 | 1,000 | 1,200 | 100 Epochs
| **Learning Rate** | 0.050 | 0.030 | 0.040 | 0.035 | 0.0001 (AdamW)
| **Tree Depth** | Unlimited (max 31) | 7 | 8 | 7 | 4-layer TransConv
| **L2 Regularization** | 0.0 | 3.0 | 4.0 | 3.0 | Weight Decay 1e-4
| **Early Stopping** | 30 rounds | 50 rounds | 60 rounds (od_wait) | 50 rounds | 15 epochs
| **Cross-Validation** | 5-Fold GroupKFold | 5-Fold GroupKFold | 5-Fold GroupKFold | 5-Fold GroupKFold | 5-Fold GroupKFold

#### Key Training Architecture Details
* **Module 3 Input Dimensionality (579 Dimensions):** Formed by concatenating the 577-D base vector + 1-D predicted pIC50 from Module 2 + 1-D log10(concentration in nM + 1e-6).
* **Regularization Strategy:** L2 leaf regularization set to 3.0 to 4.0 in CatBoost models suppresses spurious weights from rare chemical modification patterns.

### Spoken Talk Track (Presenter Notes)
> "Slide 11 gives our exact training hyperparameters audited directly from code. Notice that Module 3 has 579 inputs: it takes the 577 base features plus the predicted pIC50 from Module 2 and the log-dose. Learning rates are tuned between 0.03 and 0.05 with L2 leaf regularization at 3.0 to 4.0 to penalize rare chemical memorization."

---

## SLIDE 12: Flagship Engine: IEEE v5 Hierarchical Potency (pIC50) and Hill Modeling

### Slide Metadata
* **Category / Eyebrow**: FLAGSHIP ENGINE - IEEE V5 HIERARCHICAL MODEL
* **Title**: Flagship Engine: IEEE v5 Hierarchical Potency (pIC50) and Hill Modeling
* **Subtitle**: Decoupling Intrinsic Potency from Experimental Dose: Predicting Both pIC50 and Concentration Response
* **Badges**: IEEE V5 HIERARCHICAL, pIC50 PREDICTION, HILL SIGMOID

### Slide Content
#### Two-Stage Hierarchical Mathematical Formulation
> * **Stage 1 - Intrinsic Potency Engine (Module 2 CatBoost):**<br>
Predicts concentration-independent molecular potency: **pIC50 = -log10(IC50)**.<br>
Direct nanomolar conversion: **IC50 (nM) = 10^(9 - pIC50)**.
> * **Stage 2 - Dose-Conditioned Response Engine (Module 3 CatBoost):**<br>
Evaluates predicted potency alongside assay exposure dose C using an audited 4-parameter Hill sigmoid:<br>
**Knockdown % = Minimum + (Maximum - Minimum) / (1 + 10^((log10(IC50) - log10(Dose)) × Hill Slope))**

#### Code Implementation: predict_ieee_v5.py
```python
# Stage 1: Intrinsic Potency (pIC50)
pred_pIC50 = float(mod2_engine.predict(X_base)[0])
ic50_nM    = float(10**(9.0 - pred_pIC50))
# Stage 2: Dose-Response (Hill Sigmoid)
log_conc   = np.log10(conc_nM + 1e-6).reshape(-1, 1)
X_mod3     = np.hstack([np.array([[pred_pIC50]]), log_conc, X_base]) # 579-D
pred_kd    = float(np.clip(mod3_engine.predict(X_mod3)[0], 0.0, 100.0))
```
* **Generalization Power:** Enables the user to simulate full dose-response curves (0.01 nM to 100 nM) without retraining for each experimental assay condition.

### Spoken Talk Track (Presenter Notes)
> "Slide 12 explains our flagship IEEE v5 engine. In pharmacology, potency and dose are separate variables. Stage 1 takes the 577-D vector and predicts pIC50, which converts to nanomolar IC50. Stage 2 stacks that predicted pIC50 with the log-dose and the base features to compute % knockdown via the Hill equation. This allows scientists to simulate complete concentration curves computationally."

---

## SLIDE 13: Optimization Engine: Combinatorial Chemical Search via Guided Beam Pruning

### Slide Metadata
* **Category / Eyebrow**: OPTIMIZATION ENGINE - COMBINATORIAL BEAM SEARCH
* **Title**: Optimization Engine: Combinatorial Chemical Search via Guided Beam Pruning
* **Subtitle**: Navigating the 30^42 Chemical State Space via Fast CatBoost Scoring and Biological Viability Rules
* **Badges**: MODIFICATION_ENGINE.PY, BEAM SEARCH (WIDTH=20), CHEMICAL VIABILITY RULES

### Slide Content
#### Multi-Slot Beam Search Algorithm
* **Step 1 - Single-Mod Scan (1,260 variants):** Evaluates 30 chemistries × 21 positions × 2 strands using Model B v4 in **~150 ms**.
* **Step 2 - Round-Robin Diversification:** Groups top variants by chemical family (2'-OMe, 2'-F, LNA, MOE, PS) to seed an initial diverse beam of width = 20.
* **Step 3 - Iterative Expansion Rounds:** Pairs beam candidates with single-mod candidates, applies chemical viability rules, scores viable candidates via CatBoost (< 25 ms), and prunes to top 20.
* **Step 4 - Final High-Fidelity Rescoring:** Top 100 candidates rescored with the IEEE v5 hierarchical engine.

#### Mentor Literature Touchpoint - TANGO Conformational Search
> **CDAC Mentor Research Alignment**: Mallikarjunachari V. N. Uppuladinne & Dr. Vinod Jani  
> *Citation*: TANGO: Conformation Generation and Optimization Tool, J. Comput. Chem. (2019) 40: 2119–2127  
In *TANGO*, the C-DAC group solved high-dimensional conformational searches by pairing systematic torsional rotation with energy optimization.
<p style='margin-top:8px;'>**Engineering Translation:** HelixZero applies this exact concept to chemical space: guided beam expansion avoids combinatorial traps in the 30^42 landscape, while hard viability constraints act as steric energy cutoffs.
<p style='margin-top:8px;'>**Hard Constraints:** 5'-VP/5'-P only at position 1; 3'-P only at position 21; max 1 conjugate per strand; max 2 consecutive bulky mods (LNA/MOE).

### Spoken Talk Track (Presenter Notes)
> "Slide 13 details our combinatorial optimization engine. With 42 positions and 30 chemistries, the search space is 30 to the power of 42. Inspired by Mallikarjunachari sir and Vinod sir's TANGO tool, we run an intelligent beam search. A single-mod scan evaluates 1,260 variants in ~150 ms, creates a diverse initial beam of 20, expands iteratively, prunes inviable chemistries, and rescores the top 100 with IEEE v5."

---

## SLIDE 14: Reality Filters: 7-Module Biophysical Guardrails and Calibrated 0.12 Scaling

### Slide Metadata
* **Category / Eyebrow**: REALITY FILTERS - BIOPHYSICAL GUARDRAILS
* **Title**: Reality Filters: 7-Module Biophysical Guardrails and Calibrated 0.12 Scaling
* **Subtitle**: Literature-Grounded Deductions Preventing Synthetically Inviable or Immunogenic Candidates
* **Badges**: 7 PENALTY MODULES, 0.12 SCALING CONSTANT, SYNTHESIS & SERUM RULES

### Slide Content
#### The 7 Biophysical Penalty Engines (biophysics.py)
| **Module** | **Max Penalty** | **Biological Rationale & Literature Anchor**
| **1. Nuclease** | 20.0 pts | Unprotected 2'-OH in endoribonuclease cleavage sites (Alnylam AT3 pattern)
| **2. Immuno (TLR7/8)** | 28.0 pts | Unmasked GU-rich motifs (GUUGU, UGU) triggering cytokine storm (Judge 2005)
| **3. RISC Loading** | 60.0 pts | Inverted thermodynamic asymmetry favoring passenger strand loading (Schwarz 2003)
| **4. Thermo End** | 20.0 pts | Excessive 5' antisense GC-clamp preventing helicase unwinding
| **5. Serum Stability** | 60.0 pts | Missing 3' dinucleotide PS protection; fatal 5' AS GalNAc (Weingärtner 2020)
| **6. SPOS Synthesis** | 25.0 pts | G-quadruplex runs (G >= 4) causing solid-phase synthesis column failure
| **7. Chemistry Tier** | 40.0 pts | High-risk unapproved chemical entities vs. clinical FDA/EMA benchmarks

#### The 0.12 Calibration Constant
* **Calibrated Equation:** Adjusted Score = max(0, min(100, Raw Score - (0.12 × Total Penalty Points))) × Complementarity Gate
* **Clinical Calibration:** The 0.12 scaling factor was calibrated against FDA commercial drugs (Patisiran, Givosiran, Inclisiran), ensuring approved drugs retain **78% - 90%** of their raw ML score while heavily penalizing unstable constructs.

### Spoken Talk Track (Presenter Notes)
> "Slide 14 details our reality filter. Machine learning algorithms can easily memorize dataset quirks and reward synthetically inviable molecules. Our 7 penalty engines deduct points for nuclease vulnerability, immune-activating GU motifs, and solid-phase synthesis failures like G-quadruplexes. The 0.12 scaling factor was calibrated so FDA commercial drugs retain 78 to 90% of their raw score."

---

## SLIDE 15: Transcriptome Safety: Sub-Microsecond 2-Bit Packed K-mer Index and Auditing

### Slide Metadata
* **Category / Eyebrow**: TRANSCRIPTOME SAFETY - SUB-MICROSECOND BITWISE ENGINE
* **Title**: Transcriptome Safety: Sub-Microsecond 2-Bit Packed K-mer Index and Auditing
* **Subtitle**: Compressing 450 MB Transcriptome FASTA into a 50 MB In-Memory Hash Set for <500 ns Lookups
* **Badges**: 2-BIT PACKED K-MER, OFFTARGET.PY, O(1) SUB-MICROSECOND

### Slide Content
#### 2-Bit Packed Representation & Slicer Check
* **The Transcriptome Scanning Bottleneck:** Running BLAST or Bowtie2 against the human transcriptome (450 MB FASTA) takes 2–10 seconds per candidate, destroying interactive software performance.
* **The 2-Bit Packed Bitwise Index (offtarget.py):** Maps A=00, C=01, G=10, U/T=11. A 15-mer is packed into a single 32-bit unsigned integer:
```python
_NUC_MAP = {'A': 0, 'C': 1, 'G': 2, 'T': 3, 'U': 3}
def _pack_kmer(kmer: str) -> Optional[int]:
val = 0
for char in kmer:
val = (val << 2) | _NUC_MAP[char]
return val
```
* Compresses 450 MB of transcriptome sequences into a **50 MB memory-resident hash set** with query latency **under 500 nanoseconds**!

#### 4-Step Safety Audit Protocol
* **1. 15-Mer Slicer Match (Fatal):** If the antisense positions 1–15 match any unintended transcript, overallSafetyScore = 0.0.
* **2. Weighted Seed Match (Positions 2–8):** Seed Burden = (1.0 × 8-mer matches) + (0.8 × 7m8 matches) + (0.6 × 7a1 matches) + (0.3 × 6-mer matches).
* **3. Thermodynamic Asymmetry:** Inverted stability (Delta-Delta G > 0) docks passenger strand, triggering a 40-point safety deduction.
* **4. Chemical Seed Masking:** Toxic seeds are marked 'Mitigated' if 2'-OMe at pos 2 or GNA at pos 7 disrupts miRNA-like seed pairing.

### Spoken Talk Track (Presenter Notes)
> "Slide 15 highlights one of our best software optimizations. Calling external tools like BLAST takes several seconds per sequence. By mapping nucleotides into 2 bits, we pack 15-mers into standard 32-bit integers. A 450 MB transcriptome compresses into a 50 MB in-memory hash set, checking off-target slicer matches in under 500 nanoseconds."

---

## SLIDE 16: Lead Selection: Multi-Objective Pareto-TOPSIS Ranking and Toxicity Veto

### Slide Metadata
* **Category / Eyebrow**: LEAD SELECTION - PARETO-TOPSIS RANKING
* **Title**: Lead Selection: Multi-Objective Pareto-TOPSIS Ranking and Toxicity Veto
* **Subtitle**: Finding the Optimal Frontier Between Knockdown Efficacy, Seed Viability, and Asymmetry
* **Badges**: PARETO-TOPSIS, LEAD_SELECTOR.PY, HARD TOXICITY VETO

### Slide Content
#### Why Simple Weighted Sums Fail
* **The Masking Trap:** In drug discovery, a candidate with 99% predicted efficacy but severe off-target seed toxicity (causing cell death) must not be ranked #1. Simple weighted sums allow a high score in one dimension to mask fatal toxicity.
* **The TOPSIS Method (lead_selector.py):** Computes geometric distance to the *Ideal Best* and *Ideal Worst* in normalized multi-criteria space.

#### Multi-Criteria Weights & Hard Veto Penalties
* **1. Efficacy (Weight = 0.35):** Predicted knockdown percentage (y / 100).
* **2. Seed Cell Viability (Weight = 0.25):** Empirical cell survival score from 4,096 hexamer screen.
* **3. Thermodynamic Asymmetry (Weight = 0.15):** Normalized end-stability: (Delta-Delta G + 2.0) / 6.0 across range -2.0 to +4.0 kcal/mol.
* **4. Off-Target Clearance (Weight = 0.15):** Step function (1.0 if 0 hits, 0.5 if 1 hit, 0.1 if >= 2 hits).
* **5. Biophysical Integrity (Weight = 0.10):** Normalized penalty deduction: max(0, 1 - Penalty / 30).
* **Multiplicative Hard Vetoes:** Seed cell viability < 50% causes 30% penalty (Score × 0.70); Off-target hits > 1 cause 40% penalty (Score × 0.60).

### Spoken Talk Track (Presenter Notes)
> "Slide 16 covers lead selection. In pharmacology, simple weighted sums fail because high efficacy can easily mask fatal toxicity. We implement Pareto-TOPSIS, measuring distance to ideal and worst solutions across 5 normalized criteria, applying hard multiplicative penalties if seed viability drops below 50% or if off-target hits occur."

---

## SLIDE 17: Benchmark Audit: Single Source of Truth - 5-Model Empirical Evaluation Matrix

### Slide Metadata
* **Category / Eyebrow**: BENCHMARK AUDIT - SINGLE SOURCE OF TRUTH
* **Title**: Benchmark Audit: Single Source of Truth - 5-Model Empirical Evaluation Matrix
* **Subtitle**: Audited Empirical Metrics from final_benchmarks/master_benchmark_metrics.csv
* **Badges**: FROZEN GROUND TRUTH, PCC = 0.8187, R² = 0.6655

### Slide Content
#### Master Benchmark Metrics Table
| **Model Architecture** | **Dataset / Task** | **N** | **PCC (r)** | **SPCC (ρ)** | **ROC-AUC** | **RMSE** | **MAE** | **R² Score**
| **Model A (LightGBM)** | Takayuki Screen | 702 | **0.8788** | 0.8734 | 0.9275 | 12.39 | 9.64 | 0.6525
| **Model A (LightGBM)** | Mixset 7-Studies | 472 | **0.8291** | 0.8093 | 0.9456 | 20.32 | 17.35 | 0.4605
| **Model A (LightGBM)** | Huesken Held-Out | 2,361 | **0.8044** | 0.8065 | 0.9099 | 9.18 | 6.99 | 0.6252
<tr style='color:#f87171;'>| **Model A (Neg Control)** | CMsiRNAdb Hetero | 2,576 | **0.1771** | 0.1645 | 0.5711 | 29.59 | 24.70 | **-0.0901**
| **Model B v4 (CatBoost)** | CMsiRNAdb Homog | 472 | **0.7401** | 0.7540 | 0.8745 | 21.48 | 18.05 | 0.3989
| **Model B v4 (CatBoost)** | CMsiRNAdb Heterog | 2,576 | **0.6217** | 0.6049 | 0.8077 | 22.74 | 18.95 | 0.3563
| **MEG-mod GNN** | CMsiRNAdb Heterog | 300 | **0.0631** | 0.0788 | 0.5000 | 38.33 | 35.95 | -82.93
| **Ensemble v4** | CMsiRNAdb Homog | 472 | **0.7335** | 0.7469 | 0.8687 | 23.76 | 20.09 | 0.2646
| **Ensemble v4** | CMsiRNAdb Heterog | 2,576 | **0.6176** | 0.6018 | 0.8059 | 23.16 | 19.31 | 0.3327
<tr style='background:rgba(34,211,196,0.1); font-weight:bold;'>| **IEEE v5 Hierarchical** | **Zero-Leakage Test** | **7,674** | **0.8187** | **0.8154** | **0.9283** | **18.10** | **13.69** | **0.6655**

#### What Pearson r = 0.8187 Means Here
**Pearson r = Covariance(Actual, Predicted) / (StdDev(Actual) × StdDev(Predicted))**. Across 7,674 held-out test duplexes under strict zero-sequence leakage, an r = 0.8187 (R² = 0.6655) proves that over **66.5% of total variance** in modified siRNA knockdown potency is linearly explained by the model.
<p style='margin-top:8px;'>**Negative Control Significance:** Model A's negative R² (-0.0901) on modified data proves that sequence-only models perform worse than predicting the mean, confirming that chemical representations are indispensable.

### Spoken Talk Track (Presenter Notes)
> "Slide 17 reports our official benchmarks from final_benchmarks. On 7,674 held-out test duplexes with zero sequence leakage, the IEEE v5 engine achieves Pearson r = 0.8187 and R-squared = 0.6655. Notice the negative control: Model A on modified data gets R-squared = -0.09, proving that sequence-only models are worse than predicting the mean. Chemical awareness is mandatory."

---

## SLIDE 18: Production and Roadmap: FastAPI Microservice, Docker, and Downstream Simulation

### Slide Metadata
* **Category / Eyebrow**: PRODUCTION & ROADMAP - FASTAPI & SIMULATION
* **Title**: Production and Roadmap: FastAPI Microservice, Docker, and Downstream Simulation
* **Subtitle**: Containerized Service Architecture, CI/CD Test Automation, and Synergies with C-DAC REMD Lab
* **Badges**: FASTAPI MICROSERVICE, DOCKER MULTI-STAGE, 7 CI/CD TEST SUITES

### Slide Content
#### Production Microservice Endpoints (Port 8000)
* <code>POST /rank</code> & <code>POST /rank/upload</code>: Naked sequence screening via Model A (< 1 ms/seq).
* <code>POST /single-mod</code> & <code>POST /multi-mod-scan</code>: Real-time chemical modification optimization via Model B v4 (< 150 ms).
* <code>POST /offtarget-scan</code>: Sub-microsecond bitwise transcriptome safety audit.
* <code>GET /health</code>: Liveness & readiness probes for Docker container orchestration.

#### Downstream Synergy with C-DAC MD Simulation Lab
> **CDAC Mentor Research Alignment**: Dr. Vinod Jani (Mentor)  
> *Citation*: Microsecond Scale REMD Simulation, J. Biomol. Struct. Dyn. (2011)  
As Vinod sir's work in microsecond Replica Exchange Molecular Dynamics (REMD) has shown, all-atom physical simulation is the ultimate ground truth for free-energy landscapes, but it cannot screen 10,000 candidates.
<p style='margin-top:8px;'>**The Triage Funnel:** HelixZero functions as the high-throughput computational funnel (filtering millions of sequences down to top leads), which can then be fed directly into Dr. Vinod Jani's microsecond REMD and free-energy perturbation (FEP) pipelines for atomistic validation.
<p style='margin-top:8px;'>**Future Horizons:** Active learning retraining on newly published clinical duplex assays and integrating Uni-Mol 1B structural embeddings.

### Spoken Talk Track (Presenter Notes)
> "Finally, Slide 18 presents our production deployment and future horizons. Our FastAPI service is packaged into a multi-stage Docker container with 7 automated CI/CD test suites. Looking forward, as Vinod sir's work in microsecond REMD has shown, all-atom simulation is the ultimate ground truth. HelixZero serves as the high-throughput computational funnel, delivering the top Pareto-optimal candidates directly to C-DAC's atomistic MD pipelines. Thank you very much, I am now open to your questions and feedback."

---
