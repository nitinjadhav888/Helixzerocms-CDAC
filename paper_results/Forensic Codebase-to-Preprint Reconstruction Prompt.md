# ROLE

Act as a **senior computational biology researcher, ML researcher, scientific manuscript author, code auditor, dataset auditor, and reproducibility expert**.

Your task is to reconstruct a complete scientific preprint for **my actual implemented model/project** from the entire Antigravity workspace.

This is NOT a creative writing task.

This is NOT a generic paper-generation task.

This is NOT an opportunity to infer missing methodology.

Every technical statement, dataset statistic, architecture component, benchmark result, preprocessing step, training configuration, evaluation metric, and claim must be grounded in:

1. the actual project codebase,
2. the actual generated/intermediate/final datasets,
3. experiment outputs/logs/checkpoints/configurations,
4. documentation contained in the workspace,
5. the benchmark/literature mapping documents I provide,
6. the reference preprint ONLY for scientific organization, section structure, methodological presentation style, level of detail, and figure/table organization.

The final manuscript must describe **OUR MODEL AND OUR WORK ONLY**.

---

# 1. PRIMARY OBJECTIVE

Create a publication-quality preprint for our siRNA efficacy/modeling project by performing a complete forensic reconstruction of the project from the codebase.

The reference preprint is:

`D:\Helixx\paper_results\2026.06.13.732049v2.full.pdf`

The benchmark/literature evidence document is:

`D:\Helixx\literature_source_mapping_and_benchmarks_report.pdf`

Additional manuscript/project documentation is located at:

`D:\Helixx\helixzero_ieee_v5\docs`

You must inspect these resources deeply.

The reference preprint must be treated as a **structural and methodological-writing template**, NOT as a source of facts about our project.

DO NOT copy sentences, paragraphs, claims, numbers, dataset descriptions, architecture descriptions, experimental results, or conclusions from the reference paper.

You may reproduce the **scientific organization and style of presentation**, but all scientific content must be independently reconstructed from OUR project.

---

# 2. FIRST: FORENSICALLY INVENTORY THE ENTIRE WORKSPACE

Before writing even one sentence of the manuscript, inspect the complete project workspace.

Do not rely only on README files.

Recursively inspect:

- Python files
- notebooks
- configuration files
- YAML/JSON files
- CSV/TSV files
- NPZ/PKL/PT/PTH files
- model checkpoints
- preprocessing scripts
- training scripts
- inference scripts
- evaluation scripts
- benchmark scripts
- dataset-generation scripts
- feature-engineering scripts
- data-cleaning scripts
- split-generation scripts
- plotting scripts
- experiment logs
- result files
- generated tables
- generated figures
- documentation
- supplementary material
- shell scripts
- SLURM scripts
- environment files
- requirements files
- Git history where useful
- model architecture definitions
- saved hyperparameters
- output directories
- experiment metadata
- comments/docstrings where they reveal implementation details

Do not assume that a file is irrelevant because it appears auxiliary.

Build an internal map of the complete project.

---

# 3. CREATE A CODEBASE EVIDENCE MAP BEFORE MANUSCRIPT WRITING

Create an internal evidence table with at least these columns:

| Manuscript Claim/Component | Exact Source File | Function/Class/Section | Evidence | Verified? | Confidence |
|---|---|---|---|---|---|

Every important manuscript statement must eventually map to evidence.

For example:

- dataset size → exact dataset file/statistics script
- number of sequences → dataset-generation/counting code
- modification types → preprocessing/dataset files
- genes → dataset metadata
- cell lines → metadata/dataset
- target genes → dataset metadata
- sequence length → preprocessing code
- feature dimensions → feature-generation/model input code
- embedding dimension → embedding generation/model code
- model layers → architecture implementation
- number of parameters → model definition/checkpoint/log
- optimizer → training script
- learning rate → config/training code
- batch size → config/training code
- epochs → training script/log
- early stopping → training implementation
- loss → training implementation
- train/validation/test split → split code
- leakage prevention → split/deduplication code
- benchmark results → actual evaluation outputs
- metrics → evaluation scripts
- hardware → execution logs/configuration
- random seeds → experiment configuration
- runtime → logs where available

