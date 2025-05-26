# src/utils/utils.py
"""
Utility functions for the Task Manager application.
Provides JSON parsing, retry logic, and duration parsing.
"""

import json
import re
import logging
from typing import Any, Optional, Union
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import litellm
from src.config import MAX_RETRIES, MIN_WAIT, MAX_WAIT

logger = logging.getLogger(__name__)

def parse_json_output(raw_output: str) -> Optional[dict]:
    """
    Parse raw string output into a JSON dictionary.

    Args:
        raw_output: Raw string output from an LLM or other source.

    Returns:
        Parsed JSON dictionary, or None if parsing fails.
    """
    if not raw_output or raw_output.isspace():
        logger.error("Empty or whitespace-only output provided")
        return None

    try:
        # Extract JSON substring if embedded in text
        json_start = raw_output.find("{")
        json_end = raw_output.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = raw_output[json_start:json_end]
        else:
            json_str = raw_output.strip()

        result = json.loads(json_str)
        if not isinstance(result, dict):
            logger.warning(f"Parsed output is not a dictionary: {json_str[:100]}...")
            return None
        logger.debug(f"Successfully parsed JSON: {json_str[:100]}...")
        return result
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse JSON: {e} - Input: {raw_output[:100]}...")
        return None

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=MIN_WAIT, max=MAX_WAIT),
    retry=retry_if_exception_type((litellm.RateLimitError, litellm.APIError)),
    before_sleep=before_sleep_log(logger, logging.DEBUG)
)
def call_with_retry(crew: Any, retry_after: Optional[float] = None) -> Any:
    """
    Execute a crew operation with retries on specific exceptions.

    Args:
        crew: Crew object to execute.
        retry_after: Optional delay (seconds) before execution.

    Returns:
        Result of crew.kickoff().

    Raises:
        Exception: If all retries fail.
    """
    if retry_after is not None and retry_after > 0:
        logger.debug(f"Delaying execution by {retry_after} seconds")
        time.sleep(retry_after)
    return crew.kickoff()

def parse_duration(duration_input: Union[str, int, float, dict]) -> Optional[float]:
    """
    Parse various duration formats into a float representing hours.

    Args:
        duration_input: Duration as a number, string (e.g., "40-80h"), or dict (e.g., {"lower": 20, "upper": 40}).

    Returns:
        Float duration in hours, or None if parsing fails.
    """
    if isinstance(duration_input, (int, float)):
        return float(duration_input) if duration_input >= 0 else None

    if isinstance(duration_input, dict):
        # Handle {"lower": X, "upper": Y} or {"lower_bound": X, "upper_bound": Y}
        lower = duration_input.get("lower") or duration_input.get("lower_bound")
        upper = duration_input.get("upper") or duration_input.get("upper_bound")
        if lower is not None and upper is not None:
            try:
                return (float(lower) + float(upper)) / 2
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse dict bounds '{duration_input}': {e}")
                return None

        # Handle {"min": X, "max": Y}
        min_val = duration_input.get("min")
        max_val = duration_input.get("max")
        if min_val is not None and max_val is not None:
            try:
                return (float(min_val) + float(max_val)) / 2
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse min/max bounds '{duration_input}': {e}")
                return None

        # Handle {"total": "X-Yh"}
        total = duration_input.get("total")
        if total:
            return parse_duration(total)

        # Handle {"breakdown": {"key": "X-Yh", ...}}
        breakdown = duration_input.get("breakdown")
        if breakdown and isinstance(breakdown, dict):
            durations = [parse_duration(v) for v in breakdown.values() if v is not None]
            valid_durations = [d for d in durations if d is not None]
            return sum(valid_durations) if valid_durations else None

        # Sum nested dicts like {"API Development": {"lower": X, "upper": Y}, ...}
        durations = [parse_duration(v) for v in duration_input.values() if isinstance(v, dict)]
        valid_durations = [d for d in durations if d is not None]
        return sum(valid_durations) if valid_durations else None

    if isinstance(duration_input, str):
        # Remove units (e.g., 'hours', 'hrs', 'h') and normalize
        duration_str = re.sub(r'\s*(hours|hrs|h)\s*', '', duration_input, flags=re.IGNORECASE).strip()
        # Handle range (e.g., '40-80')
        if '-' in duration_str:
            try:
                low, high = map(float, duration_str.split('-'))
                return (low + high) / 2 if low >= 0 and high >= 0 else None
            except ValueError:
                logger.warning(f"Failed to parse range '{duration_str}'")
                return None
        # Handle single value (e.g., '50')
        try:
            value = float(duration_str)
            return value if value >= 0 else None
        except ValueError:
            logger.warning(f"Failed to parse single value '{duration_str}'")
            return None

    logger.warning(f"Unsupported duration format: {duration_input}")
    return None