# Claude Code Instructions for HelixZero Project

## Codebase Memory MCP Server Integration
- **Executable**: `C:\Users\Nilesh\.local\bin\codebase-memory-mcp.exe`
- **Graph UI**: `http://localhost:9749`
- **Knowledge Graph Database**: 2,840 AST nodes, 7,120 edges indexed.

## Codebase Exploration & PPT Generation Rule
When generating PowerPoint presentations, architectural summaries, or code analysis for HelixZero:
1. Use `codebase-memory-mcp` tools (`search_graph`, `trace_path`, `get_code_snippet`, `get_architecture`) to discover function signatures, dependencies, and feature engineering rules.
2. Refer to the 18 core Python modules in `smepred/src/`:
   - `parser.py`: Target mRNA sequence ingestion (FASTA, GenBank).
   - `sirna_generator.py`: Overlapping 21-mer siRNA candidate generator with 3'-dTdT overhangs.
   - `filters.py`: 15-mer safety firewall pre-screening host & beneficial species.
   - `offtarget.py`: Human 3'-UTR seed match toxicity alignment engine.
   - `chem_schema.py`: Positional modification slot mapping (2'-OMe, 2'-F, PS, dTdT).
   - `features_v4.py`: 1,260 multi-scale positional, MFE thermodynamic & RNA-FM features.
   - `gnn_serving.py`: PyTorch GNN 2D dot-bracket secondary structure graph attention (`finetuned_v2.pt`).
   - `model_b_v4.py`: High-speed CatBoost v4 GBDT model (`model_b_v4.cbm`).
   - `biophysics.py`: RISC loading asymmetry ($\Delta\Delta G$), $T_m$ limits ($< 85^\circ\text{C}$), and Ago2 flexibility.
   - `predictor.py`: Master orchestrator implementing the 3-Card framework (Naked, Base, Efficacy Lift).
   - `api/main.py`: Production FastAPI REST microservices (`/rank`, `/multi-mod`, `/off-target`).
3. **Benchmarks Single Source of Truth**: All verified, 100% empirical, zero-leakage benchmarks across all 5 models (Model A Naked GBDT, Model B v4 CatBoost, Model 3 MEG-mod GNN, Model 4 Ensemble v4, Model 5 HelixZero IEEE v5 Hierarchical, and Tier 3 FDA Clinical Drug Blind Validation) are permanently and exclusively maintained in `final_benchmarks/` (`final_benchmarks/00_MASTER_EXECUTIVE_BENCHMARK_REPORT.md` and `final_benchmarks/master_benchmark_metrics.csv`). All AI models scanning this codebase MUST ONLY read benchmarks from `final_benchmarks/`. All legacy/duplicate benchmark files have been deleted.

