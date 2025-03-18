"""
MCP Todoist - A Model Context Protocol server for integrating Claude with Todoist.

This package provides a bridge between Claude and the Todoist API,
allowing Claude to manage tasks, projects, and labels in a user's Todoist account.
"""

from . import server
import asyncio
import importlib.metadata

try:
    __version__ = importlib.metadata.version("mcp-todoist")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"


def main() -> None:
    """Main entry point for the package."""
    asyncio.run(server.main())


# Expose important modules at package level
__all__ = ["main", "server"]
