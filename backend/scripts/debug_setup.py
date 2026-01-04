import sys
import os

# Add parent dir to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

def check_numpy():
    try:
        import numpy
        print(f"✅ Numpy installed: {numpy.__version__}")
    except ImportError:
        print("❌ Numpy NOT installed")
        return False
    return True

def check_db_data():
    from app.database import SessionLocal
    from app.models.hospital import Hospital
    
    db = SessionLocal()
    try:
        hospital = db.query(Hospital).first()
        if hospital:
            print(f"✅ Hospital found: {hospital.hospital_name}")
            print(f"   Daily Patients: {hospital.daily_patients}")
            print(f"   Oxygen Status: {hospital.oxygen_status} (Type: {type(hospital.oxygen_status)})")
            print(f"   Medicine Status: {hospital.medicine_status} (Type: {type(hospital.medicine_status)})")
            
            if hospital.oxygen_status is None:
                print("❌ Oxygen Status is None!")
            if hospital.medicine_status is None:
                print("❌ Medicine Status is None!")
        else:
            print("⚠️ No hospitals found in DB")
    except Exception as e:
        print(f"❌ DB Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("--- Debugging Setup ---")
    if check_numpy():
        check_db_data()
