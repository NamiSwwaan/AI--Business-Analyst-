# src/agents/base_agent.py
"""
Base class for AI agents in the Task Manager application.
Provides common functionality and attributes for specialized agents.
"""

from typing import Optional
import logging
from src.config.llm_config import llm  # Default LLM instance

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all AI agents."""

    def __init__(
        self,
        role: str,
        goal: str,
        llm_instance=None,
        verbose: bool = False,
    ) -> None:
        """
        Initialize the BaseAgent with role, goal, and optional LLM settings.

        Args:
            role: The agent's role (e.g., "Business Analyst").
            goal: The agent's objective.
            llm_instance: Optional custom LLM instance; defaults to global llm.
            verbose: Enable verbose logging if True.

        Raises:
            ValueError: If role or goal is empty.
        """
        if not role.strip() or not goal.strip():
            raise ValueError("Role and goal must be non-empty strings.")
        
        self.role = role
        self.goal = goal
        self.llm = llm_instance if llm_instance is not None else llm
        self.verbose = verbose
        
        logger.info(f"Initialized {self.__class__.__name__}: role={self.role}, goal={self.goal}, verbose={self.verbose}")

    def log_action(self, action: str, details: Optional[str] = None) -> None:
        """Log an agent action with optional details."""
        message = f"Agent '{self.role}' performed {action}"
        if details:
            message += f": {details}"
        if self.verbose:
            logger.debug(message)
        else:
            logger.info(message)