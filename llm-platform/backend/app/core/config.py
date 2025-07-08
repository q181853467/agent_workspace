from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "企业级大模型克隆平台-Eve"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./llm_platform.db"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-jwt-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS - Support both field names
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"]
    BACKEND_CORS_ORIGINS: Optional[List[str]] = None
    
    # Rate limiting - Support both field names
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS: Optional[int] = None
    RATE_LIMIT_WINDOW: Optional[int] = None
    
    # Demo mode and mock service
    DEMO_MODE: bool = True
    USE_MOCK_SERVICE: Optional[bool] = None
    MOCK_RESPONSE_DELAY: Optional[int] = None
    
    # External API keys
    OPENAI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Handle compatibility with .env file fields
        if self.BACKEND_CORS_ORIGINS:
            if isinstance(self.BACKEND_CORS_ORIGINS, str):
                import json
                try:
                    self.ALLOWED_ORIGINS = json.loads(self.BACKEND_CORS_ORIGINS)
                except:
                    self.ALLOWED_ORIGINS = [self.BACKEND_CORS_ORIGINS]
            else:
                self.ALLOWED_ORIGINS = self.BACKEND_CORS_ORIGINS
        
        if self.RATE_LIMIT_REQUESTS:
            self.RATE_LIMIT_PER_MINUTE = self.RATE_LIMIT_REQUESTS
            
        if self.USE_MOCK_SERVICE is not None:
            self.DEMO_MODE = self.USE_MOCK_SERVICE
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields instead of raising validation error

settings = Settings()