import logging
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from exceptions.custom_exceptions import (
    AppException,
    ExtractionError,
    InvalidImageError,
)
from exceptions.handlers import register_exception_handlers


@pytest.fixture
def app_with_handlers():
    """Create a FastAPI app with registered exception handlers and test routes."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/test/app-exception")
    def trigger_app_exception():
        raise AppException("Custom app failure", status_code=418)

    @app.get("/test/invalid-image")
    def trigger_invalid_image():
        raise InvalidImageError("Image format not recognized")

    @app.get("/test/extraction-error")
    def trigger_extraction_error():
        raise ExtractionError("Gemini model timeout")

    @app.get("/test/unhandled")
    def trigger_unhandled():
        raise RuntimeError("Unexpected internal crash")

    return app


@pytest.fixture
def test_client(app_with_handlers):
    """Test client for exercising registered exception handlers."""
    return TestClient(app_with_handlers, raise_server_exceptions=False)


def test_app_exception_handled_by_test_client(test_client):
    """Verify AppException returns structured JSON response with its status code."""
    response = test_client.get("/test/app-exception")
    assert response.status_code == 418
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "error": "AppException",
        "message": "Custom app failure",
        "path": "/test/app-exception",
    }


def test_invalid_image_error_handled_by_test_client(test_client):
    """Verify InvalidImageError returns HTTP 400 with structured JSON."""
    response = test_client.get("/test/invalid-image")
    assert response.status_code == 400
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "error": "InvalidImageError",
        "message": "Image format not recognized",
        "path": "/test/invalid-image",
    }


def test_extraction_error_handled_by_test_client(test_client):
    """Verify ExtractionError returns HTTP 502 with structured JSON."""
    response = test_client.get("/test/extraction-error")
    assert response.status_code == 502
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "error": "ExtractionError",
        "message": "Gemini model timeout",
        "path": "/test/extraction-error",
    }


def test_unhandled_exception_handled_by_test_client(test_client):
    """Verify unhandled Exception returns HTTP 500 with generic InternalServerError."""
    response = test_client.get("/test/unhandled")
    assert response.status_code == 500
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "error": "InternalServerError",
        "message": "An unexpected error occurred.",
        "path": "/test/unhandled",
    }


@pytest.mark.anyio
async def test_app_exception_handler_function_directly(caplog):
    """Verify invocation of app_exception_handler logs warning and formats JSON."""
    app = FastAPI()
    register_exception_handlers(app)
    handler = app.exception_handlers[AppException]

    mock_request = MagicMock()
    mock_request.url.path = "/custom/endpoint"
    exc = InvalidImageError("Invalid byte stream")

    with caplog.at_level(logging.WARNING):
        response = await handler(mock_request, exc)

    assert response.status_code == 400
    import json

    body = json.loads(response.body.decode("utf-8"))
    assert body == {
        "error": "InvalidImageError",
        "message": "Invalid byte stream",
        "path": "/custom/endpoint",
    }
    assert "AppException on /custom/endpoint: [400] Invalid byte stream" in caplog.text


@pytest.mark.anyio
async def test_unhandled_exception_handler_function_directly(caplog):
    """Verify unhandled_exception_handler logs error and formats JSON."""
    app = FastAPI()
    register_exception_handlers(app)
    handler = app.exception_handlers[Exception]

    mock_request = MagicMock()
    mock_request.url.path = "/crash/endpoint"
    exc = ZeroDivisionError("division by zero")

    with caplog.at_level(logging.ERROR):
        response = await handler(mock_request, exc)

    assert response.status_code == 500
    import json

    body = json.loads(response.body.decode("utf-8"))
    assert body == {
        "error": "InternalServerError",
        "message": "An unexpected error occurred.",
        "path": "/crash/endpoint",
    }
    assert "Unhandled error on /crash/endpoint: division by zero" in caplog.text
