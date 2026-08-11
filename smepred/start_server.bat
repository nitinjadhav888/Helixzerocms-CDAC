@echo off
cd /d "%~dp0"

echo ==========================================================
echo  HelixZero-CMS — siRNA Chemical Modification Scanner
echo ==========================================================
echo  ACTIVE MODEL : HelixZero IEEE v5 Hierarchical Multi-Module Pipeline (DEFAULT)
echo  Module 1     : 30-Chemistry 20-bit NucSlot Schema (chem_ontology.py)
echo  Module 2     : Intrinsic Potency Engine (CatBoost v5 pIC50 Regressor)
echo  Module 3     : Assay Response Predictor (CatBoost v5 Knockdown % Engine)
echo  Zero Sequence Leakage Test Pearson r  : 0.8358 (MAE 9.68%)
echo  Used by     : Scan Variants + Multi-Mod + Multi-Mod Beam Search
echo ==========================================================
echo.
echo Installing / verifying dependencies...
python -m pip install -r requirements.txt --quiet
echo.
echo Starting HelixZero-CMS API on http://localhost:8000
echo The browser will open automatically.
echo Press Ctrl+C to stop.
echo.
start "HelixZero-CMS API" cmd /k "uvicorn api.main:app --reload --port 8000"
timeout /t 2 /nobreak >nul
start "" http://localhost:8000
pause
