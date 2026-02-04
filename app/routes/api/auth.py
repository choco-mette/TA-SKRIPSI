from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Endpoint untuk registrasi user baru
    """
    service = AuthService(db)

    service.register_user(data)

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint login user dan generate JWT token
    """
    service = AuthService(db)

    token = service.login_user(
        email=data.email,
        password=data.password
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_current_user_profile(
    current_user: dict = Depends(AuthService.get_current_user)
):
    """
    Mengambil data user yang sedang login
    """
    return current_user
