# src/core/__init__.py
"""
Core module for the Task Manager application.
Contains the main application logic, navigation, state management, task processing, and UI components.
"""

from .app import main
from .navigation import (
    go_to_next_step,
    go_to_previous_step,
    reset_to_step,
    create_progress_bar,
    render_navigation_sidebar,
)
from .state_management import initialize_session_state, save_persistent_state
from .task_processing import (
    check_employees_for_task,
    assign_subtasks_to_employees,
)  # Remaining from task_processing.py
from .ui_components import (
    render_step_1_ceo_input,
    render_step_2_technical_spec,
    render_step_3_task_planning,
    render_step_4_task_assignment,
    render_step_5_subtasks,
    render_step_6_project_report,
)

__all__ = [
    "main",
    "go_to_next_step",
    "go_to_previous_step",
    "reset_to_step",
    "create_progress_bar",
    "render_navigation_sidebar",
    "initialize_session_state",
    "save_persistent_state",
    "check_employees_for_task",
    "assign_subtasks_to_employees",
    "render_step_1_ceo_input",
    "render_step_2_technical_spec",
    "render_step_3_task_planning",
    "render_step_4_task_assignment",
    "render_step_5_subtasks",
    "render_step_6_project_report",
]