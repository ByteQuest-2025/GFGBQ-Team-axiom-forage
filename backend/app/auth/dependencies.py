"""
FastAPI dependencies for authentication and database access.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.security import decode_access_token
from app.models.hospital import Hospital

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_hospital(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Hospital:
    """
    Dependency to get the current authenticated hospital from JWT token.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session
        
    Returns:
        Hospital object if authenticated
        
    Raises:
        HTTPException 401 if token is invalid or hospital not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode JWT token
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    # Extract hospital email from token
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Fetch hospital from database
    hospital = db.query(Hospital).filter(Hospital.email == email).first()
    
    if hospital is None:
        raise credentials_exception
    
    if not hospital.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital account is inactive"
        )
    
    return hospital
