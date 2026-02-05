from sqlalchemy.orm import Session
from app.models.models import Conversation, Message
from typing import List, Optional
from uuid import UUID

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Conversation]:
        return self.db.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .order_by(Conversation.created_at.desc())\
            .offset(skip).limit(limit).all()

    def get_by_id(self, conversation_id: UUID) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def create_message(self, message: Message) -> Message:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, conversation_id: UUID) -> List[Message]:
        return self.db.query(Message)\
            .filter(Message.conversation_id == conversation_id)\
            .order_by(Message.created_at.asc())\
            .all()
