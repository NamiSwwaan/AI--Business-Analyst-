# src/agents/task_agent.py
"""
Task Agent module for estimating task durations and generating sub-tasks.
"""

from typing import Tuple, List, Dict
from crewai import Agent, Task, Crew
import logging
from src.config.llm_config import llm
from src.config.config import MAX_RETRIES
from src.agents.base_agent import BaseAgent
from src.utils.utils import call_with_retry, parse_json_output, parse_duration

logger = logging.getLogger(__name__)

class TaskAgent(BaseAgent):
    """Agent for processing tasks and estimating durations."""

    def __init__(self):
        """Initialize the TaskAgent."""
        super().__init__(
            role="Task Processor",
            goal="Estimate task durations and generate detailed sub-tasks.",
            verbose=True,
        )
        self.backstory = "An expert in project estimation and task breakdown."

    def process_task(self, task: str) -> Tuple[float, List[Dict]]:
        """
        Estimate duration and generate sub-tasks for a given task.

        Args:
            task: The task description.

        Returns:
            Tuple of (duration in hours, list of sub-tasks).
        """
        if not task.strip():
            logger.warning("Empty task provided.")
            return 10.0, [{"sub_task": "Default task", "help": "No description provided."}]

        self.log_action("processing task", task)
        agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.llm,
            verbose=self.verbose,
        )
        task_obj = Task(
            description=(
                f"For '{task}': "
                "1. Estimate realistic duration in hours (e.g., API dev: 20-40h, UI design: 10-20h). "
                "2. List sub-tasks as JSON: {'sub_task': str, 'help': str}. "
                "Return a JSON object with 'duration' and 'sub_tasks'."
            ),
            expected_output="JSON with duration and sub-tasks",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task_obj])

        try:
            result = call_with_retry(crew)
            raw_result = result.raw.strip()
            data = parse_json_output(raw_result)

            if not data or "duration" not in data or "sub_tasks" not in data:
                logger.warning(f"Invalid LLM output for '{task}': {raw_result[:200]}...")
                return self._fallback(task)

            duration = parse_duration(data["duration"])
            if duration is None:
                logger.warning(f"Unparseable duration '{data['duration']}' for '{task}'")
                return self._fallback(task)

            sub_tasks = data.get("sub_tasks", [{"sub_task": f"Sub-task 1 for {task}", "help": "Basic step"}])
            if not isinstance(sub_tasks, list):
                logger.warning(f"Sub-tasks not a list: {sub_tasks}")
                sub_tasks = [{"sub_task": f"Sub-task 1 for {task}", "help": "Basic step"}]

            self.log_action("task processed", f"Duration: {duration}h, Sub-tasks: {len(sub_tasks)}")
            return duration, sub_tasks

        except Exception as e:
            logger.error(f"Failed to process task '{task}': {e}")
            return self._fallback(task)

    def _fallback(self, task: str) -> Tuple[float, List[Dict]]:
        """Provide fallback values if processing fails."""
        duration = (
            30.0 if "api" in task.lower() else
            15.0 if "ui" in task.lower() else
            12.0 if "database" in task.lower() else
            10.0
        )
        sub_tasks = [{"sub_task": f"Sub-task 1 for {task}", "help": "Default step"}]
        logger.info(f"Fallback for '{task}': {duration}h, 1 sub-task")
        return duration, sub_tasks

def batch_task_processing(task: str) -> Tuple[float, List[Dict]]:
    """
    Process a task and return its duration and sub-tasks.

    Args:
        task: The task description.

    Returns:
        Tuple of (duration in hours, list of sub-tasks).
    """
    agent = TaskAgent()
    return agent.process_task(task)