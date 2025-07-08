from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyUpdate
from app.core.security import get_password_hash, generate_api_key
from datetime import datetime

class CRUDAPIKey(CRUDBase[APIKey, APIKeyCreate, APIKeyUpdate]):
    def get_by_user(self, db: Session, *, user_id: int) -> List[APIKey]:
        return db.query(APIKey).filter(APIKey.user_id == user_id).all()

    def get_by_key_hash(self, db: Session, *, key_hash: str) -> Optional[APIKey]:
        return db.query(APIKey).filter(APIKey.key_hash == key_hash).first()

    def get_by_prefix(self, db: Session, *, key_prefix: str) -> Optional[APIKey]:
        return db.query(APIKey).filter(APIKey.key_prefix == key_prefix).first()

    def create(self, db: Session, *, obj_in: APIKeyCreate, user_id: int) -> tuple[APIKey, str]:
        # Generate actual API key
        api_key = generate_api_key()
        key_hash = get_password_hash(api_key)
        key_prefix = api_key[:8] + "..."
        
        db_obj = APIKey(
            user_id=user_id,
            name=obj_in.name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            expires_at=obj_in.expires_at,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj, api_key

    def verify_key(self, db: Session, *, api_key: str) -> Optional[APIKey]:
        from app.core.security import verify_password
        
        # Check if key exists by trying to verify against all keys
        # This is not optimal for large datasets, but works for demo
        api_keys = db.query(APIKey).filter(APIKey.is_active == True).all()
        for key_obj in api_keys:
            if verify_password(api_key, key_obj.key_hash):
                # Update last used
                key_obj.last_used_at = datetime.utcnow()
                key_obj.usage_count += 1
                db.commit()
                return key_obj
        return None

    def get_active_keys(self, db: Session, *, user_id: int) -> List[APIKey]:
        return db.query(APIKey).filter(
            APIKey.user_id == user_id,
            APIKey.is_active == True
        ).all()

api_key = CRUDAPIKey(APIKey)