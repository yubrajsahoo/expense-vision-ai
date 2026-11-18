import asyncio
import io
import logging

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from exceptions.custom_exceptions import ExtractionError, InvalidImageError
from schemas.schemas import ExpenseData
from services.expense import extract_expense_data
from tests.helper.resource_utils import read_as_bytes

_logger = logging.getLogger(__name__)


@pytest.mark.anyio
async def test_extract_expense_data_integration_valid_image():
    """Integration test verifying extraction from a valid financial receipt."""
    image_bytes = read_as_bytes("images/valid_financial_image.png")

    last_error = None
    result = None
    for attempt in range(3):
        try:
            upload_file = UploadFile(
                file=io.BytesIO(image_bytes),
                filename="valid_financial_image.png",
                headers=Headers({"content-type": "image/png"}),
            )
            result = await extract_expense_data(upload_file)
            break
        except ExtractionError as e:
            last_error = e
            await asyncio.sleep(2)
    else:
        if last_error:
            raise last_error

    _logger.info("Integration extracted valid expense data: %s", result)
    assert isinstance(result, ExpenseData)
    assert result.is_financial is True
    assert result.merchant_name is not None
    assert result.amount is not None
    assert result.amount > 0


@pytest.mark.anyio
async def test_extract_expense_data_integration_invalid_image():
    """Integration test verifying Gatekeeper rejection of a non-financial image."""
    image_bytes = read_as_bytes("images/invalid_financial_image.png")
    upload_file = UploadFile(
        file=io.BytesIO(image_bytes),
        filename="invalid_financial_image.png",
        headers=Headers({"content-type": "image/png"}),
    )

    result = await extract_expense_data(upload_file)

    _logger.info("Integration extracted non-financial expense data: %s", result)
    assert isinstance(result, ExpenseData)
    assert result.is_financial is False


@pytest.mark.anyio
async def test_extract_expense_data_integration_unsupported_content_type():
    """Integration test verifying InvalidImageError on unsupported MIME type."""
    upload_file = UploadFile(
        file=io.BytesIO(b"pdf_bytes"),
        filename="report.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )

    with pytest.raises(InvalidImageError) as exc_info:
        await extract_expense_data(upload_file)

    assert exc_info.value.status_code == 400
    assert "Unsupported content type application/pdf" in exc_info.value.message


@pytest.mark.anyio
async def test_extract_expense_data_integration_empty_file():
    """Integration test verifying InvalidImageError on empty upload."""
    upload_file = UploadFile(
        file=io.BytesIO(b""),
        filename="empty.png",
        headers=Headers({"content-type": "image/png"}),
    )

    with pytest.raises(InvalidImageError) as exc_info:
        await extract_expense_data(upload_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.message == "Uploaded file is empty."
