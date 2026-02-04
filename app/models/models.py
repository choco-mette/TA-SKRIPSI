from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime, 
    ForeignKey, Enum, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(100))
    date_of_birth = Column(Date)
    gender = Column(Enum('laki-laki', 'perempuan', name='gender_enum'))
    role = Column(Enum('user', 'admin', name='role_enum'), default='user')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rules = relationship("Rule", back_populates="creator")
    personalities = relationship("PersonalityAI", back_populates="creator")
    documents = relationship("Document", back_populates="creator")
    conversations = relationship("Conversation", back_populates="user")

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    creator = relationship("User", back_populates="rules")

class PersonalityAI(Base):
    __tablename__ = "personality_ai"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User", back_populates="personalities")

class Document(Base):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    file_path = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User", back_populates="documents")
    base_knowledges = relationship("BaseKnowledge", back_populates="document")

class BaseKnowledge(Base):
    __tablename__ = "base_knowledge"

    langchain_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(Integer, ForeignKey("document.id"))
    content = Column(Text)
    # Note: Vector dimension needs to be specified if strictly enforcing schema, 
    # e.g., Vector(384) for MiniLM. Leaving generic based on ERD.
    embedding = Column(Vector) 
    langchain_metadata = Column(JSON)

    document = relationship("Document", back_populates="base_knowledges")

class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversation.id"))
    sender = Column(Enum('user', 'llm', name='sender_enum'), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")

class EnvironmentModel(Base):
    __tablename__ = "environment_models"

    id = Column(Integer, primary_key=True, index=True)
    models_name = Column(String)
    api_key = Column(String)
    base_url = Column(String)
    model_type = Column(Enum('chat', 'embedding', name='model_type_enum'))
    is_active = Column(Boolean, default=False)
    
