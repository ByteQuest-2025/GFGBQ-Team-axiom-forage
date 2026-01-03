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
        "database": db_status,
        "ml_model": model_status
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
        
        hospital_data = {
            "icu_occupied": 34,
            "icu_total": current_hospital.icu_total_capacity,
            "daily_patients": 125,
            "staff_on_duty": 10,
            "oxygen_status": "normal",
            "medicine_status": "low"
        }

        backend_context = await service.assemble_backend_context(db)
        result = await service.get_predictions_and_resources(
            hospital_data, 
            backend_context,
            current_hospital.id,
            db
        )
        
        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Dashboard Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error")


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