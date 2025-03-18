#!/bin/bash

# Set environment variables
export MCP_SERVER_NAME="mcp-todoist"
export MCP_LOG_LEVEL="INFO"
export MCP_DEBUG="true"

# Path to your Todoist MCP server
MCP_PATH="/Volumes/PRO-G40/Workspace-G40/tools/mcp-todoist"

# Log file for debugging
LOG_FILE="${MCP_PATH}/todoist-mcp.log"

# Create log file or clear existing one
echo "Starting Todoist MCP server at $(date)" > "${LOG_FILE}"

# Navigate to the project directory
cd "${MCP_PATH}"

# Start the MCP server
echo "Starting MCP server from ${MCP_PATH}" >> "${LOG_FILE}"
uv run python -m mcp_todoist >> "${LOG_FILE}" 2>&1
