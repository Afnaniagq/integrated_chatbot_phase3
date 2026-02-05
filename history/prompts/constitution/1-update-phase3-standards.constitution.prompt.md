---
id: 1
title: "Update Phase3 Standards"
stage: constitution
date_iso: 2026-02-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: "none"
branch: main
user: user
command: "sp.constitution Update constitution.md to include the architectural standards for Phase 3: Todo AI Chatbot."
labels: ["constitution", "phase3", "ai-chatbot", "standards"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - ".specify/memory/constitution.md"
tests_yaml:
  - "None needed for constitution update"
---

# Prompt Text

```
Update constitution.md to include the architectural standards for Phase 3: Todo AI Chatbot.

Add the following core principles:

Stateless AI Architecture: The backend must remain strictly stateless. All conversation history must be persisted in and retrieved from the Neon PostgreSQL database using Conversation and Message models.

MCP Tool-Centric Operations: All task management (CRUD) performed by the AI must go through the Official MCP SDK server. The AI Agent should not call internal services directly but must use the exposed MCP tools.

OpenAI Agents SDK Integration: Implement AI logic using the OpenAI Agents SDK, ensuring the 'Runner' pattern is used to handle multi-step tool calls and responses.

Multi-Tenant Security: Every chat request and MCP tool call must strictly validate and utilize the user_id. No operation should ever be performed without explicit user scoping.

Natural Language mapping: Maintain a strict mapping of user intents (add, show, complete, delete, update) to the corresponding MCP tools as defined in the Phase 3 requirements.

Ensure these rules override any previous Phase 2 instructions regarding direct API calls for task management.
```

# Response Text

Updated the constitution.md file to include the new Phase 3 architectural standards for the Todo AI Chatbot. The key changes include:

1. Updated document title to reflect Phase III Todo AI Chatbot
2. Added five new core principles:
   - Stateless AI Architecture
   - MCP Tool-Centric Operations
   - OpenAI Agents SDK Integration
   - Multi-Tenant Security
   - Natural Language mapping
3. Updated Key Standards to include AI Architecture and MCP Integration
4. Added AI Operations Constraint to the Constraints section
5. Added MCP Tool Compliance and Stateless AI Architecture to Success Criteria
6. Updated version from 1.0.0 to 1.1.0
7. Updated the last amended date to 2026-02-01
8. Added a clear statement that these rules override previous Phase 2 instructions regarding direct API calls for task management

The constitution now properly reflects the architectural requirements for Phase 3 while preserving all existing Phase 2 principles.

# Outcome

The constitution file has been successfully updated with the new Phase 3 architectural standards. The document now clearly specifies that all task management operations must go through MCP SDK tools, overriding any previous Phase 2 instructions for direct API calls.

# Evaluation

The update successfully incorporates all requested principles while maintaining the existing structure and principles from Phase 2. The version has been appropriately incremented to reflect the minor changes made.