# Feature Specification: AI Chat Agent Integration

**Feature Branch**: `1-ai-chat-agent`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Phase: 3 - AI Integration

Spec: spec-9-ai-agent.md

Focus: The Orchestrator / AI Service

Context:
I have successfully completed Spec-8. The MCP server is initialized in main.py,
and the tools (add_task, get_tasks, etc.) are verified to work with the
Neon PostgreSQL database (confirmed 201 Created on task insertion).

Requirements for Spec-9:
1. Create `src/services/ai_service.py` using the OpenAI SDK (or LangChain/LangGraph).
2. Implement a 'Chat Agent' that uses OpenAI's tool-calling (function calling)
   to interface with the MCP tools defined in Spec-8.
3. The agent must:
   - Accept a user message and conversation history.
   - Detect if the user wants to manage tasks (create, list, update, delete).
   - Call the appropriate MCP tool and process the result.
   - Return a natural language response to the user.
4. Update `src/api/messages.py` to use this new `AIService` instead of
   the current placeholder logic.
5. Ensure the Agent uses the `user_id` from the authenticated session
   to ensure users only modify their own tasks.

Constraints:
- Use the existing `Settings` class for the OPENAI_API_KEY.
- Keep the logic modular so it can be easily tested via the `/api/messages` endpoint."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manage Tasks via Chat (Priority: P1)

As a user, I want to interact with the AI chat agent to create, list, update, and delete my tasks through natural language, so that I can manage my tasks efficiently without using direct API calls.

**Why this priority**: This is the core functionality of the AI agent, providing immediate value by enabling natural language task management.

**Independent Test**: This can be fully tested by sending various task management requests (e.g., "create a task", "list my tasks", "update task X", "delete task Y") and verifying the agent correctly interprets the intent, calls the MCP tool, and responds appropriately.

**Acceptance Scenarios**:

1.  **Given** I am an authenticated user, **When** I send a message like "Create a new task to buy groceries", **Then** the AI agent creates the task using the MCP `add_task` tool for my `user_id` and responds with a confirmation in natural language.
2.  **Given** I am an authenticated user with existing tasks, **When** I send a message like "List all my tasks", **Then** the AI agent calls the MCP `get_tasks` tool for my `user_id` and responds with a list of my tasks in natural language.
3.  **Given** I am an authenticated user with an existing task, **When** I send a message like "Update task [ID] to completed", **Then** the AI agent calls the MCP `update_task` tool for my `user_id` and responds with a confirmation.
4.  **Given** I am an authenticated user with an existing task, **When** I send a message like "Delete task [ID]", **Then** the AI agent calls the MCP `delete_task` tool for my `user_id` and responds with a confirmation.

---

### User Story 2 - Get General AI Response (Priority: P2)

As a user, I want the AI chat agent to provide natural language responses to general questions or non-task-management queries, so that I can have a flexible conversational experience.

**Why this priority**: This ensures the agent is not limited to only task management and can handle general chat, improving the overall user experience.

**Independent Test**: This can be tested by sending non-task-management messages (e.g., "Hello", "How are you?") and verifying the agent provides a coherent natural language response without attempting to call an MCP tool.

**Acceptance Scenarios**:

1.  **Given** I am an authenticated user, **When** I send a general message not related to task management, **Then** the AI agent responds in natural language without invoking any MCP tools.

---

### Edge Cases

- When the AI agent fails to detect a tool call or misinterprets user intent, it will ask for clarification.
- When an MCP tool call fails (e.g., database error, invalid task ID), the system will inform the user with a generic, friendly error message.
- If a user tries to modify a task that does not belong to them, the system will deny the action and inform the user of unauthorized access.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST create `src/services/ai_service.py`.
- **FR-002**: The `AIService` in `src/services/ai_service.py` MUST implement a chat agent using OpenAI's tool-calling capabilities.
- **FR-003**: The chat agent MUST accept a user message and conversation history as input.
- **FR-004**: The chat agent MUST detect user intent for task management operations (create, list, update, delete).
- **FR-005**: The chat agent MUST call the appropriate MCP tool based on detected intent.
- **FR-006**: The chat agent MUST process the result from the MCP tool call.
- **FR-007**: The chat agent MUST return a natural language response to the user.
- **FR-008**: The system MUST update `src/api/messages.py` to use the new `AIService`.
- **FR-009**: The AI agent MUST use the `user_id` from the authenticated session for all MCP tool calls to ensure data isolation.
- **FR-010**: The `AIService` MUST use the existing `Settings` class for retrieving the `OPENAI_API_KEY`.
- **FR-011**: The `AIService` logic MUST be modular to allow easy testing via the `/api/messages` endpoint.
- **FR-012**: The agent MUST explicitly ask for clarification when it fails to detect a tool call or misinterprets user intent.
- **FR-013**: The agent MUST inform the user with a generic, friendly error message when an MCP tool call fails.
- **FR-014**: The agent MUST deny and inform the user of unauthorized access if an authenticated user attempts to modify a task they do not own.

### Key Entities

- **User**: The authenticated individual interacting with the chat agent. Identified by `user_id`.
- **Task**: A unit of work managed by the MCP tools, associated with a `user_id`, and having properties like title, description, and status.
- **Message**: An exchange of text between the user and the AI agent, forming the conversation history.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully create, list, update, and delete tasks through natural language commands with the AI agent in less than 5 seconds per interaction.
- **SC-002**: The AI agent accurately identifies user intent for task management operations over 95% of the time.
- **SC-003**: The `src/api/messages.py` endpoint successfully integrates with and utilizes the `AIService` for all message processing.
- **SC-004**: Data isolation is maintained, with users unable to view or modify tasks belonging to other users.
- **SC-005**: The `AIService` is unit-testable and can be invoked programmatically for testing purposes.