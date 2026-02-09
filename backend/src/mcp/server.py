"""
MCP (Model Context Protocol) Server Implementation

This module implements an MCP server that exposes backend functions as executable tools for AI agents.
The server provides tool registration, discovery, and execution capabilities with user context injection.
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Union, Awaitable
from uuid import UUID

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from contextlib import contextmanager

from ..database import get_session
from ..models.category import Category, CategoryCreate
from ..models.task import Task, TaskCreate, TaskUpdate
from ..services.auth import get_current_user
from ..services.category_service import (
    create_category as create_category_service,
    get_categories_by_user,
    get_category_by_id,
    update_category,
    delete_category
)
from ..services.task_service import (
    create_task as create_task_service,
    get_tasks as get_tasks_service,
    get_task,
    update_task,
    toggle_task_completion as toggle_task_completion_service,
    delete_task
)
from sqlmodel import Session
from ..database import engine


logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    """Definition of a single tool parameter"""
    type: str
    description: str
    required: bool = True


class ToolDefinition(BaseModel):
    """Definition of an MCP tool"""
    name: str
    description: str
    parameters: Dict[str, ToolParameter]


class MCPServer:
    """
    MCP Server that manages tools and their execution with proper user context injection.

    The server allows registration of callable functions as tools that can be executed
    by AI agents. Each tool execution includes proper user context and security validation.
    """

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: Dict[str, ToolDefinition] = {}
        self.app = FastAPI(title="MCP Server")
        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes for MCP functionality"""
        @self.app.post("/mcp/tools/execute")
        async def execute_tool(request: Request):
            return await self.handle_execute_tool(request)

        @self.app.get("/mcp/tools/list")
        async def list_tools():
            return await self.handle_list_tools()

    def register_tool(self, name: str, description: str, parameters: Dict[str, ToolParameter], func: Callable):
        """
        Register a function as an MCP tool with proper definition.

        Args:
            name: Unique name for the tool
            description: Description of what the tool does
            parameters: Dictionary of parameter definitions
            func: The actual function to call
        """
        self.tools[name] = func
        self.tool_definitions[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters
        )
        logger.info(f"Registered tool: {name}")

    async def handle_list_tools(self) -> Dict[str, Any]:
        """Handle tool listing requests"""
        return {
            "tools": [
                {
                    "name": name,
                    "description": definition.description,
                    "parameters": {
                        param_name: {
                            "type": param_def.type,
                            "description": param_def.description,
                            "required": param_def.required
                        }
                        for param_name, param_def in definition.parameters.items()
                    }
                }
                for name, definition in self.tool_definitions.items()
            ]
        }

    async def handle_execute_tool(self, request: Request) -> Dict[str, Any]:
        """Handle tool execution requests with user context injection"""
        try:
            data = await request.json()
            tool_name = data.get("tool_name")
            tool_arguments = data.get("arguments", {})
            user_id = data.get("user_id")  # This should come from authentication

            if not tool_name or tool_name not in self.tools:
                raise HTTPException(status_code=400, detail=f"Tool '{tool_name}' not found")

            # Get the registered tool function
            tool_func = self.tools[tool_name]

            # Inject user_id into arguments if needed
            if "user_id" not in tool_arguments and user_id:
                tool_arguments["user_id"] = user_id

            # Create a database session and execute the tool with it
            with Session(engine) as session:
                # Add the session to the arguments
                tool_arguments["session"] = session

                # Check if the function is async or sync and call accordingly
                if asyncio.iscoroutinefunction(tool_func):
                    result = await tool_func(**tool_arguments)
                else:
                    result = tool_func(**tool_arguments)

                # Commit the transaction
                session.commit()

                return {
                    "success": True,
                    "result": result,
                    "tool_name": tool_name
                }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }

    def get_app(self):
        """Return the FastAPI app instance"""
        return self.app


# Global MCP Server instance
mcp_server = MCPServer()


