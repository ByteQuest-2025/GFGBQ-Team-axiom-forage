"""
Cache service abstraction for external API data.
Provides in-memory + database caching with TTL expiration.
Redis-ready - can swap implementation without changing interface.
"""

from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.cached_data import CachedData
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Hybrid caching layer with in-memory dict and PostgreSQL persistence.
    """
    
    def __init__(self):
        # In-memory cache for fast reads
        self._memory_cache: dict = {}
    
    async def get(self, key: str, db: Session) -> Optional[dict]:
        """
        Retrieve cached value if exists and not expired.
        
        Args:
            key: Cache key identifier
            db: Database session
            
        Returns:
            Cached value dict if found and valid, None otherwise
        """
        now = datetime.now(timezone.utc)
        
        # Check in-memory cache first
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            # Ensure entry['expires_at'] is aware
            expires_at = entry['expires_at']
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
                
            if expires_at > now:
                logger.info(f"Cache HIT (memory): {key}")
                return entry['value']
            else:
                # Expired, remove from memory
                del self._memory_cache[key]
        
        # Check database cache
        cached = db.query(CachedData).filter(CachedData.cache_key == key).first()
        
        if cached:
            # Ensure cached.expires_at is aware
            expires_at = cached.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            if expires_at > now:
                logger.info(f"Cache HIT (database): {key}")
                # Populate memory cache for next time
                self._memory_cache[key] = {
                    'value': cached.cache_value,
                    'expires_at': expires_at
                }
                return cached.cache_value
            else:
                # Expired entry in database, delete it
                db.delete(cached)
                db.commit()
        
        logger.info(f"Cache MISS: {key}")
        return None
    
    async def set(self, key: str, value: dict, ttl_seconds: int, db: Session):
        """
        Store value in cache with TTL expiration.
        
        Args:
            key: Cache key identifier
            value: Data to cache (must be JSON-serializable)
            ttl_seconds: Time-to-live in seconds
            db: Database session
        """
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        
        # Store in memory
        self._memory_cache[key] = {
            'value': value,
            'expires_at': expires_at
        }
        
        # Store in database (upsert)
        existing = db.query(CachedData).filter(CachedData.cache_key == key).first()
        
        if existing:
            existing.cache_value = value
            existing.expires_at = expires_at
        else:
            new_entry = CachedData(
                cache_key=key,
                cache_value=value,
                expires_at=expires_at
            )
            db.add(new_entry)
        
        db.commit()
        logger.info(f"Cache SET: {key} (TTL: {ttl_seconds}s)")
    
    async def delete(self, key: str, db: Session):
        """
        Remove specific key from cache.
        
        Args:
            key: Cache key to delete
            db: Database session
        """
        # Remove from memory
        if key in self._memory_cache:
            del self._memory_cache[key]
        
        # Remove from database
        cached = db.query(CachedData).filter(CachedData.cache_key == key).first()
        if cached:
            db.delete(cached)
            db.commit()
        
        logger.info(f"Cache DELETE: {key}")
    
    async def clear_expired(self, db: Session):
        """
        Remove all expired entries from database.
        Memory cache clears automatically on access.
        
        Args:
            db: Database session
        """
        now = datetime.now(timezone.utc)
        expired_count = db.query(CachedData).filter(
            CachedData.expires_at <= now
        ).delete()
        db.commit()
        
        logger.info(f"Cache cleanup: removed {expired_count} expired entries")
        return expired_count


# Global cache instance
cache_service = CacheService()
