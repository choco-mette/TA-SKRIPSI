import os
import shutil
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.models.models import Document, BaseKnowledge, User
from app.repositories.document_repo import DocumentRepository, BaseKnowledgeRepository
from app.services.embedding_service import EmbeddingConfigService
from app.utils.text_cleaner import TextCleaner

# Setup Upload Directory relative to this file
BASE_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_APP_DIR, "static", "doc")

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.bk_repo = BaseKnowledgeRepository(db)
        self.embedding_service = EmbeddingConfigService(db)

    async def upload_document(self, file: UploadFile, current_user: User) -> Document:
        # 1. Save File
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        # Create unique filename to avoid overwrite
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Create DB Record
        new_doc = Document(
            title=file.filename,
            file_path=file_path,
            created_by=current_user.id
        )
        saved_doc = self.doc_repo.create(new_doc)

        # 3. Trigger Processing (Sync for now, async worker better for prod)
        try:
            self.process_document(saved_doc)
        except Exception as e:
            # Rollback file and db if processing fails
            self.doc_repo.delete(saved_doc)
            os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

        return saved_doc

    def process_document(self, document: Document):
        """
        Loads PDF, Split, Embeds, and Saves to pgvector
        """
        # A. Load Document
        loader = PyPDFLoader(document.file_path)
        raw_docs = loader.load()

        # A.1 Clean Text per Page
        for doc in raw_docs:
            doc.page_content = TextCleaner.clean_text(doc.page_content)

        # B. Split Text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(raw_docs)

        if not chunks:
            return

        # C. Generate Embeddings
        embedder = self.embedding_service.get_embedding_model()
        
        # Prepare content list for batch embedding
        texts_to_embed = [chunk.page_content for chunk in chunks]
        
        # Call API to embed (Batch)
        vectors = embedder.embed_documents(texts_to_embed)

        # D. Save to DB
        knowledge_entries = []
        for i, chunk in enumerate(chunks):
            bk = BaseKnowledge(
                doc_id=document.id,
                content=chunk.page_content,
                embedding=vectors[i],
                langchain_metadata=chunk.metadata
            )
            knowledge_entries.append(bk)
        
        self.bk_repo.bulk_create(knowledge_entries)

    def delete_document(self, doc_id: int):
        doc = self.doc_repo.get_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete vectors first
        self.bk_repo.delete_by_doc_id(doc_id)
        
        # Delete DB record
        self.doc_repo.delete(doc)
        
        # Delete physical file
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)

    def get_documents(self, skip: int = 0, limit: int = 100):
        return self.doc_repo.get_all(skip, limit)
