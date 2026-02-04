from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.personality import PersonalityCreate, PersonalityResponse, PersonalityUpdate
from app.services.admin_service import AdminService
from app.models.models import User

router = APIRouter()

@router.get("/", response_model=PersonalityResponse)
def get_personality(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = AdminService(db)
    personality = service.get_personality()
    if not personality:
        raise HTTPException(status_code=404, detail="Personality not set yet")
    return personality

@router.post("/", response_model=PersonalityResponse, status_code=status.HTTP_201_CREATED)
def create_personality(
    data: PersonalityCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = AdminService(db)
    return service.create_personality(data, current_admin)

@router.put("/", response_model=PersonalityResponse)
def update_personality(
    data: PersonalityUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = AdminService(db)
    return service.update_personality(data)
