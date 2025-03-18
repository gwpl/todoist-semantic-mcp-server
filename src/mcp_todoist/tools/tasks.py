"""
Tasks tools for MCP Todoist.

This module provides MCP tools for managing Todoist tasks.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast

import mcp.types as types
from mcp.server import Server

from ..client import TodoistClient
from ..config import get_config
from ..models import TaskMCPInput, TaskMCPOutput, TaskFilterMCPInput
from ..utils import (
    get_logger,
    handle_exceptions,
    TodoistError,
    ValidationError,
    AuthenticationError,
)

# Get logger
logger = get_logger(__name__)


def register_task_tools(server: Server) -> None:
    """
    Register task-related tools with the server.
    
    Args:
        server: The MCP server instance.
    """
    @server.list_tools()
    async def handle_list_tools() -> List[types.Tool]:
        """List available task tools."""
        return [
            types.Tool(
                name="list-tasks",
                description=(
                    "List tasks from Todoist with various filtering options.\n\n"
                    "This tool allows you to retrieve tasks from your Todoist account, with options to filter by:\n"
                    "- Project (using project_id or project_name)\n"
                    "- Label (using label_id or label_name)\n"
                    "- Due date (today, upcoming)\n"
                    "- Priority level\n"
                    "- Completion status\n"
                    "- Custom filter string using Todoist's filter syntax\n\n"
                    "Example filter strings:\n"
                    "- \"today\" - Tasks due today\n"
                    "- \"overdue\" - Overdue tasks\n"
                    "- \"p1\" - Priority 1 tasks\n"
                    "- \"@work & today\" - Tasks with label 'work' due today\n\n"
                    "Usage examples:\n"
                    "- \"Show me all my tasks due today\"\n"
                    "- \"List tasks in my 'Work' project\"\n"
                    "- \"Show high priority tasks with the 'urgent' label\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Filter tasks by project ID"
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Filter tasks by project name (will look up the project ID)"
                        },
                        "section_id": {
                            "type": "string",
                            "description": "Filter tasks by section ID"
                        },
                        "label_id": {
                            "type": "string",
                            "description": "Filter tasks by label ID"
                        },
                        "label_name": {
                            "type": "string",
                            "description": "Filter tasks by label name (will look up the label ID)"
                        },
                        "filter_string": {
                            "type": "string",
                            "description": "Filter tasks using Todoist's filter syntax"
                        },
                        "due_today": {
                            "type": "boolean",
                            "description": "Filter tasks due today"
                        },
                        "due_upcoming": {
                            "type": "boolean",
                            "description": "Filter tasks due in the next 7 days"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Whether to include completed tasks (default: false)"
                        },
                        "priority": {
                            "type": "integer",
                            "description": "Filter tasks by priority (1 = lowest, 4 = highest)",
                            "minimum": 1,
                            "maximum": 4
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tasks to return",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 50
                        }
                    }
                },
            ),
            types.Tool(
                name="create-task",
                description=(
                    "Create a new task in Todoist.\n\n"
                    "This tool allows you to create a new task with various properties, including:\n"
                    "- Task content (title)\n"
                    "- Description\n"
                    "- Project assignment\n"
                    "- Due date\n"
                    "- Priority\n"
                    "- Labels\n\n"
                    "Usage examples:\n"
                    "- \"Create a task 'Buy groceries' due tomorrow\"\n"
                    "- \"Add a task 'Prepare presentation' to project 'Work' with priority 1\"\n"
                    "- \"Create a task 'Call John' due on 2023-12-15 with label 'Personal'\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Task content (title)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project ID to add the task to"
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Project name to add the task to (will look up the project ID)"
                        },
                        "section_id": {
                            "type": "string",
                            "description": "Section ID to add the task to"
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "Parent task ID for creating subtasks"
                        },
                        "labels": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of label names to apply to the task"
                        },
                        "priority": {
                            "type": "integer",
                            "description": "Task priority (1 = lowest, 4 = highest)",
                            "minimum": 1,
                            "maximum": 4,
                            "default": 1
                        },
                        "due_string": {
                            "type": "string",
                            "description": "Due date as a string (e.g., 'tomorrow', 'next Monday')"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in YYYY-MM-DD format"
                        },
                        "due_datetime": {
                            "type": "string",
                            "description": "Due date and time in RFC3339 format (e.g., '2023-12-15T10:00:00Z')"
                        }
                    },
                    "required": ["content"]
                },
            ),
            types.Tool(
                name="update-task",
                description=(
                    "Update an existing task in Todoist.\n\n"
                    "This tool allows you to update properties of an existing task, such as:\n"
                    "- Task content (title)\n"
                    "- Description\n"
                    "- Project assignment\n"
                    "- Due date\n"
                    "- Priority\n"
                    "- Labels\n\n"
                    "Usage examples:\n"
                    "- \"Update task X to be due tomorrow\"\n"
                    "- \"Change the priority of task Y to high\"\n"
                    "- \"Move task Z to the 'Personal' project\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of the task to update"
                        },
                        "content": {
                            "type": "string",
                            "description": "New task content (title)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "New project ID"
                        },
                        "project_name": {
                            "type": "string",
                            "description": "New project name (will look up the project ID)"
                        },
                        "section_id": {
                            "type": "string",
                            "description": "New section ID"
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "New parent task ID"
                        },
                        "labels": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "New list of label names"
                        },
                        "priority": {
                            "type": "integer",
                            "description": "New task priority (1 = lowest, 4 = highest)",
                            "minimum": 1,
                            "maximum": 4
                        },
                        "due_string": {
                            "type": "string",
                            "description": "New due date as a string"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "New due date in YYYY-MM-DD format"
                        },
                        "due_datetime": {
                            "type": "string",
                            "description": "New due date and time in RFC3339 format"
                        }
                    },
                    "required": ["task_id"]
                },
            ),
            types.Tool(
                name="complete-task",
                description=(
                    "Mark a task as completed in Todoist.\n\n"
                    "This tool allows you to complete a task by its ID.\n\n"
                    "Usage examples:\n"
                    "- \"Mark task X as completed\"\n"
                    "- \"Complete the 'Buy groceries' task\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of the task to complete"
                        }
                    },
                    "required": ["task_id"]
                },
            ),
            types.Tool(
                name="delete-task",
                description=(
                    "Delete a task from Todoist.\n\n"
                    "This tool allows you to permanently delete a task by its ID.\n\n"
                    "Usage examples:\n"
                    "- \"Delete task X\"\n"
                    "- \"Remove the 'Call John' task\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, 
        arguments: Optional[Dict[str, Any]]
    ) -> List[Union[types.TextContent, types.ImageContent]]:
        """Handle tool execution requests."""
        if arguments is None:
            raise ValidationError("Arguments are required")
            
        # Create Todoist client
        client = TodoistClient()
        
        if name == "list-tasks":
            return await handle_list_tasks(client, arguments)
        elif name == "create-task":
            return await handle_create_task(client, arguments)
        elif name == "update-task":
            return await handle_update_task(client, arguments)
        elif name == "complete-task":
            return await handle_complete_task(client, arguments)
        elif name == "delete-task":
            return await handle_delete_task(client, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")


@handle_exceptions
async def handle_list_tasks(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the list-tasks tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug(f"Listing tasks with arguments: {arguments}")
    
    # Parse arguments
    filter_args = TaskFilterMCPInput(**arguments)
    
    # Prepare filter parameters
    project_id = filter_args.project_id
    section_id = filter_args.section_id
    label_id = filter_args.label_id
    filter_string = filter_args.filter_string
    
    # Handle project_name if provided
    if filter_args.project_name and not project_id:
        logger.debug(f"Looking up project ID for name: {filter_args.project_name}")
        projects = await client.get_projects()
        for project in projects:
            if project.name.lower() == filter_args.project_name.lower():
                project_id = project.id
                break
        if not project_id:
            raise ValidationError(f"Project not found: {filter_args.project_name}")
    
    # Handle label_name if provided
    if filter_args.label_name and not label_id:
        logger.debug(f"Looking up label ID for name: {filter_args.label_name}")
        labels = await client.get_labels()
        for label in labels:
            if label.name.lower() == filter_args.label_name.lower():
                label_id = label.id
                break
        if not label_id:
            raise ValidationError(f"Label not found: {filter_args.label_name}")
    
    # Handle special filters
    if filter_args.due_today:
        if filter_string:
            filter_string = f"({filter_string}) & today"
        else:
            filter_string = "today"
    
    if filter_args.due_upcoming:
        if filter_string:
            filter_string = f"({filter_string}) & (today | overdue | 7 days)"
        else:
            filter_string = "today | overdue | 7 days"
    
    if filter_args.priority:
        priority_filter = f"p{filter_args.priority}"
        if filter_string:
            filter_string = f"({filter_string}) & {priority_filter}"
        else:
            filter_string = priority_filter
    
    # Get tasks
    tasks = await client.get_tasks(
        project_id=project_id,
        section_id=section_id,
        label_id=label_id,
        filter_string=filter_string,
    )
    
    # Apply any additional filters that can't be done via the API
    if filter_args.limit and len(tasks) > filter_args.limit:
        tasks = tasks[:filter_args.limit]
    
    # Build the response
    if not tasks:
        return [types.TextContent(
            type="text",
            text="No tasks found matching your criteria."
        )]
    
    # Format tasks
    task_output = []
    for task in tasks:
        task_model = TaskMCPOutput.from_todoist(task)
        
        # Format due date
        due_str = ""
        if task_model.due:
            if task_model.due.string:
                due_str = f"Due: {task_model.due.string}"
            elif task_model.due.date:
                due_str = f"Due: {task_model.due.date}"
        
        # Format priority
        priority_map = {1: "🔵 Low", 2: "⚪ Normal", 3: "🟠 Medium", 4: "🔴 High"}
        priority_str = priority_map.get(task_model.priority, "")
        
        # Format labels
        labels_str = ""
        if task_model.labels:
            labels_str = f"Labels: {', '.join(['@' + label for label in task_model.labels])}"
        
        # Build task description
        task_desc = [
            f"• {task_model.content}",
            f"  ID: {task_model.id}",
        ]
        
        if due_str:
            task_desc.append(f"  {due_str}")
        
        if priority_str:
            task_desc.append(f"  Priority: {priority_str}")
        
        if labels_str:
            task_desc.append(f"  {labels_str}")
        
        if task_model.description:
            desc_preview = task_model.description[:100] + ("..." if len(task_model.description) > 100 else "")
            task_desc.append(f"  Description: {desc_preview}")
        
        task_output.append("\n".join(task_desc))
    
    response_text = "# Todoist Tasks\n\n" + "\n\n".join(task_output)
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]


@handle_exceptions
async def handle_create_task(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the create-task tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug(f"Creating task with arguments: {arguments}")
    
    # Parse arguments
    task_input = TaskMCPInput(**arguments)
    
    # Handle project_name if provided
    project_id = task_input.project_id
    if task_input.project_name and not project_id:
        logger.debug(f"Looking up project ID for name: {task_input.project_name}")
        projects = await client.get_projects()
        for project in projects:
            if project.name.lower() == task_input.project_name.lower():
                project_id = project.id
                break
        if not project_id:
            raise ValidationError(f"Project not found: {task_input.project_name}")
    
    # Create the task
    task = await client.create_task(
        content=task_input.content,
        description=task_input.description,
        project_id=project_id,
        section_id=task_input.section_id,
        parent_id=task_input.parent_id,
        labels=task_input.labels,
        priority=task_input.priority,
        due_string=task_input.due_string,
        due_date=task_input.due_date,
        due_datetime=task_input.due_datetime,
    )
    
    # Build the response
    task_model = TaskMCPOutput.from_todoist(task)
    
    # Format due date
    due_str = ""
    if task_model.due:
        if task_model.due.string:
            due_str = f"Due: {task_model.due.string}"
        elif task_model.due.date:
            due_str = f"Due: {task_model.due.date}"
    
    # Format priority
    priority_map = {1: "🔵 Low", 2: "⚪ Normal", 3: "🟠 Medium", 4: "🔴 High"}
    priority_str = priority_map.get(task_model.priority, "")
    
    # Format labels
    labels_str = ""
    if task_model.labels:
        labels_str = f"Labels: {', '.join(['@' + label for label in task_model.labels])}"
    
    # Build response
    response_text = f"# Task Created Successfully\n\n"
    response_text += f"**{task_model.content}**\n\n"
    response_text += f"ID: `{task_model.id}`\n"
    
    if due_str:
        response_text += f"{due_str}\n"
    
    if priority_str:
        response_text += f"Priority: {priority_str}\n"
    
    if labels_str:
        response_text += f"{labels_str}\n"
    
    if task_model.description:
        response_text += f"\nDescription:\n{task_model.description}\n"
    
    response_text += f"\nView in Todoist: {task_model.url}"
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]


@handle_exceptions
async def handle_update_task(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the update-task tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug(f"Updating task with arguments: {arguments}")
    
    # Extract task_id
    task_id = arguments.pop("task_id")
    if not task_id:
        raise ValidationError("Task ID is required")
    
    # Get original task
    original_task = await client.get_task(task_id)
    
    # Handle project_name if provided
    project_id = arguments.get("project_id")
    project_name = arguments.pop("project_name", None)
    if project_name and not project_id:
        logger.debug(f"Looking up project ID for name: {project_name}")
        projects = await client.get_projects()
        for project in projects:
            if project.name.lower() == project_name.lower():
                arguments["project_id"] = project.id
                break
        if not "project_id" in arguments:
            raise ValidationError(f"Project not found: {project_name}")
    
    # Update the task
    success = await client.update_task(task_id=task_id, **arguments)
    
    if not success:
        raise TodoistError("Failed to update task")
    
    # Get updated task
    updated_task = await client.get_task(task_id)
    
    # Build the response
    task_model = TaskMCPOutput.from_todoist(updated_task)
    
    # Format due date
    due_str = ""
    if task_model.due:
        if task_model.due.string:
            due_str = f"Due: {task_model.due.string}"
        elif task_model.due.date:
            due_str = f"Due: {task_model.due.date}"
    
    # Format priority
    priority_map = {1: "🔵 Low", 2: "⚪ Normal", 3: "🟠 Medium", 4: "🔴 High"}
    priority_str = priority_map.get(task_model.priority, "")
    
    # Format labels
    labels_str = ""
    if task_model.labels:
        labels_str = f"Labels: {', '.join(['@' + label for label in task_model.labels])}"
    
    # Build response
    response_text = f"# Task Updated Successfully\n\n"
    response_text += f"**{task_model.content}**\n\n"
    response_text += f"ID: `{task_model.id}`\n"
    
    if due_str:
        response_text += f"{due_str}\n"
    
    if priority_str:
        response_text += f"Priority: {priority_str}\n"
    
    if labels_str:
        response_text += f"{labels_str}\n"
    
    if task_model.description:
        response_text += f"\nDescription:\n{task_model.description}\n"
    
    response_text += f"\nView in Todoist: {task_model.url}"
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]


@handle_exceptions
async def handle_complete_task(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the complete-task tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug(f"Completing task with arguments: {arguments}")
    
    # Extract task_id
    task_id = arguments.get("task_id")
    if not task_id:
        raise ValidationError("Task ID is required")
    
    # Get original task
    try:
        original_task = await client.get_task(task_id)
        task_content = original_task.content
    except Exception:
        task_content = "the task"
    
    # Complete the task
    success = await client.close_task(task_id)
    
    if not success:
        raise TodoistError("Failed to complete task")
    
    # Build response
    response_text = f"# Task Completed Successfully\n\n"
    response_text += f"The task **{task_content}** (ID: `{task_id}`) has been marked as completed."
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]


@handle_exceptions
async def handle_delete_task(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the delete-task tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug(f"Deleting task with arguments: {arguments}")
    
    # Extract task_id
    task_id = arguments.get("task_id")
    if not task_id:
        raise ValidationError("Task ID is required")
    
    # Get original task
    try:
        original_task = await client.get_task(task_id)
        task_content = original_task.content
    except Exception:
        task_content = "the task"
    
    # Delete the task
    success = await client.delete_task(task_id)
    
    if not success:
        raise TodoistError("Failed to delete task")
    
    # Build response
    response_text = f"# Task Deleted Successfully\n\n"
    response_text += f"The task **{task_content}** (ID: `{task_id}`) has been deleted."
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]
