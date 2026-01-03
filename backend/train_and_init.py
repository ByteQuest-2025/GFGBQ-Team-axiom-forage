import sys
from pathlib import Path

# Ensure paths are set up correctly
base_dir = Path(__file__).resolve().parent
sys.path.append(str(base_dir))

# Import specific modules
try:
    from app.models.emergency_model import EmergencyModel
    from app.utils.preprocessing import DataPreprocessor
except ImportError:
    # Fallback to local import if structure differs
    sys.path.append(str(base_dir.parent))
    from app.models.emergency_model import EmergencyModel
    from app.utils.preprocessing import DataPreprocessor

if __name__ == "__main__":
    print("--- Starting Backend Initialization ---")
    
    # 1. Define Paths
    raw_data_path = base_dir / 'data' / 'raw' / 'enhanced_hospital_data.csv'
    processed_data_path = base_dir / 'data' / 'processed' / 'enhanced_processed_hospital_data.csv'
    
    # Ensure directories exist
    raw_data_path.parent.mkdir(parents=True, exist_ok=True)
    processed_data_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 2. Check Data
    # If the processed data doesn't exist, we generate it using the robust Preprocessor
    if not processed_data_path.exists():
        print("Processed data not found. Running Data Preprocessor...")
        
        # Create a dummy raw file if it doesn't exist, just to satisfy the preprocessor
        if not raw_data_path.exists():
            print("Creating dummy raw data to bootstrap the system...")
            import pandas as pd
            dates = pd.date_range(start='2024-01-01', periods=365)
            df = pd.DataFrame({'date': dates})
            df.to_csv(raw_data_path, index=False)
            
        preprocessor = DataPreprocessor()
        preprocessor.enhance_historical_data(str(raw_data_path), str(processed_data_path))
    else:
        print(f"✅ Found existing processed data at {processed_data_path}")
    
    # 3. Train Model
    print("Initializing model training...")
    try:
        model = EmergencyModel()
        model.train(str(processed_data_path))
        print("✅ Model training completed successfully!")
    except Exception as e:
        print(f"❌ Model training failed: {e}")
        import traceback
        traceback.print_exc()
