from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from sqlalchemy.sql import func
from app.db.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Manual FK
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    key_prefix = Column(String(10), unique=True, nullable=False)
    name = Column(String(255), nullable=False)  # Key name for identification
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True))
    last_used_at = Column(DateTime(timezone=True))
    usage_count = Column(BigInteger, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())