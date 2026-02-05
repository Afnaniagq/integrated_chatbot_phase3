"""
SQLModel User schema
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, List, Optional
import time

if TYPE_CHECKING:
    from src.models.task import Task
    from src.models.category import Category
    from src.models.trash_bin import TrashBin # ADD THIS IMPORT
    from src.models.chat import Conversation, Message

class UserBase(SQLModel):
    """Base model for User with common fields"""
    email: str = Field(unique=True, nullable=False, max_length=255)
    name: str = Field(nullable=True, max_length=255)
    is_active: bool = Field(default=True)

class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    # THIS LINE IS MISSING:
    hashed_password: str = Field(nullable=False) 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")
    categories: List["Category"] = Relationship(back_populates="user")
    trash_items: List["TrashBin"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages_sent: List["Message"] = Relationship(back_populates="user_sent_messages")

class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    email: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None