"""
Hospital model for multi-tenant authentication.
Each hospital has separate credentials and predictions.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Hospital Details
    hospital_name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    
    # Capacity Info (for context)
    icu_total_capacity = Column(Integer, default=40)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    predictions = relationship("Prediction", back_populates="hospital", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Hospital(id={self.id}, name='{self.hospital_name}', email='{self.email}')>"
