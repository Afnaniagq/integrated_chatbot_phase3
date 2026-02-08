---

description: "Task list template for feature implementation"
---

# Tasks: AI Chat Agent Integration

**Input**: Design documents from `/specs/1-ai-chat-agent/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify `OPENAI_API_KEY` is accessible via `Settings` class in `backend/src/core/config.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Create `ai_service.py` file with basic class structure in `backend/src/services/ai_service.py`
- [x] T003 [P] Add necessary imports for OpenAI SDK and MCP server to `backend/src/services/ai_service.py`
- [x] T004 [P] Initialize OpenAI client with `OPENAI_API_KEY` in `AIService` constructor in `backend/src/services/ai_service.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Manage Tasks via Chat (Priority: P1) 🎯 MVP

**Goal**: Enable users to create, list, update, and delete tasks via natural language through the AI chat agent.

**Independent Test**: This can be fully tested by sending various task management requests (e.g., "create a task", "list my tasks", "update task X", "delete task Y") and verifying the agent correctly interprets the intent, calls the MCP tool, and responds appropriately.

### Implementation for User Story 1

- [x] T005 [P] [US1] Implement `get_conversation_history` method in `AIService` to fetch messages from the database in `backend/src/services/ai_service.py`
- [x] T006 [P] [US1] Implement `process_message` method skeleton in `AIService` to accept `user_id`, `conversation_id`, and `message_content` in `backend/src/services/ai_service.py`
- [x] T007 [P] [US1] Dynamically retrieve available MCP tools using `mcp_server.handle_list_tools()` in `backend/src/services/ai_service.py`
- [x] T008 [P] [US1] Format MCP tools for OpenAI `tools` parameter in `backend/src/services/ai_service.py`
- [x] T009 [US1] Call OpenAI `chat.completions.create` with user message, conversation history, and formatted tools in `backend/src/services/ai_service.py`
- [x] T010 [US1] Check OpenAI response for `tool_calls` in `backend/src/services/ai_service.py`
- [x] T011 [US1] Execute corresponding MCP tool via `mcp_server.handle_execute_tool()` if `tool_calls` are present in `backend/src/services/ai_service.py`
- [x] T012 [P] [US1] Ensure `user_id` is explicitly included in arguments passed to `mcp_server.handle_execute_tool()` in `backend/src/services/ai_service.py`
- [x] T013 [US1] Implement natural language response generation after successful tool execution in `backend/src/services/ai_service.py`
- [x] T014 [US1] Implement error handling for generic MCP tool execution failures in `backend/src/services/ai_service.py`
- [x] T015 [US1] Implement specific error handling for unauthorized access attempts (`You are not authorized to modify this task.`) in `backend/src/services/ai_service.py`
- [x] T016 [US1] Update `create_message` endpoint in `backend/src/api/messages.py` to use `AIService.process_message` with `current_user_id` and `conversation_id`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Get General AI Response (Priority: P2)

**Goal**: Enable the AI chat agent to provide natural language responses to general questions or non-task-management queries.

**Independent Test**: This can be tested by sending non-task-management messages (e.g., "Hello", "How are you?") and verifying the agent provides a coherent natural language response without attempting to call an MCP tool.

### Implementation for User Story 2

- [x] T017 [US2] Implement logic to handle OpenAI responses without `tool_calls` for general queries in `backend/src/services/ai_service.py`
- [x] T018 [US2] Implement clarification prompt generation for AI intent failure (misinterpretation/no tool call) in `backend/src/services/ai_service.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T019 Review and refine all error handling mechanisms in `backend/src/services/ai_service.py`
- [x] T020 Ensure modularity and testability of `AIService` methods in `backend/src/services/ai_service.py`
- [x] T021 Confirm `backend/src/mcp/server.py` `user_id` injection mechanism by inspection
- [x] T022 Confirm `backend/src/services/task_service.py` and `backend/src/services/category_service.py` unauthorized access handling by inspection

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All tasks in a User Story phase marked [P] can run in parallel
- Once Foundational phase completes, User Story 1 and User Story 2 can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch Foundational tasks that can run in parallel:
Task: "Add necessary imports for OpenAI SDK and MCP server to backend/src/services/ai_service.py"
Task: "Initialize OpenAI client with OPENAI_API_KEY in AIService constructor in backend/src/services/ai_service.py"

# Launch User Story 1 tasks that can run in parallel:
Task: "Implement get_conversation_history method in AIService to fetch messages from the database in backend/src/services/ai_service.py"
Task: "Implement process_message method skeleton in AIService to accept user_id, conversation_id, and message_content in backend/src/services/ai_service.py"
Task: "Dynamically retrieve available MCP tools using mcp_server.handle_list_tools() in backend/src/services/ai_service.py"
Task: "Format MCP tools for OpenAI `tools` parameter in backend/src/services/ai_service.py"
Task: "Ensure user_id is explicitly included in arguments passed to mcp_server.handle_execute_tool() in backend/src/services/ai_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
