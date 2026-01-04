"""
Pydantic response schemas for /predict/daily endpoint.
LOCKED CONTRACT - Must remain stable even if ML model changes.
"""

from pydantic import BaseModel, Field
from typing import List


class RiskAnalysis(BaseModel):
    """Risk analysis section - ML-derived metrics"""
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Numeric risk score (0.0-1.0)")
    alert_level: str = Field(..., description="Risk level: NORMAL, ELEVATED, HIGH, CRITICAL")
    er_surge_prediction_pct: float = Field(..., ge=0.0, le=1.0, description="ER surge percentage (0.0-1.0)")
    icu_surge_prediction_pct: float = Field(..., ge=0.0, le=1.0, description="ICU surge percentage (0.0-1.0)")


class ResourceRequirements(BaseModel):
    """Resource requirements - Backend-derived decisions"""
    additional_icu_beds: int = Field(..., ge=0, description="Additional ICU beds to prepare")
    additional_staff_required: int = Field(..., ge=0, description="Additional staff to summon")
    supply_status: str = Field(..., description="Supply status: STABLE or LOW")


class DailyPredictionResponse(BaseModel):
    """
    LOCKED CONTRACT for /predict/daily endpoint.
    This schema must remain stable across ML model changes.
    """
    risk_analysis: RiskAnalysis
    resource_requirements: ResourceRequirements
    reasons: List[str] = Field(default_factory=list, description="Traceable reasons for prediction")
    recommendations: List[str] = Field(default_factory=list, description="Protocol-based recommendations")
    
    class Config:
        schema_extra = {
            "example": {
                "risk_analysis": {
                    "risk_score": 0.38,
                    "alert_level": "ELEVATED",
                    "er_surge_prediction_pct": 0.15,
                    "icu_surge_prediction_pct": 0.10
                },
                "resource_requirements": {
                    "additional_icu_beds": 4,
                    "additional_staff_required": 5,
                    "supply_status": "STABLE"
                },
                "reasons": [
                    "ICU occupancy at 75% (approaching threshold)",
                    "Weekend: Historically 15% higher accident rates"
                ],
                "recommendations": [
                    "Monitor ICU bed availability every 2 hours",
                    "Brief shift leads on expected intake increase"
                ]
            }
        }
