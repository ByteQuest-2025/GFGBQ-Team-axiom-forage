import urllib.request
import json
import sys

# Ensure this matches the port in your main.py
BASE_URL = "http://127.0.0.1:8001"

def check_endpoint(endpoint, name):
    url = f"{BASE_URL}{endpoint}"
    print(f"Checking {name} at {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            if status_code == 200:
                data = json.load(response)
                
                # Logic to verify the NEW Professional Contract
                if endpoint == "/api/v1/dashboard":
                    # Check if the new structure exists
                    if "data" in data and "risk_analysis" in data["data"]:
                        print(f"✅ {name}: SUCCESS (New Data Contract Verified)")
                        print(f"   -> Risk Score: {data['data']['risk_analysis']['score']}%")
                        print(f"   -> Alert: {data['data']['risk_analysis']['alert_level']}")
                        print(f"   -> Beds Needed: {data['data']['resource_requirements']['beds_to_prepare']}")
                    else:
                        print(f"❌ {name}: FAILED (Missing 'risk_analysis' or 'resource_requirements')")
                        return False
                else:
                    print(f"✅ {name}: SUCCESS")
                
                return True
            else:
                print(f"❌ {name}: FAILED (Status Code: {status_code})")
                return False
    except Exception as e:
        print(f"❌ {name}: ERROR: {e}")
        return False

def run_tests():
    print("--- Axiom Forage Intelligence System: Backend Verification ---")
    
    # 1. Health Check
    health_ok = check_endpoint("/", "Health Check")
    
    # 2. Intelligence Dashboard Data
    dashboard_ok = False
    if health_ok:
        dashboard_ok = check_endpoint("/api/v1/dashboard", "Intelligence Engine")
    
    print("-------------------------------------------------------")
    
    if health_ok and dashboard_ok:
        print("🎉 INTEGRATION SUCCESS: Backend and ML Model are working in sync.")
        sys.exit(0)
    else:
        print("⚠️ INTEGRATION FAILURE: Check if the .pkl model is trained and main.py is running.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()