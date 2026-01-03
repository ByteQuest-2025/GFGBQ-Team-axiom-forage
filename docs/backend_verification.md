# Backend Verification Guide

This document provides instructions on how to verify that the **Axiom Forage Backend API** is running correctly.

## Prerequisites

1.  **Python Installed**: Ensure Python is added to your PATH.
2.  **Dependencies Installed**: Run `pip install -r backend/requirements.txt` if you haven't already.

## 1. Start the Backend Server

You must have the backend server running before executing the verification script.

**Option A: Using the Batch Script (Windows)**
Double-click `backend/start_backend.bat` or run it from the command line:
```bash
backend\start_backend.bat
```

**Option B: Manual Start**
Open a terminal in the project root:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
*You should see output indicating the server is running at http://0.0.0.0:8001*

## 2. Run the Verification Script

Open a **new** terminal window (keep the server running in the first one) and run the test script:

```bash
python backend/test_backend.py
```

## 3. Interpreting Results

### Success Output
```text
--- Starting Hospital Intelligence API Verification ---
Checking Health Check at http://127.0.0.1:8001/...
✅ Health Check: SUCCESS
Checking Dashboard Forecast at http://127.0.0.1:8001/api/v1/dashboard...
✅ Dashboard Forecast: SUCCESS
-------------------------------------------------------
🎉 ALL CHECKS PASSED: Backend is functioning correctly.
```

### Failure Cases

**Connection Failed**
```text
❌ Health Check: Connection Failed. Is the server running?
```
*Solution*: Ensure the backend server window is open and shows "Uvicorn running on ...". Check if port 8001 is occupied.

**Dashboard Error**
```text
❌ Dashboard Forecast: FAILED (Status Code: 500)
```
*Solution*: This usually means the data file or model is missing.
1. Run `python backend/train_and_init.py` to regenerate data and train the model.
2. Restart the backend server.

## 4. Manual API Check

You can also visit the interactive API documentation in your browser:

*   **Docs**: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
*   **Health Check**: [http://127.0.0.1:8001/](http://127.0.0.1:8001/)
*   **Dashboard JSON**: [http://127.0.0.1:8001/api/v1/dashboard](http://127.0.0.1:8001/api/v1/dashboard)
