import runpy
from unittest.mock import patch

from fastapi import FastAPI

import main
from config.config import settings
from main import create_app


def test_create_app():
    """Verify application metadata, configuration, and registered routes."""
    application = create_app()

    assert isinstance(application, FastAPI)
    assert application.title == "Expense Vision Service"
    assert (
        application.description
        == "AI worker for processing receipts and UPI screenshots"
    )
    assert application.version == "0.1.0"

    # Verify registered openapi routes include actuator endpoints
    openapi_schema = application.openapi()
    assert "/actuators/health" in openapi_schema["paths"]

    # Verify documentation routes
    doc_paths = [route.path for route in application.routes if hasattr(route, "path")]
    assert "/docs" in doc_paths
    assert "/openapi.json" in doc_paths


def test_app_instance():
    """Verify default global app instance is created properly."""
    assert isinstance(main.app, FastAPI)
    assert main.app.title == "Expense Vision Service"


def test_main_execution():
    """Verify that running as a script invokes uvicorn.run with expected settings."""
    with patch("uvicorn.run") as mock_run:
        runpy.run_module("main", run_name="__main__")
        mock_run.assert_called_once_with(
            "src.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
        )
