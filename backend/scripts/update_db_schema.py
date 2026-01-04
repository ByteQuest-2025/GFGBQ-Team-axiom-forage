import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

def update_schema():
    print("Updating database schema...")
    with engine.connect() as conn:
        # Add role column
        try:
            conn.execute(text("ALTER TABLE hospitals ADD COLUMN role VARCHAR DEFAULT 'hospital'"))
            print("Added 'role' column.")
        except Exception as e:
            print(f"Skipped 'role' column (might exist): {e}")

        # Add services column
        try:
            conn.execute(text("ALTER TABLE hospitals ADD COLUMN services JSON DEFAULT '[]'"))
            print("Added 'services' column.")
        except Exception as e:
            print(f"Skipped 'services' column (might exist): {e}")

        # Add timings column
        try:
            conn.execute(text("ALTER TABLE hospitals ADD COLUMN timings JSON DEFAULT '{}'"))
            print("Added 'timings' column.")
        except Exception as e:
            print(f"Skipped 'timings' column (might exist): {e}")
            
        conn.commit()
    print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
