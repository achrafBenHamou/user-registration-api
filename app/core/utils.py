import logging
import tomllib

from pathlib import Path

logger = logging.getLogger(__name__)


def _get_poetry_tool_element(element: str, default_element_value: str = "") -> str:
    """
    Helper function to read elements from the [tool.poetry] section of pyproject.toml.

    Args:
        element (str): The specific element to retrieve (e.g., "description", "version").
        default_element_value (str): The value to return if the element is not found or
            an error occurs. Defaults to an empty string.

    Returns:
        str: The value of the specified element from pyproject.toml, or the default value
            if not found. Logs a warning if the element is not found in pyproject.toml.
            Handles exceptions gracefully and returns the default value in case of errors.
    """
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            poetry_tool_data = pyproject_data.get("tool", {}).get("poetry", {})
            element = poetry_tool_data.get(element)
            if not element:
                logger.warning(
                    f"'{element}' element not found in 'pyproject.toml' - returning default value"
                )
                return default_element_value
            return element
    except Exception as e:
        logger.warning(
            f"Error reading 'pyproject.toml': {e} - returning default value for '{element}'"
        )
        return default_element_value
