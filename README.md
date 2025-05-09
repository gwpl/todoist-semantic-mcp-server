# MCP Todoist

---

## 📝 Fork Motivation: Towards Semantic, Human- and LLM-Friendly MCP Servers

This repository is a fork motivated by my observations and frustrations with the current landscape of MCP (Model Context Protocol) servers for Todoist and similar tools. Most existing MCP servers are essentially carbon copies of the underlying REST APIs—they simply expose the same endpoints and function calls, often with little thought to how LLMs or humans actually interact with these systems.

### Why fork? Why "semantic"?

- **API ≠ Usable Interface:** The direct mapping of REST endpoints to MCP tools leads to poor usability. For example, if you ask for a list of projects and have thousands (as I do, after a decade of use), the server just dumps them all, overwhelming both the LLM and the user, and sometimes even causing crashes.
- **LLM/Voice/Imprecise Input:** When interacting with LLMs—especially via voice—names may be misspelled or ambiguous. Existing servers fail to handle this gracefully, so you might end up with duplicate tasks or projects just because of a minor spelling difference.
- **Too Many Rounds, Too Much Data:** LLMs struggle when they have to sift through huge lists or make many round-trips to find the right item. This is not a good user experience.

### My approach

This fork aims to start addressing these issues by introducing more *semantic* and *LLM-friendly* tool calls. For example:
- **Search with limits:** Allowing the model to request only a manageable number of results.
- **Fuzzy search:** Enabling the model to find the right task or project even if the name is not an exact match.

This is just the beginning—my goal is to make MCP servers that are truly *semantic*, meaning they are designed for how humans and LLMs actually interact, not just for mirroring an API. I may eventually create a separate repository with a "manifesto" for semantic MCP servers and more general tools for this approach. This repo is not as semantic as I would ultimately like, but I need to start somewhere.

**I hope these changes will help my workflow and, hopefully, yours too. If you have struggled with existing integrations that overwhelm LLMs or require too many steps to get things done, this fork is for you.**

*TODO: Add links to related discussions, manifesto, and other semantic MCP server resources here.*

---

A Model Context Protocol (MCP) server that enables Claude to interact with your Todoist account.

## Features

- Manage tasks: create, update, complete, and delete tasks
- Organize tasks in projects and with labels
- Search and filter tasks based on various criteria
- Seamless integration with Claude Desktop

## Prerequisites

