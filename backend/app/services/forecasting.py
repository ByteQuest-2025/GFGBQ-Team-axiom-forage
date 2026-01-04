"""
Updated Forecasting Service - Orchestrates All Components.

CLEAN ARCHITECTURE:
1. Feature Assembly (feature_assembly.py)
2. ML Inference (predictor.py) → ONLY returns numbers
3. Decision Logic (decision_logic.py) → Derives risk_level, resources
4. Reason Engine (reason_engine.py) → Traceable explanations
5. Database Persistence
"""

import pandas as pd
from datetime import date as Date
from sqlalchemy.orm import Session
import logging

from app.models.emergency_model import EmergencyModel
from app.models.prediction import Prediction
from app.services.feature_assembly import feature_assembler
from app.services.predictor import PredictorService
from app.services.decision_logic import DecisionLogic
from app.services.reason_engine import ExplanationEngine

logger = logging.getLogger(__name__)


class ForecastService:
    """
    Master orchestrator for prediction pipeline.
    Coordinates: Feature Assembly → ML → Decisions → Explanations → Persistence
    """
    
    def __init__(self, global_model: EmergencyModel = None):
        """
        Initialize with globally loaded ML model.
        
        Args:
            global_model: ML model loaded at startup (or None)
        """
        self.predictor = PredictorService(global_model)
    
    async def assemble_backend_context(self, db: Session) -> dict:
        """
        Assemble backend-only enrichment data.
        
        Returns:
            Weather + calendar + seasonal context
        """
        weather = await feature_assembler.enrich_weather(db)
        calendar = await feature_assembler.enrich_calendar(db)
        seasonal = await feature_assembler.enrich_seasonal(db)
        
        return {**weather, **calendar, **seasonal}
    
    async def get_predictions_and_resources(
        self, 
        hospital_data: dict, 
        backend_context: dict,
        hospital_id: int,
        db: Session
    ) -> dict:
        """
        MASTER PIPELINE:
        
        1. Feature Assembly & Validation
        2. Pure ML Inference (numbers only)
        3. Backend Decision Logic (risk_level, resources)
        4. Traceable Reason Generation
        5. Protocol-Based Recommendations
        6. Database Persistence
        7. API Response
        
        Args:
            hospital_data: Hospital metrics
            backend_context: External enrichment
            hospital_id: Hospital ID
            db: Database session
            
        Returns:
            Complete prediction response with explanations
        """
        
        # STEP 1: Feature Assembly
        combined_data = {**hospital_data, **backend_context}
        feature_vector = await feature_assembler.assemble_features(combined_data, db)
        feature_dict = feature_vector.to_dict(orient='records')[0]
        
        logger.info(f"✅ Features assembled: {feature_vector.shape}")
        
        # STEP 2: Pure ML Inference (ONLY NUMBERS)
        ml_predictions = self.predictor.predict(feature_vector)
        
        # STEP 3: Backend Decision Logic
        decisions = DecisionLogic.derive_all_decisions(
            ml_predictions,
            hospital_data
        )
        
        # STEP 4-5: Traceable Explanations
        explanation = ExplanationEngine.generate_explanation(
            feature_dict,
            hospital_data,
            backend_context,
            ml_predictions,
            decisions
        )
        
        # STEP 6: Database Persistence
        today = Date.today()
        existing = db.query(Prediction).filter(
            Prediction.hospital_id == hospital_id,
            Prediction.date == today
        ).first()
        
        if existing:
            # Update
            existing.risk_score = ml_predictions["risk_score"]
            existing.er_surge_pct = ml_predictions["expected_er_increase_pct"]
            existing.icu_surge_pct = ml_predictions["expected_icu_increase_pct"]
            existing.risk_level = decisions["risk_level"]
            existing.additional_icu_beds = decisions["additional_icu_beds"]
            existing.additional_staff = decisions["additional_staff"]
            existing.supply_status = decisions["supply_status"]
            existing.input_features = feature_dict
            existing.is_fallback = 1 if ml_predictions.get("is_fallback") else 0
        else:
            # Create
            new_pred = Prediction(
                hospital_id=hospital_id,
                date=today,
                risk_score=ml_predictions["risk_score"],
                er_surge_pct=ml_predictions["expected_er_increase_pct"],
                icu_surge_pct=ml_predictions["expected_icu_increase_pct"],
                risk_level=decisions["risk_level"],
                additional_icu_beds=decisions["additional_icu_beds"],
                additional_staff=decisions["additional_staff"],
                supply_status=decisions["supply_status"],
                input_features=feature_dict,
                is_fallback=1 if ml_predictions.get("is_fallback") else 0
            )
            db.add(new_pred)
        
        db.commit()
        logger.info(f"✅ Saved: hospital_id={hospital_id}, risk={decisions['risk_level']}")
        
        # STEP 7: API Response (Original Contract + Explanations)
        return {
            "risk_analysis": {
                "score": round(ml_predictions["risk_score"] * 100, 1),
                "alert_level": decisions["risk_level"],
                "er_surge_prediction": f"+{round(ml_predictions['expected_er_increase_pct'] * 100, 1)}%",
                "icu_surge_prediction": f"+{round(ml_predictions['expected_icu_increase_pct'] * 100, 1)}%"
            },
            "resource_requirements": {
                "beds_to_prepare": decisions["additional_icu_beds"],
                "staff_to_summon": decisions["additional_staff"],
                "supply_alert": decisions["supply_status"]
            },
            "recommendations": explanation["recommendations"],
            "explanation": {
                "reasons": explanation["reasons"],
                "summary": explanation["summary"]
            }
        }