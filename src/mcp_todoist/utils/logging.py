"""
Logging utilities for MCP Todoist.

This module provides consistent logging setup and functions for use throughout the MCP server.
"""

import logging
import sys
from typing import Optional

from ..config import config


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: The name of the logger. If not provided, the caller module name is used.
        
    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Set level based on global configuration
    logger.setLevel(getattr(logging, config.log_level))
    
    # If the logger doesn't have handlers yet, add one
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        
        # Use a detailed format for debug mode, simpler for normal operation
        if config.debug:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            )
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
