# src/agents/employee_agent.py
"""
Employee agent module for loading employee data and evaluating task suitability.
"""

import json
from typing import List, Dict, Optional
from crewai import Agent, Task, Crew
import logging
import os
from dotenv import load_dotenv
from src.config.llm_config import llm
from src.agents.base_agent import BaseAgent
from src.utils.utils import call_with_retry

load_dotenv()
logger = logging.getLogger(__name__)

def load_employees() -> List[Dict]:
    """
    Load employee data from the configured JSON file.

    Returns:
        List of employee dictionaries.

    Raises:
        FileNotFoundError: If the employees file is not found.
        json.JSONDecodeError: If the file is invalid JSON.
        Exception: For other unexpected errors.
    """
    employees_file = os.getenv("EMPLOYEES_FILE", "data/employees.json")
    try:
        with open(employees_file, "r") as f:
            employees = json.load(f)
        logger.info(f"Loaded {len(employees)} employees from {employees_file}")
        return employees
    except FileNotFoundError:
        logger.error(f"Employees file not found: {employees_file}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {employees_file}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading {employees_file}: {e}")
        raise

class EmployeeAgent(BaseAgent):
    """Agent to evaluate if an employee can handle a task."""

    def __init__(self, employee: Dict):
        """Initialize with employee data."""
        super().__init__(
            role=employee["role"],
            goal="Evaluate if a task aligns with my skills and expertise.",
            verbose=True,
        )
        self.name = employee["name"]
        self.my_work = employee.get("my_work", "")
        self.skills = employee.get("skills", [])
        self.backstory = f"{self.name} with role {self.role}, specializing in: {self.my_work}"

    def evaluate_task(self, task_desc: str) -> str:
        """
        Evaluate if the employee can handle the task.

        Args:
            task_desc: Description of the task.

        Returns:
            String in format 'YES|NO: reason'.
        """
        if not task_desc.strip():
            logger.warning(f"Empty task description for {self.name}")
            return "NO: No task description provided."

        self.log_action("evaluating task", task_desc)
        agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.llm,
            verbose=self.verbose,
        )
        task = Task(
            description=f"Can you handle this task: '{task_desc}'? Reply with 'YES' or 'NO' followed by a short reason.",
            expected_output="YES/NO with reasoning",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task])

        try:
            result = call_with_retry(crew)
            raw_result = result.raw.strip()
            self.log_action("task evaluated", raw_result)

            # Parse response for consistency
            if "YES" in raw_result.upper():
                reason = raw_result.split("YES", 1)[1].strip(": ") if "YES" in raw_result else "Task aligns with skills."
                return f"YES: {reason}"
            elif "NO" in raw_result.upper():
                reason = raw_result.split("NO", 1)[1].strip(": ") if "NO" in raw_result else "Task outside expertise."
                return f"NO: {reason}"
            else:
                logger.warning(f"Unparseable response from {self.name}: {raw_result}")
                return "NO: Unable to determine suitability."

        except Exception as e:
            logger.error(f"Error evaluating task '{task_desc}' for {self.name}: {e}")
            return f"NO: Evaluation failed due to error."

def create_employee_agent(employee: Dict, task_desc: str) -> str:
    """
    Create an employee agent and evaluate a task.

    Args:
        employee: Dictionary with employee data.
        task_desc: Task description to evaluate.

    Returns:
        String response from the agent (YES|NO: reason).
    """
    agent = EmployeeAgent(employee)
    return agent.evaluate_task(task_desc)