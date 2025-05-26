# src/core/navigation.py
"""
Navigation and history management for the Task Manager application.
Handles step progression, undo/redo, and UI navigation elements.
"""

import streamlit as st
from src.core.state_management import save_persistent_state
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)

# Constants
STEPS = [
    "CEO Input",
    "Technical Spec",
    "Task Planning",
    "Task Assignment",
    "Sub-tasks",
    "Project Report",
]

def go_to_next_step() -> None:
    """Move to the next step and save history."""
    save_state_to_history()
    st.session_state.current_step = min(st.session_state.current_step + 1, len(STEPS))
    save_persistent_state()
    logger.debug(f"Navigated to step {st.session_state.current_step}")

def go_to_previous_step() -> None:
    """Move to the previous step if possible and save history."""
    if st.session_state.get("current_step", 1) > 1:
        save_state_to_history()
        st.session_state.current_step -= 1
        save_persistent_state()
        logger.debug(f"Navigated to step {st.session_state.current_step}")

def reset_to_step(step: int) -> None:
    """Reset to a specific step and save history."""
    if 1 <= step <= len(STEPS):
        save_state_to_history()
        st.session_state.current_step = step
        save_persistent_state()
        logger.debug(f"Reset to step {step}")
    else:
        logger.warning(f"Invalid step reset attempted: {step}")

def save_state_to_history() -> None:
    """Save the current session state to history."""
    try:
        state = {
            "current_step": st.session_state.get("current_step", 1),
            "output": deepcopy(st.session_state.get("output")),
            "task_board": deepcopy(st.session_state.get("task_board", [])),
            "sub_tasks": deepcopy(st.session_state.get("sub_tasks", {})),
            "ceo_input": st.session_state.get("ceo_input", ""),
            "scrum_master_approval": st.session_state.get("scrum_master_approval", False),
        }
        history = st.session_state.get("history", [])
        history_index = st.session_state.get("history_index", -1)

        # Truncate future history if inserting in the middle
        if history_index < len(history) - 1:
            st.session_state.history = history[:history_index + 1]
        st.session_state.history.append(state)
        st.session_state.history_index = history_index + 1
        logger.debug(f"Saved state to history at index {st.session_state.history_index}")
    except Exception as e:
        logger.error(f"Failed to save state to history: {e}")

def undo() -> None:
    """Undo the last action if possible."""
    history_index = st.session_state.get("history_index", -1)
    if history_index > 0:
        st.session_state.history_index -= 1
        restore_state()
        logger.debug(f"Undo to history index {st.session_state.history_index}")

def redo() -> None:
    """Redo the last undone action if possible."""
    history = st.session_state.get("history", [])
    history_index = st.session_state.get("history_index", -1)
    if history_index < len(history) - 1:
        st.session_state.history_index += 1
        restore_state()
        logger.debug(f"Redo to history index {st.session_state.history_index}")

def restore_state() -> None:
    """Restore session state from the current history index."""
    try:
        history = st.session_state.get("history", [])
        history_index = st.session_state.get("history_index", -1)
        if 0 <= history_index < len(history):
            state = history[history_index]
            for key, value in state.items():
                st.session_state[key] = value
            save_persistent_state()
            logger.debug(f"Restored state from history index {history_index}")
    except Exception as e:
        logger.error(f"Failed to restore state: {e}")

def create_progress_bar() -> None:
    """Render a progress bar showing the current step."""
    cols = st.columns(len(STEPS))
    current_step = st.session_state.get("current_step", 1)
    for i, (col, step) in enumerate(zip(cols, STEPS)):
        with col:
            icon = "✅" if i < current_step - 1 else "🔵" if i == current_step - 1 else "⚪"
            st.markdown(f"{icon} **{step}**")

def render_navigation_sidebar() -> None:
    """Render the navigation sidebar with step buttons and history controls."""
    with st.sidebar:
        st.subheader("Navigation")
        for i, step in enumerate(STEPS, 1):
            if st.button(f"Step {i}: {step}", help=f"Jump to {step}"):
                reset_to_step(i)
        
        st.subheader("History")
        col1, col2 = st.columns(2)
        with col1:
            st.button(
                "Undo",
                on_click=undo,
                disabled=st.session_state.get("history_index", -1) <= 0,
                help="Revert to previous state",
            )
        with col2:
            st.button(
                "Redo",
                on_click=redo,
                disabled=st.session_state.get("history_index", -1) >= len(st.session_state.get("history", [])) - 1,
                help="Reapply next state",
            )