import sys
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Debugger")

print("--- Starting Diagnostic Check ---")

# 1. Check Python Path
current_dir = Path.cwd()
print(f"Current Directory: {current_dir}")
sys.path.append(str(current_dir))
print(f"Python Path: {sys.path}")

# 2. Check Dependencies
required_packages = ['fastapi', 'uvicorn', 'pandas', 'numpy', 'sklearn', 'joblib']
print("\n[Checking Dependencies]")
for package in required_packages:
    try:
        __import__(package)
        print(f"✅ {package} loaded")
    except ImportError as e:
        print(f"❌ {package} FAILED: {e}")

# 3. Check File Structure
print("\n[Checking Key Files]")
required_files = [
    Path("app/main.py"),
    Path("app/services/forecasting.py"),
    Path("app/models/emergency_model.py"),
    Path("saved_models/emergency_model.pkl")
]

for p in required_files:
    if p.exists():
        print(f"✅ {p} exists")
    else:
        print(f"❌ {p} MISSING")

# 4. Attempt Dry-Run Application Import
print("\n[Attempting App Import]")
try:
    from app.main import app
    print("✅ Successfully imported 'app' from 'app.main'")
except Exception as e:
    print(f"❌ Failed to import app: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Diagnostic Check Complete ---")
