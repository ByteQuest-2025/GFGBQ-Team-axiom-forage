import asyncio
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set env vars for testing
os.environ["WEATHER_API_KEY"] = "0fbd9bd5dc3528fd33c42cc1ff71f3f7"
os.environ["WEATHER_API_BASE_URL"] = "https://api.openweathermap.org/data/2.5"
os.environ["WEATHER_DEFAULT_CITY"] = "Hyderabad"
os.environ["WEATHER_UNITS"] = "metric"

from app.services.enrichment import enrichment_service
from app.services.cache import cache_service
from app.database import SessionLocal, init_db

async def verify_weather():
    print("--- Weather Integration Verification ---")
    
    # Initialize DB (for cache)
    init_db()
    db = SessionLocal()
    
    try:
        # 1. Test API Fetch
        print("\n1. Testing API Fetch (Hyderabad)...")
        start = datetime.now()
        weather = await enrichment_service.get_today_weather("Hyderabad", db)
        duration = (datetime.now() - start).total_seconds()
        print(f"Result: {weather}")
        print(f"Duration: {duration:.2f}s")
        
        if weather["weather_severity"] == 0.3 and weather["temp_max"] == 30.0:
             print("⚠️  Warning: Received fallback values. API might have failed.")
        else:
             print("✅ API Fetch Successful")

        # 2. Test Caching
        print("\n2. Testing Cache Hit...")
        start = datetime.now()
        cached_weather = await enrichment_service.get_today_weather("Hyderabad", db)
        duration = (datetime.now() - start).total_seconds()
        print(f"Result: {cached_weather}")
        print(f"Duration: {duration:.4f}s")
        
        if duration < 0.1:
            print("✅ Cache Hit Verified (Fast response)")
        else:
            print("⚠️  Warning: Response took too long for cache hit.")

        # 3. Test Failure Handling (Invalid Key)
        print("\n3. Testing Failure Handling (Invalid Key)...")
        # Temporarily break key
        original_key = enrichment_service.api_key
        enrichment_service.api_key = "INVALID_KEY"
        
        # Use a new city to avoid cache
        fallback_weather = await enrichment_service.get_today_weather("UnknownCity123", db)
        print(f"Result: {fallback_weather}")
        
        if fallback_weather["weather_severity"] == 0.3:
            print("✅ Fallback Verified")
        else:
            print(f"❌ Unexpected result during failure: {fallback_weather}")
            
        # Restore key
        enrichment_service.api_key = original_key

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify_weather())