If evidence cannot be located, mark the item:

`NOT VERIFIED`

Do NOT fill the gap with assumptions.

---

# 4. READ THE REFERENCE PREPRINT LINE-BY-LINE

Read:

`D:\Helixx\paper_results\2026.06.13.732049v2.full.pdf`

from beginning to end.

Do not only read the abstract, introduction, or methods.

Extract its complete manuscript architecture:

- title structure
- abstract structure
- keyword style
- introduction progression
- problem statement
- literature-gap presentation
- contribution list
- figure placement
- Materials and Methods organization
- dataset description
- preprocessing
- quality control
- architecture description
- feature encoding
- training setup
- evaluation strategy
- benchmark methodology
- external validation
- interpretability
- ablation studies
- optimization/design experiments
- results organization
- discussion
- limitations
- conclusions
- data/code availability
- supplementary organization

Create an internal **Reference Paper Structure Blueprint**.

For every section, record:

1. section title,
2. purpose,
3. information expected in that section,
4. order of information,
5. level of technical detail,
6. figures/tables associated with it,
7. types of quantitative evidence used.

Then construct our manuscript using the analogous structure.

---

# 5. VERY IMPORTANT: DO NOT COPY THE REFERENCE PAPER

The reference paper is a **structural template only**.

Allowed:

- similar section organization
- similar scientific narrative progression
- similar level of methodological detail
- similar placement of dataset/architecture/evaluation explanations
- similar style of describing experiments
- similar logical progression from problem → method → validation → results

Forbidden:

- copying sentences
- paraphrasing paragraph-by-paragraph merely to disguise copying
- copying numerical values
- copying their dataset descriptions
- copying their architecture
- copying their benchmark results
- copying their claims
- copying their experimental setup
- copying their biological conclusions
- copying their figures
- copying their tables
- presenting their methods as ours
- fabricating analogous experiments merely because they performed them

Every scientific fact must come from OUR project.

---

# 6. RECONSTRUCT OUR ACTUAL MODEL

Determine exactly what our model actually does.

Do not describe what you think the model SHOULD do.

Describe what the implementation actually does.

Extract:

### Input

- input sequence type
- guide/passenger representation
- sequence length
- nucleotide alphabet
- chemical modification representation
- modification positions
- target gene information
- target transcript information
- cell-line information
- concentration information
- experimental metadata
- structural features
- thermodynamic features
- embeddings
- any other input

### Preprocessing

Determine exactly:

- sequence cleaning
- normalization
- canonicalization
- missing-value handling
- duplicate removal
- filtering
- alignment
- sequence validation
- modification encoding
- target matching
- feature scaling
- embedding generation
- dimensionality reduction if any

### Architecture

Trace the actual model implementation class-by-class.

Report:

- every major module
- input dimensions
- embedding dimensions
- hidden dimensions
- convolution layers
- kernel sizes
- dilation
- attention layers
- transformer blocks
- MLP layers
- activation functions
- normalization
- dropout
- pooling
- residual connections
- fusion mechanism
- prediction head
- output dimension
- number of trainable parameters

Do not use generic language such as “deep neural network” if the code allows a more precise description.

---

# 7. RECONSTRUCT THE DATASETS EXACTLY

Identify every dataset actually used.

For each dataset determine:

- dataset name
- source
- publication/source organization
- accession/source identifier if available
- number of raw records
- number after each filtering stage
- number of unique sequences
- number of unique guide/passenger pairs
- number of genes
- number of transcripts
- number of cell lines
- number of concentrations
- number of modification types
- number of modification patterns
- sequence lengths
- target types
- assay types
- response variable
- response-unit
- missing values
- duplicates
- excluded records
- reason for exclusion

Pay particular attention to our:

- CMSIRNADB
- chemically modified siRNA data
- unmodified siRNA data
- any merged datasets
- external validation datasets
- benchmark datasets
- independently generated test datasets

Do not invent counts.

If the code produces the count, calculate/reproduce the count.

If two files give different counts, investigate why.

Do not silently choose one.

Explain the discrepancy and determine which count corresponds to the final experimental dataset.

