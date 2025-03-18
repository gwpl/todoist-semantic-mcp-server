"""
Configuration management for MCP Todoist.

This module handles loading and accessing configuration from environment variables,
providing sensible defaults and validation.
"""

import os
import logging
from enum import Enum
from typing import Optional, Dict, Any, cast
from dataclasses import dataclass, field

# Try to load environment variables from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    """Valid log levels."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class TodoistConfig:
    """Todoist API specific configuration."""
    
    api_token: str
    request_timeout: int = 30
    rate_limit_retry: bool = True
    api_url: str = "https://api.todoist.com/rest/v2"
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.api_token:
            logger.warning(
                "Todoist API token not provided. Most functionality will not work."
            )


@dataclass
class Config:
    """Configuration class for MCP Todoist."""
    
    server_name: str
    server_version: str
    log_level: LogLevel
    debug: bool
    todoist: TodoistConfig
    extra: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        # Get MCP server configuration
        server_name = os.environ.get("MCP_SERVER_NAME", "mcp-todoist")
        server_version = os.environ.get("MCP_SERVER_VERSION", "0.1.0")
        
        # Parse log level
        log_level_str = os.environ.get("MCP_LOG_LEVEL", "INFO")
        try:
            log_level = LogLevel(log_level_str.upper())
        except ValueError:
            logger.warning(f"Invalid log level '{log_level_str}', defaulting to INFO")
            log_level = LogLevel.INFO
            
        # Parse debug mode
        debug_str = os.environ.get("MCP_DEBUG", "false")
        debug = debug_str.lower() in ("true", "1", "yes", "y")
        
        # Set the logging level based on configuration
        logging.getLogger().setLevel(getattr(logging, log_level))
        
        # Get Todoist configuration
        api_token = os.environ.get("TODOIST_API_TOKEN", "")
        
        # Parse optional Todoist configuration
        request_timeout = int(os.environ.get("TODOIST_REQUEST_TIMEOUT", "30"))
        rate_limit_retry_str = os.environ.get("TODOIST_RATE_LIMIT_RETRY", "true")
        rate_limit_retry = rate_limit_retry_str.lower() in ("true", "1", "yes", "y")
        
        todoist_config = TodoistConfig(
            api_token=api_token,
            request_timeout=request_timeout,
            rate_limit_retry=rate_limit_retry,
        )
        
        return cls(
            server_name=server_name,
            server_version=server_version,
            log_level=log_level,
            debug=debug,
            todoist=todoist_config,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "server_name": self.server_name,
            "server_version": self.server_version,
            "log_level": self.log_level.value,
            "debug": self.debug,
            "todoist": {
                "api_url": self.todoist.api_url,
                "request_timeout": self.todoist.request_timeout,
                "rate_limit_retry": self.todoist.rate_limit_retry,
                "api_token": "***" if self.todoist.api_token else None,
            },
            "extra": self.extra,
        }


# Create a global configuration instance
config = Config.from_env()


def get_config() -> Config:
    """Get the application configuration."""
    return config
