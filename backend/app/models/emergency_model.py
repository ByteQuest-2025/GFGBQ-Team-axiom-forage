import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from pathlib import Path
import os

class EmergencyModel:
    def __init__(self):
        # Setting up paths relative to the project structure
        self.base_dir = Path(__file__).parent.parent.parent
        self.model_dir = self.base_dir / 'saved_models'
        self.model_path = self.model_dir / 'stress_model.pkl'
        self.model = None

    def load_model(self):
        """Loads the trained .pkl file if available."""
        if self.model is None:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
            else:
                raise FileNotFoundError(f"Model file not found at {self.model_path}. Please train the model first.")

    def train(self, data_path):
        """
        FEATURE: Multi-Output Training
        Trains the model on the Enhanced Dataset to predict stress deltas.
        """
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Enhanced dataset not found at {data_path}")

        df = pd.read_csv(data_path)
        
        # X: Features (Internal Stress + External Pressure)
        # Matches the contract: Client Data + Backend API context
        feature_cols = [
            'icu_occupancy_pct', 'staff_on_duty', 
            'oxygen_low', 'medicine_low', 'temp_max', 'rain_mm', 
            'weather_severity', 'is_weekend', 'is_festival', 'seasonal_illness_weight'
        ]
        
        # Y: The Multi-Output Contract
        # We predict the Score and the Deltas for ER and ICU
        target_cols = [
            'risk_score', 
            'expected_er_increase_pct', 
            'expected_icu_increase_pct'
        ]
        
        X = df[feature_cols]
        y = df[target_cols]

        # Multi-output Random Forest Regressor
        print("🚀 Starting Multi-Output Training...")
        self.model = RandomForestRegressor(n_estimators=150, random_state=42)
        self.model.fit(X, y)
        
        # Ensure directory exists and save
        self.model_dir.mkdir(exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"✅ Stress Model saved successfully at {self.model_path}")

    def predict(self, feature_df):
        """
        FEATURE: Multi-Target Inference
        Predicts Risk and Percent Increases based on a single feature vector.
        """
        self.load_model()
        
        # Ensure feature_df columns match the training columns exactly
        prediction = self.model.predict(feature_df)[0]
        
        # Return as a dictionary matching the backend contract
        return {
            "risk_score": round(float(prediction[0]), 3),
            "expected_er_increase_pct": round(float(prediction[1]), 3),
            "expected_icu_increase_pct": round(float(prediction[2]), 3)
        }

# Script to run training manually
if __name__ == "__main__":
    model_wrapper = EmergencyModel()
    
    # Robustly find data path relative to this file
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_path = base_dir / 'data' / 'processed' / 'enhanced_processed_hospital_data_v1.csv'
    
    if data_path.exists():
        model_wrapper.train(str(data_path))
    else:
        print(f"❌ Data file not found at: {data_path}")
        print("Please run 'python backend/app/utils/preprocessing.py' first to generate the data.")