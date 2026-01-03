import joblib
import pandas as pd
import os
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from ..utils.preprocessing import prepare_features

class EmergencyModel:
    def __init__(self):
        # Dynamically find the path to the saved model
        self.base_dir = Path(__file__).parent.parent.parent
        self.model_path = self.base_dir / 'saved_models' / 'emergency_model.pkl'
        self.model = None

    def train(self, data_path):
        # Load processed data
        df = pd.read_csv(data_path)
        train_df = prepare_features(df)

        # X = Features, y = Target (Emergency Visits)
        features = ['day_of_week', 'is_weekend', 'lag_1', 'lag_7', 'rolling_3d']
        X = train_df[features]
        y = train_df['Emergency_Visits']

        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Save the brain
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")

    def load_model(self):
        if not self.model:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
            else:
                raise FileNotFoundError(f"Model file not found at {self.model_path}")

    def predict(self, features_df):
        self.load_model()
        return self.model.predict(features_df)