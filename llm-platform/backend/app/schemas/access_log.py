from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AccessLogBase(BaseModel):
    user_id: int
    api_key_id: int
    model_id: int
    request_type: str
    status_code: int
    latency_ms: int
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    prompt_hash: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    error_message: Optional[str] = None

class AccessLogCreate(AccessLogBase):
    pass

class AccessLogInDB(AccessLogBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AccessLog(AccessLogInDB):
    pass