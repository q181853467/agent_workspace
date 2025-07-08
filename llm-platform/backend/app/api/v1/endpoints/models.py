from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.crud.model import model
from app.schemas.model import Model
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Model])
async def list_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """List all available models"""
    models = model.get_active_models(db)
    return models

@router.get("/active", response_model=List[Model])
async def list_active_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List only active models"""
    models = model.get_active_models(db)
    return models

@router.get("/{model_id}", response_model=Model)
async def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific model by ID"""
    db_model = model.get(db, id=model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    return db_model

@router.get("/name/{model_name}", response_model=Model)
async def get_model_by_name(
    model_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific model by name"""
    db_model = model.get_by_name(db, name=model_name)
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    return db_model