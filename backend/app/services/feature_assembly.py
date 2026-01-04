"""
Deterministic Feature Assembly Pipeline.

Phase 1: Fetch hospital_daily_status from DB
Phase 2: Derive computed fields (icu_occupancy_pct, oxygen_low, medicine_low)
Phase 3: Enrich with backend-only data (weather, calendar, seasonal)
Phase 4: Validate feature completeness before ML inference
"""

import pandas as pd
from datetime import date, datetime
from sqlalchemy.orm import Session
from typing import Dict, List
import logging

from app.services.cache import cache_service
import os

logger = logging.getLogger(__name__)

CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "3600"))


class FeatureAssembler:
    """
    Assembles and validates ML model features from multiple sources.
    """
    
    # Expected feature contract (must match ML model)
    REQUIRED_FEATURES = [
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
    
    def validate_hospital_data(self, hospital_data: dict) -> None:
        """
        Validate that required hospital fields are present.
        
        Raises:
            ValueError if required fields missing
        """
        required_fields = [
            "icu_occupied",
            "icu_total",
            "daily_patients",
            "staff_on_duty",
            "oxygen_status",
            "medicine_status"
        ]
        
        missing = [f for f in required_fields if f not in hospital_data]
        if missing:
            raise ValueError(f"Missing required hospital fields: {missing}")
        
        logger.debug("✅ Hospital data validation passed")
    
    def derive_fields(self, hospital_data: dict) -> dict:
        """
        Phase 2: Derive computed fields from raw hospital data.
        
        Args:
            hospital_data: Raw hospital metrics
            
        Returns:
            Dictionary with derived fields
        """
        derived = {
            "icu_occupancy_pct": hospital_data["icu_occupied"] / hospital_data["icu_total"],
            "daily_patients": hospital_data["daily_patients"],
            "staff_on_duty": hospital_data["staff_on_duty"],
            "oxygen_low": 1 if hospital_data["oxygen_status"] == "low" else 0,
            "medicine_low": 1 if hospital_data["medicine_status"] == "low" else 0
        }
        
        logger.debug(f"✅ Derived fields: icu_occupancy={derived['icu_occupancy_pct']:.2f}, oxygen_low={derived['oxygen_low']}, medicine_low={derived['medicine_low']}")
        return derived
    
    async def enrich_weather(self, db: Session) -> dict:
        """
        Phase 3a: Fetch weather data from cache or external API.
        
        Args:
            db: Database session for cache
            
        Returns:
            Weather features dict
        """
        cache_key = f"weather_{date.today()}"
        cached = await cache_service.get(cache_key, db)
        
        if cached:
            logger.debug("✅ Weather data from cache")
            return cached
        
        # Simulated weather API call (replace with real API)
        # In production: requests.get(WEATHER_API_URL)
        import numpy as np
        weather_data = {
            "temp_max": float(np.random.randint(15, 45)),
            "rain_mm": float(np.random.choice([0, 2, 10, 50])),
            "weather_severity": 0.4  # Derived from rain/temp
        }
        
        await cache_service.set(cache_key, weather_data, CACHE_TTL, db)
        logger.info(f"✅ Weather data fetched: temp={weather_data['temp_max']}°C, rain={weather_data['rain_mm']}mm")
        
        return weather_data
    
    async def enrich_calendar(self, db: Session) -> dict:
        """
        Phase 3b: Derive calendar features (weekend, festival).
        
        Args:
            db: Database session for festival lookup
            
        Returns:
            Calendar features dict
        """
        cache_key = f"calendar_{date.today()}"
        cached = await cache_service.get(cache_key, db)
        
        if cached:
            logger.debug("✅ Calendar data from cache")
            return cached
        
        today = datetime.now()
        
        # Weekend detection
        is_weekend = 1 if today.weekday() >= 5 else 0
        
        # Festival detection (in production: query DB or external API)
        # Example: SELECT * FROM festivals WHERE date = today
        is_festival = 0  # Default to no festival
        
        calendar_data = {
            "is_weekend": is_weekend,
            "is_festival": is_festival
        }
        
        await cache_service.set(cache_key, calendar_data, CACHE_TTL, db)
        logger.debug(f"✅ Calendar data: weekend={is_weekend}, festival={is_festival}")
        
        return calendar_data
    
    async def enrich_seasonal(self, db: Session) -> dict:
        """
        Phase 3c: Get seasonal illness weight from DB.
        
        Args:
            db: Database session
            
        Returns:
            Seasonal features dict
        """
        # In production: Query seasonal_illness_patterns table
        # Example: SELECT weight FROM seasonal_patterns WHERE month = current_month
        
        current_month = datetime.now().month
        
        # Simplified seasonal logic (replace with DB query)
        # High weight in winter (flu) and monsoon (dengue)
        if current_month in [12, 1, 2]:  # Winter
            weight = 0.8
        elif current_month in [7, 8, 9]:  # Monsoon
            weight = 0.7
        else:
            weight = 0.3
        
        logger.debug(f"✅ Seasonal illness weight: {weight} (month={current_month})")
        
        return {"seasonal_illness_weight": weight}
    
    async def assemble_features(
        self, 
        hospital_data: dict, 
        db: Session
    ) -> pd.DataFrame:
        """
        MASTER PIPELINE: Assemble complete feature vector.
        
        Steps:
        1. Validate hospital data
        2. Derive computed fields
        3. Enrich with weather (API + cache)
        4. Enrich with calendar (logic + DB)
        5. Enrich with seasonal patterns (DB)
        6. Validate feature completeness
        7. Return ordered DataFrame
        
        Args:
            hospital_data: Raw hospital metrics
            db: Database session
            
        Returns:
            DataFrame with 11 features in correct order
            
        Raises:
            ValueError if validation fails
        """
        logger.info("🔧 Starting feature assembly pipeline...")
        
        # Step 1: Validate input
        self.validate_hospital_data(hospital_data)
        
        # Step 2: Derive fields from hospital data
        derived = self.derive_fields(hospital_data)
        
        # Step 3: Enrich with backend-only data
        weather = await self.enrich_weather(db)
        calendar = await self.enrich_calendar(db)
        seasonal = await self.enrich_seasonal(db)
        
        # Step 4: Combine all features
        feature_dict = {
            **derived,
            **weather,
            **calendar,
            **seasonal
        }
        
        # Step 5: Validate completeness
        missing = [f for f in self.REQUIRED_FEATURES if f not in feature_dict]
        if missing:
            raise ValueError(f"Incomplete feature assembly. Missing: {missing}")
        
        # Step 6: Create ordered DataFrame (order matters for ML model)
        ordered_features = {key: feature_dict[key] for key in self.REQUIRED_FEATURES}
        feature_df = pd.DataFrame([ordered_features])
        
        logger.info(f"✅ Feature assembly complete: {len(self.REQUIRED_FEATURES)} features validated")
        logger.debug(f"   Features: {list(feature_df.columns)}")
        
        return feature_df


# Global assembler instance
feature_assembler = FeatureAssembler()