---

# 8. DATASET STATISTICS MUST BE REPRODUCIBLE

For every reported number, determine whether it is:

- raw count
- filtered count
- unique count
- sequence-level count
- measurement-level count
- gene-level count
- patient/cell-line-level count
- train count
- validation count
- test count

Do not mix these categories.

For example, never write:

“our dataset contains 10,000 sequences”

if the actual number is 10,000 experimental measurements but only 4,000 unique sequence pairs.

Report the scientifically correct unit.

---

# 9. CHEMICAL MODIFICATION ANALYSIS

Extract the complete chemical modification vocabulary from the actual data.

Determine:

- every modification type
- notation used in the dataset
- modification position encoding
- guide vs passenger modifications
- backbone modifications
- sugar modifications
- nucleotide analogues
- linker modifications
- conjugates
- number of unique modification patterns
- frequency of each modification
- positional distribution

Do not assume that a modification exists because it exists in the reference paper.

Only report modifications actually present in our data/code.

---

# 10. GENE / CELL-LINE / EXPERIMENTAL CONTEXT

Extract actual values from our dataset.

Report:

- number of unique genes
- gene names
- number of cell lines
- exact cell-line names
- concentration levels
- experimental conditions
- assay types
- knockdown/effect measurement
- treatment duration
- biological context

Where useful, provide a supplementary table containing the complete list.

Do not fabricate biological context.

---

# 11. DETERMINE THE TARGET VARIABLE EXACTLY

Trace the target variable from raw data → preprocessing → training → prediction → evaluation.

Determine:

- what the model actually predicts
- exact mathematical definition
- units
- transformation
- normalization
- clipping
- log transformation
- whether it is regression/classification/multitask
- whether multiple heads exist
- whether outputs are combined
- whether predictions are calibrated

Do not describe the model as predicting a different biological endpoint merely because that would sound more appropriate.

---

# 12. DATA SPLITTING AND LEAKAGE AUDIT — CRITICAL

Perform an explicit forensic leakage audit.

This is mandatory.

Trace the actual split implementation.

Determine:

- random split or grouped split
- sequence-level split
- gene-level split
- target-level split
- modification-pattern split
- scaffold/group split if applicable
- train/validation/test proportions
- duplicate handling
- near-duplicate handling
- preprocessing before vs after split
- embedding generation before vs after split
- feature normalization before vs after split
- hyperparameter tuning leakage
- test-set reuse
- benchmark leakage
- external validation contamination
- temporal leakage
- target transcript leakage
- sequence leakage
- chemically modified variant leakage

Explicitly determine whether:

### Exact sequence leakage exists

Can an identical guide/passenger sequence occur in both training and test?

### Near-sequence leakage exists

Can highly similar sequences occur in both?

### Gene leakage exists

Can the same gene occur in both train and test?

### Target-transcript leakage exists

Can sequences targeting the same transcript occur in both?

### Modification-pattern leakage exists

Can the same base sequence with different chemistry occur across splits?

### Experimental replicate leakage exists

Can measurements from the same biological experiment occur across splits?

### Preprocessing leakage exists

Were normalization/statistics/feature selection/embedding-derived information calculated using the complete dataset before splitting?

### Benchmark leakage exists

Was a benchmark dataset used during training, validation, feature engineering, model selection, or hyperparameter optimization?

For each answer, cite the exact code implementing it.

---

# 13. CLASSIFY THE TEST SET HONESTLY

Determine whether our final evaluation is genuinely:

- held-out test
- validation
- cross-validation
- nested CV
- external validation
- zero-shot
- gene-held-out
- sequence-held-out
- chemistry-held-out
- temporal holdout

Do NOT call something “zero leakage” unless the code actually proves it.

Use precise language.

For example:

“sequence-disjoint” is different from “gene-disjoint”.

“gene-disjoint” is different from “fully independent external validation”.

“held-out test set” is different from “cross-validation fold”.

---

# 14. BENCHMARK RECONSTRUCTION

Use:

`D:\Helixx\literature_source_mapping_and_benchmarks_report.pdf`

and the benchmark/evaluation code.

