# src/core/state_management.py
"""
Session state management for the Task Manager application.
Handles initialization, persistence, and session ID generation.
"""

import streamlit as st
import json
import os
import uuid
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def get_session_id() -> str:
    """
    Get or generate a unique session ID from query parameters.

    Returns:
        Session ID as a string.
    """
    query_params = st.query_params
    if "session_id" not in query_params:
        session_id = str(uuid.uuid4())
        st.query_params["session_id"] = session_id
        logger.debug(f"Generated new session ID: {session_id}")
    return query_params["session_id"]

def get_storage_path() -> str:
    """
    Get the file path for persistent session storage.

    Returns:
        File path as a string.
    """
    session_dir = os.getenv("SESSION_DIR", "session_data")
    os.makedirs(session_dir, exist_ok=True)
    session_id = get_session_id()
    path = os.path.join(session_dir, f"session_{session_id}.json")
    return path

def load_persistent_state() -> Optional[Dict[str, Any]]:
    """
    Load persistent state from disk.

    Returns:
        Dictionary of session state if loaded, None otherwise.
    """
    file_path = get_storage_path()
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
            logger.info(f"Loaded persistent state for session {get_session_id()} from {file_path}")
            return data
        logger.debug(f"No persistent state found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load state from {file_path}: {e}")
        return None

def save_persistent_state() -> None:
    """Save the current session state to disk."""
    file_path = get_storage_path()
    try:
        state_to_save = {
            "current_step": st.session_state.get("current_step", 1),
            "output": st.session_state.get("output"),
            "task_board": st.session_state.get("task_board", []),
            "sub_tasks": st.session_state.get("sub_tasks", {}),
            "ceo_input": st.session_state.get("ceo_input", ""),
            "scrum_master_approval": st.session_state.get("scrum_master_approval", False),
            "history": st.session_state.get("history", []),
            "history_index": st.session_state.get("history_index", -1),
            "assignment_responses": st.session_state.get("assignment_responses", {}),
        }
        with open(file_path, "w") as f:
            json.dump(state_to_save, f, default=str, indent=2)
        logger.debug(f"Saved state for session {get_session_id()} to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save state to {file_path}: {e}")

def initialize_session_state() -> None:
    """Initialize or restore the session state."""
    if "initialized" not in st.session_state:
        persistent_state = load_persistent_state()
        defaults = {
            "current_step": 1,
            "output": None,
            "task_board": [],
            "sub_tasks": {},
            "ceo_input": "",
            "scrum_master_approval": False,
            "history": [],
            "history_index": -1,
            "assignment_responses": {},
        }
        
        try:
            if persistent_state:
                for key, value in defaults.items():
                    st.session_state[key] = persistent_state.get(key, value)
                st.success("Session restored successfully!", icon="✅")
                logger.info(f"Restored session {get_session_id()}")
            else:
                st.session_state.update(defaults)
                st.info("Starting a new project. Progress will be auto-saved.", icon="ℹ️")
                logger.info(f"Initialized new session {get_session_id()}")
            st.session_state.initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize session state: {e}")
            st.session_state.update(defaults)  # Fallback to defaults
            st.warning("Failed to load session, starting fresh.", icon="⚠️")
            st.session_state.initialized = True