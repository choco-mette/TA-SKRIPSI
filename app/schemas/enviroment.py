from pydantic import BaseModel, Field
from typing import Optional, Literal

class EnvironmentBase(BaseModel):
    models_name: str
    api_key: str
    base_url: str
    model_type: Literal['chat', 'embedding']
    is_active: bool = False

class EnvironmentCreate(EnvironmentBase):
    pass

class EnvironmentUpdate(BaseModel):
    models_name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_type: Optional[Literal['chat', 'embedding']] = None
    is_active: Optional[bool] = None

class EnvironmentResponse(EnvironmentBase):
    id: int

    class Config:
        from_attributes = True
