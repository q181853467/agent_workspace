from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.crud.api_key import api_key
from app.schemas.api_key import APIKey, APIKeyCreate, APIKeyCreateResponse, APIKeyUpdate
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[APIKey])
async def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's API keys"""
    api_keys = api_key.get_by_user(db, user_id=current_user.id)
    return api_keys

@router.post("/", response_model=APIKeyCreateResponse)
async def create_api_key(
    api_key_in: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new API key"""
    db_api_key, key = api_key.create(db, obj_in=api_key_in, user_id=current_user.id)
    return APIKeyCreateResponse(api_key=db_api_key, key=key)

@router.put("/{api_key_id}", response_model=APIKey)
async def update_api_key(
    api_key_id: int,
    api_key_update: APIKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an API key"""
    db_api_key = api_key.get(db, id=api_key_id)
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    if db_api_key.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_api_key = api_key.update(db, db_obj=db_api_key, obj_in=api_key_update)
    return updated_api_key

@router.delete("/{api_key_id}")
async def delete_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an API key"""
    db_api_key = api_key.get(db, id=api_key_id)
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    if db_api_key.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    api_key.remove(db, id=api_key_id)
    return {"message": "API key deleted successfully"}

@router.get("/active", response_model=List[APIKey])
async def list_active_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's active API keys"""
    api_keys = api_key.get_active_keys(db, user_id=current_user.id)
    return api_keys