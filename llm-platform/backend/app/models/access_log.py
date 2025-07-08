from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, Float
from sqlalchemy.sql import func
from app.db.database import Base

class AccessLog(Base):
    __tablename__ = "access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Manual FK
    api_key_id = Column(Integer, nullable=False, index=True)  # Manual FK
    model_id = Column(Integer, nullable=False, index=True)  # Manual FK
    request_type = Column(String(50), nullable=False)  # 'chat', 'completions', 'embeddings'
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(BigInteger, nullable=False)  # Request latency in milliseconds
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    prompt_hash = Column(String(255))  # For caching
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)