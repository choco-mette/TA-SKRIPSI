from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.rule import RuleCreate, RuleResponse, RuleUpdate
from app.services.admin_service import AdminService
from app.models.models import User

router = APIRouter()

@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    data: RuleCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = AdminService(db)
    return service.create_rule(data, current_admin)

@router.get("/", response_model=List[RuleResponse])
def get_rules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = AdminService(db)
    return service.get_rules(skip, limit)

@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(
    rule_id: int,
    data: RuleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = AdminService(db)
    return service.update_rule(rule_id, data)

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = AdminService(db)
    service.delete_rule(rule_id)