For every benchmark:

- identify the published source
- identify the exact model/version
- identify publication year
- identify original dataset
- identify original task
- identify whether it supports modified siRNA
- identify its expected input format
- identify any sequence-length restriction
- identify whether our implementation calls the original model/server/API
- identify preprocessing adaptations
- identify mapping between our data and benchmark input
- identify exclusions
- identify failed predictions
- identify whether benchmark predictions were generated before/after model development
- identify whether the benchmark itself was used in training
- identify whether the benchmark comparison is zero-shot
- identify whether weights were retrained
- identify whether the comparison is apples-to-apples

NEVER claim “state of the art” unless the evidence actually supports that statement.

Use careful language such as:

“outperformed the evaluated baselines under the specified split and preprocessing protocol”

when that is what the evidence demonstrates.

---

# 15. BENCHMARK LEAKAGE / INDEPENDENCE TABLE

Create an internal table:

| Benchmark | Published Model | Original Training Data | Our Training Data Overlap? | Test Data Overlap? | Zero-Shot? | Retrained? | Leakage Risk | Evidence |
|---|---|---|---|---|---|---|---|---|

This must be completed before writing benchmark claims.

If overlap cannot be established, explicitly say:

`OVERLAP NOT DETERMINED`

Do not assume independence.

---

# 16. REPRODUCE EVERY RESULT

Do not trust numbers found in README files, screenshots, previous notes, or generated prose without tracing them to actual experiment outputs.

For every reported result identify:

- experiment script
- configuration
- dataset version
- split
- random seed
- checkpoint
- metric
- output file
- date/run if available

Where computationally feasible, rerun the evaluation.

If rerunning is impossible, verify against the saved result artifacts.

For every result record:

`RESULT VERIFIED / RESULT NOT VERIFIED / RESULT PARTIALLY VERIFIED`

---

# 17. METRICS

Determine exactly which metrics our experiments use.

Examples may include:

- Pearson correlation
- Spearman correlation
- R²
- RMSE
- MAE
- MSE
- AUROC
- AUPRC
- accuracy
- F1
- top-k hit rate

Only include metrics actually implemented.

Define every metric correctly.

Do not substitute a metric with another merely because the reference paper uses it.

---

# 18. MODEL ABLATIONS

Search the workspace for all ablation experiments.

Determine whether we actually tested:

- sequence-only
- chemistry-only
- metadata-only
- thermodynamic-only
- embedding-only
- combinations
- architecture variants
- feature removal
- embedding replacement
- ensemble vs single model
- other variants

Only include ablations supported by actual experiments.

Calculate percentage performance changes directly from verified results.

---

# 19. TRAINING DETAILS

Extract exact:

- optimizer
- learning rate
- scheduler
- batch size
- epochs
- early stopping
- patience
- loss function
- weight decay
- dropout
- initialization
- random seeds
- number of runs
- cross-validation folds
- hardware
- GPU
- CUDA version if relevant
- PyTorch version if relevant
- Python version if relevant
- training time if recorded

Do not invent hyperparameters.

---

# 20. FIGURES AND TABLES

After understanding the reference preprint, identify the analogous figures/tables needed for OUR manuscript.

Potential categories:

1. graphical overview of our model
2. dataset curation pipeline
3. dataset composition
4. model architecture
5. training/evaluation workflow
6. benchmark comparison
7. predicted vs observed performance
8. ablation study
9. leakage/split visualization
10. embedding analysis if actually performed
11. error analysis
12. external validation if actually performed

Do not automatically create all of these.

Only include figures supported by our actual experiments.

For each proposed figure, identify:

- source data
- generating script
- exact values
- caption
- interpretation

---

# 21. MANUSCRIPT STRUCTURE

Construct our manuscript using a scientifically analogous structure to the reference paper.

Use an appropriate structure such as:

1. Title
2. Abstract
3. Keywords
4. Introduction
5. Contributions
6. Materials and Methods
   - Dataset Collection
   - Dataset Curation
   - Quality Control
   - Data Preprocessing
   - Chemical Modification Representation
   - Feature Engineering
   - Model Architecture
   - Training Procedure
   - Data Splitting
   - Leakage Prevention
   - Evaluation Metrics
   - Benchmark Models
   - Benchmark Preprocessing
   - Ablation Studies
   - External Validation
   - Interpretability/Analysis
