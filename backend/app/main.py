from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
try:
    from .services.forecasting import ForecastService
except ImportError:
    from services.forecasting import ForecastService

# 1. Setup Logging (This will show errors in your terminal)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hospital Resource Intelligence API",
    description="PS-06: Predictive analytics for ER and ICU load management"
)

# 2. Robust CORS Configuration
# This is critical so your Next.js frontend can actually talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Service
try:
    forecast_service = ForecastService()
    logger.info("✅ Forecast Service initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Forecast Service: {e}")

@app.get("/")
async def root():
    return {
        "message": "Hospital Intelligence API is online",
        "docs": "/docs",
        "status": "active"
    }

@app.get("/api/v1/dashboard")
async def get_dashboard_data():
    """
    Returns the 7-day forecast and actionable recommendations.
    """
    try:
        # Generate the data using our ML service
        data = forecast_service.generate_7_day_forecast()
        
        if not data:
            raise HTTPException(status_code=404, detail="No forecast data generated")

        # Get recommendations based on tomorrow's alert level
        tomorrow_alert = data[0]['alert_level']
        recommendations = forecast_service.get_recommendations(tomorrow_alert)

        return {
            "success": True,
            "data": {
                "summary": {
                    "alert_level": tomorrow_alert,
                    "predicted_visits": data[0]['emergency_visits'],
                    "predicted_workload": data[0]['workload_index']
                },
                "forecast": data,
                "recommendations": recommendations
            }
        }
    except FileNotFoundError:
        logger.error("CSV file or ML Model not found!")
        raise HTTPException(status_code=500, detail="Backend data files missing. Please run training script.")
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Host 0.0.0.0 makes it accessible on your local network
    # Changed to port 8001 to properly avoid WinError 10013 (Port 8000 often used)
    uvicorn.run(app, host="0.0.0.0", port=8001)