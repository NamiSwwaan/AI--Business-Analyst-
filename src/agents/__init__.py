# src/agents/__init__.py
"""
Agents module for the Task Manager application.
Contains AI agent implementations for business analysis, employee evaluation, and task processing.
"""

from .ba_agent import run_ba_agent
from .employee_agent import load_employees, create_employee_agent
from .base_agent import BaseAgent
from .task_agent import batch_task_processing  # Assuming task_agent.py will contain this

__all__ = [
    "run_ba_agent",
    "load_employees",
    "create_employee_agent",
    "BaseAgent",
    "batch_task_processing",
]