import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine
from sqlalchemy import inspect

def check_schema():
    print(f"Connecting to: {engine.url}")
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns('predictions')
        print("Columns in 'predictions' table:")
        for column in columns:
            print(f"- {column['name']} ({column['type']})")
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    check_schema()
