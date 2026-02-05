# Implementation Plan: Core Chat Orchestrator

**Branch**: 7-chat-orchestrator
**Created**: 2026-02-01
**Status**: Draft
**Feature**: specs/7-chat-orchestrator/spec.md

## Technical Context

### Current State
The application currently has:
- Working database models for Conversation and Message (implemented in previous phase)
- Working API endpoints for conversations and messages
- User authentication and authorization system
- Existing task and category models with user relationships
- OpenAI integration capabilities (requires installation)

### Target State
Need to implement an AI orchestrator service that:
- Connects user messages with database context
- Calls OpenAI API with enriched context
- Persists all messages to maintain conversation history
- Maintains statelessness by using database for context

### Dependencies
- OpenAI library for AI integration
- SQLModel and database connection for context retrieval
- Existing models: User, Conversation, Message, Task, Category
- Environment variables for API keys
- Async capabilities for non-blocking operations

### Integration Points
- Create backend/src/services/ai_service.py
- Update POST /api/messages/ endpoint to use the AI service
- Database access for context injection and message persistence

## Constitution Check

### Relevant Principles from Constitution
- **Stateless AI Architecture**: Backend must remain stateless with conversation history persisted in database
- **Schema Integrity**: SQLModel schema must be single source of truth for database and API validation
- **Multi-Tenant Security**: All operations must validate user_id to ensure data isolation
- **Strict User Isolation**: Users must only access their own conversations and messages

### Compliance Verification
- [ ] All conversation and message data will be persisted in database (Stateless AI Architecture)
- [ ] SQLModel will be used consistently for schema definition (Schema Integrity)
- [ ] Proper foreign key relationships will ensure user isolation (Multi-Tenant Security)
- [ ] Access controls will ensure users only see their own data (Strict User Isolation)

### Gate Status
- [x] **COMPLETED**: All dependencies and integration points are understood
- [x] **COMPLETED**: All research findings incorporated into implementation plan

## Phase 0: Outline & Research

### Completed Research
Research has been completed and documented in `research.md`. Key findings include:
1. OpenAI library integration patterns using AsyncClient
2. Async service patterns in FastAPI with proper error handling
3. Best practices for context injection in AI prompts with structured formatting
4. Error handling for external API calls with graceful degradation
5. Review of existing database access patterns using SQLModel and dependency injection

### Outcomes Achieved
- [x] Understanding of OpenAI library usage patterns
- [x] Best practices for async operations in FastAPI
- [x] Proper context injection techniques for AI prompts
- [x] Error handling strategies for external API calls
- [x] Consistency with existing database access patterns

## Phase 1: Design & Contracts

### Data Model Design
- [x] Define AIService class with methods for context injection, message processing, and response handling (documented in data-model.md)
- [x] Design proper async methods for non-blocking operations (documented in data-model.md)
- [x] Define clear interfaces for database access and AI integration (documented in data-model.md)

### Implementation Steps
1. [ ] Create backend/src/services/ai_service.py with AIService class
2. [ ] Implement context injection methods to fetch user's tasks and categories
3. [ ] Implement message history retrieval (last 10 messages)
4. [ ] Implement OpenAI API call with proper context and error handling
5. [ ] Update POST /api/messages/ endpoint to use AI service
6. [ ] Ensure all messages are persisted before/after AI processing

### Success Criteria
- [ ] AI service properly integrates database context with AI responses
- [ ] Message persistence is guaranteed regardless of AI API success/failure
- [ ] Async operations don't block user interface
- [ ] Proper error handling maintains system stability

## Phase 2: Implementation Plan

### Task Breakdown
- [ ] Research OpenAI library integration
- [ ] Design AIService architecture
- [ ] Implement context injection functionality
- [ ] Implement message history retrieval
- [ ] Implement OpenAI API integration
- [ ] Update messages endpoint to use AI service
- [ ] Test service functionality

### Timeline
- Phase 0: 0.5 days (Research and understanding)
- Phase 1: 1 day (Service design and implementation)
- Phase 2: 0.5 days (Testing and validation)

## Phase 3: Validation & Testing

### Testing Approach
- Unit tests for AI service methods
- Integration tests for context injection
- Error handling tests for API failures
- End-to-end tests for complete message flow