"""
Authentication API endpoints for hospital registration and login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.hospital import Hospital
from app.schemas.auth import HospitalRegister, HospitalLogin, Token, HospitalResponse
from app.auth.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.dependencies import get_current_hospital

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
def register_hospital(hospital_data: HospitalRegister, db: Session = Depends(get_db)):
    """
    Register a new hospital account.
    
    Args:
        hospital_data: Registration payload
        db: Database session
        
    Returns:
        Created hospital object
        
    Raises:
        HTTPException 400 if email already registered
    """
    # Check if email already exists
    existing = db.query(Hospital).filter(Hospital.email == hospital_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new hospital
    new_hospital = Hospital(
        email=hospital_data.email,
        hashed_password=get_password_hash(hospital_data.password),
        hospital_name=hospital_data.hospital_name,
        location=hospital_data.location,
        icu_total_capacity=hospital_data.icu_total_capacity,
        is_active=True
    )
    
    db.add(new_hospital)
    db.commit()
    db.refresh(new_hospital)
    
    return new_hospital


@router.post("/login", response_model=Token)
def login_hospital(credentials: HospitalLogin, db: Session = Depends(get_db)):
    """
    Authenticate a hospital and return JWT access token.
    
    Args:
        credentials: Login payload (email + password)
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException 401 if credentials are invalid
    """
    # Fetch hospital by email
    hospital = db.query(Hospital).filter(Hospital.email == credentials.email).first()
    
    if not hospital or not verify_password(credentials.password, hospital.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not hospital.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": hospital.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=HospitalResponse)
def get_current_hospital_profile(current_hospital: Hospital = Depends(get_current_hospital)):
    """
    Get the current authenticated hospital's profile.
    
    Args:
        current_hospital: Authenticated hospital from JWT token
        
    Returns:
        Hospital profile
    """
    return current_hospital
