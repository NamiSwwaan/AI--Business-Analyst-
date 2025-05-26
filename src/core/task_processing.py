# src/core/task_processing.py
"""
Task processing utilities for the Task Manager application.
Handles employee assignment and sub-task distribution.
"""

import time
import logging
from typing import List, Dict, Tuple, Any
from src.config import BASE_DELAY
from src.agents.employee_agent import create_employee_agent
from src.utils.utils import parse_duration  # Moved here

logger = logging.getLogger(__name__)

def check_employees_for_task(
    task: str,
    employees: List[Dict[str, Any]],
    scored_employees: List[Tuple[Dict[str, Any], float]],
    required_employees: int
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Evaluate and assign employees to a task based on scores and availability.

    Args:
        task: Task description.
        employees: List of all employee dictionaries.
        scored_employees: List of (employee, score) tuples from task_matcher.
        required_employees: Number of employees needed.

    Returns:
        Tuple of (assigned employees, response messages).
    """
    if not task.strip() or not employees or required_employees <= 0:
        logger.warning(f"Invalid inputs: task='{task}', employees={len(employees)}, required={required_employees}")
        return [], ["No assignment possible due to invalid inputs."]

    # Map scores to employees, defaulting to 0 if not found
    employee_scores = {emp["name"]: 0.0 for emp in employees}
    for emp, score in scored_employees:
        employee_scores[emp["name"]] = score

    # Sort employees by score
    sorted_employees = sorted(employees, key=lambda e: employee_scores.get(e["name"], 0), reverse=True)
    assigned, responses = [], []

    for emp in sorted_employees[:required_employees]:
        try:
            time.sleep(BASE_DELAY)  # Rate limiting
            reply = create_employee_agent(emp, task)
            accepted = "YES" in reply.split(":")[0].upper()
            score = employee_scores.get(emp["name"], 0)
            reason = reply.split(":", 1)[1].strip() if ":" in reply else "No reason provided."
            response = f"{'✅' if accepted else '❌'} {emp['name']} {'accepted' if accepted else 'declined'} — {reason} (Score: {score:.2f})"
            responses.append(response)
            if accepted:
                assigned.append(emp)
            logger.debug(f"Evaluated {emp['name']} for '{task}': {reply}")
        except Exception as e:
            error_msg = f"❌ {emp['name']} — Error: {str(e)}"
            responses.append(error_msg)
            logger.error(f"Error evaluating {emp['name']} for '{task}': {e}")

    if not assigned:
        logger.warning(f"No employees assigned to '{task}'")
        responses.append("⚠️ No suitable employees found.")
    return assigned, responses

def assign_subtasks_to_employees(
    sub_tasks: List[Dict[str, str]],
    assigned_employees: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """
    Assign sub-tasks to employees in a round-robin fashion.

    Args:
        sub_tasks: List of sub-task dictionaries.
        assigned_employees: List of assigned employee dictionaries.

    Returns:
        Updated sub-tasks with 'assigned' field.
    """
    if not sub_tasks or not assigned_employees:
        logger.debug("No sub-tasks or employees to assign.")
        return sub_tasks if sub_tasks else []

    employee_names = [emp["name"] for emp in assigned_employees]
    updated_sub_tasks = [
        {**subtask, "assigned": employee_names[i % len(employee_names)]}
        for i, subtask in enumerate(sub_tasks)
    ]
    logger.debug(f"Assigned {len(sub_tasks)} sub-tasks to {len(assigned_employees)} employees")
    return updated_sub_tasks