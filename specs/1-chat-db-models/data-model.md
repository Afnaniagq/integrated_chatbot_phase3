# Data Model Design: Chat Database Models (Phase III)

## Overview
This document defines the data model for the Conversation and Message entities required for the AI Chatbot functionality. The models follow the same patterns as existing models in the codebase to ensure consistency.

## Entity Definitions

### 1. Conversation Model

**Entity Name**: Conversation
**Description**: Represents a chat session with a user, containing multiple messages, with metadata like title and timestamps

#### Fields:
- `id`: UUID (Primary Key)
  - Type: `UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)`
  - Purpose: Unique identifier for the conversation
  - Pattern: Same as existing models (Task, User)

- `user_id`: UUID (Foreign Key)
  - Type: `UUID = Field(foreign_key="user.id", index=True)`
  - Purpose: Links the conversation to the user who owns it
  - Pattern: Same as Task.user_id relationship

- `title`: String (Optional)
  - Type: `str = Field(default=None, max_length=255)`
  - Purpose: Optional title for the conversation for chat list display
  - Pattern: Similar to Task.title but optional

- `created_at`: DateTime
  - Type: `datetime = Field(default_factory=datetime.utcnow)`
  - Purpose: Timestamp when the conversation was created
  - Pattern: Same as existing models

- `updated_at`: DateTime
  - Type: `datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})`
  - Purpose: Timestamp when the conversation was last updated
  - Pattern: Same as existing models with onupdate trigger

#### Relationships:
- `messages`: One-to-Many (to Message model)
  - Type: `List["Message"] = Relationship(back_populates="conversation")`
  - Purpose: Links to all messages in this conversation
  - Pattern: Same as User.tasks relationship

#### Validation Rules:
- All UUID fields use the same factory pattern as existing models
- Foreign key constraint ensures user_id references a valid user
- Proper indexing on user_id for efficient queries

### 2. Message Model

**Entity Name**: Message
**Description**: Represents individual chat interactions with role (user/assistant), content, and timestamp

#### Fields:
- `id`: UUID (Primary Key)
  - Type: `UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)`
  - Purpose: Unique identifier for the message
  - Pattern: Same as existing models (Task, User)

- `conversation_id`: UUID (Foreign Key)
  - Type: `UUID = Field(foreign_key="conversation.id", index=True)`
  - Purpose: Links the message to its parent conversation
  - Pattern: Similar to Task.user_id but referencing Conversation

- `user_id`: UUID (Foreign Key)
  - Type: `UUID = Field(foreign_key="user.id", index=True)`
  - Purpose: Links the message to the user who sent it (for user messages)
  - Pattern: Same as Task.user_id relationship

- `role`: String (Enum)
  - Type: `str = Field(sa_column=sa.Column(sa.Enum("user", "assistant", name="message_role_enum")))`
  - Alternative: `str = Field(max_length=20)` with validation
  - Purpose: Defines whether the message is from a user or assistant
  - Values: "user" or "assistant"

- `content`: Text
  - Type: `str = Field(max_length=10000)` (or `Text` for unlimited length)
  - Purpose: The actual message content/body
  - Pattern: Similar to Task.description but potentially longer

- `created_at`: DateTime
  - Type: `datetime = Field(default_factory=datetime.utcnow)`
  - Purpose: Timestamp when the message was created
  - Pattern: Same as existing models

#### Relationships:
- `conversation`: Many-to-One (to Conversation model)
  - Type: `"Conversation" = Relationship(back_populates="messages")`
  - Purpose: Links to the parent conversation
  - Pattern: Same as Task.user relationship

#### Validation Rules:
- Role field restricted to "user" or "assistant" values
- Foreign key constraints ensure data integrity
- Proper indexing on conversation_id and user_id for efficient queries
- Content length validation to prevent extremely large messages

## Relationship Mapping

### User ↔ Conversation
- **Type**: One-to-Many
- **Pattern**: User has many conversations, each conversation belongs to one user
- **Implementation**:
  - User model: `conversations: List["Conversation"] = Relationship(back_populates="user")`
  - Conversation model: `user: "User" = Relationship(back_populates="conversations")`

### Conversation ↔ Message
- **Type**: One-to-Many
- **Pattern**: Conversation has many messages, each message belongs to one conversation
- **Implementation**:
  - Conversation model: `messages: List["Message"] = Relationship(back_populates="conversation")`
  - Message model: `conversation: "Conversation" = Relationship(back_populates="messages")`

### User ↔ Message
- **Type**: One-to-Many
- **Pattern**: User has many messages (sent by the user), each message is associated with one user
- **Implementation**:
  - User model: `messages: List["Message"] = Relationship(back_populates="user_sent_messages")`
  - Message model: `user_sent_messages: "User" = Relationship(back_populates="messages")`

## Security & Isolation

### Multi-Tenant Security
- Foreign key constraints ensure messages and conversations are tied to specific users
- Indexes on user_id fields for efficient user isolation queries
- Proper relationship definitions prevent cross-user data access

### Data Integrity
- Foreign key constraints maintain referential integrity
- Cascading behaviors to be defined based on business requirements
- Proper indexing for query performance

## Indexes for Performance

### Conversation Model
- Primary index on `id`
- Index on `user_id` for efficient user-based queries
- Index on `created_at` for chronological sorting

### Message Model
- Primary index on `id`
- Index on `conversation_id` for conversation-based queries
- Index on `user_id` for user-based queries
- Index on `created_at` for chronological sorting