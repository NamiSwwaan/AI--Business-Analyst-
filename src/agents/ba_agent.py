# src/agents/ba_agent.py
"""
Business Analyst agent for analyzing CEO requirements and generating structured project plans.
"""

from crewai import Agent, Task, Crew
from typing import Optional
import logging
import json
from src.config.llm_config import llm
from src.utils.utils import parse_json_output, call_with_retry

logger = logging.getLogger(__name__)

def create_ba_agent() -> Agent:
    """Create a Business Analyst agent instance."""
    return Agent(
        role="Business Analyst",
        goal="Analyze CEO requirements and produce a structured technical plan with resource allocation.",
        backstory="An expert in translating high-level startup goals into actionable technical plans across tech, legal, finance, and marketing domains.",
        llm=llm,
        verbose=True,
        max_iter=15,  # Limit iterations to prevent infinite loops
    )

def run_ba_agent(ceo_input: str) -> Optional[str]:
    """
    Analyze CEO input and return a JSON string with technical specs and resources.

    Args:
        ceo_input: The CEO's project requirement.

    Returns:
        A JSON string with technical_spec, tasks, dependencies, skills, and resources, or None on failure.
    """
    if not ceo_input.strip():
        logger.error("Empty CEO input provided.")
        return None

    logger.info(f"Processing CEO requirement: '{ceo_input}'")
    ba_agent = create_ba_agent()
    task = Task(
        description=(
            f"Analyze this CEO requirement: '{ceo_input}'. "
            "Generate a JSON object with: "
            "- 'technical_spec' (string): Detailed technical overview "
            "- 'tasks' (list of strings): Specific tasks to complete "
            "- 'dependencies' (list of strings): External or internal dependencies "
            "- 'skills' (list of strings): Required skills "
            "- 'resources' (dict): Keys 'tech', 'legal', 'finance', 'marketing' with lists of needs. "
            "Return a valid JSON string."
        ),
        expected_output="A valid JSON string",
        agent=ba_agent,
    )
    crew = Crew(agents=[ba_agent], tasks=[task])

    try:
        result = call_with_retry(crew)
        raw_result = result.raw.strip()
        parsed_result = parse_json_output(raw_result)

        if not parsed_result or not all(key in parsed_result for key in ["technical_spec", "tasks", "dependencies", "skills", "resources"]):
            logger.warning(f"Invalid or incomplete JSON from LLM: {raw_result[:200]}...")
            # Fallback: Return a minimal valid structure
            fallback = {
                "technical_spec": f"Basic implementation for {ceo_input}",
                "tasks": [f"Implement {ceo_input}"],
                "dependencies": [],
                "skills": [],
                "resources": {"tech": [], "legal": [], "finance": [], "marketing": []}
            }
            raw_result = json.dumps(fallback)
            logger.info("Applied fallback JSON structure.")

        logger.info(f"BA Agent result: {raw_result[:200]}...")
        return raw_result

    except Exception as e:
        logger.error(f"Failed to process CEO input '{ceo_input}': {str(e)}")
        return None