# 25. FUTURE WORK & RESEARCH ROADMAP
## Planned Extensions, Experimental Directions, and Architecture Upgrades
**Status:** `PLANNED / NOT CURRENTLY IMPLEMENTED`  

---

### 1. Architectural & Machine Learning Extensions

1. **Stereopure Phosphorothioate Modeling:**
   - *Objective:* Train chiral-specific GBDT branches on emerging stereopure oligonucleotide datasets to predict differential exonuclease cleavage and Ago2 catalytic acceleration between $R_p$ and $S_p$ configurations.
   - *Status:* `PLANNED / NOT CURRENTLY IMPLEMENTED`.

2. **Extrahepatic PK/PD Multi-Task Regression:**
   - *Objective:* Expand the continuous covariate space to include tissue-specific pharmacokinetic distributions for central nervous system (CNS, intrathecal), pulmonary (inhalation), and ocular deliveries.
   - *Status:* `PLANNED / NOT CURRENTLY IMPLEMENTED`.

3. **Active Learning Experimental Loop:**
   - *Objective:* Interface HelixZero with high-throughput automated solid-phase synthesis workcells (e.g. ChemSpeed, Biolytic) to propose batch candidate libraries and ingest real-time RT-qPCR readouts into an iterative active learning loop.
   - *Status:* `PLANNED / NOT CURRENTLY IMPLEMENTED`.

---

### 2. Algorithmic & Platform Enhancements

1. **3D Docking with Molecular Dynamics:**
   - *Objective:* Couple the current fast A-form PDB coordinate generator with OpenMM or Amber molecular dynamics relaxation to simulate Ago2-duplex binding free energy in explicit solvent.
   - *Status:* `EXPERIMENTAL / PROTOTYPE`.

2. **Whole-Genome Human Genetic Variation Integration:**
   - *Objective:* Cross-reference target mRNA transcripts against gnomAD and ClinVar variant databases to ensure candidate siRNAs do not target polymorphic loci subject to population-level resistance mutations.
   - *Status:* `PLANNED / NOT CURRENTLY IMPLEMENTED`.

3. **Multi-Species Conservation Screening:**
   - *Objective:* Automated cross-species alignment against cynomolgus monkey (*Macaca fascicularis*), mouse (*Mus musculus*), and rat (*Rattus norvegicus*) transcriptomes to identify 100% homologous duplexes for preclinical toxicology studies.
   - *Status:* `PLANNED / NOT CURRENTLY IMPLEMENTED`.
