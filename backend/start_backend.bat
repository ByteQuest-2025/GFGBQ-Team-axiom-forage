@echo off
echo Starting Backend Initialization...
python -m pip install -r requirements.txt
python train_and_init.py
echo Starting FastAPI Server...
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
pause
