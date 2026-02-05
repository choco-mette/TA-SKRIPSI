from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from app.models.models import Message

class ChatMemory:
    def __init__(self, db: Session):
        self.db = db

    def get_chat_history(self, conversation_id: str, limit: int = 10) -> List[BaseMessage]:
        """
        Retrieves the last N messages from a conversation and formates them 
        as LangChain Message objects (HumanMessage/AIMessage).
        """
        # Fetch messages sorted by created_at DESC to get the latest ones
        messages_db = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.created_at)).limit(limit).all()

        # Reverse to chronological order (Oldest -> Newest) for the LLM context
        messages_db.reverse()

        chat_history = []
        for msg in messages_db:
            if msg.sender == 'user':
                chat_history.append(HumanMessage(content=msg.message))
            elif msg.sender == 'llm':
                chat_history.append(AIMessage(content=msg.message))
        
        return chat_history
