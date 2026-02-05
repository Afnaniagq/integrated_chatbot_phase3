"""
SQLModel Chat schema for Conversation and Message models
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, List, Optional
import sqlalchemy

if TYPE_CHECKING:
    from src.models.user import User

class ConversationBase(SQLModel):
    """Base model for Conversation with common fields"""
    title: Optional[str] = Field(default=None, max_length=255)
    user_id: UUID = Field(foreign_key="user.id", index=True)


class Conversation(ConversationBase, table=True):
    """
    Conversation model for the database
    Groups messages into chat sessions for users
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationRead(ConversationBase):
    """Response model for reading conversation data"""
    id: UUID
    created_at: datetime
    updated_at: datetime


class ConversationCreate(ConversationBase):
    """Request model for creating a conversation"""
    pass


class ConversationUpdate(SQLModel):
    """Request model for updating a conversation"""
    title: Optional[str] = None


class MessageBase(SQLModel):
    """Base model for Message with common fields"""
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str = Field(max_length=10000)  # Support longer messages


class Message(MessageBase, table=True):
    """
    Message model for the database
    Stores individual chat interactions with role and content
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    user_sent_messages: "User" = Relationship(back_populates="messages_sent")


class MessageRead(MessageBase):
    """Response model for reading message data"""
    id: UUID
    created_at: datetime


class MessageCreate(MessageBase):
    """Request model for creating a message"""
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str = Field(max_length=10000)


class MessageUpdate(SQLModel):
    """Request model for updating a message"""
    content: Optional[str] = Field(default=None, max_length=10000)