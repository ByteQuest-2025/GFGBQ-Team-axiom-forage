import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Robust import to handle both package and script execution
try:
    from ..models.emergency_model import EmergencyModel
except ImportError:
    # If running directly or path not set correctly
    file_path = Path(__file__).resolve()
    # Go up to 'backend' directory
    root_path = file_path.parent.parent.parent
    if str(root_path) not in sys.path:
        sys.path.append(str(root_path))
    from app.models.emergency_model import EmergencyModel

class ForecastService:
    def __init__(self):
        # Initialize the Multi-Output Model
        self.model = EmergencyModel()
        
    def get_predictions_and_resources(self, hospital_data, backend_context):
        """
        Main engine that glues Internal + External data, gets ML deltas,
        and computes exact resource numbers.
        """
        # 1. Construct the exact 11-feature vector required by the ML Contract
        feature_vector = {
            "icu_occupancy_pct": hospital_data['icu_occupied'] / hospital_data['icu_total'],
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
        
        # 2. ML Inference (Returns Risk Score and % Increase Deltas)
        # We wrap in a DataFrame because Scikit-learn expects 2D input
        df_vector = pd.DataFrame([feature_vector])
        ml_output = self.model.predict(df_vector)
        
        # 3. Decision Logic (Backend Calculation of Resource Numbers)
        
        # BEDS: Total ICU Capacity * Expected ICU Increase %
        additional_beds = np.ceil(
            hospital_data['icu_total'] * ml_output['expected_icu_increase_pct']
        )
        
        # STAFF: (New Total Patients / Ratio) - Current Staff
        # Standard clinical ratio: 1 staff per 10 patients
        total_expected_patients = hospital_data['daily_patients'] * (1 + ml_output['expected_er_increase_pct'])
        ideal_staff_count = np.ceil(total_expected_patients / 10)
        additional_staff = ideal_staff_count - hospital_data['staff_on_duty']
        
        # 4. Final Risk Categorization (Feature 4)
        risk_score = ml_output['risk_score']
        if risk_score > 0.75:
            alert = "Critical"
        elif risk_score > 0.50:
            alert = "High"
        elif risk_score > 0.30:
            alert = "Elevated"
        else:
            alert = "Normal"

        # 5. Build Final Response for Frontend
        return {
            "risk_analysis": {
                "score": round(risk_score * 100, 1),
                "alert_level": alert,
                "er_surge_prediction": f"+{round(ml_output['expected_er_increase_pct'] * 100, 1)}%",
                "icu_surge_prediction": f"+{round(ml_output['expected_icu_increase_pct'] * 100, 1)}%"
            },
            "resource_requirements": {
                "beds_to_prepare": int(max(0, additional_beds)),
                "staff_to_summon": int(max(0, additional_staff)),
                "supply_alert": "Low" if (ml_output['expected_er_increase_pct'] > 0.2 and hospital_data['oxygen_status'] == 'low') else "Stable"
            },
            "recommendations": self.get_recommendations(alert)
        }

    def get_recommendations(self, alert_level):
        """
        FEATURE 5: Mapping Alert Levels to Protocol-Based Actions
        """
        recs = {
            "Critical": [
                "URGENT: Activate Surge Staffing (Level 3)",
                "Immediately divert non-critical ambulances",
                "Suspend all elective surgeries for 48 hours",
                "Open emergency overflow wards"
            ],
            "High": [
                "Call in on-call nursing staff",
                "Expedite discharge for medically fit patients",
                "Prioritize ICU bed turnaround",
                "Review oxygen and PPE inventory levels"
            ],
            "Elevated": [
                "Monitor ICU bed availability every 2 hours",
                "Brief shift leads on expected intake increase",
                "Ensure trauma units are on standby",
                "Conduct routine equipment checks"
            ],
            "Normal": [
                "Standard shift rotations",
                "Routine maintenance and equipment checks",
                "No change to elective schedules",
                "Maintain standard community health monitoring"
            ]
        }
        return recs.get(alert_level, ["Continue standard monitoring"])