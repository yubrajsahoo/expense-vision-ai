from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient

from exceptions.custom_exceptions import ExtractionError, InvalidImageError
from main import create_app
from router.v1.expense import expense, expense_router
from schemas.schemas import ExpenseData
from tests.helper import mock_helper


@pytest.fixture
def client():
    """Create a test client with application routes and exception handlers."""
    application = create_app()
    return TestClient(application, raise_server_exceptions=False)


def test_expense_router_configuration():
    """Verify route path, method, response model, and tags for expense endpoint."""
    routes = [r for r in expense_router.routes if hasattr(r, "path")]
    assert len(routes) == 1
    route = routes[0]
    assert route.path == "/expense"
    assert "POST" in route.methods
    assert "expense" in route.tags
    assert route.response_model is ExpenseData


@pytest.mark.anyio
async def test_expense_endpoint_function_direct_call():
    """Verify direct call to expense endpoint awaits extract_expense_data."""
    mock_upload = MagicMock(spec=UploadFile)
    expected_result = ExpenseData(
        is_financial=True,
        merchant_name="Starbucks",
        amount=450.0,
        date="2026-11-18",
        payment_method="Card",
        utr_number="UTR123",
    )

    with mock_helper.mock_method(
        "services.expense.extract_expense_data",
        side_effect=AsyncMock(return_value=expected_result),
    ) as mock_extract:
        result = await expense(image=mock_upload)

    mock_extract.assert_awaited_once_with(mock_upload)
    assert result == expected_result


def test_post_expense_success(client):
    """Verify POST /api/v1/expense returns 200 and structured ExpenseData."""
    expected_data = ExpenseData(
        is_financial=True,
        merchant_name="Cafe Day",
        amount=120.0,
        date="2026-11-18",
        payment_method="UPI",
        utr_number="123456789012",
    )

    with mock_helper.mock_method(
        "services.expense.extract_expense_data",
        side_effect=AsyncMock(return_value=expected_data),
    ):
        response = client.post(
            "/api/v1/expense",
            files={"image": ("receipt.png", b"fake_png_data", "image/png")},
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == expected_data.model_dump()


def test_post_expense_non_financial(client):
    """Verify POST /api/v1/expense returns 200 with is_financial=False."""
    expected_data = ExpenseData(is_financial=False)

    with mock_helper.mock_method(
        "services.expense.extract_expense_data",
        side_effect=AsyncMock(return_value=expected_data),
    ):
        response = client.post(
            "/api/v1/expense",
            files={"image": ("landscape.jpg", b"fake_jpg_data", "image/jpeg")},
        )

    assert response.status_code == 200
    assert response.json() == expected_data.model_dump()


def test_post_expense_missing_image_file_returns_422(client):
    """Verify POST /api/v1/expense without file returns 422 Unprocessable Entity."""
    response = client.post("/api/v1/expense")
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any(err["loc"] == ["body", "image"] for err in data["detail"])


def test_post_expense_invalid_image_error_returns_400(client):
    """Verify InvalidImageError converts to 400 Bad Request via handler."""
    with mock_helper.mock_method(
        "services.expense.extract_expense_data",
        side_effect=AsyncMock(
            side_effect=InvalidImageError("Unsupported content type application/pdf")
        ),
    ):
        response = client.post(
            "/api/v1/expense",
            files={"image": ("doc.pdf", b"pdf_data", "application/pdf")},
        )

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "error": "InvalidImageError",
        "message": "Unsupported content type application/pdf",
        "path": "/api/v1/expense",
    }


def test_post_expense_extraction_error_returns_502(client):
    """Verify ExtractionError converts to 502 Bad Gateway via app exception handler."""
    with mock_helper.mock_method(
        "services.expense.extract_expense_data",
        side_effect=AsyncMock(
            side_effect=ExtractionError("Empty Response getting from AI")
        ),
    ):
        response = client.post(
            "/api/v1/expense",
            files={"image": ("receipt.png", b"png_data", "image/png")},
        )

    assert response.status_code == 502
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "error": "ExtractionError",
        "message": "Empty Response getting from AI",
        "path": "/api/v1/expense",
    }


def test_post_expense_unhandled_exception_returns_500(client):
    """Verify unexpected exception converts to 500 Internal Server Error."""
    with mock_helper.mock_method(
        "services.expense.extract_expense_data",
        side_effect=AsyncMock(side_effect=RuntimeError("Unexpected server crash")),
    ):
        response = client.post(
            "/api/v1/expense",
            files={"image": ("receipt.png", b"png_data", "image/png")},
        )

    assert response.status_code == 500
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "error": "InternalServerError",
        "message": "An unexpected error occurred.",
        "path": "/api/v1/expense",
    }
