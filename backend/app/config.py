import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Weather API
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_API_BASE_URL: str = os.getenv("WEATHER_API_BASE_URL", "https://api.openweathermap.org/data/2.5")
    WEATHER_DEFAULT_CITY: str = os.getenv("WEATHER_DEFAULT_CITY", "Hyderabad")
    WEATHER_UNITS: str = os.getenv("WEATHER_UNITS", "metric")

    class Config:
        env_file = ".env"

settings = Settings()
