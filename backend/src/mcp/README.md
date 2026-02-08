# MCP (Model Context Protocol) Server

This module implements an MCP server that exposes backend functions as executable tools for AI agents. The server provides tool registration, discovery, and execution capabilities with user context injection.

## Architecture

The MCP server consists of:

1. **MCPServer Class**: The main server class that handles tool registration, discovery, and execution
2. **Tool Registration**: Functions to register backend service functions as MCP tools
3. **Tool Discovery**: Endpoint to list available tools with their parameters
4. **Tool Execution**: Endpoint to execute tools with proper user context injection

## Components

### MCPServer Class
- Handles registration of callable functions as tools
- Manages tool definitions and metadata
- Provides endpoints for tool listing and execution
- Ensures proper user context injection

### Tool Registration
- Each tool is registered with a name, description, and parameter definitions
- Tool functions are wrapped to accept database sessions and user context
- Parameter validation is enforced through Pydantic models

### Security Features
- User isolation: Each tool execution enforces user_id context
- Database session management: Proper session handling for each tool call
- Input validation: All parameters are validated through Pydantic models
- Error handling: Comprehensive error handling for all tool operations

## Registered Tools

### Task Management Tools
- `add_task`: Create a new task for the user
- `update_task_status`: Update the status of a task (complete/incomplete)
- `get_tasks`: Get all tasks for the user with optional filtering

### Category Management Tools
- `create_category`: Create a new category for the user
- `get_user_context`: Get user context including tasks and categories

## Usage

The MCP server is initialized during application startup through the `initialize_mcp_tools()` function. The tools are then available for the AI service to discover and execute based on natural language requests.

## Integration with AIService

The AIService has been updated to:
- Discover available MCP tools during message processing
- Enable the AI model to call tools using OpenAI's function calling
- Execute MCP tools when requested by the AI
- Handle tool execution results and incorporate them into the conversation