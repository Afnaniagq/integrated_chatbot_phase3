# Implementation Tasks: Core Chat Orchestrator

**Feature**: Core Chat Orchestrator
**Branch**: 7-chat-orchestrator
**Created**: 2026-02-01
**Status**: Ready for Implementation

## Dependencies

- User Story 2 [US2] depends on User Story 1 [US1] (requires basic AI service)
- User Story 3 [US3] depends on User Story 1 [US1] (requires message persistence functionality)

## Parallel Execution Examples

- [P] T001-T002: Setup tasks can run in parallel (different aspects)
- [P] T005-T006: Service methods can be developed in parallel after base class is created

## Implementation Strategy

Start with User Story 1 (AI-Powered Productivity Assistance) as MVP, then add User Story 2 (Persistent Conversation Context) and User Story 3 (Reliable Message Persistence).

## Phase 1: Setup

- [X] T001 Install OpenAI library dependency in backend
- [X] T002 Verify environment variable setup for OPENAI_API_KEY

## Phase 2: Foundational

- [X] T003 Create backend/src/services/ai_service.py with AIService class skeleton
- [X] T004 Implement constructor with OpenAI AsyncClient initialization
- [X] T005 Define format_ai_prompt method to structure context for AI
- [X] T006 Add error handling framework for OpenAI API calls

## Phase 3: [US1] AI-Powered Productivity Assistance

Goal: Enable users to interact with an AI assistant that understands their current tasks and priorities to provide contextual help with organizing and managing productivity.

Independent Test: Can be fully tested by sending a message to the AI about task management and verifying that it responds with knowledge of the user's current tasks and categories.

- [X] T007 [US1] Implement get_user_context method to fetch user's tasks and categories from database
- [X] T008 [US1] Implement get_conversation_history method to retrieve last 10 messages from conversation
- [X] T009 [US1] Implement process_message method with basic message flow (save, call AI, return response)
- [X] T010 [US1] Update POST /api/messages/ endpoint to use AI service instead of basic message creation
- [X] T011 [US1] Test basic AI functionality with context injection

## Phase 4: [US2] Persistent Conversation Context

Goal: Enable AI conversations to maintain context across messages so users don't have to repeat information when discussing related topics.

Independent Test: Can be fully tested by having a multi-message conversation where the AI demonstrates knowledge of earlier exchanges.

- [X] T012 [US2] Enhance AI prompt formatting to better incorporate conversation history
- [X] T013 [US2] Improve context assembly to ensure relevant history is provided to AI
- [X] T014 [US2] Test multi-message conversations for context awareness

## Phase 5: [US3] Reliable Message Persistence

Goal: Ensure all messages in conversation are reliably saved so users can return to conversations and maintain conversation history.

Independent Test: Can be fully tested by sending messages and verifying they are saved to the database before and after AI responses.

- [X] T015 [US3] Implement guaranteed message persistence before AI API calls
- [X] T016 [US3] Implement robust AI response saving after API success
- [X] T017 [US3] Add error recovery to ensure messages are saved even when AI API fails
- [X] T018 [US3] Test message persistence under various error conditions

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T019 Validate all security aspects (user isolation, context injection)
- [X] T020 Test proper async operation without blocking
- [X] T021 Verify graceful degradation when OpenAI API is unavailable
- [X] T022 Clean up temporary code or debugging statements
- [X] T023 Update documentation with new service architecture