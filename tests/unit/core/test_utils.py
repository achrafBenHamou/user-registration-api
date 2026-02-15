import pytest
from unittest.mock import patch, mock_open
import builtins

from app.core.utils import _get_poetry_tool_element

# ----------------------------
# SUCCESS CASE
# ----------------------------


def test_get_poetry_element_success():
    toml_content = b"""
[tool.poetry]
name = "my-app"
version = "1.2.3"
"""

    with patch.object(builtins, "open", mock_open(read_data=toml_content)), patch(
        "app.core.utils.tomllib.load"
    ) as mock_load:

        mock_load.return_value = {
            "tool": {
                "poetry": {
                    "name": "my-app",
                    "version": "1.2.3",
                }
            }
        }

        result = _get_poetry_tool_element("name")

        assert result == "my-app"


# ----------------------------
# ELEMENT NOT FOUND
# ----------------------------


def test_get_poetry_element_missing_logs_warning(caplog):
    caplog.set_level("WARNING")

    with patch("app.core.utils.tomllib.load") as mock_load:
        mock_load.return_value = {"tool": {"poetry": {}}}

        result = _get_poetry_tool_element("description", "default-value")

        assert result == "default-value"
        assert "not found" in caplog.text


# ----------------------------
# tool.poetry SECTION MISSING
# ----------------------------


def test_get_poetry_element_no_poetry_section():
    with patch("app.core.utils.tomllib.load") as mock_load:
        mock_load.return_value = {"tool": {}}

        result = _get_poetry_tool_element("name", "fallback")

        assert result == "fallback"


# ----------------------------
# FILE READ ERROR
# ----------------------------


def test_get_poetry_element_file_error(caplog):
    caplog.set_level("WARNING")

    with patch("app.core.utils.open", side_effect=Exception("File error")):
        result = _get_poetry_tool_element("name", "fallback")

        assert result == "fallback"
        assert "Error reading" in caplog.text
