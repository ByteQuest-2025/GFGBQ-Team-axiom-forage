@echo off
cd /d "%~dp0"
echo Starting Backend Initialization...
python -m pip install -r requirements.txt
python train_and_init.py

echo.
echo ========================================================
echo   LAUNCHING AXIOM FORAGE SYSTEM
echo ========================================================
echo 1. Starting FastAPI Server in a new window...
start "Axiom Forage Backend" cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"

echo 2. Waiting 10 seconds for server to start...
timeout /t 10 /nobreak > nul

echo 3. Running Automated Verification...
python test_backend.py

echo 4. Opening Swagger UI in Browser...
start http://127.0.0.1:8001/docs

echo.
echo ========================================================
echo   SYSTEM READY
echo ========================================================
pause
