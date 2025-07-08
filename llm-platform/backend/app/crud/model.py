from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.model import Model
from app.schemas.model import ModelCreate, ModelUpdate

class CRUDModel(CRUDBase[Model, ModelCreate, ModelUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Model]:
        return db.query(Model).filter(Model.name == name).first()

    def get_active_models(self, db: Session) -> List[Model]:
        return db.query(Model).filter(Model.is_active == True).all()

    def get_by_provider(self, db: Session, *, provider: str) -> List[Model]:
        return db.query(Model).filter(
            Model.provider == provider,
            Model.is_active == True
        ).all()

    def get_ordered_by_priority(self, db: Session) -> List[Model]:
        return db.query(Model).filter(
            Model.is_active == True
        ).order_by(Model.priority.desc()).all()

model = CRUDModel(Model)