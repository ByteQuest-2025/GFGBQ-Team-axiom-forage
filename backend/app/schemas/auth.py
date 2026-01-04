"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


# --- Authentication Schemas ---

class HospitalRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    hospital_name: str
    location: Optional[str] = None
    icu_total_capacity: int = Field(default=40, ge=1)


class HospitalLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class HospitalResponse(BaseModel):
    id: int
    email: str
    hospital_name: str
    location: Optional[str]
    icu_total_capacity: int
    is_active: bool
    
    class Config:
        from_attributes = True


# --- Prediction Schemas ---

class PredictionRequest(BaseModel):
    """
    Input data for making a prediction.
    Combines hospital operational data with external context.
    """
    # Hospital operational data
    icu_occupancy_pct: float = Field(..., ge=0.0, le=1.0)
    daily_patients: int = Field(..., ge=0)
    staff_on_duty: int = Field(..., ge=0)
    oxygen_low: int = Field(..., ge=0, le=1)  # Binary: 0 or 1
    medicine_low: int = Field(..., ge=0, le=1)  # Binary: 0 or 1
    
    # External context (from cache or APIs)
    temp_max: float
    rain_mm: float
    weather_severity: float = Field(..., ge=0.0, le=1.0)
    is_weekend: int = Field(..., ge=0, le=1)
    is_festival: int = Field(..., ge=0, le=1)
    seasonal_illness_weight: float = Field(..., ge=0.0, le=1.0)


class PredictionResponse(BaseModel):
    """
    Complete prediction response matching original API contract.
    """
    success: bool
    data: dict  # Matches original response format


class PredictionHistoryItem(BaseModel):
    id: int
    date: date
    risk_score: float
    risk_level: str
    er_surge_pct: float
    icu_surge_pct: float
    additional_icu_beds: int
    additional_staff: int
    supply_status: str
    is_fallback: int
    created_at: str
    
    class Config:
        from_attributes = True