- Python 3.11+
- [Astral UV](https://docs.astral.sh/uv/installation/)
- [Todoist account](https://todoist.com/) and [API token](https://app.todoist.com/app/settings/integrations/developer)
- Claude Desktop (for using the MCP server)

## Quick Start

### 1. Installation

```bash
# Install using UV
uvx mcp-todoist
```

### 2. Configuration

1. Get your Todoist API token from [Todoist Integrations settings](https://app.todoist.com/app/settings/integrations/developer)

2. Configure the environment variable:
   ```bash
   # Add to your .env file or environment
   TODOIST_API_TOKEN=your_api_token_here
   ```
3. (Optional) Customize server behavior via JSON config:
   ```bash
   # Provide default limits and thresholds
   export TODOIST_SERVER_CONFIG_JSON='{"defaultLimit":50,"fuzzyThreshold":80}'
   ```

4. Configure Claude Desktop:
   ```json
   // ~/.config/claude/claude_desktop_config.json or equivalent
   {
     "mcpServers": {
       "mcp-todoist": {
         "command": "uvx",
         "args": ["mcp-todoist"]
       }
     }
   }
   ```

### 5. Using with Claude

Once configured, you can ask Claude to interact with your Todoist account:

- "Show me my tasks due today"
- "Create a new task to buy groceries tomorrow"
- "Mark my 'send email' task as complete"
- "Create a new project called 'Home Renovation'"
- "Show me all tasks in my Work project"

## Available Tools

### Task Management

- `list-tasks` - Retrieve and filter tasks
- `create-task` - Create a new task
- `update-task` - Update an existing task
- `complete-task` - Mark a task as completed
- `delete-task` - Delete a task

### Project Management

- `list-projects` - Get all projects
- `create-project` - Create a new project
- `update-project` - Update a project
- `delete-project` - Delete a project

### Label Management

- `list-labels` - Get all labels
- `create-label` - Create a new label
- `update-label` - Update a label
- `delete-label` - Delete a label

<!-- Removed obsolete search utility; no generic search tool implemented -->

## Running the MCP Server

There are multiple ways to run the Todoist MCP server:

### Method 1: Direct Command Line

Run the server in a terminal window:

```bash
# Set your API token
export TODOIST_API_TOKEN=your_api_token_here

# Run the server using UV
uvx mcp-todoist

# Alternative: Run from source
cd /path/to/mcp-todoist
uv run python -m mcp_todoist
```

Keep this terminal window open while using Claude Desktop.

### Method 2: Using a Startup Script (Recommended)

Create a startup script that Claude Desktop can use to automatically start the server:

1. Create a file named `start-todoist-mcp.sh` with the following content:

```bash
#!/bin/bash

# Set environment variables
export MCP_SERVER_NAME="mcp-todoist"
export MCP_LOG_LEVEL="INFO"
export MCP_DEBUG="true"
export TODOIST_API_TOKEN="your_todoist_api_token_here"

# Path to your Todoist MCP server
MCP_PATH="/path/to/mcp-todoist"

# Log file for debugging
LOG_FILE="${MCP_PATH}/todoist-mcp.log"

# Create log file or clear existing one
echo "Starting Todoist MCP server at $(date)" > "${LOG_FILE}"

# Navigate to the project directory
cd "${MCP_PATH}"

# Start the MCP server
echo "Starting MCP server from ${MCP_PATH}" >> "${LOG_FILE}"
uv run python -m mcp_todoist >> "${LOG_FILE}" 2>&1
```

2. Make the script executable:

```bash
chmod +x start-todoist-mcp.sh
```

3. Update your Claude Desktop configuration to use this script:

```json
{
  "mcpServers": {
    "mcp-todoist": {
      "command": "/absolute/path/to/start-todoist-mcp.sh",
      "args": []
    }
  }
}
```

---
## Docker Deployment

The following instructions show how to build and run the MCP Todoist server in Docker.

### 1. Build the Docker Image

```bash
# From the project root (contains Dockerfile above)
docker build -t mcp-todoist .
```

### 2. Configure Environment Variables

The container requires at least:
- `TODOIST_API_TOKEN`: your Todoist API token
- `TODOIST_SERVER_CONFIG_JSON` (optional): JSON string for extra server settings, e.g. `{"defaultLimit":50}`

#### a) Using an `.env` file (simple)

1. Create a file named `.env` next to your Dockerfile:

   ```ini
   TODOIST_API_TOKEN=your_api_token_here
   TODOIST_SERVER_CONFIG_JSON={"defaultLimit":50}
   ```

2. Run the container:

   ```bash
   docker run -d \
     --name mcp-todoist \
     --env-file .env \
     -p 127.0.0.1:3742:3742 \
     --restart unless-stopped \
     mcp-todoist
   ```

3. View logs:

   ```bash
   docker logs mcp-todoist
   ```

To update your token or config, edit `.env` and then:  
```bash
docker restart mcp-todoist
```

#### b) Using Docker secrets (secure, Swarm/Kubernetes)

For production, avoid passing secrets on the CLI or embedding them in image layers. Use Docker secrets or a secrets manager.

1. Create a secret (example in Swarm):
   ```bash
   echo -n "your_api_token_here" | docker secret create todoist_token -
   ```

2. Deploy the container referencing the secret:
   ```bash
   docker service create \
     --name mcp-todoist \
     --secret source=todoist_token,target=TODOIST_API_TOKEN \
     -p 127.0.0.1:3742:3742 \
     --restart-condition any \
     mcp-todoist
   ```

Refer to Docker/Swarm documentation for updating secrets and rolling restarts.

This approach offers several advantages:
- The server starts automatically with Claude Desktop
- All logs are captured in a file for easier debugging
- Environment variables are set consistently

## Debugging

If you encounter issues with the MCP server, here are some debugging strategies:

### 1. Check the Logs

If using the startup script, check the log file:

```bash
cat /path/to/mcp-todoist/todoist-mcp.log
```

### 2. Enable Debug Mode

Set the `MCP_DEBUG` environment variable to `true` for more verbose logging:

```bash
export MCP_DEBUG=true
uvx mcp-todoist
```

### 3. Verify API Token

Ensure your Todoist API token is correct and still valid:

```bash
# Test the token with a simple curl request
curl -X GET \
  https://api.todoist.com/rest/v2/projects \
  -H "Authorization: Bearer $TODOIST_API_TOKEN"
```

### 4. Use the MCP Inspector

The MCP Inspector is a powerful tool for debugging MCP servers:

```bash
npx @modelcontextprotocol/inspector uvx mcp-todoist
```

This will open a web interface showing all communications between Claude and the MCP server.

### 5. Common Issues and Solutions

- **"MCP Server not available" error**: Ensure the server is running in a separate terminal or via a startup script.
- **Authentication errors**: Check that your Todoist API token is correctly set in your environment.
- **"Command not found" errors**: Make sure Astral UV is installed and in your PATH.
- **Timeout errors**: If your MCP server is slow to respond, try increasing the timeout in Claude Desktop settings.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-todoist.git
cd mcp-todoist

# Install dependencies
uv sync
```

### Testing

```bash
# Run tests
uv run pytest
```

### Local Development

For local development, you can create a `.env` file with your Todoist API token:

```
TODOIST_API_TOKEN=your_api_token_here
```

Then run the server:

```bash
uv run python -m mcp_todoist
```

## License

MIT License - see LICENSE file for details.

---

## Manual Debugging via mcptools

Manual debugging or direct command-line usage of the MCP Todoist tool can be done using [mcptools](https://github.com/f/mcptools). Assuming you have Go installed, install mcptools on Linux with:

```bash
go install github.com/f/mcptools/cmd/mcptools@latest
```

Once installed, you can list the available Todoist MCP tools:

```bash
export TODOIST_API_TOKEN=your_api_token_here
mcptools tools docker run -i --rm -e TODOIST_API_TOKEN mcp-todoist
```

