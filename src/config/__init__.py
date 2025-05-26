# src/config/__init__.py
"""
Configuration module for the Task Manager application.
Handles general settings and LLM configuration.
"""

from .config import (
    set_page_config,
    BASE_DELAY,
    MAX_RETRIES,
    MIN_WAIT,
    MAX_WAIT,
    MAX_EMPLOYEES_PER_TASK,
    HOURS_PER_DAY,
    DEBUG,  # Added here
)
from .llm_config import llm

__all__ = [
    "set_page_config",
    "BASE_DELAY",
    "MAX_RETRIES",
    "MIN_WAIT",
    "MAX_WAIT",
    "MAX_EMPLOYEES_PER_TASK",
    "HOURS_PER_DAY",
    "DEBUG",  # Added here
    "llm",
]