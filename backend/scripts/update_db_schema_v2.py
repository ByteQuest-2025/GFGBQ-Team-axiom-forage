import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

def update_schema():
    print("Updating database schema (v2)...")
    with engine.connect() as conn:
        try:
            # Add daily_patients
            conn.execute(text("ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS daily_patients INTEGER DEFAULT 0"))
            print("Added 'daily_patients' column.")
            
            # Add staff_on_duty
            conn.execute(text("ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS staff_on_duty INTEGER DEFAULT 0"))
            print("Added 'staff_on_duty' column.")
            
            # Add oxygen_status
            conn.execute(text("ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS oxygen_status VARCHAR DEFAULT 'Normal'"))
            print("Added 'oxygen_status' column.")
            
            # Add medicine_status
            conn.execute(text("ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS medicine_status VARCHAR DEFAULT 'Normal'"))
            print("Added 'medicine_status' column.")
            
            conn.commit()
            print("Schema update complete.")
        except Exception as e:
            print(f"Error updating schema: {e}")
            conn.rollback()

if __name__ == "__main__":
    update_schema()
