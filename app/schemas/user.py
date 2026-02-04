from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, Literal

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: str 
    date_of_birth: date
    gender: Literal['laki-laki', 'perempuan']

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True
