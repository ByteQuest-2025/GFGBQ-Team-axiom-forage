import httpx
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session
from app.config import settings
from app.services.cache import cache_service

logger = logging.getLogger(__name__)

class EnrichmentService:
    """
    Service to fetch external enrichment data (Weather, etc.)
    Integrates with CacheService for resilience and performance.
    """
    
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_BASE_URL
        self.default_city = settings.WEATHER_DEFAULT_CITY
        self.units = settings.WEATHER_UNITS
        
    async def get_today_weather(self, city: str = None, db: Session = None) -> Dict[str, Any]:
        """
        Fetch today's weather forecast for the given city.
        
        Returns:
            dict: {
                "temp_max": float,
                "rain_mm": float,
                "weather_severity": float
            }
        """
        target_city = city or self.default_city
        today_str = datetime.now().strftime("%Y-%m-%d")
        cache_key = f"weather_{target_city}_{today_str}"
        
        # 1. Try Cache
        if db:
            cached = await cache_service.get(cache_key, db)
            if cached:
                return cached

        # 2. Fetch from API
        try:
            weather_data = await self._fetch_weather_from_api(target_city)
            
            # 3. Process and Normalize
            result = self._process_weather_data(weather_data)
            
            # 4. Cache Result (TTL 24h)
            if db:
                await cache_service.set(cache_key, result, ttl_seconds=86400, db=db)
                
            return result
            
        except Exception as e:
            logger.error(f"Weather API failed for {target_city}: {str(e)}")
            
            # 5. Fallback
            return self._get_fallback_weather()

    async def _fetch_weather_from_api(self, city: str) -> Dict:
        """
        Call OpenWeatherMap API
        """
        if not self.api_key:
            raise ValueError("WEATHER_API_KEY not set")
            
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": self.units
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=5.0)
            response.raise_for_status()
            return response.json()

    def _process_weather_data(self, data: Dict) -> Dict:
        """
        Extract relevant fields and compute severity.
        """
        main = data.get("main", {})
        rain = data.get("rain", {})
        
        temp_max = main.get("temp_max", 30.0)
        # OpenWeatherMap returns rain volume for last 1h or 3h
        rain_mm = rain.get("1h", rain.get("3h", 0.0))
        
        severity = self._calculate_severity(temp_max, rain_mm)
        
        return {
            "temp_max": float(temp_max),
            "rain_mm": float(rain_mm),
            "weather_severity": float(severity)
        }

    def _calculate_severity(self, temp: float, rain: float) -> float:
        """
        Deterministic severity score (0.0 to 1.0)
        Based on high temp or heavy rain.
        """
        score = 0.0
        
        # Temperature penalty (above 35C)
        if temp > 35:
            score += (temp - 35) * 0.05
            
        # Rain penalty (above 5mm)
        if rain > 5:
            score += (rain - 5) * 0.02
            
        # Cap at 1.0
        return min(max(score, 0.0), 1.0)

    def _get_fallback_weather(self) -> Dict:
        """
        Safe default values if API fails
        """
        return {
            "temp_max": 30.0,
            "rain_mm": 0.0,
            "weather_severity": 0.3  # Default severity as requested
        }

# Global instance
enrichment_service = EnrichmentService()
