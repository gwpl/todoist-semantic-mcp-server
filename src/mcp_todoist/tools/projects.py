"""
Projects tools for MCP Todoist.

This module provides MCP tools for managing Todoist projects.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union, cast

import mcp.types as types
from mcp.server import Server

from ..client import TodoistClient
from ..models import ProjectMCPInput, ProjectMCPOutput
from ..utils import (
    get_logger,
    handle_exceptions,
    TodoistError,
    ValidationError,
    AuthenticationError,
)

# Get logger
logger = get_logger(__name__)


def register_project_tools(server: Server) -> None:
    """
    Register project-related tools with the server.
    
    Args:
        server: The MCP server instance.
    """
    @server.list_tools()
    async def handle_list_tools() -> List[types.Tool]:
        """List available project tools."""
        return [
            types.Tool(
                name="list-projects",
                description=(
                    "List all projects in your Todoist account.\n\n"
                    "This tool retrieves all projects from your Todoist account, including:\n"
                    "- Project names\n"
                    "- IDs\n"
                    "- Colors\n"
                    "- Parent projects (for nested projects)\n"
                    "- Favorites status\n\n"
                    "Usage examples:\n"
                    "- \"Show me all my projects\"\n"
                    "- \"List my Todoist projects\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of projects to return",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 50
                        }
                    }
                },
            ),
            types.Tool(
                name="create-project",
                description=(
                    "Create a new project in Todoist.\n\n"
                    "This tool allows you to create a new project with various properties, including:\n"
                    "- Name\n"
                    "- Color\n"
                    "- Parent project (for nested projects)\n"
                    "- Favorite status\n\n"
                    "Usage examples:\n"
                    "- \"Create a new project called 'Home Renovation'\"\n"
                    "- \"Add a project 'Q2 Goals' with color red\"\n"
                    "- \"Create a project 'Books' as a favorite\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Project name"
                        },
                        "color": {
                            "type": "string",
                            "description": "Project color (e.g., 'berry_red', 'blue', 'green')"
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "Parent project ID (for nested projects)"
                        },
                        "parent_name": {
                            "type": "string",
                            "description": "Parent project name (will look up the project ID)"
                        },
                        "favorite": {
                            "type": "boolean",
                            "description": "Whether the project is a favorite",
                            "default": false
                        }
                    },
                    "required": ["name"]
                },
            ),
            types.Tool(
                name="update-project",
                description=(
                    "Update an existing project in Todoist.\n\n"
                    "This tool allows you to update properties of an existing project, such as:\n"
                    "- Name\n"
                    "- Color\n"
                    "- Favorite status\n\n"
                    "Usage examples:\n"
                    "- \"Rename project X to 'Work 2025'\"\n"
                    "- \"Change the color of project Y to blue\"\n"
                    "- \"Mark project Z as a favorite\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "ID of the project to update"
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Current name of the project to update (will look up the project ID)"
                        },
                        "name": {
                            "type": "string",
                            "description": "New project name"
                        },
                        "color": {
                            "type": "string",
                            "description": "New project color"
                        },
                        "favorite": {
                            "type": "boolean",
                            "description": "Whether the project should be a favorite"
                        }
                    },
                    "anyOf": [
                        {"required": ["project_id"]},
                        {"required": ["project_name"]}
                    ]
                },
            ),
            types.Tool(
                name="delete-project",
                description=(
                    "Delete a project from Todoist.\n\n"
                    "This tool allows you to permanently delete a project and all its tasks.\n"
                    "WARNING: This action cannot be undone!\n\n"
                    "Usage examples:\n"
                    "- \"Delete project X\"\n"
                    "- \"Remove the 'Old Tasks' project\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "ID of the project to delete"
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project to delete (will look up the project ID)"
                        }
                    },
                    "anyOf": [
                        {"required": ["project_id"]},
                        {"required": ["project_name"]}
                    ]
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
            arguments = {}
            
        # Create Todoist client
        client = TodoistClient()
        
        if name == "list-projects":
            return await handle_list_projects(client, arguments)
        elif name == "create-project":
            return await handle_create_project(client, arguments)
        elif name == "update-project":
            return await handle_update_project(client, arguments)
        elif name == "delete-project":
            return await handle_delete_project(client, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")


@handle_exceptions
async def handle_list_projects(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the list-projects tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug("Listing projects")
    
    # Get projects
    projects = await client.get_projects()
    # Apply limit if provided
    limit = arguments.get("limit") if isinstance(arguments, dict) else None
    if isinstance(limit, int) and limit > 0:
        projects = projects[:limit]
    
    # Build project tree
    project_map = {project.id: ProjectMCPOutput.from_todoist(project) for project in projects}
    
    root_projects = []
    child_projects = {}
    
    for project_id, project in project_map.items():
        if project.parent_id:
            if project.parent_id not in child_projects:
                child_projects[project.parent_id] = []
            child_projects[project.parent_id].append(project)
        else:
            root_projects.append(project)
    
    # Sort projects
    root_projects.sort(key=lambda p: p.order if p.order is not None else 999)
    for parent_id in child_projects:
        child_projects[parent_id].sort(key=lambda p: p.order if p.order is not None else 999)
    
    # Build response
    if not projects:
        return [types.TextContent(
            type="text",
            text="You don't have any projects in your Todoist account."
        )]
    
    # Format projects
    formatted_projects = []
    
    def format_project(project, level=0):
        indent = "  " * level
        star = "⭐ " if project.is_favorite else ""
        inbox = " (Inbox)" if project.is_inbox_project else ""
        
        formatted = f"{indent}• {star}{project.name}{inbox}\n"
        formatted += f"{indent}  ID: {project.id}\n"
        formatted += f"{indent}  Color: {project.color}\n"
        
        if project.id in child_projects:
            for child in child_projects[project.id]:
                formatted += format_project(child, level + 1)
        
        return formatted
    
    for project in root_projects:
        formatted_projects.append(format_project(project))
    
    response_text = "# Todoist Projects\n\n" + "\n".join(formatted_projects)
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]


@handle_exceptions
async def handle_create_project(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the create-project tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug(f"Creating project with arguments: {arguments}")
    
    # Handle parent_name if provided
    parent_id = arguments.get("parent_id")
    parent_name = arguments.pop("parent_name", None)
    
    if parent_name and not parent_id:
        logger.debug(f"Looking up project ID for name: {parent_name}")
        projects = await client.get_projects()
        for project in projects:
            if project.name.lower() == parent_name.lower():
                parent_id = project.id
                break
        if not parent_id:
            raise ValidationError(f"Parent project not found: {parent_name}")
    
    # Parse arguments
    project_input = ProjectMCPInput(
        name=arguments["name"],
        parent_id=parent_id,
        color=arguments.get("color"),
        favorite=arguments.get("favorite", False),
    )
    
    # Create the project
    project = await client.create_project(
        name=project_input.name,
        parent_id=project_input.parent_id,
        color=project_input.color,
        favorite=project_input.favorite,
    )
    
    # Build the response
    project_model = ProjectMCPOutput.from_todoist(project)
    
    response_text = f"# Project Created Successfully\n\n"
    response_text += f"**{project_model.name}**\n\n"
    response_text += f"ID: `{project_model.id}`\n"
    response_text += f"Color: {project_model.color}\n"
    
    if parent_id:
        try:
            parent = await client.get_project(parent_id)
            response_text += f"Parent Project: {parent.name}\n"
        except:
            response_text += f"Parent Project ID: {parent_id}\n"
    
    if project_model.is_favorite:
        response_text += f"Favorite: Yes\n"
    
    response_text += f"\nView in Todoist: {project_model.url}"
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]


@handle_exceptions
async def handle_update_project(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the update-project tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug(f"Updating project with arguments: {arguments}")
    
    # Extract project_id or project_name
    project_id = arguments.pop("project_id", None)
    project_name = arguments.pop("project_name", None)
    
    if not project_id and not project_name:
        raise ValidationError("Either project_id or project_name is required")
    
    # If project_name is provided, look up the project_id
    if not project_id and project_name:
        logger.debug(f"Looking up project ID for name: {project_name}")
        projects = await client.get_projects()
        for project in projects:
            if project.name.lower() == project_name.lower():
                project_id = project.id
                break
        if not project_id:
            raise ValidationError(f"Project not found: {project_name}")
    
    # Get original project
    original_project = await client.get_project(project_id)
    
    # Update the project
    success = await client.update_project(
        project_id=project_id,
        name=arguments.get("name"),
        color=arguments.get("color"),
        favorite=arguments.get("favorite"),
    )
    
    if not success:
        raise TodoistError("Failed to update project")
    
    # Get updated project
    updated_project = await client.get_project(project_id)
    
    # Build the response
    project_model = ProjectMCPOutput.from_todoist(updated_project)
    
    response_text = f"# Project Updated Successfully\n\n"
    response_text += f"**{project_model.name}**\n\n"
    response_text += f"ID: `{project_model.id}`\n"
    response_text += f"Color: {project_model.color}\n"
    
    if project_model.parent_id:
        try:
            parent = await client.get_project(project_model.parent_id)
            response_text += f"Parent Project: {parent.name}\n"
        except:
            response_text += f"Parent Project ID: {project_model.parent_id}\n"
    
    if project_model.is_favorite:
        response_text += f"Favorite: Yes\n"
    
    response_text += f"\nView in Todoist: {project_model.url}"
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]


@handle_exceptions
async def handle_delete_project(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the delete-project tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug(f"Deleting project with arguments: {arguments}")
    
    # Extract project_id or project_name
    project_id = arguments.get("project_id")
    project_name = arguments.get("project_name")
    
    if not project_id and not project_name:
        raise ValidationError("Either project_id or project_name is required")
    
    # If project_name is provided, look up the project_id
    if not project_id and project_name:
        logger.debug(f"Looking up project ID for name: {project_name}")
        projects = await client.get_projects()
        for project in projects:
            if project.name.lower() == project_name.lower():
                project_id = project.id
                break
        if not project_id:
            raise ValidationError(f"Project not found: {project_name}")
    
    # Get original project
    try:
        original_project = await client.get_project(project_id)
        project_name = original_project.name
    except Exception:
        project_name = project_name or "the project"
    
    # Delete the project
    success = await client.delete_project(project_id)
    
    if not success:
        raise TodoistError("Failed to delete project")
    
    # Build response
    response_text = f"# Project Deleted Successfully\n\n"
    response_text += f"The project **{project_name}** (ID: `{project_id}`) has been deleted."
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]
