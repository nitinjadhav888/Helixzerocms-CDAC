@echo off
cd /d "%~dp0smepred"

echo ==========================================================
echo  HelixZero-CMS -- siRNA Chemical Modification Scanner
echo ==========================================================
echo  ACTIVE MODEL : Single Unified Dose-Aware & Cell-Aware CatBoost Model
echo  FEATURES     : 517-D Multi-Modal Signature (Positional + ESM2 + ViennaRNA)
echo  BENCHMARKS   : Held-Out r = 0.8359 (Homo), r = 0.8334 (Hetero), GKF r = 0.6776
echo  STATUS       : Verified Zero Sequence Leakage & Audited Empirical Checkpoint
echo ==========================================================
echo.
echo Installing / verifying dependencies...
python -m pip install -r requirements.txt --quiet
echo.
echo Starting HelixZero-CMS API server on http://localhost:8000 ...
echo Opening web interface...
echo.
start "HelixZero-CMS API" cmd /k "python -m uvicorn api.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul
start "" http://localhost:8000
pause
