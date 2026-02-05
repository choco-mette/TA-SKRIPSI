from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID

class BaseKnowledgeResponse(BaseModel):
    langchain_id: UUID
    doc_id: int
    content: str
    langchain_metadata: Optional[Any] = None
    document_title: Optional[str] = None

    class Config:
        from_attributes = True
