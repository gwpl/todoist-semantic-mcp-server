"""
Main MCP server implementation for MCP Todoist.

This module defines the MCP server, registers tools, and handles server initialization.
"""

import asyncio
import sys
from typing import Any, Dict, Optional, cast

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from .config import get_config
from .tools import register_tools
from .utils import get_logger

# Get configuration
config = get_config()

# Set up logging
logger = get_logger(__name__)

# Create server instance
server = Server(config.server_name)


# Register the server's capabilities
async def initialize_server() -> None:
    """
    Initialize the server with all tools and capabilities.
    """
    # Register all tools from the tools package
    register_tools(server)
    
    # Log the initialization
    logger.info(f"Initialized {config.server_name} v{config.server_version}")
    if config.debug:
        logger.debug(f"Configuration: {config.to_dict()}")


async def main() -> None:
    """
    Run the server using stdin/stdout streams.
    
    This is the main entry point for the MCP server.
    """
    try:
        # Initialize server
        await initialize_server()
        
        # Check Todoist API token
        if not config.todoist.api_token:
            logger.warning(
                "Todoist API token not provided. Set the TODOIST_API_TOKEN environment variable."
            )
        
        # Run the server with stdin/stdout
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info(f"Starting {config.server_name} v{config.server_version}")
            
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=config.server_name,
                    server_version=config.server_version,
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        sys.exit(1)
