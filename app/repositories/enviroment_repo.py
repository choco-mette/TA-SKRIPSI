from sqlalchemy.orm import Session
from app.models.models import EnvironmentModel
from typing import List, Optional

class EnvironmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, env: EnvironmentModel) -> EnvironmentModel:
        self.db.add(env)
        self.db.commit()
        self.db.refresh(env)
        return env

    def get_all(self, skip: int = 0, limit: int = 100) -> List[EnvironmentModel]:
        return self.db.query(EnvironmentModel).offset(skip).limit(limit).all()

    def get_by_id(self, env_id: int) -> Optional[EnvironmentModel]:
        return self.db.query(EnvironmentModel).filter(EnvironmentModel.id == env_id).first()

    def update(self, env: EnvironmentModel) -> EnvironmentModel:
        self.db.commit()
        self.db.refresh(env)
        return env

    def delete(self, env: EnvironmentModel):
        self.db.delete(env)
        self.db.commit()

    def deactivate_others(self, model_type: str, exclude_id: Optional[int] = None):
        """
        Deactivate other models of the same type to ensure single active model per type.
        """
        query = self.db.query(EnvironmentModel).filter(
            EnvironmentModel.model_type == model_type,
            EnvironmentModel.is_active == True
        )
        if exclude_id:
            query = query.filter(EnvironmentModel.id != exclude_id)
        
        active_models = query.all()
        for model in active_models:
            model.is_active = False
        
        if active_models:
            self.db.commit()
