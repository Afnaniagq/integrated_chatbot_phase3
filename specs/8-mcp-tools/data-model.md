# Data Model & Service Design: MCP Server & Tool Definitions (Phase III)

## Overview
This document defines the architecture for the MCP (Model Context Protocol) server that will expose backend functionality as executable tools for AI agents.

## Service Architecture

### MCP Server Class Design

**Class Name**: MCPServer
**Responsibility**: Manage tool registration, discovery, and execution for AI agents

#### Methods:

1. **Constructor** (`__init__`):
   - Parameters: None (will use existing application dependencies)
   - Initializes the tool registry
   - Sets up authentication and security components

2. **register_tool** (sync):
   - Parameters: tool_name, tool_function, tool_schema
   - Returns: None
   - Purpose: Register a new tool with the server
   - Implementation: Add tool to internal registry with its schema

3. **list_tools** (async):
   - Parameters: session, user_id
   - Returns: List of available tools with schemas
   - Purpose: Provide tool discovery for AI agents
   - Implementation: Return filtered list of tools user is authorized to use

4. **execute_tool** (async):
   - Parameters: session, user_id, tool_name, tool_arguments
   - Returns: Tool execution result or error
   - Purpose: Execute a registered tool with security validation
   - Implementation: Validate access, sanitize inputs, call tool function, return result

5. **validate_user_access** (sync):
   - Parameters: user_id, resource_id, resource_type
   - Returns: Boolean indicating access permission
   - Purpose: Verify user has permission to access specific resource
   - Implementation: Check that resource belongs to user

## Tool Interface Specifications

### Task Management Tools

#### 1. add_task Tool
- **Function Signature**: `add_task(title: str, description: Optional[str], priority: str, due_date: Optional[str]) -> Dict`
- **Purpose**: Creates a new task for the authenticated user
- **Security**: Validates that user_id matches the authenticated user
- **Validation**: Ensures required parameters and valid priority values
- **Return**: Created task object with all properties

#### 2. update_task_status Tool
- **Function Signature**: `update_task_status(task_id: UUID, status: str) -> Dict`
- **Purpose**: Updates the status of an existing task
- **Security**: Validates that task_id belongs to the authenticated user
- **Validation**: Checks that task exists and status is valid
- **Return**: Updated task object

#### 3. get_tasks Tool
- **Function Signature**: `get_tasks(status: Optional[str], category: Optional[str]) -> List[Dict]`
- **Purpose**: Retrieves tasks for the authenticated user with optional filters
- **Security**: Only returns tasks belonging to the authenticated user
- **Validation**: Validates filter parameters
- **Return**: List of task objects matching criteria

### Category & Context Tools

#### 1. create_category Tool
- **Function Signature**: `create_category(name: str, color: Optional[str]) -> Dict`
- **Purpose**: Creates a new category for the authenticated user
- **Security**: Associates category with authenticated user's account
- **Validation**: Ensures name is not empty and color is valid hex
- **Return**: Created category object

#### 2. get_user_context Tool
- **Function Signature**: `get_user_context() -> Dict`
- **Purpose**: Fetches user's current tasks and categories for AI context
- **Security**: Only returns data for the authenticated user
- **Validation**: None needed beyond authentication
- **Return**: User context including tasks and categories

## Security Architecture

### Context Injection Pattern
- **User Context**: The authenticated user_id is injected into each tool call
- **Resource Validation**: Each tool validates that requested resources belong to the authenticated user
- **Permission Checking**: Centralized function to verify user access to resources

### Security Validation Flow
1. MCP endpoint receives tool call with JWT authentication
2. Extract authenticated user_id from token
3. Validate that user has permission to execute requested tool
4. Validate that all parameters refer to resources the user owns
5. Execute tool function with validated parameters
6. Return results or appropriate error

## Integration Points

### With Existing Service Layer
- **Task Service**: `add_task` and `update_task_status` will delegate to existing task service functions
- **Category Service**: `create_category` will delegate to existing category service functions
- **User Service**: `get_user_context` will aggregate data from user-related services

### With AI Service
- **Tool Discovery**: AI Service calls MCP server's `list_tools` method to discover available tools
- **Tool Execution**: AI Service calls MCP server's `execute_tool` method when deciding to use a tool
- **Response Handling**: AI Service processes tool results to include in AI response

## Data Flow Design

### Tool Execution Flow
1. **AI Decision**: AI determines a tool should be called based on user request
2. **Tool Call**: AI calls MCP server's execute_tool with tool name and parameters
3. **Security Check**: MCP server validates user authentication and authorization
4. **Parameter Validation**: MCP server validates input parameters
5. **Service Delegation**: MCP server calls appropriate service layer function
6. **Database Operation**: Service layer performs database operation with user isolation
7. **Result Return**: MCP server returns tool execution result to AI
8. **AI Processing**: AI incorporates tool result into response to user

## Error Handling Design

### Error Types and Responses
1. **Authentication Errors**: Return 401 Unauthorized
2. **Authorization Errors**: Return 403 Forbidden with generic message
3. **Validation Errors**: Return 400 Bad Request with parameter validation details
4. **Resource Not Found**: Return 404 Not Found
5. **Execution Errors**: Return 500 Internal Server Error with safe error message

### Graceful Degradation
- If MCP server unavailable, AI can fall back to general conversation mode
- Partial context failure (some tools unavailable) shouldn't block entire AI response
- Tool-specific errors should be handled gracefully with helpful messages to the AI agent

## Performance Considerations

### Tool Execution Efficiency
- Tools should be lightweight wrappers around existing service functions
- Minimize additional database queries beyond those required by service functions
- Cache frequently accessed data when appropriate
- Implement proper indexing on all foreign key relationships

### Concurrent Access
- Tools should be thread-safe and handle concurrent execution
- Use proper database session management for each tool call
- Implement appropriate locking for critical sections if needed