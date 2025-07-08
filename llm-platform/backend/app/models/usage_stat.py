from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Date
from sqlalchemy.sql import func
from app.db.database import Base

class UsageStat(Base):
    __tablename__ = "usage_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Manual FK
    model_id = Column(Integer, nullable=False, index=True)  # Manual FK
    date = Column(Date, nullable=False, index=True)
    request_count = Column(BigInteger, default=0)
    total_tokens = Column(BigInteger, default=0)
    prompt_tokens = Column(BigInteger, default=0)
    completion_tokens = Column(BigInteger, default=0)
    total_cost = Column(BigInteger, default=0)  # Cost in cents
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())