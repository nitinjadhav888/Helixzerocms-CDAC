@echo off
cd /d "%~dp0smepred"

echo ==========================================================
echo  HelixZero-CMS -- siRNA Chemical Modification Scanner
echo ==========================================================
echo  ACTIVE MODEL : HelixZero IEEE v5 Hierarchical Multi-Module Pipeline
echo  STATUS       : All 5 Phases Audited, Implemented & Verified
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
