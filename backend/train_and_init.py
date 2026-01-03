import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Ensure we can import backend imports
sys.path.append(str(Path(__file__).parent))

# Import EmergencyModel (assuming it handles relative imports correctly now)
try:
    from app.models.emergency_model import EmergencyModel
except ImportError:
    # Fallback if running from backend/ directly
    sys.path.append(str(Path(__file__).parent))
    from app.models.emergency_model import EmergencyModel

def generate_synthetic_data(output_path):
    print("Generating synthetic data for demonstration...")
    dates = pd.date_range(end=datetime.now(), periods=365)
    
    data = []
    for date in dates:
        # Simple seasonality
        base_visits = 50
        weekend_factor = 1.2 if date.weekday() >= 5 else 1.0
        random_noise = np.random.randint(-10, 15)
        visits = int(base_visits * weekend_factor + random_noise)
        
        data.append({
            'date': date,
            'Emergency_Visits': max(0, visits),
            'Patient Admission Flag': np.random.choice([0, 1], p=[0.7, 0.3]) # Dummy
        })
        
    df = pd.DataFrame(data)
    
    # Save to processed directly as the model expects 'Emergency_Visits' and 'date'
    # Actually model expects 'Emergency_Visits' and date for sorting
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Synthetic data saved to {output_path}")
    return df

if __name__ == "__main__":
    base_dir = Path(__file__).parent
    processed_data_path = base_dir / 'data' / 'processed' / 'processed_hospital_data.csv'
    
    if not processed_data_path.exists():
        print(f"Processed data not found at {processed_data_path}.")
        generate_synthetic_data(processed_data_path)
    
    print("Initializing model training...")
    try:
        model = EmergencyModel()
        model.train(processed_data_path)
        print("Model training completed successfully!")
    except Exception as e:
        print(f"Model training failed: {e}")
