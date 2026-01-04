import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth.security import get_password_hash

try:
    print("Testing hash...")
    pw = "admin123"
    hashed = get_password_hash(pw)
    print(f"Hash success: {hashed[:10]}...")
except Exception as e:
    print(f"Hash failed: {e}")
    import traceback
    traceback.print_exc()
