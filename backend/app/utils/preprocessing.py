import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

class DataPreprocessor:
    def __init__(self):
        # Configuration for heuristics used during dataset generation
        self.icu_capacity = 40
        self.staff_patient_ratio = 8  # 1 staff per 8 patients

    def enhance_historical_data(self, raw_csv_path, output_csv_path):
        """
        TRANSFORMATION STEP:
        Converts a simple date/visit CSV into the professional 
        Enhanced Dataset with Internal Stress & External Pressure.
        Generates all 11 features for the ML contract.
        """
        df = pd.read_csv(raw_csv_path)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        n = len(df)

        # --- 1. Internal Operational Data (Client Side) ---
        # Simulating historical occupancy and supply levels
        df['icu_total'] = self.icu_capacity
        df['icu_occupied'] = np.random.randint(15, 39, size=n)
        df['icu_occupancy_pct'] = (df['icu_occupied'] / df['icu_total']).round(2)
        df['daily_patients'] = np.random.randint(80, 200, size=n)  # ER daily arrivals
        df['staff_on_duty'] = np.random.randint(8, 16, size=n)
        
        # Binary status for supply chain
        df['oxygen_low'] = np.random.choice([0, 1], size=n, p=[0.9, 0.1])
        df['medicine_low'] = np.random.choice([0, 1], size=n, p=[0.95, 0.05])

        # --- 2. External Context Data (Backend Side) ---
        df['temp_max'] = np.random.randint(15, 45, size=n)
        df['rain_mm'] = np.random.choice([0, 2, 10, 50], size=n, p=[0.7, 0.15, 0.1, 0.05])
        df['weather_severity'] = df['rain_mm'].apply(lambda x: 0.8 if x > 30 else 0.2)
        
        df['is_weekend'] = df['date'].dt.dayofweek.apply(lambda x: 1 if x >= 5 else 0)
        df['is_festival'] = np.random.choice([0, 1], size=n, p=[0.96, 0.04])
        df['seasonal_illness_weight'] = np.random.uniform(0.1, 0.9, size=n).round(2)

        # --- 3. Generate ML Target Labels (The 'Ground Truth') ---
        # Risk score is a weighted combination of internal and external stress
        df['risk_score'] = (
            0.4 * df['icu_occupancy_pct'] + 
            0.2 * df['weather_severity'] + 
            0.2 * df['is_festival'] + 
            0.2 * df['oxygen_low']
        ).clip(0, 1).round(2)

        # Deltas: Percentage increase based on the risk score
        df['expected_er_increase_pct'] = (df['risk_score'] * 0.4).round(2)
        df['expected_icu_increase_pct'] = (df['risk_score'] * 0.25).round(2)

        df.to_csv(output_csv_path, index=False)
        return output_csv_path

    def create_inference_vector(self, hospital_data, backend_context):
        """
        INFERENCE STEP:
        Used by the API to glue real-time DB data with API context 
        to create the vector the ML model expects (11 features).
        """
        vector = {
            "icu_occupancy_pct": hospital_data['icu_occupied'] / hospital_data['icu_total'],
            "daily_patients": hospital_data['daily_patients'],
            "staff_on_duty": hospital_data['staff_on_duty'],
            "oxygen_low": 1 if hospital_data['oxygen_status'] == 'low' else 0,
            "medicine_low": 1 if hospital_data['medicine_status'] == 'low' else 0,
            
            "temp_max": backend_context['temp_max'],
            "rain_mm": backend_context['rain_mm'],
            "weather_severity": backend_context['weather_severity'],
            "is_weekend": backend_context['is_weekend'],
            "is_festival": backend_context['is_festival'],
            "seasonal_illness_weight": backend_context['seasonal_illness_weight']
        }
        return pd.DataFrame([vector])

# Usage example for training initialization:
if __name__ == "__main__":
    # Resolve paths relative to this file: backend/app/utils/preprocessing.py
    # We want to reach: backend/data/processed/
    base_dir = Path(__file__).resolve().parent.parent.parent # Points to 'backend' dir
    
    raw_path = base_dir / 'data' / 'raw' / 'enhanced_hospital_data.csv'
    processed_path = base_dir / 'data' / 'processed' / 'enhanced_processed_hospital_data.csv'
    
    # Ensure directories exist
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    
    preprocessor = DataPreprocessor()
    
    # Check if input file exists, or warn user
    if raw_path.exists():
        preprocessor.enhance_historical_data(str(raw_path), str(processed_path))
        print(f"✅ Preprocessing Complete. Saved to: {processed_path}")
    else:
        print(f"⚠️ Input file not found at: {raw_path}")
        print("Please ensure 'enhanced_hospital_data.csv' exists in backend/data/raw/")