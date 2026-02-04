from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.enviroment_repo import EnvironmentRepository
from app.schemas.enviroment import EnvironmentCreate, EnvironmentUpdate
from app.models.models import EnvironmentModel

class EnvironmentService:
    def __init__(self, db: Session):
        self.repo = EnvironmentRepository(db)

    def create_environment(self, data: EnvironmentCreate) -> EnvironmentModel:
        # If setting to active, deactivate others of same type
        if data.is_active:
            self.repo.deactivate_others(data.model_type)

        new_env = EnvironmentModel(
            models_name=data.models_name,
            api_key=data.api_key,
            base_url=data.base_url,
            model_type=data.model_type,
            is_active=data.is_active
        )
        return self.repo.create(new_env)

    def get_environments(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip, limit)

    def update_environment(self, env_id: int, data: EnvironmentUpdate) -> EnvironmentModel:
        env = self.repo.get_by_id(env_id)
        if not env:
            raise HTTPException(status_code=404, detail="Environment configuration not found")

        # Logic to handle activation exclusivity
        if data.is_active is True:
            # Determining model type: use new if provided, else current
            m_type = data.model_type if data.model_type else env.model_type
            self.repo.deactivate_others(m_type, exclude_id=env.id)

        # Update fields
        if data.models_name is not None:
            env.models_name = data.models_name
        if data.api_key is not None:
            env.api_key = data.api_key
        if data.base_url is not None:
            env.base_url = data.base_url
        if data.model_type is not None:
            env.model_type = data.model_type
        if data.is_active is not None:
            env.is_active = data.is_active

        return self.repo.update(env)

    def delete_environment(self, env_id: int):
        env = self.repo.get_by_id(env_id)
        if not env:
            raise HTTPException(status_code=404, detail="Environment configuration not found")
        self.repo.delete(env)
