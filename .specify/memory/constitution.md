<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0 (Phase 3 addition of AI Chatbot principles)
- Modified principles: Strict User Isolation → Strict User Isolation (moved position), Stateless Authentication → Stateless Authentication (moved position), Schema Integrity → Schema Integrity (moved position), Responsive Excellence → Responsive Excellence (moved position), Data Privacy Protection → Data Privacy Protection (moved position)
- Added sections: Stateless AI Architecture, MCP Tool-Centric Operations, OpenAI Agents SDK Integration, Multi-Tenant Security, Natural Language mapping, AI Architecture, MCP Integration, AI Operations Constraint, MCP Tool Compliance, Stateless AI Architecture (success criterion)
- Removed sections: None
- Templates requiring updates: ✅ .specify/templates/plan-template.md, ✅ .specify/templates/spec-template.md, ✅ .specify/templates/tasks-template.md
- Follow-up TODOs: None
-->

# Todo AI Chatbot Full-Stack Web Application (Phase III) Constitution

## Core Principles

### Stateless AI Architecture
The backend must remain strictly stateless. All conversation history must be persisted in and retrieved from the Neon PostgreSQL database using Conversation and Message models. This ensures scalability and consistent state management across multiple instances.
<!-- All conversation data must be stored in the database; no in-memory state should be relied upon -->

### MCP Tool-Centric Operations
All task management (CRUD) performed by the AI must go through the Official MCP SDK server. The AI Agent should not call internal services directly but must use the exposed MCP tools. This ensures centralized control and monitoring of all operations.
<!-- AI agents must route all task operations through MCP tools, never making direct API calls -->

### OpenAI Agents SDK Integration
Implement AI logic using the OpenAI Agents SDK, ensuring the 'Runner' pattern is used to handle multi-step tool calls and responses. This provides consistent handling of complex AI interactions.
<!-- All AI processing must follow the Runner pattern for proper multi-step tool orchestration -->

### Multi-Tenant Security
Every chat request and MCP tool call must strictly validate and utilize the user_id. No operation should ever be performed without explicit user scoping. This ensures complete data isolation between users.
<!-- All operations must be validated against the requesting user's identity and permissions -->

### Natural Language mapping
Maintain a strict mapping of user intents (add, show, complete, delete, update) to the corresponding MCP tools as defined in the Phase 3 requirements. This ensures consistent interpretation of user commands.
<!-- User intents must be precisely mapped to appropriate MCP tools without deviation -->

### Strict User Isolation
No user shall ever see, modify, or delete data belonging to another user_id. This principle ensures data privacy and security across all user accounts.
<!-- Every API endpoint must verify that the requesting user owns the data being accessed -->

### Stateless Authentication
All API requests must be verified via JWT tokens; no session state on the backend. This enables horizontal scaling and reduces server-side complexity.
<!-- Authentication tokens must be validated on every request without relying on server-side session storage -->

### Schema Integrity
The SQLModel schema is the single source of truth for both the database and API validation. This ensures consistency between data storage and API contracts.
<!-- Database migrations must align with schema definitions; API validation must use the same models -->

### Responsive Excellence
The UI must be fully functional on mobile and desktop without layout breakage. This ensures accessibility across all device types.
<!-- All components must implement responsive design principles using Tailwind CSS -->

### Data Privacy Protection
Pydantic schemas must exclude internal database IDs or sensitive user fields from public responses. This prevents exposure of internal implementation details.
<!-- Response models must explicitly define which fields are safe for public consumption -->

## Key Standards

### AI Architecture
OpenAI Agents SDK with 'Runner' pattern for multi-step tool orchestration. This ensures consistent handling of complex AI interactions.
<!-- All AI processing must follow the Runner pattern for proper tool orchestration -->

### MCP Integration
All task management operations must use Official MCP SDK tools. Direct API calls are prohibited for CRUD operations. This ensures centralized control and monitoring.
<!-- AI agents must route all task operations through MCP tools -->

### Authentication
Better Auth (TS) + FastAPI (Python) using shared HS256 JWT signing. This provides consistent authentication across frontend and backend.
<!-- JWT tokens must be verified using the same secret key across services -->

### Security
"Authorization: Bearer <token>" required for all /api/ paths. This enforces consistent authentication headers across all protected endpoints.
<!-- All API routes must validate the presence and validity of JWT tokens -->

### Database
Neon Serverless PostgreSQL with mandatory SSL (sslmode=require). Conversation and Message models must store all chat history. This ensures secure and scalable database connectivity with persistent state.
<!-- All conversation data must be stored in the database; no in-memory state should be relied upon -->

### Code Style
Follow frontend/CLAUDE.md and backend/CLAUDE.md naming conventions. This maintains consistency across the full-stack application.
<!-- Naming conventions must be consistent between frontend and backend components -->

### Error Handling
Standardized JSON error responses with appropriate HTTP status codes (401, 403, 404, 422). This provides predictable error handling for clients.
<!-- All error responses must follow the same JSON structure -->

## Constraints

### Stack Requirements
Stack: Next.js 16 (App Router), FastAPI, SQLModel, Tailwind CSS, Shadcn/UI, OpenAI Agents SDK, MCP SDK. This defines the core technology stack for the application.
<!-- No additional frameworks should be introduced without explicit approval -->

### AI Operations Constraint
All task management (CRUD) operations must go through Official MCP SDK tools. Direct API calls for task management are strictly prohibited. This overrides any previous Phase 2 instructions regarding direct API calls for task management.
<!-- AI agents must route all task operations through MCP tools -->

### Data Privacy
Pydantic schemas must exclude internal database IDs or sensitive user fields from public responses. This prevents data leakage.
<!-- Response models must be explicitly designed to exclude sensitive information -->

### Environment
All secrets (BETTER_AUTH_SECRET, DATABASE_URL) must reside in .env files. This ensures secure handling of sensitive configuration.
<!-- No hardcoded secrets should exist in the source code -->

## Success Criteria

### 100% User Isolation
Verification that cross-user data access is impossible. This ensures the security and privacy of user data.
<!-- Tests must verify that users cannot access data belonging to other users -->

### MCP Tool Compliance
All AI task operations must route through MCP SDK tools, not direct API calls. This ensures adherence to the new architectural constraint.
<!-- Tests must verify that AI agents use MCP tools for all task management -->

### Stateless AI Architecture
Conversation history must be persisted in and retrieved from the database using Conversation and Message models. This ensures proper state management.
<!-- Tests must verify that all conversation data is stored in the database -->

### Performance
Optimized database queries using indexes on user_id and task status. This ensures efficient data retrieval and application responsiveness.
<!-- All queries must utilize appropriate database indexes -->

### UI/UX
Zero-config deployment readiness and mobile-responsive task management cockpit. This ensures easy deployment and excellent user experience.
<!-- The application must be deployable without configuration changes -->

### Security
All tests pass for "Unauthorized" (401) and "Forbidden" (403) scenarios. This ensures proper access control implementation.
<!-- Security tests must validate that unauthorized access is properly blocked -->

## Governance

All code must comply with these constitutional principles. Changes to these principles require explicit approval and must be documented with clear rationale. Code reviews must verify compliance with all principles before merging. The constitution serves as the ultimate authority for technical decisions in this project. This constitution specifically overrides any previous Phase 2 instructions regarding direct API calls for task management, requiring all task operations to go through MCP SDK tools.

**Version**: 1.1.0 | **Ratified**: 2026-01-10 | **Last Amended**: 2026-02-01
