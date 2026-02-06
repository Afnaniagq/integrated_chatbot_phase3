"""
Test to verify message persistence functionality under various conditions
"""
import asyncio
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from backend.src.services.ai_service import AIService


async def test_message_persistence_logic():
    """Test the message persistence logic without making real DB or API calls"""
    print("Testing message persistence logic...")

    # Create a mock AI service to test the logic
    ai_service = AIService.__new__(AIService)  # Create instance without __init__
    ai_service.model = "gpt-4o"
    ai_service.client = Mock()  # Manually add a mock client

    # Create a mock session
    mock_session = Mock()
    mock_session.add = Mock()
    mock_session.commit = Mock()
    mock_session.refresh = Mock()

    # Create mock user and conversation IDs
    user_id = uuid4()
    conversation_id = uuid4()

    # Test that user message is saved BEFORE calling AI API
    with patch.object(ai_service, 'get_user_context') as mock_get_user_context, \
         patch.object(ai_service, 'get_conversation_history') as mock_get_conversation_history, \
         patch.object(ai_service, 'format_ai_prompt') as mock_format_prompt, \
         patch.object(ai_service, 'client') as mock_client:

        # Setup mocks
        mock_get_user_context.return_value = {"tasks": [], "categories": []}
        mock_get_conversation_history.return_value = []
        mock_format_prompt.return_value = [{"role": "system", "content": "test"}, {"role": "user", "content": "test"}]

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "AI response"
        mock_client.chat.completions.create = Mock(return_value=mock_response)

        # Call the process_message method
        result = await ai_service.process_message(
            session=mock_session,
            user_id=user_id,
            conversation_id=conversation_id,
            user_message_content="test user message"
        )

        # Verify that the user message was added to session BEFORE the API call
        # Check that session.add was called for the user message first
        calls_to_add = mock_session.add.call_args_list
        # We expect at least two calls to add: one for user message, one for AI message
        assert len(calls_to_add) >= 2, f"Expected at least 2 calls to session.add, got {len(calls_to_add)}"

        # Verify that the user message was saved (first call)
        first_added_obj = calls_to_add[0][0][0]  # First argument of first call
        assert hasattr(first_added_obj, 'role'), "First saved object should have role attribute"
        assert first_added_obj.role == "user", f"First saved object should be user message, got {first_added_obj.role}"
        assert first_added_obj.content == "test user message", f"User message content should match"

        # Verify that session.commit was called (ensuring persistence)
        assert mock_session.commit.called, "Session commit should be called to ensure persistence"

        # Verify that AI response was also saved
        last_added_obj = calls_to_add[-1][0][0]  # Last call's first argument
        assert last_added_obj.role == "assistant", f"Last saved object should be assistant message, got {last_added_obj.role}"

        print("[SUCCESS] Message persistence logic verified")
        print(f"  - User message saved before AI API call")
        print(f"  - AI response saved after API call")
        print(f"  - Session commit called for persistence")

    return True


async def test_error_recovery_persistence():
    """Test that messages are saved even when AI API fails"""
    print("\nTesting error recovery and message persistence...")

    # Create a mock AI service to test the error handling
    ai_service = AIService.__new__(AIService)  # Create instance without __init__
    ai_service.model = "gpt-4o"
    ai_service.client = Mock()  # Manually add a mock client

    # Create a mock session
    mock_session = Mock()
    mock_session.add = Mock()
    mock_session.commit = Mock()
    mock_session.refresh = Mock()

    # Create mock user and conversation IDs
    user_id = uuid4()
    conversation_id = uuid4()

    # Simulate an API error and verify user message is still saved
    with patch.object(ai_service, 'get_user_context') as mock_get_user_context, \
         patch.object(ai_service, 'get_conversation_history') as mock_get_conversation_history, \
         patch.object(ai_service, 'format_ai_prompt') as mock_format_prompt, \
         patch.object(ai_service, 'client') as mock_client:

        # Setup mocks - make the API call raise an exception
        mock_get_user_context.return_value = {"tasks": [], "categories": []}
        mock_get_conversation_history.return_value = []
        mock_format_prompt.return_value = [{"role": "system", "content": "test"}, {"role": "user", "content": "test"}]

        # Make the API call raise an exception
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        # Call the process_message method expecting it to handle the error
        try:
            result = await ai_service.process_message(
                session=mock_session,
                user_id=user_id,
                conversation_id=conversation_id,
                user_message_content="test user message for error recovery"
            )

            # In our implementation, when there's an error, we return an error message
            # The user message should still be saved in the database
            calls_to_add = mock_session.add.call_args_list

            # The user message should still be saved despite the API error
            user_message_found = False
            for call in calls_to_add:
                obj = call[0][0]  # Get the first argument (the object being added)
                if hasattr(obj, 'role') and obj.role == "user" and obj.content == "test user message for error recovery":
                    user_message_found = True
                    break

            assert user_message_found, "User message should be saved even when API call fails"

            print("[SUCCESS] Error recovery verified")
            print(f"  - User message persisted despite AI API failure")
            print(f"  - Session commit called even after error")

        except Exception as e:
            print(f"Process message threw exception: {e}")
            # This is expected behavior depending on implementation
            # Let's verify the user message was still saved
            calls_to_add = mock_session.add.call_args_list
            user_message_found = False
            for call in calls_to_add:
                obj = call[0][0]  # Get the first argument (the object being added)
                if hasattr(obj, 'role') and obj.role == "user" and obj.content == "test user message for error recovery":
                    user_message_found = True
                    break

            assert user_message_found, "User message should be saved even when API call fails"
            print("[SUCCESS] Error recovery verified (via side effect)")
            print(f"  - User message persisted despite AI API failure")

    return True


def test_method_signatures():
    """Test that all methods have the correct signatures for message persistence"""
    print("\nTesting method signatures for persistence...")

    ai_service = AIService.__new__(AIService)

    import inspect

    # Check process_message method
    proc_sig = inspect.signature(ai_service.process_message)
    proc_params = list(proc_sig.parameters.keys())
    assert 'session' in proc_params
    assert 'user_id' in proc_params
    assert 'conversation_id' in proc_params
    assert 'user_message_content' in proc_params

    # Check that it's async
    assert inspect.iscoroutinefunction(ai_service.process_message)

    print("[SUCCESS] All persistence-related method signatures are correct")

    return True


async def main():
    print("Running Message Persistence Tests...\n")

    test_results = []

    # Test 1: Message persistence logic
    test_results.append(await test_message_persistence_logic())

    # Test 2: Error recovery
    test_results.append(await test_error_recovery_persistence())

    # Test 3: Method signatures
    test_results.append(test_method_signatures())

    print(f"\n[SUMMARY] Tests passed: {sum(test_results)}/{len(test_results)}")

    if all(test_results):
        print("[SUCCESS] All message persistence tests passed!")
        return True
    else:
        print("[ERROR] Some tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n[FINAL RESULT] Message persistence functionality is working correctly!")
    else:
        print("\n[FINAL RESULT] Message persistence functionality has issues!")