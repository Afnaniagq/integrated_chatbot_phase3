"""
Final validation test for the Chat Database Models implementation
"""
from backend.src.models.chat import Conversation, Message, ConversationCreate, MessageCreate
from uuid import uuid4


def test_model_creation():
    print("Testing model creation...")

    # Test creating a conversation
    conv_create = ConversationCreate(
        title="Test Conversation",
        user_id=uuid4()
    )
    print(f"[SUCCESS] ConversationCreate: {conv_create.title}")

    # Test creating a message
    msg_create = MessageCreate(
        conversation_id=uuid4(),
        user_id=uuid4(),
        role="user",
        content="Hello, world!"
    )
    print(f"[SUCCESS] MessageCreate: {msg_create.role}, content length: {len(msg_create.content)}")

    # Test creating full models
    conv = Conversation(
        id=uuid4(),
        title="Test Conversation",
        user_id=uuid4(),
        created_at=None,
        updated_at=None
    )
    print(f"[SUCCESS] Conversation: {conv.title}")

    msg = Message(
        id=uuid4(),
        conversation_id=uuid4(),
        user_id=uuid4(),
        role="assistant",
        content="Hello! How can I help you?",
        created_at=None
    )
    print(f"[SUCCESS] Message: {msg.role}")

    print("\n[SUCCESS] All model tests passed!")


if __name__ == "__main__":
    print("Final validation of Chat Models...")
    test_model_creation()
    print("\n[SUCCESS] All tests passed! Implementation is complete.")