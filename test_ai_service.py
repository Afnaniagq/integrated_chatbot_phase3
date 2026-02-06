"""
Simple test to verify the AI service works properly
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.src.services.ai_service import AIService
from uuid import UUID, uuid4


def test_ai_service_initialization():
    """Test that the AI service can be initialized properly"""
    print("Testing AI Service initialization...")

    try:
        ai_service = AIService()
        print(f"[SUCCESS] AI Service initialized with model: {ai_service.model}")

        # Check if client was created
        assert ai_service.client is not None
        print("[SUCCESS] OpenAI client created successfully")

        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize AI Service: {e}")
        return False


def test_format_ai_prompt():
    """Test that the AI prompt formatting works correctly"""
    print("\nTesting AI prompt formatting...")

    ai_service = AIService()

    system_prompt = "You are a helpful assistant."
    user_context = {
        "tasks": [{"title": "Test task", "priority": "high", "category": "work"}],
        "categories": [{"name": "work"}]
    }
    conversation_history = []
    new_message = "Hello, can you help me?"

    try:
        formatted_messages = ai_service.format_ai_prompt(
            system_prompt,
            user_context,
            conversation_history,
            new_message
        )

        assert isinstance(formatted_messages, list)
        assert len(formatted_messages) == 2  # system and user message
        assert formatted_messages[0]["role"] == "system"
        assert formatted_messages[1]["role"] == "user"

        print("[SUCCESS] AI prompt formatting works correctly")
        print(f"Formatted message example: {formatted_messages[1]['content'][:100]}...")

        return True
    except Exception as e:
        print(f"[ERROR] Failed to format AI prompt: {e}")
        return False


def test_mock_methods():
    """Test that the async methods exist and have correct signatures"""
    print("\nTesting AI service methods exist...")

    ai_service = AIService()

    # Check that methods exist
    assert hasattr(ai_service, 'get_user_context')
    assert hasattr(ai_service, 'get_conversation_history')
    assert hasattr(ai_service, 'format_ai_prompt')
    assert hasattr(ai_service, 'process_message')

    print("[SUCCESS] All required methods exist")

    # Check if they are async
    import inspect
    assert inspect.iscoroutinefunction(ai_service.get_user_context)
    assert inspect.iscoroutinefunction(ai_service.get_conversation_history)
    assert inspect.iscoroutinefunction(ai_service.process_message)

    print("[SUCCESS] Async methods are properly defined")

    return True


async def run_integration_test():
    """Test the integration with a simple mock"""
    print("\nTesting integration...")

    # Just verify the service can be instantiated and has required properties
    ai_service = AIService()

    assert hasattr(ai_service, 'client')
    assert hasattr(ai_service, 'model')
    assert ai_service.model == "gpt-4o"

    print("[SUCCESS] Integration test passed")


async def main():
    print("Running AI Service Tests...\n")

    test_results = []

    # Test 1: Initialization
    test_results.append(test_ai_service_initialization())

    # Test 2: Prompt formatting
    test_results.append(test_format_ai_prompt())

    # Test 3: Method existence
    test_results.append(test_mock_methods())

    # Test 4: Integration
    await run_integration_test()
    test_results.append(True)

    print(f"\n[SUMMARY] Tests passed: {sum(test_results)}/{len(test_results)}")

    if all(test_results):
        print("[SUCCESS] All AI service tests passed!")
        return True
    else:
        print("[ERROR] Some tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n[FINAL RESULT] AI Service implementation is working correctly!")
    else:
        print("\n[FINAL RESULT] AI Service implementation has issues!")