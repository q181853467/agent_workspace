from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import verify_token
from app.crud.user import user
from app.crud.api_key import api_key
from app.models.user import User
from app.models.api_key import APIKey

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    db_user = user.get_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active(db_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return db_user

async def get_current_api_key(
    request: Request,
    db: Session = Depends(get_db)
) -> tuple[APIKey, User]:
    """Get current API key and associated user"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )
    
    # Support both "Bearer token" and "Bearer api_key" formats
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    # Try to verify as API key first
    db_api_key = api_key.verify_key(db, api_key=token)
    
    if db_api_key:
        # Get the user associated with this API key
        db_user = user.get(db, id=db_api_key.user_id)
        if not db_user or not user.is_active(db_user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        return db_api_key, db_user
    
    # If not an API key, try as JWT token
    username = verify_token(token)
    if username:
        db_user = user.get_by_username(db, username=username)
        if db_user and user.is_active(db_user):
            # Create a temporary API key object for JWT auth
            temp_api_key = APIKey(
                id=0,
                user_id=db_user.id,
                name="JWT Token",
                key_prefix="jwt_",
                is_active=True
            )
            return temp_api_key, db_user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key or token",
    )

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current admin user"""
    if not user.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user