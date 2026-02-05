from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from ..database import get_session
from ..models.chat import Message, MessageCreate, MessageRead, MessageUpdate, Conversation
from uuid import UUID
from src.api.deps import get_current_user_id
from ..services.ai_service import AIService


router = APIRouter()


@router.post("/", response_model=MessageRead)
async def create_message(
    *,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    message: MessageCreate
):
    """
    Process a new message with AI assistance.
    For user messages, calls the AI service to generate a response.
    For AI responses, saves directly to the database.
    """
    from uuid import UUID as PyUUID
    user_uuid = PyUUID(current_user_id)

    # Verify that the user has access to the conversation
    conversation = session.get(Conversation, message.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized to add messages to this conversation")

    # Check if this is a user message (as opposed to an AI-generated message)
    if message.role == "user":
        # Initialize AI service and process the message
        ai_service = AIService()

        # Process the message using the AI service
        # This will save the user message, call the AI, and save the AI response
        ai_response_content = await ai_service.process_message(
            session=session,
            user_id=user_uuid,
            conversation_id=message.conversation_id,
            user_message_content=message.content
        )

        # Return the AI-generated response message
        # Find the AI message that was just created
        ai_message = session.exec(
            select(Message)
            .where(
                Message.conversation_id == message.conversation_id,
                Message.role == "assistant",
                Message.content == ai_response_content
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        ).first()

        if not ai_message:
            # If we can't find the AI message, create a generic one
            ai_message = Message(
                conversation_id=message.conversation_id,
                user_id=user_uuid,
                role="assistant",
                content=ai_response_content
            )
            session.add(ai_message)
            session.commit()
            session.refresh(ai_message)

        return ai_message

    elif message.role == "assistant":
        # If this is an AI-generated message being saved directly
        db_message = Message.model_validate(message)
        db_message.user_id = user_uuid

        session.add(db_message)
        session.commit()
        session.refresh(db_message)

        return db_message

    else:
        raise HTTPException(status_code=400, detail="Invalid message role. Must be 'user' or 'assistant'.")


@router.get("/", response_model=List[MessageRead])
async def read_messages(
    *,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    conversation_id: UUID,
    offset: int = 0,
    limit: int = 100
):
    """
    Retrieve messages for a specific conversation.
    """
    from uuid import UUID as PyUUID
    user_uuid = PyUUID(current_user_id)

    # Verify that the user has access to the conversation
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    # Return messages for the specified conversation
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
    ).all()

    return messages


@router.get("/{message_id}", response_model=MessageRead)
async def read_message(
    *,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    conversation_id: UUID,
    message_id: UUID
):
    """
    Get a specific message by ID.
    """
    from uuid import UUID as PyUUID
    user_uuid = PyUUID(current_user_id)

    # Verify that the user has access to the conversation
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    message = session.get(Message, message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Verify that the message belongs to the specified conversation
    if message.conversation_id != conversation_id:
        raise HTTPException(status_code=404, detail="Message not found in this conversation")

    return message


@router.put("/{message_id}", response_model=MessageRead)
async def update_message(
    *,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    conversation_id: UUID,
    message_id: UUID,
    message: MessageUpdate
):
    """
    Update a message.
    """
    from uuid import UUID as PyUUID
    user_uuid = PyUUID(current_user_id)

    # Verify that the user has access to the conversation
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    db_message = session.get(Message, message_id)

    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Verify that the message belongs to the specified conversation and user
    if db_message.conversation_id != conversation_id or db_message.user_id != user_uuid:
        raise HTTPException(status_code=404, detail="Message not found in this conversation")

    update_data = message.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_message, field, value)

    session.add(db_message)
    session.commit()
    session.refresh(db_message)

    return db_message


@router.delete("/{message_id}")
async def delete_message(
    *,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    conversation_id: UUID,
    message_id: UUID
):
    """
    Delete a message.
    """
    from uuid import UUID as PyUUID
    user_uuid = PyUUID(current_user_id)

    # Verify that the user has access to the conversation
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    message = session.get(Message, message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Verify that the message belongs to the specified conversation and user
    if message.conversation_id != conversation_id or message.user_id != user_uuid:
        raise HTTPException(status_code=404, detail="Message not found in this conversation")

    session.delete(message)
    session.commit()

    return {"message": "Message deleted successfully"}