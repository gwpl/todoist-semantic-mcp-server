# MCP Todoist

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

3. Configure Claude Desktop:
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

### 3. Using with Claude

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

### Utilities

- `search` - Search across tasks with complex filtering

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
