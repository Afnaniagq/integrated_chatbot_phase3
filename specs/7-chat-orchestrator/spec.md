# Feature Specification: Core Chat Orchestrator

**Feature Branch**: `7-chat-orchestrator`
**Created**: 2026-02-01
**Status**: Draft
**Input**: User description: "# Spec 7: Core Chat Orchestrator



**Status**: Next Phase

**Focus**: The Orchestrator Logic (Connecting DB to AI)



## Context

We have successfully implemented the `Conversation` and `Message` database models (Spec 6). Now, we need to create the "Brain" of the backend—the Orchestrator—which handles the flow between the user, the database context, and the OpenAI API.



## Objectives

1. **Create `backend/src/services/ai_service.py`**:

   - Implement a service class to handle AI logic.

   - **Context Injection**: Functionality to fetch the user's current `tasks` and `categories` from the database to include in the AI's System Prompt.

   - **History Retrieval**: Functionality to pull the last 10 messages from the `message` table for the specific `conversation_id` to maintain short-term memory.

   - **OpenAI Integration**: Use the `openai` library to send the combined context (system prompt + history + new message) to `gpt-4o` (or preferred model).



2. **Database Persistence Loop**:

   - Ensure that every incoming user message is saved to the `message` table before the AI call.

   - Ensure that every AI response is saved to the `message` table before being returned to the user.



3. **Update API Logic**:

   - Refactor `POST /api/messages/` in `backend/src/api/messages.py` to trigger the `ai_service`.

   - Ensure the endpoint remains asynchronous.



## Technical Requirements

- **System Prompt**: Define a clear persona: "You are a proactive Productivity Assistant. You have access to the user's current task list and help them organize, prioritize, and manage their time."

- **Environment**: Load `OPENAI_API_KEY` from the existing `.env` file.

- **Error Handling**: Implement try/except blocks for OpenAI API failures to ensure the database doesn't get stuck in an inconsistent state.



## Constraints

- **No Tools Yet**: Do not implement Function Calling or MCP tools in this spec (that is saved for Spec 8 & 9).

- **Statelessness**: The AI should rely on the database for history, not in-memory variables."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI-Powered Productivity Assistance (Priority: P1)

As a user, I want to interact with an AI assistant that understands my current tasks and priorities so that I can get contextual help with organizing and managing my productivity.

**Why this priority**: This is the core functionality that differentiates the chatbot from a generic AI assistant - it leverages the user's personal data to provide personalized assistance.

**Independent Test**: Can be fully tested by sending a message to the AI about task management and verifying that it responds with knowledge of the user's current tasks and categories.

**Acceptance Scenarios**:

1. **Given** a user has tasks in their list, **When** they ask the AI about their priorities, **Then** the AI responds with awareness of their specific tasks and can provide relevant suggestions
2. **Given** a user sends a message to the AI, **When** the system retrieves the user's context, **Then** the AI has access to the user's current tasks and categories

---

### User Story 2 - Persistent Conversation Context (Priority: P2)

As a user, I want my AI conversations to maintain context across messages so that I don't have to repeat information when discussing related topics.

**Why this priority**: Essential for creating a natural, flowing conversation experience where the AI remembers what was previously discussed.

**Independent Test**: Can be fully tested by having a multi-message conversation where the AI demonstrates knowledge of earlier exchanges.

**Acceptance Scenarios**:

1. **Given** a user is in a conversation with the AI, **When** they continue the discussion, **Then** the AI remembers previous messages and can reference them
2. **Given** a conversation history exists, **When** a new message arrives, **Then** the AI has access to the recent message history (last 10 messages)

---

### User Story 3 - Reliable Message Persistence (Priority: P3)

As a user, I want all messages in my conversation to be reliably saved so that I can return to conversations and maintain my conversation history.

**Why this priority**: Critical for data integrity and ensuring users don't lose their conversation history due to system failures.

**Independent Test**: Can be fully tested by sending messages and verifying they are saved to the database before and after AI responses.

**Acceptance Scenarios**:

1. **Given** a user sends a message, **When** the AI processes it, **Then** the message is saved to the database regardless of AI processing outcome
2. **Given** the AI generates a response, **When** the response is sent back to the user, **Then** the AI response is saved to the database

---

### Edge Cases

- What happens when the OpenAI API is unavailable or times out?
- How does the system handle extremely long conversations (when message history exceeds practical limits)?
- What occurs when the database is temporarily unavailable during AI processing?
- How does the system handle malformed messages or unexpected API responses?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create an AI service module that orchestrates communication between user, database, and OpenAI API
- **FR-002**: System MUST inject user's current tasks and categories into the AI's system prompt context
- **FR-003**: System MUST retrieve the last 10 messages from the conversation for AI context before each request
- **FR-004**: System MUST persist every user message to the database before calling the AI API
- **FR-005**: System MUST persist every AI response to the database before returning it to the user
- **FR-006**: System MUST handle OpenAI API failures gracefully without corrupting conversation data
- **FR-007**: System MUST maintain conversation isolation so users only see their own conversation data
- **FR-008**: System MUST use a clear system prompt persona of "proactive Productivity Assistant" with access to task lists
- **FR-009**: System MUST load OpenAI API key from environment variables for security
- **FR-010**: System MUST process messages asynchronously to prevent blocking the user interface

### Key Entities *(include if feature involves data)*

- **AI Service**: Core component that coordinates between database context and AI API, managing the orchestration logic
- **Conversation Context**: Collection of user data (tasks, categories, recent messages) provided to the AI for contextual responses
- **Message Persistence Loop**: Process that ensures all messages (both user and AI) are reliably stored in the database

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can engage in AI conversations where the AI demonstrates awareness of their current tasks and categories
- **SC-002**: Conversation history is maintained with AI responses showing knowledge of previous exchanges
- **SC-003**: All messages are reliably persisted in the database with no data loss during normal operation
- **SC-004**: System handles AI API failures gracefully without corrupting conversation state