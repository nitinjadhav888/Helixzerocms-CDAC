# 22. RESEARCH REFERENCES & CODE-TO-PAPER MAPPINGS
## Comprehensive Scientific Literature Foundations and Implementation Traceability
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. Research-to-Implementation Traceability Matrix

Every scientific reference below directly grounds an architectural, feature engineering, or biophysical penalty implementation in the codebase:

```text
===================================================================================================
PAPER CITATION              SCIENTIFIC PROBLEM                HELIXZERO IMPLEMENTATION & CODE
===================================================================================================
1. Khvorova / Schwarz 2003  Thermodynamic Asymmetry Rule      smepred/src/features.py:extract_batch_v4()
   (Cell 115:209-219)       Guide strand selection by Ago2    Delta-Delta-G > 0 requirement
---------------------------------------------------------------------------------------------------
2. Reynolds et al. 2004     Empirical Composition Rules       smepred/src/features.py:extract_batch_v4()
   (Nat Biotechnol 22:326)  GC content, terminal base rules   Reynolds 8-rule scoring matrix
---------------------------------------------------------------------------------------------------
3. Elmén et al. 2005        LNA Catalytic Inactivation        smepred/src/biophysics.py:279-301
   (NAR 33:439-447)         LNA at AS pos 1 abolishes RNAi    +8.0 penalty for AS pos 1 LNA
---------------------------------------------------------------------------------------------------
4. Huesken et al. 2005      Canonical Sequence Screening      smepred/data/oligoformer/Hu.csv
   (Nat Biotechnol 23:995)  qPCR screening across 34 genes    Model A gold-standard training set
---------------------------------------------------------------------------------------------------
5. Bramsen et al. 2009      Seed Region Rigidity Dynamics     smepred/src/features_v2.py:90-96
   (NAR 37:2867-2881)       Bulky sugars in seed cause tox    seed_bulky_rigid_frac feature
---------------------------------------------------------------------------------------------------
6. Schirle & MacRae 2012    Human Ago2 Crystal Structure      smepred/src/biophysics.py:247-251
   (Science 336:1037-1040)  MID pocket requires 5'-phosphate  +5.0 penalty for missing 5'-phosphate
---------------------------------------------------------------------------------------------------
7. Nair et al. 2014         Targeted GalNAc Delivery          smepred/src/features_v2.py:127-134
   (JACS 136:16958-16961)   Trivalent GalNAc on sense 3' end  sense_3p_galnac feature flag
---------------------------------------------------------------------------------------------------
8. Parmar et al. 2016       Phosphate Mimics in Vivo          smepred/src/features_v2.py:110-113
   (ChemBioChem 17:985-989) 5'-VP resists phosphatases        as_pos1_5p_phosphate_mimic feature
---------------------------------------------------------------------------------------------------
9. Janas et al. 2018        Seed-Mediated Cytotoxicity        smepred/src/filters.py:40-120
   (Nat Commun 9:723)       4,096-hexamer HeLa cell death     cell_viability.tsv empirical lookup
---------------------------------------------------------------------------------------------------
10. Sakamuri et al. 2020    Clinical PS Backbone Pattern      smepred/src/biophysics.py:87-108
    (ChemBioChem 21:1-11)   Alnylam AT3 design (4 AS + 2 SS)  Tandem di-PS terminal requirement
---------------------------------------------------------------------------------------------------
11. Chen et al. 2022        RNA Foundation Representations    smepred/src/features_v4.py:134-147
    (bioRxiv: RNA-FM)       100M transformer on 23M ncRNAs    Dual PCA-32 projections (64-D)
---------------------------------------------------------------------------------------------------
12. Davis et al. 2025       Multi-Dose Titration Screens      smepred/data/processed/homo_val.csv
    (Molecular Therapy)     Concentration titration assays    Held-out multi-dose validation lake
===================================================================================================
```

---

### 2. Granular Code-to-Paper Mappings

#### Khvorova / Schwarz 2003 (Cell) $\to$ Thermodynamic Asymmetry
- **Scientific Finding:** Ago2 preferentially loads the siRNA strand with the lower thermodynamic binding stability at its $5'$ end ($\Delta G_{5p} > \Delta G_{3p}$).
- **HelixZero Implementation:** `smepred/src/features.py` computes $\Delta\Delta G^\circ_{37} = \Delta G_{3p} - \Delta G_{5p}$ using nearest-neighbor Turner parameters. In `smepred/src/predictor.py`, duplexes with $\Delta\Delta G < 0$ (passenger strand favored) are penalized or rejected from curated lead sets.

#### Elmén et al. 2005 (NAR) $\to$ LNA Inactivation
- **Scientific Finding:** Incorporating Locked Nucleic Acid (LNA) at position 1 of the antisense strand completely abolishes RNAi activity across multiple targets (*Firefly*, *Renilla*, *NPY*), and cannot be rescued even by 5'-phosphorylation. Furthermore, LNA at positions 10, 12, 14 flanks the Ago2 cleavage site, perturbing the catalytic cleft.
- **HelixZero Implementation:** In `smepred/src/biophysics.py:280-301`, an antisense position 1 LNA receives a heavy $+8.0$ deduction. LNAs at positions 10, 12, and 14 receive weighted penalties of $+4.0, +3.0, +2.0$ respectively.

#### Sakamuri et al. 2020 (ChemBioChem) $\to$ Phosphorothioate Kinetics
- **Scientific Finding:** Clinical optimization of antithrombin (AT3) siRNAs demonstrated that the optimal nuclease-resistant pattern is 4 PS linkages on the antisense strand (positions 0, 1, 20, 21) and 2 PS linkages on the sense strand (positions 0, 1). Dense internal PS linkages impair RISC loading and induce off-target cytotoxicity.
- **HelixZero Implementation:** In `smepred/src/biophysics.py:87-108`, the engine checks terminal vs. internal PS distribution. Duplexes missing terminal PS protection receive nuclease deductions, while duplexes with $> 3$ internal PS linkages in the antisense body receive over-density penalties.

#### Janas et al. 2018 (Nat Commun) $\to$ Seed Cytotoxicity
- **Scientific Finding:** Certain 6-mer seed sequences (nucleotides 2–7 of the guide strand) trigger extensive cell death by down-regulating essential housekeeping genes. This toxicity is mediated through microRNA-like off-target binding and can be chemically mitigated by $2'$-O-methyl substitution at position 2.
- **HelixZero Implementation:** In `smepred/src/filters.py:40-120`, the guide seed is queried against the empirical Janas 4,096-hexamer viability table (`cell_viability.tsv`). Seeds with $< 50\%$ viability are classified as `Toxic` and rejected from lead candidate selection.
