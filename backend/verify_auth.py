
import sys
import os
import urllib.request
import urllib.error
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.models.hospital import Hospital
from app.auth.security import create_access_token

def verify_auth():
    db = SessionLocal()
    try:
        # Get a hospital
        hospital = db.query(Hospital).first()
        if not hospital:
            print("❌ No hospital found in database.")
            return

        print(f"Found hospital: {hospital.email}")
        
        # Generate token
        token = create_access_token(data={"sub": hospital.email})
        
        # Make request
        url = "http://127.0.0.1:8001/api/v1/auth/me"
        headers = {"Authorization": f"Bearer {token}"}
        
        req = urllib.request.Request(url, headers=headers)
        
        print(f"Sending GET request to {url}...", flush=True)
        try:
            with urllib.request.urlopen(req) as response:
                print(f"Status Code: {response.status}", flush=True)
                print("START_RESPONSE", flush=True)
                print(response.read().decode('utf-8'), flush=True)
                print("END_RESPONSE", flush=True)
        except urllib.error.HTTPError as e:
            print(f"Status Code: {e.code}", flush=True)
            print("START_RESPONSE", flush=True)
            print(e.read().decode('utf-8'), flush=True)
            print("END_RESPONSE", flush=True)
        except Exception as e:
            print(f"Request failed: {e}", flush=True)
        
    except Exception as e:
        print(f"Error: {e}", flush=True)
    finally:
        db.close()

if __name__ == "__main__":
    verify_auth()
