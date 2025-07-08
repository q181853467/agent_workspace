from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, date
from app.crud.base import CRUDBase
from app.models.access_log import AccessLog
from app.schemas.access_log import AccessLogCreate

class AccessLogCreate:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class CRUDAccessLog(CRUDBase[AccessLog, AccessLogCreate, dict]):
    def create_log(
        self,
        db: Session,
        *,
        user_id: int,
        api_key_id: int,
        model_id: int,
        request_type: str,
        status_code: int,
        latency_ms: int,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        prompt_hash: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> AccessLog:
        db_obj = AccessLog(
            user_id=user_id,
            api_key_id=api_key_id,
            model_id=model_id,
            request_type=request_type,
            status_code=status_code,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            prompt_hash=prompt_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user(self, db: Session, *, user_id: int, limit: int = 100) -> List[AccessLog]:
        return (
            db.query(AccessLog)
            .filter(AccessLog.user_id == user_id)
            .order_by(desc(AccessLog.created_at))
            .limit(limit)
            .all()
        )

    def get_stats_by_date(
        self, db: Session, *, start_date: date, end_date: date, user_id: Optional[int] = None
    ):
        query = db.query(
            func.date(AccessLog.created_at).label('date'),
            func.count(AccessLog.id).label('request_count'),
            func.sum(AccessLog.total_tokens).label('total_tokens'),
            func.avg(AccessLog.latency_ms).label('avg_latency'),
        ).filter(
            and_(
                func.date(AccessLog.created_at) >= start_date,
                func.date(AccessLog.created_at) <= end_date
            )
        )
        
        if user_id:
            query = query.filter(AccessLog.user_id == user_id)
            
        return query.group_by(func.date(AccessLog.created_at)).all()

access_log = CRUDAccessLog(AccessLog)