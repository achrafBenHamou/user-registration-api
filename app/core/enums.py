"""
This module defines enumerations used throughout application.
"""

from enum import Enum


class Environment(str, Enum):
    """Enumeration of supported environments."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
