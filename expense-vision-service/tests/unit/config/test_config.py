import pytest
from pydantic import ValidationError

from config.config import Settings, settings


def test_default_settings():
    """Test that default values are applied when optional settings are omitted."""
    test_settings = Settings(gemini_api_key="test_key", _env_file=None)
    assert test_settings.gemini_api_key == "test_key"
    assert test_settings.host == "0.0.0.0"
    assert test_settings.port == 8000
    assert test_settings.reload is True


def test_custom_settings():
    """Test that custom parameters correctly override defaults."""
    custom_settings = Settings(
        gemini_api_key="custom_api_key",
        host="127.0.0.1",
        port=9000,
        reload=False,
        _env_file=None,
    )
    assert custom_settings.gemini_api_key == "custom_api_key"
    assert custom_settings.host == "127.0.0.1"
    assert custom_settings.port == 9000
    assert custom_settings.reload is False


def test_missing_gemini_api_key_raises_validation_error(monkeypatch):
    """Test that a ValidationError is raised if gemini_api_key is not provided."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_loaded_from_environment(monkeypatch):
    """Test that settings load correctly from environment variables."""
    monkeypatch.setenv("GEMINI_API_KEY", "env_gemini_key")
    monkeypatch.setenv("HOST", "192.168.1.100")
    monkeypatch.setenv("PORT", "8888")
    monkeypatch.setenv("RELOAD", "false")

    env_settings = Settings(_env_file=None)
    assert env_settings.gemini_api_key == "env_gemini_key"
    assert env_settings.host == "192.168.1.100"
    assert env_settings.port == 8888
    assert env_settings.reload is False


def test_global_settings_instance():
    """Test that the global singleton settings instance is properly created."""
    assert isinstance(settings, Settings)
    assert isinstance(settings.host, str)
    assert isinstance(settings.port, int)
    assert isinstance(settings.reload, bool)
