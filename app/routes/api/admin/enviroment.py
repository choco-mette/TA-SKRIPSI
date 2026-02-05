from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.enviroment import EnvironmentCreate, EnvironmentResponse, EnvironmentUpdate
from app.services.enviroment_service import EnvironmentService
from app.models.models import User

router = APIRouter()

@router.post("/", response_model=EnvironmentResponse, status_code=status.HTTP_201_CREATED)
def create_environment(
    data: EnvironmentCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = EnvironmentService(db)
    return service.create_environment(data)

@router.get("/", response_model=List[EnvironmentResponse])
def get_environments(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = EnvironmentService(db)
    return service.get_environments(skip, limit)

@router.put("/{env_id}", response_model=EnvironmentResponse)
def update_environment(
    env_id: int,
    data: EnvironmentUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = EnvironmentService(db)
    return service.update_environment(env_id, data)

@router.delete("/{env_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environment(
    env_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = EnvironmentService(db)
    service.delete_environment(env_id)
