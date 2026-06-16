from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import User
from app.schemas.user import UserCreate
from app.core import security
from app.repositories.auth_repo import AuthRepository

class AuthService:
    def __init__(self, db: Session):
        self.repo = AuthRepository(db)

    def register_user(self, data: UserCreate) -> User:
        # Check if email exists
        if self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username exists
        if self.repo.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create new user
        new_user = User(
            username=data.username,
            email=data.email,
            password_hash=security.hash_password(data.password),
            full_name=data.full_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            role="user" 
        )

        return self.repo.create(new_user)

    def login_user(self, email: str, password: str) -> str:
        # Find user
        user = self.repo.get_by_email(email)

        if not user or not security.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create token
        access_token = security.create_access_token(
            data={"sub": user.username, "id": user.id, "role": user.role}
        )
        
        return access_token
