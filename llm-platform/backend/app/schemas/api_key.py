from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class APIKeyBase(BaseModel):
    name: str
    expires_at: Optional[datetime] = None

class APIKeyCreate(APIKeyBase):
    pass

class APIKeyUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class APIKeyInDB(APIKeyBase):
    id: int
    user_id: int
    key_prefix: str
    is_active: bool
    last_used_at: Optional[datetime]
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class APIKey(APIKeyInDB):
    pass

class APIKeyCreateResponse(BaseModel):
    api_key: APIKeyInDB
    key: str  # The actual key is only returned once