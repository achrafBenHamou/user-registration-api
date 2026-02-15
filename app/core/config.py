"""Configuration settings for the application using pydantic-settings"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.enums import Environment
from app.core.utils import _get_poetry_tool_element


class Settings(BaseSettings):
    """Application settings with environment variable support.
    All settings have default values, which can be overridden by environment variables or a .env file.
    """

    # Environment
    environment: str = Environment.LOCAL.value

    # Activation code
    activation_code_ttl_seconds: int = 60  # 1 minute

    # Application
    app_description: str = _get_poetry_tool_element(
        element="description", default_element_value="User Registration API"
    )
    app_version: str = _get_poetry_tool_element("version")

    # Security
    bcrypt_rounds: int = 12

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


settings = Settings()
