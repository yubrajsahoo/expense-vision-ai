"""Application configuration loaded from environment variables and .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings model managing environment variables and defaults.

    :cvar gemini_api_key: API key used for Google Gemini AI model requests.
    :cvar host: Host interface binding for the web server (default: '0.0.0.0').
    :cvar port: Port number for the web server (default: 8000).
    :cvar reload: Whether auto-reload is enabled during development (default: True).
    """

    # API Keys
    gemini_api_key: str

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # Looks for a .env file in the root directory
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instantiate the settings so they can be imported across the app
settings = Settings()
