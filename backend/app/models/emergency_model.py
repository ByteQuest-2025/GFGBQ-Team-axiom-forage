import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)


class EmergencyModel:
    """
    ML Model Wrapper with strict contract enforcement.
    
    CONTRACT:
    - Input: 11 features (ordered vector)
    - Output: 3 numeric predictions (risk_score, er_increase_pct, icu_increase_pct)
    - Backend derives: risk_level, resource counts, recommendations
    """
    
    # Exact feature contract (order matters!)
    FEATURE_CONTRACT = [
        "icu_occupancy_pct",
        "daily_patients",
        "staff_on_duty",
        "oxygen_low",
        "medicine_low",
        "temp_max",
        "rain_mm",
        "weather_severity",
        "is_weekend",
        "is_festival",
        "seasonal_illness_weight"
    ]
    
    # Fallback values if model fails
    FALLBACK_PREDICTIONS = {
        "risk_score": 0.5,  # Elevated risk
        "expected_er_increase_pct": 0.15,
        "expected_icu_increase_pct": 0.10
    }
    
    def __init__(self):
        # Setting up paths relative to the project structure
        self.base_dir = Path(__file__).parent.parent.parent
        self.model_dir = self.base_dir / 'saved_models'
        self.model_path = self.model_dir / 'stress_model.pkl'
        self.model = None
        self.model_status = "not_loaded"

    def load_model(self):
        """Loads the trained .pkl file if available."""
        if self.model is None:
            if self.model_path.exists():
                try:
                    self.model = joblib.load(self.model_path)
                    self.model_status = "loaded"
                    logger.info(f"✅ ML Model loaded from {self.model_path}")
                except Exception as e:
                    self.model_status = "load_failed"
                    logger.error(f"❌ Failed to load model: {e}")
                    raise FileNotFoundError(f"Model file corrupted or incompatible at {self.model_path}")
            else:
                self.model_status = "not_found"
                logger.error(f"❌ Model file not found at {self.model_path}")
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
        # Must match FEATURE_CONTRACT exactly
        X = df[self.FEATURE_CONTRACT]
        
        # Y: The Multi-Output Contract (Numeric Only)
        target_cols = [
            'risk_score', 
            'expected_er_increase_pct', 
            'expected_icu_increase_pct'
        ]
        
        y = df[target_cols]

        # Multi-output Random Forest Regressor
        logger.info("🚀 Starting Multi-Output Training...")
        self.model = RandomForestRegressor(n_estimators=150, random_state=42)
        self.model.fit(X, y)
        
        # Ensure directory exists and save
        self.model_dir.mkdir(exist_ok=True)
        joblib.dump(self.model, self.model_path)
        self.model_status = "loaded"
        logger.info(f"✅ Stress Model saved successfully at {self.model_path}")

    def predict(self, feature_df: pd.DataFrame) -> dict:
        """
        FEATURE: Multi-Target Inference with Fallback
        Predicts Risk and Percent Increases based on feature vector.
        
        Returns ONLY numeric values. Backend derives text fields.
        
        Args:
            feature_df: DataFrame with 11 features matching FEATURE_CONTRACT
            
        Returns:
            {
                "risk_score": float (0.0-1.0),
                "expected_er_increase_pct": float (0.0-1.0),
                "expected_icu_increase_pct": float (0.0-1.0),
                "is_fallback": bool
            }
        """
        try:
            self.load_model()
            
            # Validate feature contract
            if list(feature_df.columns) != self.FEATURE_CONTRACT:
                raise ValueError(
                    f"Feature mismatch. Expected: {self.FEATURE_CONTRACT}, "
                    f"Got: {list(feature_df.columns)}"
                )
            
            # ML Inference
            prediction = self.model.predict(feature_df)[0]
            
            # Return ONLY numeric values (backend derives everything else)
            result = {
                "risk_score": round(float(prediction[0]), 3),
                "expected_er_increase_pct": round(float(prediction[1]), 3),
                "expected_icu_increase_pct": round(float(prediction[2]), 3),
                "is_fallback": False
            }
            
            logger.info(f"✅ ML Prediction: risk={result['risk_score']}")
            return result
            
        except Exception as e:
            # FALLBACK LOGIC: System continues even if ML fails
            logger.error(f"❌ ML Model failed: {e}. Using fallback predictions.")
            
            return {
                **self.FALLBACK_PREDICTIONS,
                "is_fallback": True
            }
    
    def get_status(self) -> dict:
        """
        Get model status for health checks.
        
        Returns:
            Status dict with model availability and version
        """
        return {
            "status": self.model_status,
            "model_path": str(self.model_path),
            "model_exists": self.model_path.exists(),
            "feature_count": len(self.FEATURE_CONTRACT),
            "output_count": 3
        }


# Script to run training manually
if __name__ == "__main__":
    model_wrapper = EmergencyModel()
    
    # Robustly find data path relative to this file
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_path = base_dir / 'data' / 'processed' / 'enhanced_processed_hospital_data.csv'
    
    if data_path.exists():
        model_wrapper.train(str(data_path))
    else:
        print(f"❌ Data file not found at: {data_path}")
        print("Please run 'python backend/app/utils/preprocessing.py' first to generate the data.")