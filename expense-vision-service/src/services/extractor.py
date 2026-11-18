"""Gemini AI extractor service for structured receipt and expense processing."""

import logging

from google import genai
from google.genai import types

from config.config import settings
from exceptions.custom_exceptions import ExtractionError
from schemas.schemas import ExpenseData

_logger = logging.getLogger(__name__)

_client = genai.Client(api_key=settings.gemini_api_key)

_EXTRACTION_PROMPT = (
    "Analyze this receipt or UPI screenshot and extract the financial data. "
    "Return the date in YYYY-MM-DD format and include the UTR number if present."
)


def extract_expense_data(image_bytes: bytes, mime_type: str) -> ExpenseData:
    """Send validated image bytes to the Gemini model and return structured ExpenseData.

    Packages the image bytes and extraction prompt into the Gemini generate_content call
    with strict JSON response schema enforcement, validating the returned payload.

    :param image_bytes: Raw bytes of the validated receipt or screenshot.
    :param mime_type: MIME type of the input image (e.g., 'image/png').
    :return: Validated ExpenseData instance populated with extracted attributes.
    :raises ExtractionError: If the Gemini API returns an empty response.
    :raises pydantic.ValidationError: If the returned JSON fails schema validation.
    """
    response = _client.models.generate_content(
        model=settings.gemini_model,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            _EXTRACTION_PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExpenseData,
        ),
    )

    _logger.debug("Gemini response: %s", response)

    if not response.text:
        _logger.error("Gemini returned an empty response.")
        raise ExtractionError("Empty Response getting from AI")

    return ExpenseData.model_validate_json(str(response.text))
