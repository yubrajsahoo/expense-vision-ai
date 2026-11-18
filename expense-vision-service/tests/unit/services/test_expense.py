import io
import logging

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from config.config import settings
from exceptions.custom_exceptions import ExtractionError, InvalidImageError
from schemas.schemas import ExpenseData
from services.expense import _ALLOWED_CONTENT_TYPES, extract_expense_data
from tests.helper import mock_helper


def _create_mock_upload_file(
    content: bytes = b"dummy_image_data",
    content_type: str | None = "image/png",
    filename: str = "receipt.png",
) -> UploadFile:
    """Create an UploadFile instance for testing."""
    headers = Headers({"content-type": content_type}) if content_type else Headers()
    file_obj = io.BytesIO(content)
    return UploadFile(
        file=file_obj,
        filename=filename,
        headers=headers,
    )


def test_allowed_content_types_constant():
    """Verify the exact allowed MIME types for image uploads."""
    assert _ALLOWED_CONTENT_TYPES == {
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp",
    }


@pytest.mark.anyio
@pytest.mark.parametrize(
    "unsupported_type",
    ["application/pdf", "text/plain", "image/gif", "image/bmp", None],
)
async def test_extract_expense_data_unsupported_content_type(unsupported_type, caplog):
    """Verify InvalidImageError is raised for unsupported content types with logging."""
    upload_file = _create_mock_upload_file(
        content=b"some1 bytes", content_type=unsupported_type
    )

    with caplog.at_level(logging.INFO):
        with pytest.raises(InvalidImageError) as exc_info:
            await extract_expense_data(upload_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.message == f"Unsupported content type {unsupported_type}"
    assert f"Unsupported content type {unsupported_type}" in caplog.text


@pytest.mark.anyio
async def test_extract_expense_data_empty_file():
    """Verify InvalidImageError is raised when uploaded file has 0 bytes."""
    upload_file = _create_mock_upload_file(content=b"", content_type="image/png")

    with pytest.raises(InvalidImageError) as exc_info:
        await extract_expense_data(upload_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.message == "Uploaded file is empty."


@pytest.mark.anyio
async def test_extract_expense_data_exceeds_max_file_size():
    """Verify InvalidImageError is raised when file size exceeds maximum limit."""
    oversized_content = b"x" * (settings.max_file_size_bytes + 1)
    upload_file = _create_mock_upload_file(
        content=oversized_content, content_type="image/png"
    )

    with pytest.raises(InvalidImageError) as exc_info:
        await extract_expense_data(upload_file)

    assert exc_info.value.status_code == 400
    assert "File size exceeds maximum limit" in exc_info.value.message


@pytest.mark.anyio
async def test_extract_expense_data_rejected_by_gatekeeper():
    """Verify non-financial image returns ExpenseData(is_financial=False)."""
    upload_file = _create_mock_upload_file(
        content=b"scenery_photo_bytes", content_type="image/jpeg"
    )

    with mock_helper.mock_method(
        "services.expense.is_valid_financial_image", return_value=False
    ) as mock_gatekeeper:
        with mock_helper.mock_method(
            "services.expense.extractor.extract_expense_data"
        ) as mock_extractor:
            result = await extract_expense_data(upload_file)

    mock_gatekeeper.assert_called_once_with(b"scenery_photo_bytes")
    mock_extractor.assert_not_called()
    assert isinstance(result, ExpenseData)
    assert result.is_financial is False
    assert result.merchant_name is None
    assert result.amount is None
    assert result.date is None
    assert result.payment_method is None
    assert result.utr_number is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mime_type", ["image/png", "image/jpeg", "image/jpg", "image/webp"]
)
async def test_extract_expense_data_valid_financial_success(mime_type):
    """Verify valid financial image calls extractor and returns ExpenseData."""
    raw_bytes = b"real_financial_receipt_bytes"
    upload_file = _create_mock_upload_file(content=raw_bytes, content_type=mime_type)
    expected_data = ExpenseData(
        is_financial=True,
        merchant_name="Walmart",
        amount=84.50,
        date="2026-11-18",
        payment_method="UPI",
        utr_number="UTR11223344",
    )

    with mock_helper.mock_method(
        "services.expense.is_valid_financial_image", return_value=True
    ) as mock_gatekeeper:
        with mock_helper.mock_method(
            "services.expense.extractor.extract_expense_data",
            return_value=expected_data,
        ) as mock_extractor:
            result = await extract_expense_data(upload_file)

    mock_gatekeeper.assert_called_once_with(raw_bytes)
    mock_extractor.assert_called_once_with(raw_bytes, mime_type)
    assert result == expected_data


@pytest.mark.anyio
async def test_extract_expense_data_propagates_extraction_error():
    """Verify ExtractionError from extractor is re-raised directly."""
    raw_bytes = b"receipt_bytes"
    upload_file = _create_mock_upload_file(content=raw_bytes, content_type="image/png")
    origin_error = ExtractionError("Empty Response getting from AI")

    with mock_helper.mock_method(
        "services.expense.is_valid_financial_image", return_value=True
    ):
        with mock_helper.mock_method(
            "services.expense.extractor.extract_expense_data",
            exception=origin_error,
        ):
            with pytest.raises(ExtractionError) as exc_info:
                await extract_expense_data(upload_file)

    assert exc_info.value is origin_error
    assert exc_info.value.status_code == 502
    assert exc_info.value.message == "Empty Response getting from AI"


@pytest.mark.anyio
async def test_extract_expense_data_wraps_unexpected_exception(caplog):
    """Verify unexpected exceptions are wrapped in ExtractionError."""
    raw_bytes = b"receipt_bytes"
    upload_file = _create_mock_upload_file(content=raw_bytes, content_type="image/png")
    unexpected_error = RuntimeError("Google Gemini API socket crash")

    with caplog.at_level(logging.ERROR):
        with mock_helper.mock_method(
            "services.expense.is_valid_financial_image", return_value=True
        ):
            with mock_helper.mock_method(
                "services.expense.extractor.extract_expense_data",
                exception=unexpected_error,
            ):
                with pytest.raises(ExtractionError) as exc_info:
                    await extract_expense_data(upload_file)

    assert exc_info.value.status_code == 502
    assert exc_info.value.message == "Unable to extract expense data"
    assert exc_info.value.__cause__ is unexpected_error
    expected_log = "Failed to extract expense data: Google Gemini API socket crash"
    assert expected_log in caplog.text