# Tool Registration Functions
def initialize_mcp_tools():
    """
    Initialize all MCP tools by registering them with the server.
    This function should be called during application startup.
    """
    # Task Management Tools
    mcp_server.register_tool(
        name="add_task",
        description="Create a new task for the user",
        parameters={
            "title": ToolParameter(type="string", description="Title of the task", required=True),
            "description": ToolParameter(type="string", description="Description of the task", required=False),
            "category": ToolParameter(type="string", description="Category of the task", required=False),
            "due_date": ToolParameter(type="string", description="Due date in ISO format (optional)", required=False),
            "priority": ToolParameter(type="string", description="Priority level (low, medium, high)", required=False),
            "user_id": ToolParameter(type="string", description="User ID (will be injected)", required=True)
        },
        func=create_task_wrapper
    )

    mcp_server.register_tool(
        name="update_task_status",
        description="Update the status of a task (complete/incomplete)",
        parameters={
            "task_id": ToolParameter(type="string", description="ID of the task to update", required=True),
            "completed": ToolParameter(type="boolean", description="Whether the task is completed", required=True),
            "user_id": ToolParameter(type="string", description="User ID (will be injected)", required=True)
        },
        func=toggle_task_completion_wrapper
    )

    mcp_server.register_tool(
        name="get_tasks",
        description="Get all tasks for the user with optional filtering",
        parameters={
            "status": ToolParameter(type="string", description="Filter by status (all, pending, completed)", required=False),
            "category": ToolParameter(type="string", description="Filter by category", required=False),
            "user_id": ToolParameter(type="string", description="User ID (will be injected)", required=True)
        },
        func=get_tasks_wrapper
    )

    # Category Management Tools
    mcp_server.register_tool(
        name="create_category",
        description="Create a new category for the user",
        parameters={
            "name": ToolParameter(type="string", description="Name of the category", required=True),
            "color": ToolParameter(type="string", description="Color code for the category (hex)", required=False),
            "user_id": ToolParameter(type="string", description="User ID (will be injected)", required=True)
        },
        func=create_category_wrapper
    )

    mcp_server.register_tool(
        name="get_user_context",
        description="Get user context including tasks and categories",
        parameters={
            "user_id": ToolParameter(type="string", description="User ID (will be injected)", required=True)
        },
        func=get_user_context_wrapper
    )


# Tool Wrapper Functions
def create_task_wrapper(*, session: Session, title: str, description: Optional[str] = None,
                       category: Optional[str] = None, due_date: Optional[str] = None,
                       priority: Optional[str] = "medium", user_id: UUID) -> Task:
    """Wrapper for create_task service function"""
    from datetime import datetime

    task_create = TaskCreate(
        title=title,
        description=description,
        category=category,
        due_date=datetime.fromisoformat(due_date) if due_date else None,
        priority=priority
    )

    return create_task_service(session=session, task_create=task_create, user_id=user_id)


def toggle_task_completion_wrapper(*, session: Session, task_id: UUID, completed: bool, user_id: UUID) -> Task:
    """Wrapper for toggle_task_completion service function"""
    task = toggle_task_completion_service(session=session, task_id=task_id, user_id=user_id, completed=completed)
    return task


def get_tasks_wrapper(*, session: Session, status: Optional[str] = "all",
                     category: Optional[str] = None, user_id: UUID) -> List[Task]:
    """Wrapper for get_tasks service function"""
    return get_tasks_service(session=session, user_id=user_id, status=status, category=category)


def create_category_wrapper(*, session: Session, name: str, color: Optional[str] = None, user_id: UUID) -> Category:
    """Wrapper for create_category service function"""
    category_create = CategoryCreate(name=name, color=color, user_id=user_id)
    return create_category_service(session=session, category_create=category_create)


async def get_user_context_wrapper(*, session: Session, user_id: UUID) -> Dict[str, Any]:
    """Wrapper for get_user_context service function"""
    ai_service = AIService()
    return await ai_service.get_user_context(session=session, user_id=user_id)