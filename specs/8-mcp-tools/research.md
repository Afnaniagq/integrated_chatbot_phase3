# Research Findings: MCP Server & Tool Definitions (Phase III)

## Overview
This document captures research on Model Context Protocol (MCP) implementation approaches and related technology considerations for exposing backend functions as executable tools for AI agents.

## Model Context Protocol (MCP) Standards

### What is MCP?
The Model Context Protocol (MCP) is a standard for connecting AI models to external tools and data sources. It allows AI agents to execute actions and access resources beyond their training data.

### MCP Architecture Components
1. **MCP Server**: Hosts tools and makes them available to clients
2. **MCP Client**: Usually an AI model or agent that discovers and invokes tools
3. **Tool Definitions**: Standardized descriptions of available tools (typically in JSON Schema format)
4. **Transport Layer**: Typically HTTP/REST or WebSocket for communication

### Standard Tool Definition Format
MCP typically uses JSON Schema to define tools:
```json
{
  "type": "function",
  "function": {
    "name": "add_task",
    "description": "Add a new task to the user's list",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {"type": "string", "description": "The task title"},
        "description": {"type": "string", "description": "Detailed description of the task"},
        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
        "due_date": {"type": "string", "format": "date", "description": "Due date in YYYY-MM-DD format"}
      },
      "required": ["title"]
    }
  }
}
```

## MCP Server Implementation Approaches

### Option 1: Standalone MCP Server
- Pros: Independent of main application, easy to develop/maintain separately
- Cons: Additional infrastructure, authentication complexity, potential network latency

### Option 2: Integrated MCP Server (Recommended)
- Pros: Leverages existing authentication and data access layers, easier maintenance
- Cons: Slightly more complex initial setup

### Recommended Architecture
Since we want to ensure tight integration with the existing authentication and database systems, the integrated approach is recommended. The MCP server would run as part of the existing FastAPI application.

## Technology Decisions

### Framework Choice
- **FastAPI**: Since the main application is already using FastAPI, we'll extend it with MCP endpoints
- **Benefits**: Shared authentication, database connections, and middleware

### Authentication & Security
- **User Context Injection**: Extract user_id from JWT tokens and inject into tool calls
- **Access Control**: Each tool must validate that the user has permission to access the requested resources
- **Best Practice**: Use the existing `get_current_user_id` dependency

### Database Access
- **Shared Sessions**: Use existing database session management
- **Transaction Safety**: Each tool should manage its own transaction scope
- **Consistency**: Maintain the same data validation and constraints as regular endpoints

## Tool Integration Patterns

### 1. Function Mapping Pattern
Map existing service functions to MCP tools by creating thin wrapper functions that:
- Accept parameters from the MCP client
- Inject the authenticated user's context
- Call existing service functions
- Return results in MCP-compatible format

### 2. Parameter Validation
- Use existing Pydantic models where possible
- Convert natural language parameters to structured inputs
- Validate parameters before passing to service functions

### 3. Error Handling
- Map service exceptions to MCP-compatible error responses
- Maintain security by not leaking internal information
- Provide actionable feedback to AI agents

## Security Considerations

### User Isolation
- Every tool must verify that requested resources belong to the authenticated user
- Use user_id to filter database queries
- Return appropriate error if user doesn't have access

### Input Sanitization
- Validate all parameters received from AI agents
- Sanitize content to prevent injection attacks
- Implement rate limiting to prevent abuse

### Auditing
- Log all tool calls with user_id, tool name, and parameters
- Monitor for unusual usage patterns
- Track success/failure rates

## Integration with AIService

### Current AIService Flow
1. Receive user message
2. Fetch user context (tasks, categories)
3. Fetch conversation history
4. Format prompt with context
5. Call OpenAI API
6. Process response and save to database

### Enhanced Flow with MCP
1. Receive user message
2. Determine if message requires tool use
3. If yes, identify appropriate tool and call MCP server
4. If no, use current flow with context
5. Combine tool results with OpenAI processing if needed
6. Process response and save to database

## Recommended Implementation Strategy

### Phase 1: Foundation
1. Create MCP server module
2. Implement tool registration and discovery
3. Create tool adapters for existing service functions

### Phase 2: Security
1. Implement user_id context injection
2. Add access control validation
3. Add parameter validation

### Phase 3: Integration
1. Update AIService to use MCP tools
2. Implement tool identification and calling logic
3. Test security and functionality

## Risks and Mitigation

### Risk 1: Authentication Complexity
**Issue**: MCP tools need to know the user identity without duplicating auth logic
**Mitigation**: Design MCP endpoints to work with existing JWT auth dependencies

### Risk 2: Performance Impact
**Issue**: Tool calls may slow down AI responses
**Mitigation**: Optimize tool execution and consider async patterns where appropriate

### Risk 3: Security Vulnerabilities
**Issue**: Direct tool access could bypass security controls
**Mitigation**: Implement strict access controls and input validation in all tools