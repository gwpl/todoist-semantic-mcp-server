"""
Tools for the MCP Todoist server.

This package contains all the tools that are provided by the MCP server.
Each tool is implemented in its own module and registered in the server.
"""

from .tasks import register_task_tools
from .projects import register_project_tools
from .labels import register_label_tools

__all__ = ["register_tools"]


def register_tools(server):
    """
    Register all tools with the server.
    
    Args:
        server: The MCP server instance.
    """
    # Register each group of tools with the server
    register_task_tools(server)
    register_project_tools(server)
    register_label_tools(server)
