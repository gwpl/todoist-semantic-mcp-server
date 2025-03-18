# Debugging Guide for MCP Todoist

This guide provides comprehensive instructions for troubleshooting and debugging the MCP Todoist server.

## Understanding the MCP Architecture

The Model Context Protocol (MCP) framework operates on a client-server architecture:

1. **Claude Desktop** (client) - Sends tool invocation requests
2. **MCP Todoist** (server) - Processes requests and communicates with the Todoist API
3. **Todoist API** - External service providing task management functionality

Problems can occur at any of these layers or in their communication.

## Server Startup Issues

### Common Startup Problems

1. **Server Not Starting**

   Symptoms:
   - Claude says "MCP Server not available"
   - No response when trying to use Todoist tools

   Possible Causes:
   - The server process isn't running
   - Path to the script is incorrect
   - Permission issues with the script
   - Python environment issues

   Solutions:
   - Start the server manually to check for errors:
     ```bash
     uvx mcp-todoist
     ```
   - Check script permissions:
     ```bash
     chmod +x start-todoist-mcp.sh
     ```
   - Verify Python and UV installation:
     ```bash
     python --version
     uv --version
     ```

2. **Configuration Errors**

   Symptoms:
   - Server starts but terminates immediately
   - Error messages about missing configuration

   Solutions:
   - Check environment variables:
     ```bash
     # In your startup script or command line
     export MCP_SERVER_NAME="mcp-todoist"
     export MCP_LOG_LEVEL="INFO"
     export TODOIST_API_TOKEN="your_api_token_here"
     ```

3. **Dependency Issues**

   Symptoms:
   - "ModuleNotFoundError" or similar import errors

   Solutions:
   - Reinstall dependencies:
     ```bash
     cd /path/to/mcp-todoist
     uv sync
     ```
   - Check that all dependencies are available:
     ```bash
     uv pip list
     ```

## Runtime Issues

### API Connection Problems

1. **Authentication Failures**

   Symptoms:
   - Error messages about invalid API token
   - "Unauthorized" errors in logs

   Solutions:
   - Verify your Todoist API token is correct:
     ```bash
     curl -X GET \
       https://api.todoist.com/rest/v2/projects \
       -H "Authorization: Bearer $TODOIST_API_TOKEN"
     ```
   - Regenerate your token in the Todoist settings
   - Check for trailing spaces or newlines in your token

2. **Rate Limiting**

   Symptoms:
   - "Too many requests" errors
   - Intermittent failures

   Solutions:
   - Add delays between requests
   - Implement exponential backoff (already included in the client)
   - Reduce the frequency of requests

3. **Network Issues**

   Symptoms:
   - Connection timeouts
   - "Network error" messages

   Solutions:
   - Check your internet connection
   - Verify that Todoist API is accessible from your network
   - Check for any proxy or firewall issues

### MCP Protocol Issues

1. **Version Mismatches**

   Symptoms:
   - Errors about invalid JSON or unexpected protocol formats

   Solutions:
   - Update to the latest MCP SDK:
     ```bash
     uv sync
     ```
   - Ensure Claude Desktop is up-to-date

2. **Tool Definition Issues**

   Symptoms:
   - Tool not appearing in Claude
   - "Tool not found" errors

   Solutions:
   - Check tool registration in your code
   - Verify the tool names match between list_tools and call_tool handlers

## Using Debugging Tools

### MCP Inspector

The MCP Inspector is a powerful tool for debugging MCP servers:

```bash
npx @modelcontextprotocol/inspector uvx mcp-todoist
```

Key features:
- View all requests and responses
- Simulate tool calls
- Inspect tool definitions
- Test server responses

### Logging

Enable detailed logging for better visibility:

1. **Standard Logs**

   Set the log level in your environment or startup script:
   ```bash
   export MCP_LOG_LEVEL="DEBUG"
   ```

2. **Custom Log File**

   Create a dedicated log file for easier debugging:
   ```bash
   # In your startup script
   LOG_FILE="/path/to/todoist-mcp.log"
   uvx mcp-todoist >> "${LOG_FILE}" 2>&1
   ```

