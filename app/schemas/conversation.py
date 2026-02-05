from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class MessageResponse(BaseModel):
    sender: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    messages: List[MessageResponse]
