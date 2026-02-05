from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.conversation import ConversationResponse, MessageResponse, ChatRequest, ChatResponse, ConversationCreate
from app.services.conversation_service import ConversationService
from app.models.models import User

router = APIRouter()

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    data: ConversationCreate = None, # Make it optional for backward compatibility if needed, or default
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ConversationService(db)
    title = data.title if data else None
    return service.create_conversation(current_user, title)

@router.get("/", response_model=List[ConversationResponse])
def get_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ConversationService(db)
    return service.get_user_conversations(current_user, skip, limit)

@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation_detail(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ConversationService(db)
    return service.get_conversation_details(conversation_id, current_user)

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ConversationService(db)
    success = service.delete_conversation(conversation_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation could not be deleted")
    return None

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def get_raw_messages(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ConversationService(db)
    return service.get_messages(conversation_id, current_user)

@router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def chat_message(
    conversation_id: UUID,
    chat_data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ConversationService(db)
    new_messages = await service.send_message(conversation_id, chat_data.message, current_user)
    return {"messages": new_messages}
