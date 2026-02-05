from sqlalchemy.orm import Session
from app.models.models import Document, BaseKnowledge
from typing import List, Optional

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Document]:
        return self.db.query(Document).offset(skip).limit(limit).all()

    def get_by_id(self, doc_id: int) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == doc_id).first()

    def delete(self, document: Document):
        self.db.delete(document)
        self.db.commit()

class BaseKnowledgeRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_create(self, knowledges: List[BaseKnowledge]):
        self.db.bulk_save_objects(knowledges)
        self.db.commit()

    def delete_by_doc_id(self, doc_id: int):
        self.db.query(BaseKnowledge).filter(BaseKnowledge.doc_id == doc_id).delete()
        self.db.commit()
