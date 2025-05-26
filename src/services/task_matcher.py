# src/services/task_matcher.py
"""
Task-employee matching service for the Task Manager application.
Computes similarity scores between tasks and employee expertise using TF-IDF.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from typing import List, Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_similarity_scores(task: str, employees: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], float]]:
    """
    Compute similarity scores between a task and employee expertise.

    Args:
        task: Task description to match against.
        employees: List of employee dictionaries with 'skills' and 'my_work' fields.

    Returns:
        List of tuples (employee, similarity_score) sorted by score descending.

    Raises:
        ValueError: If task is empty or employees list is invalid.
    """
    if not task or not task.strip():
        logger.warning("Empty task provided for similarity scoring.")
        raise ValueError("Task description cannot be empty.")
    if not employees or not isinstance(employees, list):
        logger.warning(f"Invalid employees list: {employees}")
        raise ValueError("Employees must be a non-empty list.")

    try:
        # Prefer 'skills' field if available, fall back to 'my_work'
        employee_texts = [
            " ".join(emp.get("skills", [])) if emp.get("skills") else emp.get("my_work", "")
            for emp in employees
        ]
        if not any(employee_texts):
            logger.warning("No valid expertise data (skills or my_work) found in employees.")
            return [(emp, 0.0) for emp in employees]

        texts = [task] + employee_texts
        vectorizer = TfidfVectorizer(stop_words="english").fit_transform(texts)
        task_vector = vectorizer[0:1]
        employee_vectors = vectorizer[1:]
        sim_scores = cosine_similarity(task_vector, employee_vectors).flatten()
        scores = list(zip(employees, sim_scores))

        logger.info(f"Computed similarity scores for task '{task}' across {len(employees)} employees")
        return sorted(scores, key=lambda x: x[1], reverse=True)
    except Exception as e:
        logger.error(f"Error computing similarity scores for task '{task}': {e}")
        return [(emp, 0.0) for emp in employees]

def find_best_match(task: str, employees: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], float]:
    """
    Find the employee with the highest similarity score for a task.

    Args:
        task: Task description to match against.
        employees: List of employee dictionaries with 'skills' and 'my_work' fields.

    Returns:
        Tuple of (best matching employee, similarity_score), or (None, 0.0) if no match.
    """
    try:
        scores = get_similarity_scores(task, employees)
        if not scores:
            logger.info(f"No matches found for task '{task}'")
            return None, 0.0

        best_emp, best_score = scores[0]  # First item after sorting by score descending
        logger.info(f"Best match for '{task}': {best_emp['name']} with score {best_score:.2f}")
        return best_emp, best_score
    except ValueError as e:
        logger.warning(f"Invalid input for best match: {e}")
        return None, 0.0
    except Exception as e:
        logger.error(f"Error finding best match for '{task}': {e}")
        return None, 0.0