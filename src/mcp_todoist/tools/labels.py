"""
Labels tools for MCP Todoist.

This module provides MCP tools for managing Todoist labels.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union, cast

import mcp.types as types
from mcp.server import Server

from ..client import TodoistClient
from ..models import LabelMCPInput, LabelMCPOutput
from ..utils import (
    get_logger,
    handle_exceptions,
    TodoistError,
    ValidationError,
    AuthenticationError,
)

# Get logger
logger = get_logger(__name__)


def register_label_tools(server: Server) -> None:
    """
    Register label-related tools with the server.
    
    Args:
        server: The MCP server instance.
    """
    @server.list_tools()
    async def handle_list_tools() -> List[types.Tool]:
        """List available label tools."""
        return [
            types.Tool(
                name="list-labels",
                description=(
                    "List all labels in your Todoist account.\n\n"
                    "This tool retrieves all labels from your Todoist account, including:\n"
                    "- Label names\n"
                    "- IDs\n"
                    "- Colors\n"
                    "- Favorites status\n\n"
                    "Usage examples:\n"
                    "- \"Show me all my labels\"\n"
                    "- \"List my Todoist labels\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of labels to return",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 50
                        }
                    }
                },
            ),
            types.Tool(
                name="create-label",
                description=(
                    "Create a new label in Todoist.\n\n"
                    "This tool allows you to create a new label with various properties, including:\n"
                    "- Name\n"
                    "- Color\n"
                    "- Favorite status\n\n"
                    "Usage examples:\n"
                    "- \"Create a new label called 'urgent'\"\n"
                    "- \"Add a label 'research' with color blue\"\n"
                    "- \"Create a label 'important' as a favorite\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Label name"
                        },
                        "color": {
                            "type": "string",
                            "description": "Label color (e.g., 'berry_red', 'blue', 'green')"
                        },
                        "favorite": {
                            "type": "boolean",
                            "description": "Whether the label is a favorite",
                            "default": True
                        }
                    },
                    "required": ["name"]
                },
            ),
            types.Tool(
                name="update-label",
                description=(
                    "Update an existing label in Todoist.\n\n"
                    "This tool allows you to update properties of an existing label, such as:\n"
                    "- Name\n"
                    "- Color\n"
                    "- Favorite status\n\n"
                    "Usage examples:\n"
                    "- \"Rename label X to 'critical'\"\n"
                    "- \"Change the color of label Y to red\"\n"
                    "- \"Mark label Z as a favorite\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "label_id": {
                            "type": "string",
                            "description": "ID of the label to update"
                        },
                        "label_name": {
                            "type": "string",
                            "description": "Current name of the label to update (will look up the label ID)"
                        },
                        "name": {
                            "type": "string",
                            "description": "New label name"
                        },
                        "color": {
                            "type": "string",
                            "description": "New label color"
                        },
                        "favorite": {
                            "type": "boolean",
                            "description": "Whether the label should be a favorite"
                        }
                    },
                    "anyOf": [
                        {"required": ["label_id"]},
                        {"required": ["label_name"]}
                    ]
                },
            ),
            types.Tool(
                name="delete-label",
                description=(
                    "Delete a label from Todoist.\n\n"
                    "This tool allows you to permanently delete a label.\n"
                    "NOTE: This will remove the label from all tasks that use it.\n\n"
                    "Usage examples:\n"
                    "- \"Delete label X\"\n"
                    "- \"Remove the 'old' label\"\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "label_id": {
                            "type": "string",
                            "description": "ID of the label to delete"
                        },
                        "label_name": {
                            "type": "string",
                            "description": "Name of the label to delete (will look up the label ID)"
                        }
                    },
                    "anyOf": [
                        {"required": ["label_id"]},
                        {"required": ["label_name"]}
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
        
        if name == "list-labels":
            return await handle_list_labels(client, arguments)
        elif name == "create-label":
            return await handle_create_label(client, arguments)
        elif name == "update-label":
            return await handle_update_label(client, arguments)
        elif name == "delete-label":
            return await handle_delete_label(client, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")


@handle_exceptions
async def handle_list_labels(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the list-labels tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug("Listing labels")
    
    # Get labels
    labels = await client.get_labels()
    # Apply limit if provided
    limit = arguments.get("limit") if isinstance(arguments, dict) else None
    if isinstance(limit, int) and limit > 0:
        labels = labels[:limit]
    
    # Build response
    if not labels:
        return [types.TextContent(
            type="text",
            text="You don't have any labels in your Todoist account."
        )]
    
    # Sort labels
    sorted_labels = sorted(labels, key=lambda l: getattr(l, 'order', 999) or 999)
    
    # Format labels
    formatted_labels = []
    
    for label in sorted_labels:
        label_model = LabelMCPOutput.from_todoist(label)
        
        star = "⭐ " if label_model.is_favorite else ""
        
        label_text = f"• {star}@{label_model.name}\n"
        label_text += f"  ID: {label_model.id}\n"
        label_text += f"  Color: {label_model.color}\n"
        
        formatted_labels.append(label_text)
    
    response_text = "# Todoist Labels\n\n" + "\n".join(formatted_labels)
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]


@handle_exceptions
async def handle_create_label(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the create-label tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug(f"Creating label with arguments: {arguments}")
    
    # Parse arguments
    label_input = LabelMCPInput(
        name=arguments["name"],
        color=arguments.get("color"),
        favorite=arguments.get("favorite", False),
    )
    
    # Create the label
    label = await client.create_label(
        name=label_input.name,
        color=label_input.color,
        favorite=label_input.favorite,
    )
    
    # Build the response
    label_model = LabelMCPOutput.from_todoist(label)
    
    response_text = f"# Label Created Successfully\n\n"
    response_text += f"**@{label_model.name}**\n\n"
    response_text += f"ID: `{label_model.id}`\n"
    response_text += f"Color: {label_model.color}\n"
    
    if label_model.is_favorite:
        response_text += f"Favorite: Yes\n"
    
    response_text += f"\nUse this label in tasks by including '@{label_model.name}' in your task content."
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]


@handle_exceptions
async def handle_update_label(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the update-label tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug(f"Updating label with arguments: {arguments}")
    
    # Extract label_id or label_name
    label_id = arguments.pop("label_id", None)
    label_name = arguments.pop("label_name", None)
    
    if not label_id and not label_name:
        raise ValidationError("Either label_id or label_name is required")
    
    # If label_name is provided, look up the label_id
    if not label_id and label_name:
        logger.debug(f"Looking up label ID for name: {label_name}")
        labels = await client.get_labels()
        for label in labels:
            if label.name.lower() == label_name.lower():
                label_id = label.id
                break
        if not label_id:
            raise ValidationError(f"Label not found: {label_name}")
    
    # Get original label
    original_label = await client.get_label(label_id)
    
    # Update the label
    success = await client.update_label(
        label_id=label_id,
        name=arguments.get("name"),
        color=arguments.get("color"),
        favorite=arguments.get("favorite"),
    )
    
    if not success:
        raise TodoistError("Failed to update label")
    
    # Get updated label
    updated_label = await client.get_label(label_id)
    
    # Build the response
    label_model = LabelMCPOutput.from_todoist(updated_label)
    
    response_text = f"# Label Updated Successfully\n\n"
    response_text += f"**@{label_model.name}**\n\n"
    response_text += f"ID: `{label_model.id}`\n"
    response_text += f"Color: {label_model.color}\n"
    
    if label_model.is_favorite:
        response_text += f"Favorite: Yes\n"
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]


@handle_exceptions
async def handle_delete_label(
    client: TodoistClient, 
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle the delete-label tool.
    
    Args:
        client: The Todoist client
        arguments: Tool arguments
        
    Returns:
        List of TextContent objects
    """
    logger.debug(f"Deleting label with arguments: {arguments}")
    
    # Extract label_id or label_name
    label_id = arguments.get("label_id")
    label_name = arguments.get("label_name")
    
    if not label_id and not label_name:
        raise ValidationError("Either label_id or label_name is required")
    
    # If label_name is provided, look up the label_id
    if not label_id and label_name:
        logger.debug(f"Looking up label ID for name: {label_name}")
        labels = await client.get_labels()
        for label in labels:
            if label.name.lower() == label_name.lower():
                label_id = label.id
                break
        if not label_id:
            raise ValidationError(f"Label not found: {label_name}")
    
    # Get original label
    try:
        original_label = await client.get_label(label_id)
        label_name = original_label.name
    except Exception:
        label_name = label_name or "the label"
    
    # Delete the label
    success = await client.delete_label(label_id)
    
    if not success:
        raise TodoistError("Failed to delete label")
    
    # Build response
    response_text = f"# Label Deleted Successfully\n\n"
    response_text += f"The label **@{label_name}** (ID: `{label_id}`) has been deleted."
    
    return [types.TextContent(
        type="text",
        text=response_text
    )]
