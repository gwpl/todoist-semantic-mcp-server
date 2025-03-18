"""
Error handling utilities for MCP Todoist.

This module provides exception classes and decorator functions for consistent
error handling across the MCP server.
"""

import functools
import logging
import traceback
from typing import Any, Callable, TypeVar, cast

T = TypeVar("T")


class MCPError(Exception):
    """Base exception class for MCP Todoist errors."""
    
    def __init__(self, message: str, details: Any = None) -> None:
        """Initialize the exception with a message and optional details."""
        self.message = message
        self.details = details
        super().__init__(message)


class ValidationError(MCPError):
    """Raised when input validation fails."""
    pass


class AuthenticationError(MCPError):
    """Raised when authentication with Todoist API fails."""
    pass


class TodoistError(MCPError):
    """Raised when a Todoist API call fails."""
    pass


def handle_exceptions(
    func: Callable[..., T],
) -> Callable[..., T]:
    """
    Decorator to handle exceptions in a consistent way.
    
    This decorator catches all exceptions, logs them appropriately, and re-raises
    them as MCPError or its subclasses with meaningful error messages.
    
    Args:
        func: The function to decorate.
        
    Returns:
        The decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except MCPError:
            # Re-raise MCP errors without modification
            raise
        except ValueError as e:
            # Convert ValueError to ValidationError
            logging.warning(f"Validation error: {str(e)}")
            raise ValidationError(str(e)) from e
        except Exception as e:
            # Log unexpected errors and convert to TodoistError if appropriate
            logging.error(
                f"Unexpected error in {func.__name__}: {str(e)}\n"
                f"{traceback.format_exc()}"
            )
            
            # Check if it's a Todoist API error
            if "todoist" in str(e).lower():
                raise TodoistError(
                    f"Todoist API error: {str(e)}",
                    details={"function": func.__name__},
                ) from e
            
            # Otherwise, raise as generic MCPError
            raise MCPError(
                f"An unexpected error occurred: {str(e)}",
                details={"function": func.__name__},
            ) from e
            
    return cast(Callable[..., T], wrapper)
