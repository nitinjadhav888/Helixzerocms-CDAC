# Claude Code Instructions for HelixZero Project

## Codebase Memory MCP Server Integration
- **Executable**: `C:\Users\Nilesh\.local\bin\codebase-memory-mcp.exe`
- **Graph UI**: `http://localhost:9749`
- **Knowledge Graph Database**: 2,840 AST nodes, 7,120 edges indexed.

## Codebase Exploration & PPT Generation Rule
When generating PowerPoint presentations, architectural summaries, or code analysis for HelixZero:
1. Use `codebase-memory-mcp` tools (`search_graph`, `trace_path`, `get_code_snippet`, `get_architecture`) to discover function signatures, dependencies, and feature engineering rules.
2. Refer to the core Python modules in `smepred/src/`:
   - `parser.py`: Target mRNA sequence ingestion (FASTA, GenBank).
   - `sirna_generator.py`: Overlapping 21-mer siRNA candidate generator with 3'-dTdT overhangs.
   - `filters.py`: 15-mer safety firewall pre-screening host & beneficial species.
   - `offtarget.py`: Human 3'-UTR seed match toxicity alignment engine (2-bit binary hash).
   - `chem_schema.py`: Positional modification slot mapping (2'-OMe, 2'-F, PS, 5'-VP, GalNAc, etc.).
   - `features_v4.py`: 517-D continuous multi-modal feature vectorization (444 chemical slots, 64 RNA-FM, 5 ViennaRNA, 4 dose covariates).
   - `model_b_v4.py`: Production Single Unified Dose-Aware CatBoost model (`model_b_v4.cbm`, 517-D).
   - `biophysics.py`: Deterministic 4-domain biophysical penalties (thermodynamic unwinding, serum exonuclease, TLR7/8, cytotoxicity).
   - `modification_engine.py`: Single-modification scanner and heuristic multi-modification beam search optimizer.
   - `pdb_generator.py`: Continuous A-form double-helix 3D structural coordinate generator (504 atoms) mapping chemistry to B-factors.
   - `api/main.py`: Production FastAPI REST microservice (`/rank`, `/single-mod`, `/multi-mod-scan`, `/multi-mod-from-single`, `/offtarget-scan`).
3. **Production Architecture Consolidation**: The active production stack runs strictly on the **Single Unified Dose-Aware CatBoost Model** (517-D). Historical architectures (IEEE v5 cascading two-stage $pIC_{50} \to \text{Hill}$, MEG-mod GNN, 85/15 ensemble) are retired from the runtime path and preserved solely in `helixzero_ieee_v5/` and `MEG-mod-main/` for ablation reproducibility.
4. **Authoritative Sources of Truth**:
   - Benchmarks: `final_benchmarks/` (`final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md` and `master_benchmark_metrics.csv`).
   - System Documentation & Specifications: `docs/` (`docs/00_MASTER_SYSTEM_ARCHITECTURE.md` to `05_AUTHORITATIVE_BENCHMARKS_AND_CLINICAL_VALIDATION.md`).

