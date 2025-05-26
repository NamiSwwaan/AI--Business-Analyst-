# src/config/config.py
"""
General configuration settings for the Task Manager application.
Defines constants and Streamlit page setup.
"""

import os
from typing import Optional
from dotenv import load_dotenv
import streamlit as st
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Constants with defaults, overridable via .env
BASE_DELAY: float = float(os.getenv("BASE_DELAY", 0.01))  # Delay between retries (seconds)
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 10))       # Max retry attempts for LLM calls
MIN_WAIT: float = float(os.getenv("MIN_WAIT", 0.083))      # Min wait time for retries (seconds)
MAX_WAIT: float = float(os.getenv("MAX_WAIT", 60))         # Max wait time for retries (seconds)
MAX_EMPLOYEES_PER_TASK: int = int(os.getenv("MAX_EMPLOYEES_PER_TASK", 4))  # Max employees per task
HOURS_PER_DAY: int = int(os.getenv("HOURS_PER_DAY", 8))    # Hours in a workday
DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true" # Debug mode toggle

def set_page_config(title: Optional[str] = None) -> None:
    """
    Configure the Streamlit page settings.

    Args:
        title: Optional custom page title; defaults to .env or "Startup Crew AI Manager".
    """
    default_title = os.getenv("PAGE_TITLE", "Startup Crew AI Manager")
    page_title = title if title is not None else default_title
    
    try:
        st.set_page_config(
            page_title=page_title,
            layout="wide",
            initial_sidebar_state="expanded" if DEBUG else "auto",
        )
        logger.info(f"Page configured: title='{page_title}', layout='wide'")
    except Exception as e:
        logger.error(f"Failed to set page config: {e}")
        st.set_page_config(page_title="Task Manager (Error)", layout="wide")  # Fallback

# Validate and log constants
try:
    assert BASE_DELAY >= 0, "BASE_DELAY must be non-negative"
    assert MAX_RETRIES > 0, "MAX_RETRIES must be positive"
    assert MIN_WAIT > 0, "MIN_WAIT must be positive"
    assert MAX_WAIT >= MIN_WAIT, "MAX_WAIT must be >= MIN_WAIT"
    assert MAX_EMPLOYEES_PER_TASK > 0, "MAX_EMPLOYEES_PER_TASK must be positive"
    assert HOURS_PER_DAY > 0, "HOURS_PER_DAY must be positive"
    logger.debug(f"Config loaded: BASE_DELAY={BASE_DELAY}, MAX_RETRIES={MAX_RETRIES}, "
                 f"MIN_WAIT={MIN_WAIT}, MAX_WAIT={MAX_WAIT}, "
                 f"MAX_EMPLOYEES_PER_TASK={MAX_EMPLOYEES_PER_TASK}, HOURS_PER_DAY={HOURS_PER_DAY}, "
                 f"DEBUG={DEBUG}")
except AssertionError as e:
    logger.error(f"Invalid configuration: {e}")
    raise