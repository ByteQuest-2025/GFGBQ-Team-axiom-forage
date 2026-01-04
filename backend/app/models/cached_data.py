"""
Generic cache storage for external API data (weather, festivals, seasonal patterns).
Provides TTL-based expiration and Redis-ready abstraction.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class CachedData(Base):
    __tablename__ = "cached_data"

    id = Column(Integer, primary_key=True, index=True)
    
    # Cache key (unique identifier, e.g., "weather_2026-01-03", "festival_calendar_2026")
    cache_key = Column(String, unique=True, index=True, nullable=False)
    
    # Cached value (JSONB for flexible data structures)
    cache_value = Column(JSON, nullable=False)
    
    # Expiration timestamp
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<CachedData(key='{self.cache_key}', expires={self.expires_at})>"
