import time

import pytest
from fastapi.testclient import TestClient

from main import create_app
from tests.helper.resource_utils import read_as_bytes


@pytest.fixture
def client():
    """Create test client for full integration tests."""
    application = create_app()
    return TestClient(application, raise_server_exceptions=False)


def test_post_expense_integration_valid_financial_image(client):
    """End-to-end integration test with real valid receipt image."""
    image_bytes = read_as_bytes("images/valid_financial_image.png")

    response = None
    for attempt in range(3):
        response = client.post(
            "/api/v1/expense",
            files={"image": ("valid_financial_image.png", image_bytes, "image/png")},
        )
        if response.status_code == 200:
            break
        time.sleep(2)

    assert response is not None
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert data["is_financial"] is True
    assert data["amount"] is not None
    assert data["amount"] > 0
    assert data["merchant_name"] is not None


def test_post_expense_integration_invalid_financial_image(client):
    """End-to-end integration test with non-financial image rejected by Gatekeeper."""
    image_bytes = read_as_bytes("images/invalid_financial_image.png")

    response = client.post(
        "/api/v1/expense",
        files={"image": ("invalid_financial_image.png", image_bytes, "image/png")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert data["is_financial"] is False


def test_post_expense_integration_unsupported_content_type(client):
    """End-to-end integration test rejecting unsupported mime types with HTTP 400."""
    response = client.post(
        "/api/v1/expense",
        files={"image": ("notes.txt", b"some plain text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "error": "InvalidImageError",
        "message": "Unsupported content type text/plain",
        "path": "/api/v1/expense",
    }


def test_post_expense_integration_empty_file(client):
    """End-to-end integration test rejecting empty files with HTTP 400."""
    response = client.post(
        "/api/v1/expense",
        files={"image": ("empty.png", b"", "image/png")},
    )

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "error": "InvalidImageError",
        "message": "Uploaded file is empty.",
        "path": "/api/v1/expense",
    }


def test_post_expense_integration_missing_file_payload(client):
    """End-to-end integration test verifying 422 for missing required file."""
    response = client.post("/api/v1/expense")
    assert response.status_code == 422
