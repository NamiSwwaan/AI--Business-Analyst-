# src/config/llm_config.py
"""
LLM configuration for the Task Manager application.
Sets up the language model instance used by AI agents.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from crewai import LLM
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def get_llm() -> LLM:
    """
    Create and return an LLM instance based on environment variables.

    Returns:
        Configured LLM instance.

    Raises:
        ValueError: If required LLM parameters are missing or invalid.
    """
    # Load LLM settings from .env with defaults
    api_key: Optional[str] = os.getenv("LLM_API_KEY")
    model_name: str = os.getenv("LLM_MODEL_NAME", "groq/llama-3.1-8b-instant")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", 0.7))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", 512))
    base_url: str = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")

    # Validate critical parameters
    if not api_key:
        logger.error("LLM_API_KEY is not set in .env")
        raise ValueError("LLM_API_KEY must be provided in .env")
    if not model_name.strip():
        logger.error("LLM_MODEL_NAME is empty or invalid")
        raise ValueError("LLM_MODEL_NAME must be a non-empty string")
    if temperature < 0 or temperature > 1:
        logger.warning(f"LLM_TEMPERATURE={temperature} is out of range [0, 1], defaulting to 0.7")
        temperature = 0.7
    if max_tokens <= 0:
        logger.warning(f"LLM_MAX_TOKENS={max_tokens} must be positive, defaulting to 512")
        max_tokens = 512

    try:
        llm_instance = LLM(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            base_url=base_url,
            api_key=api_key,
        )
        logger.info(f"LLM initialized: model={model_name}, temperature={temperature}, "
                    f"max_tokens={max_tokens}, base_url={base_url}")
        return llm_instance
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise

# Global LLM instance
llm = get_llm()