7. Results
   - Dataset Overview
   - Main Model Performance
   - Benchmark Comparison
   - Ablation Results
   - Generalization Analysis
   - Error Analysis
   - External Validation
8. Discussion
9. Limitations
10. Conclusion
11. Data and Code Availability
12. References
13. Supplementary Information

However, modify this structure whenever our actual project does not support a section.

Do NOT add fake experiments merely to make the manuscript structurally symmetrical with the reference paper.

---

# 22. INTRODUCTION

Write the Introduction using the reference paper's logical progression:

1. biological/technical problem
2. importance
3. current computational approaches
4. limitations
5. data limitations
6. methodological gap
7. motivation for our approach
8. what our model contributes
9. concise contribution list

But all scientific claims must be supported by appropriate literature.

Do not copy the reference paper's wording.

Use our actual problem and model.

---

# 23. METHODS MUST BE CODE-FAITHFUL

The Methods section must be sufficiently detailed that another researcher could reconstruct our implementation.

For every computational stage explain:

`Input → Transformation → Output`

Include equations when they are genuinely implemented.

For architecture:

`Input → Encoder → Feature transformation → Fusion → Prediction head → Output`

For preprocessing:

`Raw dataset → filtering → normalization → encoding → split → training tensors`

For evaluation:

`Held-out data → prediction → metric calculation → aggregation`

---

# 24. RESULTS MUST BE EVIDENCE-FIRST

Never write a result first and search for supporting evidence afterward.

Instead:

1. find result artifact,
2. verify experiment,
3. identify dataset/split,
4. identify metric,
5. reproduce if possible,
6. then write the result.

Every numerical statement must have a traceable origin.

---

# 25. DO NOT OVERCLAIM

Do NOT automatically use:

- state-of-the-art
- clinically validated
- highly generalizable
- zero-shot
- leakage-free
- production-ready
- experimentally validated
- superior
- robust
- general-purpose

unless our evidence supports the exact claim.

Scientific wording must reflect evidence strength.

Use:

- “we observed”
- “under the evaluated split”
- “in our experiments”
- “the model achieved”
- “the evaluated benchmark”
- “we found”
- “these results suggest”

where appropriate.

---

# 26. DISTINGUISH THREE TYPES OF INFORMATION

Internally classify every statement as:

### A. CODE-VERIFIED

Directly demonstrated by implementation.

### B. EXPERIMENT-VERIFIED

Supported by actual experiment output.

### C. LITERATURE-SUPPORTED

Supported by external published research.

Never present A, B, and C as interchangeable evidence.

---

# 27. BUILD A CLAIM AUDIT

Before finalizing, create:

| Claim | Type | Evidence | Source | Verified |
|---|---|---|---|---|

The manuscript should contain NO unsupported quantitative claims.

---

# 28. FINAL CONSISTENCY AUDIT

Before delivering the manuscript, check:

### Dataset consistency
- Does Abstract dataset count = Methods dataset count = Results dataset count?
- Are sequence counts and measurement counts distinguished?
- Are gene/cell-line/modification counts consistent?

### Architecture consistency
- Does Figure architecture match code?
- Does Methods match implementation?
- Do parameter counts match model?

### Training consistency
- Are optimizer/LR/batch/epochs consistent across Methods, config and logs?

### Evaluation consistency
- Are reported metrics generated by the stated split?
- Is the test set truly held out?

### Benchmark consistency
- Are benchmark results from the correct models?
- Are preprocessing adaptations documented?
- Is zero-shot status correct?

### Leakage consistency
- Are duplicate and near-duplicate handling correctly described?
- Are embeddings/features leakage-safe?
- Is test-set reuse absent?
- Is benchmark overlap understood?

### Citation consistency
- Every external scientific claim has an appropriate reference.
- Benchmark model descriptions cite the original publication.
- Dataset sources are cited.
- No reference-paper content is accidentally attributed to our work.

---

