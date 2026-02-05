from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from ..database import get_session
from ..models.chat import Conversation, ConversationCreate, ConversationRead, ConversationUpdate
from uuid import UUID
from src.api.deps import get_current_user_id


router = APIRouter()


@router.post("/", response_model=ConversationRead)
async def create_conversation(
    *,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    conversation: ConversationCreate
):
    """
    Create a new conversation for the current user.
    """
    # Convert the string user_id to UUID for the database
    from uuid import UUID as PyUUID
    user_uuid = PyUUID(current_user_id)

    db_conversation = Conversation.model_validate(conversation)
    db_conversation.user_id = user_uuid

    session.add(db_conversation)
    session.commit()
    session.refresh(db_conversation)

    return db_conversation


@router.get("/", response_model=List[ConversationRead])
async def read_conversations(
    *,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    offset: int = 0,
    limit: int = 100
):
    """
    Retrieve conversations for the current user.
    """
    from uuid import UUID as PyUUID
    user_uuid = PyUUID(current_user_id)

    # Only return conversations owned by the current user
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_uuid)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return conversations


@router.get("/{conversation_id}", response_model=ConversationRead)
async def read_conversation(
    *,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    conversation_id: UUID
):
    """
    Get a specific conversation by ID.
    """
    from uuid import UUID as PyUUID
    user_uuid = PyUUID(current_user_id)

    conversation = session.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Verify that the conversation belongs to the current user
    if conversation.user_id != user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    return conversation


@router.put("/{conversation_id}", response_model=ConversationRead)
async def update_conversation(
    *,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    conversation_id: UUID,
    conversation: ConversationUpdate
):
    """
    Update a conversation.
    """
    from uuid import UUID as PyUUID
    user_uuid = PyUUID(current_user_id)

    db_conversation = session.get(Conversation, conversation_id)

    if not db_conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Verify that the conversation belongs to the current user
    if db_conversation.user_id != user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized to update this conversation")

    update_data = conversation.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_conversation, field, value)

    session.add(db_conversation)
    session.commit()
    session.refresh(db_conversation)

    return db_conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    *,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    conversation_id: UUID
):
    """
    Delete a conversation.
    """
    from uuid import UUID as PyUUID
    user_uuid = PyUUID(current_user_id)

    conversation = session.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Verify that the conversation belongs to the current user
    if conversation.user_id != user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized to delete this conversation")

    session.delete(conversation)
    session.commit()

    return {"message": "Conversation deleted successfully"}