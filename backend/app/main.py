from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime

# Import the service using relative package notation
from .services.forecasting import ForecastService

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Axiom Forage HealthAI",
    description="PS-06: Enterprise Predictive Stress-Scoring for ER & ICU Load Management"
)

# 1. Enable CORS for Frontend communication
# This allows your Next.js dashboard to fetch data from this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Intelligence Service
try:
    service = ForecastService()
    logger.info("✅ Forecast Service and ML Model loaded successfully.")
except Exception as e:
    logger.error(f"❌ Initialization Failed: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "system": "Axiom Forage HealthAI",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/dashboard")
async def get_dashboard():
    """
    Main Data Endpoint:
    Simulates the 'Hybrid Glue' of Internal DB data + External API data.
    """
    try:
        # A) SIMULATED INTERNAL DATA (Ground Truth from Hospital DB)
        # In a real deployment, these values would be fetched via SQL/ORM
        hospital_data = {
            "icu_occupied": 34,         # Current beds filled
            "icu_total": 40,            # Total bed capacity
            "daily_patients": 125,      # Total ER arrivals today
            "staff_on_duty": 10,        # Current nurses/doctors
            "oxygen_status": "normal",  # Supply chain signal
            "medicine_status": "low"    # Supply chain signal
        }

        # B) SIMULATED EXTERNAL CONTEXT (Considered directly by Backend/APIs)
        # In a real deployment, these would come from Weather and Calendar APIs
        backend_context = {
            "temp_max": 39,             # Heatwaves increase cardiac/respiratory stress
            "rain_mm": 15,              # Rain increases accident rates
            "weather_severity": 0.4,    # Normalized 0-1 score
            "is_weekend": 1 if datetime.now().weekday() >= 5 else 0,
            "is_festival": 0,           # Festivals indicate mass-gathering spikes
            "seasonal_illness_weight": 0.7  # High during Flu/Dengue seasons
        }

        # C) Execute Intelligence Logic
        # This calls the multi-output ML model and performs resource math
        result = service.get_predictions_and_resources(hospital_data, backend_context)
        
        return {
            "success": True,
            "data": result
        }

    except FileNotFoundError:
        logger.error("ML Model file (.pkl) missing. Run training script first.")
        raise HTTPException(status_code=500, detail="Model brain missing on server.")
    except Exception as e:
        logger.error(f"Prediction Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Intelligence Engine Error.")

if __name__ == "__main__":
    # Run server on port 8001 to avoid WinError 10013
    uvicorn.run(app, host="0.0.0.0", port=8001)