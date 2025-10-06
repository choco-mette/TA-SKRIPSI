from sqlalchemy import (
    Column, Integer, String, Text, Float, TIMESTAMP,
    ForeignKey, func
)
# from sqlalchemy.dialects.postgresql import VECTOR
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ---------------------------
# USERS
# ---------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(50), default="user")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete")
    knowledge_vectors = relationship("KnowledgeVector", back_populates="creator", cascade="all, delete")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete")


# ---------------------------
# USER_SESSIONS
# ---------------------------
class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    session_token = Column(Text, nullable=False)
    device_info = Column(Text)
    ip_address = Column(String(100))
    expired_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    user = relationship("User", back_populates="sessions")


# ---------------------------
# AI_PERSONALITIES
# ---------------------------
class AIPersonality(Base):
    __tablename__ = "ai_personalities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    prompt_style = Column(Text)
    temperature = Column(Float,)
    top_p = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


# ---------------------------
# KNOWLEDGE_VECTORS
# ---------------------------
class KnowledgeVector(Base):
    __tablename__ = "knowledge_vectors"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text)
    content = Column(Text)
    embedding = Column(Vector)
    source_type = Column(String(100))
    source_path = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    creator = relationship("User", back_populates="knowledge_vectors")


# ---------------------------
# CHAT_HISTORY
# ---------------------------
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    message = Column(Text, nullable=False)
    role = Column(String(20))  # 'user' or 'assistant'
    sentiment = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    user = relationship("User", back_populates="chat_history")
    ai_responses = relationship("AIResponse", back_populates="chat", cascade="all, delete")


# ---------------------------
# AI_RESPONSES
# ---------------------------
class AIResponse(Base):
    __tablename__ = "ai_responses"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chat_history.id", ondelete="CASCADE"))
    response_text = Column(Text, nullable=False)
    response_type = Column(String(50), default="rag")
    confidence = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    chat = relationship("ChatHistory", back_populates="ai_responses")

if __name__ == "__main__":
    from app.db.database import engine
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Migration completed successfully.")
