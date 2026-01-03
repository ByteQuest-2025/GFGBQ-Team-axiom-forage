"""
Database connection and session management for PostgreSQL.
Uses SQLAlchemy ORM with connection pooling.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/axiom_forage")

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20,
    echo=os.getenv("ENVIRONMENT") == "development"  # SQL logging in dev mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency for FastAPI routes to get database session.
    
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    from app.models import hospital, prediction, cached_data
    Base.metadata.create_all(bind=engine)
