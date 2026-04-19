from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.rag_pipeline import RAGPipeline
from app.models.models import Conversation, Message, User
from app.repositories.conversation_repo import ConversationRepository
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationService:
    def __init__(self, db: Session):
        self.repo = ConversationRepository(db)
        self.rag = RAGPipeline(db)

    def create_conversation(
        self, current_user: User, title: str = None
    ) -> Conversation:
        if not title:
            title = f"Chat {current_user.username}"

        new_conv = Conversation(user_id=current_user.id, title=title)
        return self.repo.create_conversation(new_conv)

    def get_user_conversations(
        self, current_user: User, skip: int = 0, limit: int = 100
    ):
        return self.repo.get_by_user(current_user.id, skip, limit)

    def get_conversation_details(
        self, conversation_id: UUID, current_user: User
    ) -> Conversation:
        conv = self.repo.get_by_id(conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conv.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to see this conversation"
            )
        return conv

    def get_messages(self, conversation_id: UUID, current_user: User):
        # Validate ownership first
        self.get_conversation_details(conversation_id, current_user)
        return self.repo.get_messages(conversation_id)

    def delete_conversation(self, conversation_id: UUID, current_user: User):
        # Validate ownership
        self.get_conversation_details(conversation_id, current_user)
        return self.repo.delete_conversation(conversation_id)

    async def send_message(
        self, conversation_id: UUID, message_text: str, current_user: User
    ):
        # 1. Validate Conversation
        conv = self.get_conversation_details(conversation_id, current_user)

        # 2. Save User Message
        user_msg = Message(
            conversation_id=conversation_id, sender="user", message=message_text
        )
        saved_user_msg = self.repo.create_message(user_msg)

        # 3. Generate AI Response (RAG)
        try:
            ai_response_text = self.rag.run(str(conversation_id), message_text)
        except Exception as e:
            # Fallback if AI fails
            logger.error(
                f"AI Generation Error for conversation {conversation_id}: {str(e)}",
                exc_info=True,
            )
            ai_response_text = "Maaf, saya sedang mengalami gangguan sistem sementara."

        # 4. Save AI Response
        ai_msg = Message(
            conversation_id=conversation_id, sender="llm", message=ai_response_text
        )
        saved_ai_msg = self.repo.create_message(ai_msg)

        # Return both new messages to update UI immediately
        return [saved_user_msg, saved_ai_msg]
