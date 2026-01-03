import urllib.request
import json
import sys
import time

BASE_URL = "http://127.0.0.1:8001"

def check_endpoint(endpoint, name):
    url = f"{BASE_URL}{endpoint}"
    print(f"Checking {name} at {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            if status_code == 200:
                data = json.load(response)
                print(f"✅ {name}: SUCCESS")
                # print(json.dumps(data, indent=2))
                return True
            else:
                print(f"❌ {name}: FAILED (Status Code: {status_code})")
                return False
    except urllib.error.URLError as e:
        print(f"❌ {name}: Connection Failed. Is the server running? Error: {e}")
        return False
    except Exception as e:
        print(f"❌ {name}: ERROR: {e}")
        return False

def run_tests():
    print("--- Starting Hospital Intelligence API Verification ---")
    
    # Check 1: Health Check
    health_ok = check_endpoint("/", "Health Check")
    
    # Check 2: Dashboard Data
    if health_ok:
        dashboard_ok = check_endpoint("/api/v1/dashboard", "Dashboard Forecast")
    else:
        print("Skipping Dashboard check due to Health Check failure.")
        dashboard_ok = False
        
    print("-------------------------------------------------------")
    
    if health_ok and dashboard_ok:
        print("🎉 ALL CHECKS PASSED: Backend is functioning correctly.")
        sys.exit(0)
    else:
        print("⚠️ SOME CHECKS FAILED: Please inspect the server logs.")
        sys.exit(1)

if __name__ == "__main__":
    # Optional: Wait a moment for server if running via batch script mostly relevant for CI/CD
    # time.sleep(1)
    run_tests()
