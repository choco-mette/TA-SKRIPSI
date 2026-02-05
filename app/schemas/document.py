from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True

class DeleteResponse(BaseModel):
    message: str
    doc_id: int
