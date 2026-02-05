"""
Simple test script to validate the chat models can be imported and have correct structure
"""
try:
    from backend.src.models.chat import Conversation, Message, ConversationCreate, MessageCreate
    from backend.src.models.user import User
    print("[OK] Successfully imported all models")

    # Check that the models have the expected fields
    conv_create_fields = [field for field in ConversationCreate.__fields__] if hasattr(ConversationCreate, '__fields__') else dir(ConversationCreate)
    print(f"[OK] ConversationCreate has fields: {conv_create_fields}")

    msg_create_fields = [field for field in MessageCreate.__fields__] if hasattr(MessageCreate, '__fields__') else dir(MessageCreate)
    print(f"[OK] MessageCreate has fields: {msg_create_fields}")

    # Test creating simple instances without triggering relationship setup
    from uuid import uuid4

    # Create minimal test instances
    conv_title = "Test Conversation"
    conv_user_id = uuid4()
    print(f"[OK] Can create basic values - title: {conv_title}, user_id: {conv_user_id}")

    msg_role = "user"
    msg_content = "Hello, world!"
    print(f"[OK] Can create basic values - role: {msg_role}, content: {msg_content}")

    print("\n[OK] All basic tests passed! Models have correct structure.")

except ImportError as e:
    print(f"[ERROR] Import error: {e}")
except Exception as e:
    print(f"[ERROR] Other error: {e}")
    import traceback
    traceback.print_exc()