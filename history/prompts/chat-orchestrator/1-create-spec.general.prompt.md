---
id: 1
title: "Create Spec Chat Orchestrator"
stage: general
date_iso: 2026-02-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: "chat-orchestrator"
branch: 7-chat-orchestrator
user: user
command: "sp.specify # Spec 7: Core Chat Orchestrator"
labels: ["spec", "ai", "orchestration", "database", "integration"]
links:
  spec: "specs/7-chat-orchestrator/spec.md"
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "specs/7-chat-orchestrator/spec.md"
  - "specs/7-chat-orchestrator/checklists/requirements.md"
tests_yaml:
  - "None needed for spec creation"
---

# Prompt Text

```
 # Spec 7: Core Chat Orchestrator



\*\*Status\*\*: Next Phase

\*\*Focus\*\*: The Orchestrator Logic (Connecting DB to AI)



\## Context

We have successfully implemented the `Conversation` and `Message` database models (Spec 6). Now, we need to create the "Brain" of the backend—the Orchestrator—which handles the flow between the user, the database context, and the OpenAI API.



\## Objectives

1\. \*\*Create `backend/src/services/ai\_service.py`\*\*:

&nbsp;   - Implement a service class to handle AI logic.

&nbsp;   - \*\*Context Injection\*\*: Functionality to fetch the user's current `tasks` and `categories` from the database to include in the AI's System Prompt.

&nbsp;   - \*\*History Retrieval\*\*: Functionality to pull the last 10 messages from the `message` table for the specific `conversation\_id` to maintain short-term memory.

&nbsp;   - \*\*OpenAI Integration\*\*: Use the `openai` library to send the combined context (system prompt + history + new message) to `gpt-4o` (or preferred model).



2\. \*\*Database Persistence Loop\*\*:

&nbsp;   - Ensure that every incoming user message is saved to the `message` table before the AI call.

&nbsp;   - Ensure that every AI response is saved to the `message` table before being returned to the user.

&nbsp;   - Ensure the endpoint remains asynchronous.

3\. \*\*Update API Logic\*\*:

&nbsp;   - Refactor `POST /api/messages/` in `backend/src/api/messages.py` to trigger the `ai\_service`.

&nbsp;   - Ensure the endpoint remains asynchronous.



\## Technical Requirements

\- \*\*System Prompt\*\*: Define a clear persona: "You are a proactive Productivity Assistant. You have access to the user's current task list and help them organize, prioritize, and manage their time."

\- \*\*Environment\*\*: Load `OPENAI\_API\_KEY` from the existing `.env` file.

\- \*\*Error Handling\*\*: Implement try/except blocks for OpenAI API failures to ensure the database doesn't get stuck in an inconsistent state.

\## Constraints

\- \*\*No Tools Yet\*\*: Do not implement Function Calling or MCP tools in this spec (that is saved for Spec 8 \& 9).

\- \*\*Statelessness\*\*: The AI should rely on the database for history, not in-memory variables.
```

# Response Text

Successfully created the specification for Core Chat Orchestrator (Spec 7). The spec includes:

1. User Stories for AI-powered productivity assistance (P1), persistent conversation context (P2), and reliable message persistence (P3)
2. Functional requirements covering the AI service creation, context injection, message persistence loop, and error handling
3. Key entities defining the AI service, conversation context, and message persistence loop
4. Success criteria for measuring the feature's completion

Created a new branch "7-chat-orchestrator" and the spec file at "specs/7-chat-orchestrator/spec.md". Also created a quality checklist at "specs/7-chat-orchestrator/checklists/requirements.md".

The specification focuses on creating the "brain" of the backend that orchestrates communication between user, database context, and OpenAI API, with proper context injection, message persistence, and error handling. All requirements from the original request have been captured in a user-focused, technology-agnostic manner.

# Outcome

The specification document is complete and ready for the next phase of planning. All requirements from the original request have been translated into user scenarios, functional requirements, and measurable success criteria.

# Evaluation

The specification successfully translates the technical requirements into user scenarios, functional requirements, and measurable success criteria. The quality checklist confirms that all necessary elements are present and properly defined.