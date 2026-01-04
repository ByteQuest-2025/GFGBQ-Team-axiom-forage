import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models.hospital import Hospital
from app.auth.security import get_password_hash

def create_test_users():
    db = SessionLocal()
    try:
        # 1. Create Admin User
        admin_email = "admin@axiom.com"
        admin = db.query(Hospital).filter(Hospital.email == admin_email).first()
        if not admin:
            print(f"Creating admin user: {admin_email}")
            admin = Hospital(
                email=admin_email,
                hashed_password=get_password_hash("admin123"),
                hospital_name="Axiom Admin",
                location="HQ",
                role="admin",
                icu_total_capacity=0,
                is_active=True
            )
            db.add(admin)
        else:
            print(f"Updating admin user: {admin_email}")
            admin.hashed_password = get_password_hash("admin123")
            admin.role = "admin"
        
        # 2. Create Manager User
        manager_email = "manager@hospital.com"
        manager = db.query(Hospital).filter(Hospital.email == manager_email).first()
        if not manager:
            print(f"Creating manager user: {manager_email}")
            manager = Hospital(
                email=manager_email,
                hashed_password=get_password_hash("manager123"),
                hospital_name="Apollo Jubilee Hills",
                location="Hyderabad",
                role="hospital",
                icu_total_capacity=50,
                is_active=True,
                services=["Emergency", "ICU", "Cardiology", "Neurology"],
                timings={"emergency": "24/7", "opd": "9:00 AM - 8:00 PM"}
            )
            db.add(manager)
        else:
            print(f"Updating manager user: {manager_email}")
            manager.hashed_password = get_password_hash("manager123")
            manager.role = "hospital"
            manager.services = ["Emergency", "ICU", "Cardiology", "Neurology"]
            manager.timings = {"emergency": "24/7", "opd": "9:00 AM - 8:00 PM"}

        db.commit()
        print("✅ Test users created/updated successfully.")
        
    except Exception as e:
        import traceback
        print(f"❌ Error creating test users: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()
