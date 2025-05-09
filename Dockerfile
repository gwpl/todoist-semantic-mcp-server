### Dockerfile for MCP Todoist
# Use slim Python base image
FROM python:3.11-slim

# Install OS-level build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build backend
RUN pip install --upgrade pip \
    && pip install --no-cache-dir hatchling

# Set working directory
WORKDIR /app

COPY pyproject.toml README.md uv.lock ./
COPY src/ src/

# Install the package and its dependencies, and install the uvx HTTP wrapper
RUN pip install --no-cache-dir . \
    && pip install --no-cache-dir uv

# Expose default MCP JSON-RPC port (used by uvx)
EXPOSE 3742

# Default command: start the MCP Todoist server
CMD ["mcp-todoist"]