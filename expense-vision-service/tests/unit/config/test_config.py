import logging
import sys

import pytest
from pydantic import ValidationError

from config.config import Settings, configure_logging, settings


def test_default_settings():
    """Test that default values are applied when optional settings are omitted."""
    test_settings = Settings(gemini_api_key="test_key", _env_file=None)
    assert test_settings.gemini_api_key == "test_key"
    assert test_settings.gemini_model == "gemini-3.8-flash"
    assert test_settings.host == "0.0.0.0"
    assert test_settings.port == 8000
    assert test_settings.reload is True
    assert test_settings.max_file_size_mb == 10
    assert test_settings.max_file_size_bytes == 10 * 1024 * 1024


def test_custom_settings():
    """Test that custom parameters correctly override defaults."""
    custom_settings = Settings(
        gemini_api_key="custom_api_key",
        gemini_model="gemini-1.5-pro",
        host="127.0.0.1",
        port=9000,
        reload=False,
        max_file_size_mb=25,
        _env_file=None,
    )
    assert custom_settings.gemini_api_key == "custom_api_key"
    assert custom_settings.gemini_model == "gemini-1.5-pro"
    assert custom_settings.host == "127.0.0.1"
    assert custom_settings.port == 9000
    assert custom_settings.reload is False
    assert custom_settings.max_file_size_mb == 25
    assert custom_settings.max_file_size_bytes == 25 * 1024 * 1024


def test_missing_gemini_api_key_raises_validation_error(monkeypatch):
    """Test that a ValidationError is raised if gemini_api_key is not provided."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_loaded_from_environment(monkeypatch):
    """Test that settings load correctly from environment variables."""
    monkeypatch.setenv("GEMINI_API_KEY", "env_gemini_key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-env")
    monkeypatch.setenv("HOST", "192.168.1.100")
    monkeypatch.setenv("PORT", "8888")
    monkeypatch.setenv("RELOAD", "false")
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "15")

    env_settings = Settings(_env_file=None)
    assert env_settings.gemini_api_key == "env_gemini_key"
    assert env_settings.gemini_model == "gemini-test-env"
    assert env_settings.host == "192.168.1.100"
    assert env_settings.port == 8888
    assert env_settings.reload is False
    assert env_settings.max_file_size_mb == 15
    assert env_settings.max_file_size_bytes == 15 * 1024 * 1024


def test_global_settings_instance():
    """Test that the global singleton settings instance is properly created."""
    assert isinstance(settings, Settings)
    assert isinstance(settings.gemini_api_key, str)
    assert isinstance(settings.gemini_model, str)
    assert isinstance(settings.host, str)
    assert isinstance(settings.port, int)
    assert isinstance(settings.reload, bool)
    assert isinstance(settings.max_file_size_mb, int)
    assert isinstance(settings.max_file_size_bytes, int)


def test_configure_logging_initialization():
    """Test configure_logging sets up root logger with INFO level and stream handler."""
    configure_logging()
    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO
    handlers = root_logger.handlers
    assert any(
        isinstance(h, logging.StreamHandler) and h.stream == sys.stdout
        for h in handlers
    )
