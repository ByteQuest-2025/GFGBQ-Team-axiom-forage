import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..models.emergency_model import EmergencyModel

class ForecastService:
    def __init__(self):
        self.model = EmergencyModel()
        # Path relative to the root folder where you run the server
        from pathlib import Path
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_path = self.base_dir / 'data' / 'processed' / 'processed_hospital_data.csv'

    def generate_7_day_forecast(self):
        """
        Calculates Feature 1, 2, 3, and 4 in a recursive 7-day loop.
        """
        # 1. Load the "Gold Dataset" to get the starting point
        # In a real app, this would query a database.
        try:
            df = pd.read_csv(self.data_path)
        except FileNotFoundError:
            raise Exception(f"Processed data not found at {self.data_path}. Please run training first.")

        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        last_record = df.iloc[-1]
        last_date = last_record['date']
        
        forecast_results = []
        
        # Initial signals for the recursive model
        curr_lag_1 = last_record['Emergency_Visits']
        curr_lag_7 = df.iloc[-7]['Emergency_Visits']
        curr_rolling_3d = df.iloc[-3:]['Emergency_Visits'].mean()

        for i in range(1, 8):
            target_date = last_date + timedelta(days=i)
            
            # Prepare Input for ML Model
            features_df = pd.DataFrame([{
                'day_of_week': target_date.weekday(),
                'is_weekend': 1 if target_date.weekday() >= 5 else 0,
                'lag_1': curr_lag_1,
                'lag_7': curr_lag_7,
                'rolling_3d': curr_rolling_3d
            }])
            
            # FEATURE 1: ML Prediction (Emergency Visits)
            # The model predicts visits based on the patterns it learned.
            prediction = self.model.predict(features_df)[0]
            visits = int(max(0, round(prediction)))
            
            # FEATURE 2: ICU Demand 
            # (Logic: Heuristic based on ~20% of ER visits)
            icu = int(visits * 0.20 + np.random.randint(-1, 2))
            
            # FEATURE 3: Staff Workload Pressure Index (0-100)
            # WEIGHTED FORMULA: ICU patients require 2.5x more staff resources.
            capacity_factor = 0.6  # Scaler to map raw load to a 0-100 scale
            raw_pressure = (visits + (icu * 2.5))
            workload_index = min(100, round(raw_pressure / capacity_factor, 1))
            
            # FEATURE 4: Risk Alerts & Surge Warnings
            # Thresholds derived from the Workload Index
            if workload_index > 85:
                alert = "Critical"
            elif workload_index > 70:
                alert = "High"
            elif workload_index > 45:
                alert = "Elevated"
            else:
                alert = "Normal"

            forecast_results.append({
                "date": target_date.strftime("%Y-%m-%d"),
                "day_name": target_date.strftime("%A"),
                "emergency_visits": visits,
                "icu_demand": max(0, icu),
                "workload_index": workload_index,
                "alert_level": alert
            })

            # Update lag_1 for the next day's prediction (Recursive/Auto-regressive logic)
            curr_lag_1 = visits
            
        return forecast_results

    def get_recommendations(self, alert_level):
        """
        FEATURE 5: Actionable Recommendations Engine
        Based on the predicted Alert Level for decision support.
        """
        recs = {
            "Critical": [
                "URGENT: Activate Surge Staffing (Level 3).",
                "Immediately suspend elective surgeries.",
                "Divert all non-critical ambulances to sister facilities.",
                "Open emergency overflow wards."
            ],
            "High": [
                "Call in on-call nursing staff for next 24 hours.",
                "Expedite discharge of 'Medically Fit' patients.",
                "Prioritize bed cleaning and turnaround.",
                "Brief Trauma units on high intake risk."
            ],
            "Elevated": [
                "Monitor ICU bed availability every 2 hours.",
                "Ensure supply inventory is topped up (PPE, Oxygen).",
                "Advise staff to minimize non-clinical administrative tasks.",
                "Notify shift leads of expected volume increase."
            ],
            "Normal": [
                "Maintain standard shift rotations.",
                "Conduct routine equipment checks.",
                "No immediate change to elective schedules.",
                "Continue standard community health monitoring."
            ]
        }
        return recs.get(alert_level, ["Continue monitoring trends."])