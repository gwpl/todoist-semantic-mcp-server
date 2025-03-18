"""
Basic tests for MCP Todoist server.

This module contains basic tests for the MCP server, focusing on tool registration.
More comprehensive tests would require mocking the Todoist API.
"""

import pytest
from typing import List, Dict

from mcp.server import Server
from mcp_todoist.server import server
from mcp_todoist.config import Config
from mcp_todoist.utils import TodoistError, AuthenticationError


@pytest.fixture
def test_server() -> Server:
    """Create a test server instance."""
    return server


def test_tool_registration(test_server: Server) -> None:
    """Test that all tools are correctly registered with the server."""
    # Get all tool descriptions
    tool_descriptions = test_server.get_tool_descriptions()
    
    # Check that we have the expected tools
    tool_names = [tool.name for tool in tool_descriptions]
    
    # Task tools
    assert "list-tasks" in tool_names
    assert "create-task" in tool_names
    assert "update-task" in tool_names
    assert "complete-task" in tool_names
    assert "delete-task" in tool_names
    
    # Project tools
    assert "list-projects" in tool_names
    assert "create-project" in tool_names
    assert "update-project" in tool_names
    assert "delete-project" in tool_names
    
    # Label tools
    assert "list-labels" in tool_names
    assert "create-label" in tool_names
    assert "update-label" in tool_names
    assert "delete-label" in tool_names


def test_config() -> None:
    """Test configuration object creation."""
    # Create a test config
    config = Config(
        server_name="test-server",
        server_version="0.1.0",
        log_level="INFO",
        debug=False,
        todoist=Config.TodoistConfig(
            api_token="test-token",
            request_timeout=30,
            rate_limit_retry=True,
        ),
    )
    
    # Check values
    assert config.server_name == "test-server"
    assert config.server_version == "0.1.0"
    assert config.debug is False
    assert config.todoist.api_token == "test-token"
    assert config.todoist.request_timeout == 30
    assert config.todoist.rate_limit_retry is True
