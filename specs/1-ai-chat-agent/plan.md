# Plan: AI Chat Agent Implementation

## Context
This plan addresses the integration of an AI Chat Agent into the existing FastAPI backend to enable natural language task management. The primary goal is to enhance user interaction by allowing task creation, listing, updating, and deletion through conversational AI, while strictly enforcing user data isolation. This integration leverages OpenAI's tool-calling capabilities and builds upon the robust `user_id` handling already present in the MCP server and task/category services.

## Recommended Approach

The core of the implementation will involve modifying the `AIService.process_message` method in `backend/src/services/ai_service.py`. This method will be responsible for orchestrating the AI interaction, including:

1.  **AI Tool-Calling Integration**:
    *   The `AIService` will dynamically retrieve the available MCP tools from `mcp_server.handle_list_tools()`.
    *   These tools will be formatted and passed to the OpenAI API in the `tools` parameter during `chat.completions.create` calls.
    *   The AI's response will be checked for `tool_calls`. If present, the corresponding MCP tool will be executed via `mcp_server.handle_execute_tool()`.

2.  **`user_id` Propagation**:
    *   The existing architecture already ensures that `user_id` is passed from the `messages.py` API endpoint to `AIService.process_message`.
    *   Crucially, when `mcp_server.handle_execute_tool()` is called, the `user_id` will be explicitly included in the arguments passed to the MCP tool wrapper functions. The exploration confirmed that the MCP server correctly injects this `user_id` into the tool arguments, and the `task_service.py` and `category_service.py` functions already use `user_id` for authorization.

3.  **Conversation History Management**:
    *   The `AIService.get_conversation_history()` method will fetch recent messages.
    *   This history will be included in the `messages` parameter of the OpenAI API call to provide context to the AI.

4.  **Error Handling and Clarification**:
    *   **AI Intent Failure (Misinterpretation/No Tool Call)**: If the OpenAI API response does not contain `tool_calls` but the user's intent strongly suggested a task management action, or if the general response is unhelpful, the `AIService` will generate a clarification prompt (e.g., "I'm not sure I understood your request. Could you please rephrase it?"). This will be implemented by inspecting the AI's first response.
    *   **MCP Tool Execution Failure (Generic)**: After `mcp_server.handle_execute_tool()` returns, its result will be checked for failure indicators (e.g., `{"success": False, "error": "..."}`). If a failure is detected, a generic friendly error message will be returned to the user (e.g., "Sorry, I encountered an issue while trying to perform that action. Please try again.").
    *   **Unauthorized Access**: The `task_service.py` and `category_service.py` functions already return `None` or `False` if a user attempts an unauthorized operation (e.g., modifying another user's task). The `AIService` will interpret these specific failure responses from `mcp_server.handle_execute_tool()` (which propagates these service-level failures) and return an explicit "You are not authorized to modify this task." message to the user.

5.  **`src/api/messages.py` Update**:
    *   The `create_message` endpoint in `backend/src/api/messages.py` already correctly calls `ai_service.process_message`, passing the `current_user_id` and `conversation_id`. No significant changes are required here, beyond ensuring proper import and instantiation of the `AIService`.

### Critical Files to be Modified/Inspected

*   `backend/src/services/ai_service.py`: This will be the primary file for implementing the AI orchestration logic, tool integration, conversation history management, and detailed error/clarification handling.
*   `backend/src/api/messages.py`: Will require updating to import and use the new `AIService` with its enhanced capabilities.
*   `backend/src/mcp/server.py`: Will be inspected to confirm the `user_id` injection mechanism for tool execution, but no modifications are anticipated.
*   `backend/src/services/task_service.py`: Will be inspected to ensure unauthorized access attempts result in distinct exceptions or `None`/`False` returns that `ai_service.py` can interpret for specific unauthorized access messages.
*   `backend/src/services/category_service.py`: Similar to `task_service.py`, this will be inspected for its unauthorized access handling.

### Verification
End-to-end testing will involve:
1.  Sending various natural language prompts to the `/api/messages` endpoint, covering task creation, listing, updating, and deletion.
2.  Verifying that tasks are correctly managed (created, listed, updated, deleted) in the Neon PostgreSQL database for the authenticated `user_id`.
3.  Testing edge cases for AI intent failure, MCP tool execution failure, and unauthorized task modification, and verifying that the AI agent responds with the specified clarification or error messages.
4.  Ensuring conversation history is maintained and influences AI responses.
5.  Confirming that non-task-management queries receive appropriate general AI responses.
