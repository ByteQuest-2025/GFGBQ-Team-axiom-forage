"""
Daily Prediction API Router
Implements /predict/daily with locked contract.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.auth.dependencies import get_current_hospital
from app.models.hospital import Hospital
from app.schemas.prediction import DailyPredictionResponse
from app.services.forecasting import ForecastService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/predict", tags=["predictions"])

# Global model instance (set by main.py at startup)
_global_model = None


def set_global_model(model):
    """Called by main.py to inject global model"""
    global _global_model
    _global_model = model


@router.post("/daily", response_model=DailyPredictionResponse)
async def predict_daily(
    current_hospital: Hospital = Depends(get_current_hospital),
    db: Session = Depends(get_db)
):
    """
    Daily Prediction Endpoint (LOCKED CONTRACT)
    
    Flow:
    1. Fetch hospital data (simulated - in production: query DB)
    2. Enrich features (weather, calendar, seasonal)
    3. Run ML inference (or fallback)
    4. Compute backend decisions
    5. Persist prediction to DB
    6. Return standardized response
    
    Contract remains stable even if ML model changes.
    """
    try:
        # Initialize service with global model
        service = ForecastService(_global_model)
        
        # STEP 1: Fetch hospital daily status
        # In production: db.query(HospitalDailyStatus).filter_by(...).first()
        hospital_data = {
            "icu_occupied": 30,
            "icu_total": current_hospital.icu_total_capacity,
            "daily_patients": 120,
            "staff_on_duty": 12,
            "oxygen_status": "normal",
            "medicine_status": "normal"
        }
        
        # STEP 2: Enrich features (backend-only data)
        backend_context = await service.assemble_backend_context(db)
        
        # STEP 3-6: ML inference, decisions, persistence
        result = await service.get_predictions_and_resources(
            hospital_data,
            backend_context,
            current_hospital.id,
            db
        )
        
        # STEP 7: Format to LOCKED CONTRACT
        response = DailyPredictionResponse(
            risk_analysis={
                "risk_score": result["risk_analysis"]["score"] / 100.0,  # Convert to 0.0-1.0
                "alert_level": result["risk_analysis"]["alert_level"].upper(),
                "er_surge_prediction_pct": float(result["risk_analysis"]["er_surge_prediction"].strip("+%")) / 100.0,
                "icu_surge_prediction_pct": float(result["risk_analysis"]["icu_surge_prediction"].strip("+%")) / 100.0
            },
            resource_requirements={
                "additional_icu_beds": result["resource_requirements"]["beds_to_prepare"],
                "additional_staff_required": result["resource_requirements"]["staff_to_summon"],
                "supply_status": result["resource_requirements"]["supply_alert"].upper()
            },
            reasons=result["explanation"]["reasons"],
            recommendations=result["recommendations"]
        )
        
        logger.info(f"✅ Daily prediction for hospital_id={current_hospital.id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Daily prediction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction engine error: {str(e)}"
        )
