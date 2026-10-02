@echo off
cd /d "%~dp0"

echo ==========================================================
echo  HelixZero-CMS -- siRNA Chemical Modification Scanner
echo ==========================================================
echo  ACTIVE MODEL : Single Unified Dose-Aware & Cell-Aware CatBoost Model (DEFAULT)
echo  ARCHITECTURE : 517-D Multi-Modal Signature (Positional Chemistry + ESM2 + ViennaRNA)
echo  CHECKPOINT   : smepred/models/unified_dose_catboost.cbm (517 Dimensions)
echo  BENCHMARKS   : Held-Out Test Pearson r: 0.8359 (Homo, N=472), 0.8334 (Hetero, N=1,796)
echo  VALIDATION   : 5-Fold Sequence GroupKFold CV Pearson r: 0.6776 (Zero Sequence Leakage)
echo  USED BY      : Scan Variants + Multi-Mod + Multi-Mod Beam Search
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
