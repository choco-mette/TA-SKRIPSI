from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.document import DocumentResponse, DeleteResponse
from app.services.document_service import DocumentService
from app.models.models import User

router = APIRouter()

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = DocumentService(db)
    return await service.upload_document(file, current_admin)

@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = DocumentService(db)
    return service.get_documents(skip, limit)

@router.delete("/{doc_id}", response_model=DeleteResponse)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = DocumentService(db)
    service.delete_document(doc_id)
    return {"message": "Document and knowledge base deleted successfully", "doc_id": doc_id}
