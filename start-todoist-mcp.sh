#!/usr/bin/env bash

export MCP_SERVER_NAME="${MCP_SERVER_NAME:-mcp-todoist}"
export MCP_LOG_LEVEL="${MCP_LOG_LEVEL:-INFO}"
export MCP_DEBUG="${MCP_DEBUG:-true}"

# Launch the MCP server via CLI script
exec mcp-todoist