3. **Log Analysis**

   Useful commands for analyzing logs:
   ```bash
   # View the last 100 lines of the log
   tail -n 100 todoist-mcp.log
   
   # Watch the log file in real-time
   tail -f todoist-mcp.log
   
   # Search for error messages
   grep -i "error" todoist-mcp.log
   
   # Search for specific API calls
   grep -i "get_tasks" todoist-mcp.log
   ```

## Claude Desktop Configuration

Claude Desktop requires proper configuration to connect to your MCP server:

1. **Find the Configuration File**

   Location:
   - macOS: `~/Library/Application Support/claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\claude\claude_desktop_config.json`

2. **Configure the MCP Server**

   Example configuration:
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

3. **Configuration Options**

   - `command`: The command or script to start the MCP server
   - `args`: Command-line arguments to pass to the server
   - `env`: Additional environment variables (optional)
   - `cwd`: Working directory (optional)

4. **Restart Claude Desktop**

   After changing the configuration, restart Claude Desktop for changes to take effect.

## Todoist API Debugging

To isolate issues with the Todoist API:

1. **API Documentation**

   Refer to the [Todoist API Documentation](https://developer.todoist.com/rest/v2) for correct endpoint usage.

2. **API Testing**

   Test API endpoints directly to verify they work as expected:
   ```bash
   # List projects
   curl -X GET \
     https://api.todoist.com/rest/v2/projects \
     -H "Authorization: Bearer $TODOIST_API_TOKEN"
   
   # Get tasks
   curl -X GET \
     https://api.todoist.com/rest/v2/tasks \
     -H "Authorization: Bearer $TODOIST_API_TOKEN"
   ```

3. **API Limitations**

   Be aware of Todoist API limitations:
   - Rate limits (approximately 450 requests per hour)
   - Maximum request size (1MB)
   - API downtime or maintenance

## Advanced Debugging Techniques

### Debugging MCP Communication

1. **Intercepting Traffic**

   Use a proxy tool like `mitmproxy` to intercept and analyze the traffic:
   ```bash
   pip install mitmproxy
   mitmproxy -p 8888
   ```

   Then update your environment to use the proxy:
   ```bash
   export HTTP_PROXY="http://localhost:8888"
   export HTTPS_PROXY="http://localhost:8888"
   ```

2. **Process Monitoring**

   Monitor the MCP server process:
   ```bash
   # View process information
   ps aux | grep mcp-todoist
   
   # Monitor resource usage
   top -p $(pgrep -f mcp-todoist)
   ```

### Code-Level Debugging

1. **Python Debugger**

   Use `pdb` for step-by-step debugging:
   ```python
   import pdb; pdb.set_trace()
   ```

2. **Mock Testing**

   Create mock tests to simulate the Todoist API:
   ```python
   from unittest.mock import patch, MagicMock
   
   @patch('todoist_api_python.api.TodoistAPI')
   def test_list_tasks(mock_api):
       # Mock API responses...
       mock_api.return_value.get_tasks.return_value = [...]
   ```

## Common Error Messages and Solutions

| Error Message | Possible Cause | Solution |
|---------------|----------------|----------|
| "MCP Server not available" | Server not running | Start the server using the provided script |
| "Invalid API token" | Incorrect Todoist API token | Check and update your API token |
| "Failed to get tasks" | API error or connectivity issue | Check your internet connection and Todoist API status |
| "Tool not found" | Misconfiguration in tool registration | Verify tool names and registration |
| "Module not found" | Missing dependencies | Reinstall dependencies with `uv sync` |

## Getting Help

If you're still experiencing issues:

1. **Check Issue Tracker**

   Look for similar issues in the project's issue tracker.

2. **Provide Detailed Information**

   When reporting issues, include:
   - Error messages
   - MCP server logs
   - Steps to reproduce
   - Environment details (OS, Python version, etc.)

3. **Community Resources**

   - [MCP Documentation](https://modelcontextprotocol.io/docs/)
   - [Todoist API Documentation](https://developer.todoist.com/rest/v2)
