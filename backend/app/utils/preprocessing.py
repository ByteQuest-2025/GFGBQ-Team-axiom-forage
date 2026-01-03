# Preprocessing Utils
import pandas as pd

def prepare_features(df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # 1. Calendar Features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    # 2. Lag Features (Memory)
    df['lag_1'] = df['Emergency_Visits'].shift(1) # Yesterday's visits
    df['lag_7'] = df['Emergency_Visits'].shift(7) # Same day last week
    
    # 3. Trend Feature
    df['rolling_3d'] = df['Emergency_Visits'].shift(1).rolling(window=3).mean()
    
    return df.dropna() # Remove rows without enough history