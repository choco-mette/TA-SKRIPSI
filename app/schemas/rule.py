from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RuleBase(BaseModel):
    content: str
    is_active: bool = True

class RuleCreate(RuleBase):
    pass

class RuleUpdate(RuleBase):
    content: Optional[str] = None
    is_active: Optional[bool] = None

class RuleResponse(RuleBase):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True
