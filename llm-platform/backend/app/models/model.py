from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.db.database import Base

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)  # e.g., 'gpt-4', 'deepseek-coder'
    display_name = Column(String(255), nullable=False)  # Human readable name
    provider = Column(String(255), nullable=False)  # e.g., 'OpenAI', 'Deepseek'
    endpoint_url = Column(String(255))  # API endpoint
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0)  # For load balancing
    max_tokens = Column(Integer, default=4096)
    description = Column(Text)
    model_metadata = Column(JSON)  # Additional configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())