from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.base_knowledge import BaseKnowledgeResponse
from app.repositories.document_repo import BaseKnowledgeRepository
from app.models.models import User

router = APIRouter()

@router.get("/", response_model=List[BaseKnowledgeResponse])
def get_base_knowledge(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    repo = BaseKnowledgeRepository(db)
    results = repo.get_all_chunks(skip, limit)
    
    # Map result to schema
    response = []
    for chunk, title in results:
        response.append(BaseKnowledgeResponse(
            langchain_id=chunk.langchain_id,
            doc_id=chunk.doc_id,
            content=chunk.content,
            langchain_metadata=chunk.langchain_metadata,
            document_title=title
        ))
    return response
