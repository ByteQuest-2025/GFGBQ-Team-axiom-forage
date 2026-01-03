"""
Prediction model for storing ML inference results and derived decisions.

ML Model Output (Numeric Only):
- risk_score (0.0-1.0)
- expected_er_increase_pct (0.0-1.0)
- expected_icu_increase_pct (0.0-1.0)

Backend Derived Fields:
- risk_level (Critical/High/Elevated/Normal)
- additional_icu_beds (integer)
- additional_staff (integer)
- supply_status (Low/Stable)
"""

from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant: Link to hospital
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    
    # Prediction date
    date = Column(Date, nullable=False, index=True)
    
    # --- RAW ML MODEL OUTPUT (Numeric Only) ---
    risk_score = Column(Float, nullable=False)  # 0.0-1.0
    er_surge_pct = Column(Float, nullable=False)  # expected_er_increase_pct
    icu_surge_pct = Column(Float, nullable=False)  # expected_icu_increase_pct
    
    # --- BACKEND DERIVED DECISIONS ---
    risk_level = Column(String, nullable=False)  # Critical/High/Elevated/Normal
    additional_icu_beds = Column(Integer, nullable=False)
    additional_staff = Column(Integer, nullable=False)
    supply_status = Column(String, nullable=False)  # Low/Stable
    
    # Input features snapshot (JSONB for flexibility)
    input_features = Column(JSON, nullable=True)
    
    # Metadata
    model_version = Column(String, default="v1.0")
    is_fallback = Column(Integer, default=0)  # 1 if ML model failed, 0 if successful
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    hospital = relationship("Hospital", back_populates="predictions")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('hospital_id', 'date', name='unique_prediction_per_hospital_per_day'),
    )
    
    def __repr__(self):
        return f"<Prediction(hospital_id={self.hospital_id}, date={self.date}, risk={self.risk_level})>"
