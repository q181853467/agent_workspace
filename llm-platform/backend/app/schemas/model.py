from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ModelBase(BaseModel):
    name: str
    display_name: str
    provider: str
    endpoint_url: Optional[str] = None
    is_active: bool = True
    priority: int = 0
    max_tokens: int = 4096
    description: Optional[str] = None
    model_metadata: Optional[Dict[str, Any]] = None

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    provider: Optional[str] = None
    endpoint_url: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    max_tokens: Optional[int] = None
    description: Optional[str] = None
    model_metadata: Optional[Dict[str, Any]] = None

class ModelInDB(ModelBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Model(ModelInDB):
    pass