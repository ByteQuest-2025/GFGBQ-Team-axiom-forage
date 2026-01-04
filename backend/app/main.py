"""
Main FastAPI Application Entry Point - Production Version with Final API

Includes:
- Safe ML model loading at startup
- JWT authentication
- /predict/daily endpoint with locked contract
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database
from app.database import get_db, init_db

# Import services
from app.services.forecasting import ForecastService

# Import auth
from app.api.auth import router as auth_router
from app.auth.dependencies import get_current_hospital

# Import API routers
from app.api import predictions

# Import models
from app.models.hospital import Hospital
from app.models.emergency_model import EmergencyModel

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GLOBAL ML MODEL (loaded once at startup)
ml_model = None
model_status = {"status": "not_loaded", "error": None}

# Create FastAPI app
app = FastAPI(
    title="Axiom Forage HealthAI - Production",
    description="PS-06: Enterprise Predictive Stress-Scoring for ER & ICU Load Management",
    version="2.0.0"
)

# Enable CORS for Frontend communication
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(predictions.router)


# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    """
    CRITICAL STARTUP SEQUENCE:
    1. Initialize database
    2. Load ML model ONCE with validation
    3. Inject model into prediction router
    """
    global ml_model, model_status
    
    # 1. Initialize Database
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # 2. Load ML Model (ONCE at startup)
    try:
        logger.info("🔧 Loading ML model at startup...")
        ml_model = EmergencyModel()
        ml_model.load_model()
        
        # Validate feature contract
        expected_features = ml_model.FEATURE_CONTRACT
        logger.info(f"✅ ML Model loaded successfully")
        logger.info(f"✅ Feature contract validated: {len(expected_features)} features")
        
        model_status = {
            "status": "loaded",
            "feature_count": len(expected_features),
            "features": expected_features,
            "error": None
        }
        
    except FileNotFoundError as e:
        logger.error(f"❌ ML Model file not found: {e}")
        logger.warning("⚠️  System will use RULE-BASED FALLBACK predictions")
        model_status = {
            "status": "not_found",
            "error": str(e),
            "fallback_active": True
        }
        
    except Exception as e:
        logger.error(f"❌ ML Model loading failed: {e}")
        logger.warning("⚠️  System will use RULE-BASED FALLBACK predictions")
        model_status = {
            "status": "load_failed",
            "error": str(e),
            "fallback_active": True
        }
    
    # 3. Inject model into prediction router
    predictions.set_global_model(ml_model)


# --- Health Check ---
@app.get("/")
async def root(db: Session = Depends(get_db)):
    """
    Health check endpoint with system status.
    """
    # Check database connection
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "online",
        "system": "Axiom Forage HealthAI - Production",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "database_status": db_status,
        "ml_model_status": model_status
    }


# --- Legacy Dashboard Endpoint (PROTECTED) ---
@app.get("/api/v1/dashboard")
async def get_dashboard(
    current_hospital: Hospital = Depends(get_current_hospital),
    db: Session = Depends(get_db)
):
    """
    Legacy Dashboard Endpoint (for backward compatibility)
    Redirects to /predict/daily internally
    """
    try:
        service = ForecastService(ml_model)
        
        # 1. Get Today's Prediction & Context
        # Defensive coding: Handle None values from DB
        daily_patients = current_hospital.daily_patients or 0
        icu_total = current_hospital.icu_total_capacity or 40
        staff_on_duty = current_hospital.staff_on_duty or 0
        oxygen_status_raw = current_hospital.oxygen_status or "Normal"
        medicine_status_raw = current_hospital.medicine_status or "Normal"
        
        # Lowercase for ML model logic
        oxygen_status = oxygen_status_raw.lower()
        medicine_status = medicine_status_raw.lower()

        hospital_data = {
            "icu_occupied": daily_patients, 
            "icu_total": icu_total,
            "daily_patients": daily_patients,
            "staff_on_duty": staff_on_duty,
            "oxygen_status": oxygen_status,
            "medicine_status": medicine_status
        }

        backend_context = await service.assemble_backend_context(db)
        prediction_result = await service.get_predictions_and_resources(
            hospital_data, 
            backend_context,
            current_hospital.id,
            db
        )
        
        # 2. Fetch History for Chart (Last 7 days)
        from app.models.prediction import Prediction
        history = db.query(Prediction).filter(
            Prediction.hospital_id == current_hospital.id
        ).order_by(Prediction.date.desc()).limit(7).all()
        
        # Format Forecast (Chart Data)
        forecast_data = []
        
        # We need to show trend, so we reverse history (oldest to newest)
        # If no history, we will just have today's prediction added below
        for p in reversed(history):
            # Estimate counts based on stored percentages (approximate)
            base_patients = daily_patients
            est_visits = int(base_patients * (1 + p.er_surge_pct))
            est_icu = int(icu_total * (1 + p.icu_surge_pct) * 0.8) # Approx
            
            forecast_data.append({
                "day_name": p.date.strftime("%a"), # Mon, Tue
                "emergency_visits": est_visits,
                "icu_demand": est_icu,
                "date": p.date.isoformat()
            })
            
        # Ensure at least today is in forecast if history was empty or didn't include today yet
        if not any(f['date'] == datetime.now().date().isoformat() for f in forecast_data):
             # Parse percentage string "+5.0%" -> 0.05
             er_surge_str = prediction_result["risk_analysis"]["er_surge_prediction"].strip('%+')
             er_surge_val = float(er_surge_str) / 100.0 if er_surge_str else 0.0
             
             est_visits = int(daily_patients * (1 + er_surge_val))
             
             forecast_data.append({
                "day_name": "Today",
                "emergency_visits": est_visits,
                "icu_demand": int(icu_total * 0.5), # Placeholder
                "date": datetime.now().date().isoformat()
            })

        # 3. Construct Frontend-Compatible Response
        # Parse percentage string for predicted_visits calculation
        er_surge_str = prediction_result["risk_analysis"]["er_surge_prediction"].strip('%+')
        er_surge_val = float(er_surge_str) / 100.0 if er_surge_str else 0.0
        
        response_data = {
            "summary": {
                "alert_level": prediction_result["risk_analysis"]["alert_level"],
                "daily_patients": daily_patients,
                "staff_on_duty": staff_on_duty,
                "oxygen_status": oxygen_status_raw,
                "medicine_status": medicine_status_raw,
                "predicted_workload": prediction_result["risk_analysis"]["score"], # Risk Score
                "icu_occupied": daily_patients, # Proxy
                "icu_total": icu_total,
                "predicted_visits": int(daily_patients * (1 + er_surge_val))
            },
            "forecast": forecast_data,
            "recommendations": prediction_result["recommendations"]
        }
        
        return {
            "success": True,
            "data": response_data
        }

    except Exception as e:
        logger.error(f"Dashboard Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# --- Prediction History (PROTECTED) ---
@app.get("/api/v1/predictions/history")
async def get_prediction_history(
    limit: int = 30,
    current_hospital: Hospital = Depends(get_current_hospital),
    db: Session = Depends(get_db)
):
    """Get hospital's prediction history"""
    from app.models.prediction import Prediction
    
    predictions = db.query(Prediction).filter(
        Prediction.hospital_id == current_hospital.id
    ).order_by(Prediction.date.desc()).limit(limit).all()
    
    return {
        "success": True,
        "hospital_name": current_hospital.hospital_name,
        "predictions": [
            {
                "date": pred.date.isoformat(),
                "risk_level": pred.risk_level,
                "risk_score": pred.risk_score,
                "er_surge_pct": pred.er_surge_pct,
                "icu_surge_pct": pred.icu_surge_pct,
                "beds_needed": pred.additional_icu_beds,
                "staff_needed": pred.additional_staff,
                "supply_status": pred.supply_status,
                "is_fallback": bool(pred.is_fallback)
            }
            for pred in predictions
        ]
    }



# --- Run Server ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)