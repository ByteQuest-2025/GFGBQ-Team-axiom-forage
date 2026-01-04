"""
SQLAlchemy models for the healthcare intelligence system.
"""

from app.models.hospital import Hospital
from app.models.prediction import Prediction
from app.models.cached_data import CachedData

__all__ = ["Hospital", "Prediction", "CachedData"]
