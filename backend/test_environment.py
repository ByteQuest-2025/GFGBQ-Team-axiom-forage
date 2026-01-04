
import sys
import traceback

try:
    print("Importing numpy...")
    import numpy as np
    print(f"Numpy version: {np.__version__}")

    print("Importing pandas...")
    import pandas as pd
    print(f"Pandas version: {pd.__version__}")

    print("Testing feature assembly logic...")
    
    # Simulate enrich_weather
    weather_data = {
        "temp_max": float(np.random.randint(15, 45)),
        "rain_mm": float(np.random.choice([0, 2, 10, 50])),
        "weather_severity": 0.4
    }
    print("Weather data generated:", weather_data)

    # Simulate dataframe creation
    data = {
        "icu_occupancy_pct": 0.5,
        "daily_patients": 10,
        "staff_on_duty": 5,
        "oxygen_low": 0,
        "medicine_low": 0,
        "temp_max": weather_data["temp_max"],
        "rain_mm": weather_data["rain_mm"],
        "weather_severity": weather_data["weather_severity"],
        "is_weekend": 0,
        "is_festival": 0,
        "seasonal_illness_weight": 0.5
    }
    
    df = pd.DataFrame([data])
    print("DataFrame created successfully:")
    print(df)
    
    print("Environment test PASSED")

except Exception:
    print("Environment test FAILED")
    traceback.print_exc()
    sys.exit(1)
