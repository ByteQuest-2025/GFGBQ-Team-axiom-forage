"""
Database initialization and seeding script.
Creates tables and optionally seeds with test data.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import Base, engine, SessionLocal
from app.models.hospital import Hospital
from app.models.prediction import Prediction
from app.models.cached_data import CachedData
from app.auth.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database(seed_data=True):
    """
    Initialize database tables and optionally seed with test data.
    
    Args:
        seed_data: Whether to create test hospital account
    """
    logger.info("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Tables created successfully")
    
    if seed_data:
        logger.info("Seeding test data...")
        db = SessionLocal()
        
        try:
            # Check if test hospital already exists
            existing = db.query(Hospital).filter(Hospital.email == "test@hospital.com").first()
            
            if not existing:
                # Create test hospital
                test_hospital = Hospital(
                    email="test@hospital.com",
                    hashed_password=get_password_hash("password123"),
                    hospital_name="Test General Hospital",
                    location="Test City",
                    icu_total_capacity=40,
                    is_active=True
                )
                
                db.add(test_hospital)
                db.commit()
                db.refresh(test_hospital)
                
                logger.info(f"✅ Test hospital created:")
                logger.info(f"   Email: test@hospital.com")
                logger.info(f"   Password: password123")
                logger.info(f"   Hospital ID: {test_hospital.id}")
            else:
                logger.info(f"Test hospital already exists (ID: {existing.id})")
        
        except Exception as e:
            logger.error(f"❌ Error seeding data: {e}")
            db.rollback()
        finally:
            db.close()
    
    logger.info("✅ Database initialization complete")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Axiom Forage database")
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="Skip seeding test data"
    )
    
    args = parser.parse_args()
    
    init_database(seed_data=not args.no_seed)