# 29. ZERO-INVENTION RULE

This is an absolute rule.

If something cannot be established from:

- code,
- data,
- logs,
- experiment outputs,
- project documentation,
- or verified literature,

DO NOT INVENT IT.

Instead write internally:

`INSUFFICIENT EVIDENCE`

and identify exactly what is missing.

Do not infer:

- dataset counts
- modification counts
- model dimensions
- training settings
- split methodology
- benchmark performance
- leakage status
- biological interpretation
- validation status

from context or intuition.

---

# 30. IMPORTANT: DO NOT CHANGE THE IMPLEMENTATION TO FIT THE PAPER

The manuscript must describe our actual implementation.

Do not modify code merely to make it resemble the reference paper.

Do not add architecture components simply because the reference paper has them.

Do not add experiments simply because the reference paper has them.

Do not alter our evaluation protocol to manufacture better-looking results.

The paper follows the implementation, NOT the other way around.

---

# 31. REQUIRED OUTPUTS BEFORE WRITING THE FINAL PAPER

First generate these internal/auditable artifacts:

### A. Workspace Inventory

Complete map of relevant files.

### B. Dataset Census

Exact dataset statistics and provenance.

### C. Model Architecture Specification

Code-derived architecture specification.

### D. Experiment Registry

Every major experiment and result.

### E. Leakage Audit

Detailed train/validation/test independence analysis.

### F. Benchmark Provenance Matrix

Published model → source → dataset → overlap → evaluation protocol.

### G. Reference Paper Structure Blueprint

Section-by-section structure extracted from FENNEC.

### H. Claim-Evidence Matrix

Every major manuscript claim mapped to evidence.

Only after these are complete should the manuscript be drafted.

---

# 32. FINAL MANUSCRIPT REQUIREMENT

Write the final manuscript as if it were being submitted for scientific peer review.

It should be:

- technically precise
- reproducible
- evidence-based
- scientifically conservative
- detailed
- internally consistent
- free of unsupported claims
- based exclusively on our actual implementation and experiments

Match the reference preprint's **depth and scientific presentation quality**, not its content.

The final paper should feel like a naturally written independent research paper belonging to our project, not a rewritten version of the reference paper.

---

# 33. FINAL "RED TEAM" REVIEW

After drafting, attack the manuscript as a skeptical reviewer.

Ask:

1. Can every dataset number be reproduced?
2. Can every model component be found in code?
3. Can every reported benchmark result be traced to an experiment?
4. Is the test set genuinely independent?
5. Is there sequence leakage?
6. Is there gene leakage?
7. Is there modification-pattern leakage?
8. Is there preprocessing leakage?
9. Is there benchmark-data overlap?
10. Are any benchmark comparisons unfair?
11. Are any claims stronger than the evidence?
12. Are any experiments described that were never performed?
13. Are any model components described that do not exist?
14. Are any numbers copied or inherited from the reference paper?
15. Could a reviewer reproduce the reported results from the described methodology?

For every failure, fix the manuscript before final output.

---

# 34. ABSOLUTE PRIORITY ORDER

When information conflicts, use this priority:

1. Actual executed code
2. Actual generated dataset/output
3. Experiment logs/checkpoints
4. Project documentation
5. Verified benchmark/literature evidence
6. Reference preprint structure
7. General scientific knowledge

Never reverse this order.

The reference paper can tell you **how to organize and explain a method**.

It cannot tell you **what our method is**.

---

# FINAL INSTRUCTION

Do not rush.

First understand the entire workspace.

Then understand the reference preprint.

Then reconstruct our datasets.

Then reconstruct our model.

Then audit leakage.

Then audit benchmarks.

Then verify experiments.

Then construct the manuscript.

If something is uncertain, investigate the codebase further rather than guessing.

I want a **forensic, code-grounded, publication-quality reconstruction of our actual research**, with the reference preprint serving only as the structural and scientific-writing blueprint.

No invented facts.
No invented numbers.
No copied content.
No unsupported claims.
No silent assumptions.
No fake validation.
No fake zero-leakage claims.
No benchmark misrepresentation.

Every important sentence must be defensible from evidence.