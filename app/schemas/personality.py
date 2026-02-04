from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PersonalityBase(BaseModel):
    content: str

class PersonalityCreate(PersonalityBase):
    pass

class PersonalityUpdate(PersonalityBase):
    pass

class PersonalityResponse(PersonalityBase):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True
