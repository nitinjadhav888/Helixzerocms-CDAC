# 07. DATA COLLECTION & INGESTION METHODOLOGY
## Primary Data Sources, Assembly Protocols, and Verification
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. Primary Empirical Sources

The empirical datasets assembled in HelixZero originate from verified scientific literature and curated public biological databases:

1. **CMsiRNAdb (Chemical Modification siRNA Database):**
   - *Provenance:* Published in *Nucleic Acids Research* (PMC12870949, Jan 2026).
   - *Contents:* Over 43,000 manually curated siRNA chemical modification records extracted from patent literature, peer-reviewed clinical trials, and pharmacology journals.
   - *Data Extracted:* Sense/antisense sequence strings, non-canonical modification symbols, reported biological knockdown percentage, incubation duration, cell line lineage, and assay concentration (nM).

2. **Novartis High-Throughput siRNA Profiling (Huesken et al., 2005):**
   - *Provenance:* Published in *Nature Biotechnology* 23(8):995–1001.
   - *Contents:* 2,361 unmodified 21-mer siRNAs systematically tiled across 34 human transcripts (including *CDK2*, *PLK1*, *BCL2*, *EGFR*) with standardized real-time RT-qPCR efficacy readouts.

3. **Takayuki Dual-Luciferase Screen (Takayuki et al., 2008):**
   - *Provenance:* Published in *FEBS Letters* 582(13):1920–1924.
   - *Contents:* 702 unmodified 21-mer siRNAs evaluated against dual-luciferase reporter constructs across 70 mammalian genes.

4. **Multi-Dose Pharmacodynamic Screens (Davis et al., 2025):**
   - *Provenance:* Modern automated robotic transfection screens compiled across multi-concentration series (0.001 nM to 10,000 nM).
   - *Contents:* Full concentration-response titration series providing empirical validation data for closed-form Hill kinetics.

5. **NCBI RefSeq Human Transcriptome (GRCh38.p14):**
   - *Provenance:* NCBI RefSeq / Ensembl cDNA database.
   - *Contents:* Comprehensive set of all curated protein-coding and non-coding human transcripts used to construct the 2-bit off-target safety index.

6. **FDA Commercial Drug Regulatory Approval Packages:**
   - *Provenance:* United States Food and Drug Administration (FDA) Center for Drug Evaluation and Research (CDER) clinical pharmacology review documents.
   - *Contents:* Exact chemical modification maps and Phase 3 trial knockdown ranges for Patisiran (NDA 210922), Givosiran (NDA 212194), Lumasiran (NDA 214103), Inclisiran (NDA 214012), Vutrisiran (NDA 215559), and Nedosiran (NDA 215740).

---

### 2. Assembly & Ingestion Protocols

- **Multi-Slot Notation Normalization:** Raw chemical modification strings vary across sources (e.g. Alnylam notation `mU`, `fC`, `s`, `VP` vs. patent notation `2'-OMe-U`, `2'-F-C`, `[thio]`). HelixZero ingests these strings through `smepred/src/chem_schema.py` and `helixzero_ieee_v5/src/chem_ontology.py`, translating non-standard characters into the standardized 30-modification ontology.
- **Transcriptome 2-Bit Compilation:** The raw 449.5 MB FASTA file (`human_transcriptome.fasta`) is pre-processed into a 30-bit packed integer hash index (`human_transcriptome.idx.pkl`) using `smepred/src/offtarget_store.py`, mapping all contiguous 15-mers and 6/7/8-mer seed frequency counts for sub-microsecond query performance.
