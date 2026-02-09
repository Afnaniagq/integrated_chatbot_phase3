---

description: "Task list for Chat UI (Phase 5) implementation"
---

# Tasks: Chat UI (Phase 5)

**Input**: Design documents from `/specs/10-chat-ui/`
**Prerequisites**: spec.md (required), plan.md (required for architecture/component details)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4 from `spec.md`)
- Include exact file paths in descriptions

## Path Conventions

-   All chat UI components will be located in `frontend/src/components/chat/`

---

## Phase 1: Chat UI Implementation (Priority: P1) 🎯 MVP

**Goal**: Build a high-fidelity, responsive Chat UI for the AI agent, integrated into the existing dashboard.

**Independent Test**: The chat UI can be fully tested by opening the dashboard, activating the chat widget, sending messages, and verifying AI responses, Markdown rendering, thinking indicators, history loading, and error handling.

### Implementation for Chat UI

-   [x] T001 [P]: Install dependencies: `openai-chatkit`, `lucide-react`, and `react-markdown`. Configure Tailwind in `frontend/tailwind.config.js`.
-   [x] T002 [P]: Create `ChatWidget.tsx` (floating bubble). Requirement: Use `fixed bottom-4 right-4 z-50` to stay above all dashboard elements.
-   [x] T003: Implement toggle logic in `ChatWidget.tsx` to mount/unmount the `ChatPanel`.
-   [x] T004 [P]: Create `ChatPanel.tsx` container with a flex-column layout.
-   [x] T005: Integrate `useChat` hooks from ChatKit in `ChatPanel.tsx` for real-time streaming.
-   [x] T006 [P]: Create `ChatMessage.tsx` (rendering content via `react-markdown`) and `ThinkingIndicator.tsx`.
-   [x] T007: Create `MessageList.tsx` using a `useRef` hook and `useEffect` to trigger `scrollIntoView({ behavior: 'smooth' })` when new messages arrive.
-   [x] T008: Assemble `ChatMessage`, `ThinkingIndicator`, and `MessageList` into `ChatPanel.tsx`.
-   [x] T009: Create `ChatInput.tsx` and integrate it into the bottom of `ChatPanel.tsx`.
-   [x] T010: Implement initialization logic to fetch previous conversation history from the backend.
-   [x] T011: Add error boundaries and UI alerts for unauthorized (401) or timeout errors.
-   [x] T012: Implement side-effect logic to trigger a dashboard state refresh when the AI executes a tool successfully.
