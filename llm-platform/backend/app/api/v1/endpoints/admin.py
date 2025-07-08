from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.database import get_db
from app.middleware.auth import get_current_admin_user
from app.crud.user import user
from app.crud.model import model
from app.crud.api_key import api_key
from app.crud.access_log import access_log
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.model import Model, ModelCreate, ModelUpdate
from app.models.user import User as UserModel
from app.models.access_log import AccessLog

router = APIRouter()

# User Management
@router.get("/users", response_model=List[User])
async def list_all_users(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100
):
    """List all users (admin only)"""
    users = user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/users", response_model=User)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user)
):
    """Create a new user (admin only)"""
    # Check if user already exists
    if user.get_by_username(db, username=user_in.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if user.get_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = user.create(db, obj_in=user_in)
    return new_user

@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user)
):
    """Update a user (admin only)"""
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = user.update(db, db_obj=db_user, obj_in=user_update)
    return updated_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user)
):
    """Delete a user (admin only)"""
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Cannot delete the current admin
    if db_user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user.remove(db, id=user_id)
    return {"message": "User deleted successfully"}

# Model Management
@router.get("/models", response_model=List[Model])
async def list_all_models(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100
):
    """List all models (admin only)"""
    models = model.get_multi(db, skip=skip, limit=limit)
    return models

@router.post("/models", response_model=Model)
async def create_model(
    model_in: ModelCreate,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user)
):
    """Create a new model (admin only)"""
    # Check if model name already exists
    if model.get_by_name(db, name=model_in.name):
        raise HTTPException(status_code=400, detail="Model name already exists")
    
    new_model = model.create(db, obj_in=model_in)
    return new_model

@router.put("/models/{model_id}", response_model=Model)
async def update_model(
    model_id: int,
    model_update: ModelUpdate,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user)
):
    """Update a model (admin only)"""
    db_model = model.get(db, id=model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    updated_model = model.update(db, db_obj=db_model, obj_in=model_update)
    return updated_model

@router.delete("/models/{model_id}")
async def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user)
):
    """Delete a model (admin only)"""
    db_model = model.get(db, id=model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model.remove(db, id=model_id)
    return {"message": "Model deleted successfully"}

# Statistics and Analytics
@router.get("/stats/overview")
async def get_overview_stats(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user)
):
    """Get platform overview statistics"""
    # Get counts
    total_users = db.query(func.count(UserModel.id)).scalar()
    active_users = db.query(func.count(UserModel.id)).filter(UserModel.is_active == True).scalar()
    total_models = db.query(func.count(Model.id)).scalar()
    active_models = db.query(func.count(Model.id)).filter(Model.is_active == True).scalar()
    
    # Get recent API calls (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_calls = db.query(func.count(AccessLog.id)).filter(
        AccessLog.created_at >= yesterday
    ).scalar()
    
    # Get average latency (last 24 hours)
    avg_latency = db.query(func.avg(AccessLog.latency_ms)).filter(
        AccessLog.created_at >= yesterday,
        AccessLog.status_code == 200
    ).scalar()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_models": total_models,
        "active_models": active_models,
        "recent_api_calls_24h": recent_calls,
        "avg_latency_ms": float(avg_latency) if avg_latency else 0
    }

@router.get("/stats/usage")
async def get_usage_stats(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user),
    days: int = Query(7, ge=1, le=30)
):
    """Get usage statistics for the last N days"""
    start_date = date.today() - timedelta(days=days)
    end_date = date.today()
    
    stats = access_log.get_stats_by_date(db, start_date=start_date, end_date=end_date)
    
    return {
        "period_days": days,
        "start_date": start_date,
        "end_date": end_date,
        "daily_stats": [
            {
                "date": stat.date,
                "request_count": stat.request_count,
                "total_tokens": stat.total_tokens or 0,
                "avg_latency_ms": float(stat.avg_latency) if stat.avg_latency else 0
            }
            for stat in stats
        ]
    }

@router.get("/logs/recent")
async def get_recent_logs(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user),
    limit: int = Query(50, ge=1, le=1000)
):
    """Get recent access logs"""
    logs = (
        db.query(AccessLog)
        .order_by(desc(AccessLog.created_at))
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "model_id": log.model_id,
            "request_type": log.request_type,
            "status_code": log.status_code,
            "latency_ms": log.latency_ms,
            "total_tokens": log.total_tokens,
            "created_at": log.created_at,
            "error_message": log.error_message
        }
        for log in logs
    ]