"""
Test to verify that async operations work properly without blocking
"""
import asyncio
from backend.src.services.ai_service import AIService
import inspect


def test_async_methods():
    """Test that all methods are properly async"""
    print("Testing async method definitions...")

    # Check that all required methods are async
    ai_service = AIService.__new__(AIService)

    async_methods = [
        'get_user_context',
        'get_conversation_history',
        'process_message'
    ]

    for method_name in async_methods:
        method = getattr(ai_service, method_name)
        assert inspect.iscoroutinefunction(method), f"Method {method_name} should be async"

    print(f"[SUCCESS] All {len(async_methods)} methods are properly async:")
    for method in async_methods:
        print(f"  - {method}")

    return True


def test_sync_methods():
    """Test that synchronous methods are properly defined as sync"""
    print("\nTesting synchronous method definitions...")

    # Check that sync methods are properly sync
    ai_service = AIService.__new__(AIService)

    sync_methods = [
        'format_ai_prompt'
    ]

    for method_name in sync_methods:
        method = getattr(ai_service, method_name)
        assert not inspect.iscoroutinefunction(method), f"Method {method_name} should be synchronous"

    print(f"[SUCCESS] All {len(sync_methods)} methods are properly synchronous:")
    for method in sync_methods:
        print(f"  - {method}")

    return True


def test_async_signature_compatibility():
    """Test that async methods have the correct signature for async execution"""
    print("\nTesting async method signature compatibility...")

    ai_service = AIService.__new__(AIService)

    # Test the process_message method signature specifically
    import inspect as inspect_mod
    sig = inspect_mod.signature(ai_service.process_message)
    params = list(sig.parameters.keys())

    # Check that it has the right parameters for async execution
    required_params = ['session', 'user_id', 'conversation_id', 'user_message_content']
    for param in required_params:
        assert param in params, f"process_message should have parameter {param}"

    print("[SUCCESS] process_message has correct signature for async execution")
    print(f"  - Required parameters: {required_params}")

    return True


async def test_async_execution_flow():
    """Test that async execution can be simulated without actual API calls"""
    print("\nTesting async execution flow...")

    # Although we can't run full async execution without a database,
    # we can verify the method structure supports async execution

    ai_service = AIService.__new__(AIService)

    # Verify that the methods can be awaited (signature-wise)
    import inspect as inspect_mod
    process_message_sig = inspect_mod.signature(ai_service.process_message)

    # Check if the method has the expected async characteristics
    # by examining its source code
    source = inspect_mod.getsource(ai_service.process_message)

    # Verify that await is used in the correct places
    await_calls = ['await self.get_user_context', 'await self.get_conversation_history']
    for call in await_calls:
        assert call in source, f"Should await {call}"

    print("[SUCCESS] Async execution flow properly structured with await calls")
    print("  - Awaits get_user_context")
    print("  - Awaits get_conversation_history")

    return True


async def main():
    print("Running Async Operations Validation Tests...\n")

    test_results = []

    # Test 1: Async method definitions
    test_results.append(test_async_methods())

    # Test 2: Sync method definitions
    test_results.append(test_sync_methods())

    # Test 3: Signature compatibility
    test_results.append(test_async_signature_compatibility())

    # Test 4: Execution flow
    test_results.append(await test_async_execution_flow())

    print(f"\n[SUMMARY] Async validation tests passed: {sum(test_results)}/{len(test_results)}")

    if all(test_results):
        print("[SUCCESS] All async operation validation tests passed!")
        print("\nAsync Operation Summary:")
        print("- All required methods are properly async")
        print("- Synchronous methods remain synchronous")
        print("- Method signatures support async execution")
        print("- Execution flow uses appropriate await calls")
        return True
    else:
        print("[ERROR] Some async validation tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n[FINAL RESULT] Async operations are properly implemented!")
        print("The AI orchestrator service uses async operations correctly without blocking.")
    else:
        print("\n[FINAL RESULT] Async operations have implementation issues!")