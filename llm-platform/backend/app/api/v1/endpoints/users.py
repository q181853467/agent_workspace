from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.crud.user import user
from app.schemas.user import User, UserUpdate
from app.models.user import User as UserModel

router = APIRouter()

@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update current user information"""
    updated_user = user.update(db, db_obj=current_user, obj_in=user_update)
    return updated_user

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get user by ID (admin only or own profile)"""
    if user_id != current_user.id and not user.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return db_user