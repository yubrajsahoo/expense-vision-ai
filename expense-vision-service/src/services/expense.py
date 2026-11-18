"""Expense orchestration service for validating images and coordinating extraction.

Handles MIME type validation, file read operations, invokes local OCR Gatekeeper
checks, and forwards verified financial images to the Gemini extractor.
"""

import logging

from fastapi import File, UploadFile

from exceptions.custom_exceptions import ExtractionError, InvalidImageError
from schemas.schemas import ExpenseData
from services import extractor
from services.gatekeeper import is_valid_financial_image

_logger = logging.getLogger(__name__)

_ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
}


async def extract_expense_data(file: UploadFile = File(...)) -> ExpenseData:
    """Validate uploaded image, run Gatekeeper OCR, and extract ExpenseData.

    Validates that the file has an allowed image MIME type and non-empty content.
    If the Gatekeeper detects no financial keywords, returns non-financial ExpenseData
    without calling the AI model. Otherwise, calls Gemini to extract structured fields.

    :param file: The uploaded FastAPI UploadFile instance.
    :return: Extracted structured ExpenseData model.
    :raises InvalidImageError: If the content type is unsupported or the file is empty.
    :raises ExtractionError: If extraction fails or an AI error occurs.
    """
    content_type = file.content_type

    if content_type not in _ALLOWED_CONTENT_TYPES:
        _logger.info("Unsupported content type %s", content_type)
        raise InvalidImageError(f"Unsupported content type {content_type}")

    image_bytes = await file.read()

    if not image_bytes:
        raise InvalidImageError("Uploaded file is empty.")

    if not is_valid_financial_image(image_bytes):
        return ExpenseData(
            is_financial=False,
        )

    try:
        return extractor.extract_expense_data(image_bytes, str(content_type))

    except ExtractionError as e:
        raise e
    except Exception as e:
        _logger.error("Failed to extract expense data: %s", e)
        raise ExtractionError("Unable to extract expense data") from e
