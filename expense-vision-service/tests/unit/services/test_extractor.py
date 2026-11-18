import logging

import pytest
from google import genai
from google.genai import types
from pydantic import ValidationError

from config.config import settings
from exceptions.custom_exceptions import ExtractionError
from schemas.schemas import ExpenseData
from src.services.extractor import (
    _EXTRACTION_PROMPT,
    _client,
    extract_expense_data,
)
from tests.helper import mock_helper
from tests.helper.resource_utils import read_as_bytes, read_as_json

_VALID_IMAGE_PATH = "images/valid_financial_image.png"
_INVALID_IMAGE_PATH = "images/invalid_financial_image.png"
_VALID_JSON_PATH = "json/valid_expense_response.json"
_NON_FINANCIAL_JSON_PATH = "json/non_financial_expense_response.json"


def test_module_constants_and_client_initialization():
    """Verify module-level extraction prompt and GenAI client setup."""
    expected_prompt = (
        "Analyze this receipt or UPI screenshot and extract the financial data. "
        "Return the date in YYYY-MM-DD format and include the UTR number if present."
    )
    assert _EXTRACTION_PROMPT == expected_prompt
    assert isinstance(_client, genai.Client)


def test_extract_expense_data_financial_receipt_success(caplog):
    """Verify extraction using mock_helper with exact call args and returned values."""
    image_bytes = read_as_bytes(_VALID_IMAGE_PATH)
    expected_json = read_as_json(_VALID_JSON_PATH)

    with caplog.at_level(logging.DEBUG):
        with mock_helper.mock_generate_content(
            json_path=_VALID_JSON_PATH
        ) as mock_generate:
            expense = extract_expense_data(image_bytes, "image/png")

    mock_generate.assert_called_once()
    call_args, call_kwargs = mock_generate.call_args
    assert not call_args

    assert call_kwargs["model"] == settings.gemini_model
    contents = call_kwargs["contents"]
    assert len(contents) == 2

    part = contents[0]
    assert isinstance(part, types.Part)
    assert part.inline_data.data == image_bytes
    assert part.inline_data.mime_type == "image/png"

    prompt = contents[1]
    assert prompt == _EXTRACTION_PROMPT

    config = call_kwargs["config"]
    assert isinstance(config, types.GenerateContentConfig)
    assert config.response_mime_type == "application/json"
    assert config.response_schema is ExpenseData

    assert isinstance(expense, ExpenseData)
    assert expense.is_financial is True
    assert expense.merchant_name == expected_json["merchant_name"]
    assert expense.merchant_name == "Coffee House"
    assert expense.amount == expected_json["amount"]
    assert expense.amount == 245.5
    assert expense.date == expected_json["date"]
    assert expense.date == "2026-11-18"
    assert expense.payment_method == expected_json["payment_method"]
    assert expense.payment_method == "UPI"
    assert expense.utr_number == expected_json["utr_number"]
    assert expense.utr_number == "123456789012"

    assert expense == ExpenseData(**expected_json)
    assert expense.model_dump() == expected_json

    assert "Gemini response:" in caplog.text


def test_extract_expense_data_non_financial_image_success():
    """Verify non-financial extraction and argument passing for MIME types."""
    image_bytes = read_as_bytes(_INVALID_IMAGE_PATH)
    expected_json = read_as_json(_NON_FINANCIAL_JSON_PATH)

    with mock_helper.mock_generate_content(
        json_path=_NON_FINANCIAL_JSON_PATH
    ) as mock_generate:
        expense = extract_expense_data(image_bytes, "image/jpeg")

    mock_generate.assert_called_once()
    _, call_kwargs = mock_generate.call_args
    part = call_kwargs["contents"][0]
    assert part.inline_data.data == image_bytes
    assert part.inline_data.mime_type == "image/jpeg"

    assert isinstance(expense, ExpenseData)
    assert expense.is_financial is False
    assert expense.merchant_name == "N/A"
    assert expense.amount == 0.0
    assert expense.date == "2026-11-18"
    assert expense.payment_method == "N/A"
    assert expense.utr_number == "N/A"

    assert expense == ExpenseData(**expected_json)
    assert expense.model_dump() == expected_json


def test_extract_expense_data_with_generic_mock_method():
    """Verify mocking via the generic mock_method helper with JSON fixture data."""
    image_bytes = read_as_bytes(_VALID_IMAGE_PATH)
    expected_json = read_as_json(_VALID_JSON_PATH)

    with mock_helper.mock_method(
        mock_helper.TARGET_EXTRACTOR_GENERATE_CONTENT,
        as_response=True,
        json_path=_VALID_JSON_PATH,
    ) as mock_generate:
        expense = extract_expense_data(image_bytes, "image/png")

    mock_generate.assert_called_once()
    assert expense == ExpenseData(**expected_json)


def test_extract_expense_data_uses_configured_gemini_model():
    """Verify that settings changes via mock_helper.mock_attribute are honored."""
    image_bytes = read_as_bytes(_VALID_IMAGE_PATH)
    custom_model = "custom-gemini-test-model"

    with mock_helper.mock_attribute(settings, "gemini_model", custom_model):
        with mock_helper.mock_generate_content(
            json_path=_VALID_JSON_PATH
        ) as mock_generate:
            extract_expense_data(image_bytes, "image/png")

    mock_generate.assert_called_once()
    assert mock_generate.call_args.kwargs["model"] == custom_model


def test_extract_expense_data_rejects_empty_string_response(caplog):
    """Verify ExtractionError and error logging using mock_helper empty response."""
    image_bytes = read_as_bytes(_VALID_IMAGE_PATH)

    with caplog.at_level(logging.ERROR):
        with mock_helper.mock_empty_generate_content() as mock_generate:
            with pytest.raises(
                ExtractionError, match=r"^Empty Response getting from AI$"
            ) as exc_info:
                extract_expense_data(image_bytes, "image/png")

    assert exc_info.value.status_code == 502
    assert exc_info.value.message == "Empty Response getting from AI"
    assert str(exc_info.value) == "Empty Response getting from AI"
    assert "Gemini returned an empty response." in caplog.text
    mock_generate.assert_called_once()


def test_extract_expense_data_rejects_none_response(caplog):
    """Verify ExtractionError and error logging using mock_helper None response."""
    image_bytes = read_as_bytes(_VALID_IMAGE_PATH)

    with caplog.at_level(logging.ERROR):
        with mock_helper.mock_none_generate_content() as mock_generate:
            with pytest.raises(
                ExtractionError, match=r"^Empty Response getting from AI$"
            ) as exc_info:
                extract_expense_data(image_bytes, "image/png")

    assert exc_info.value.status_code == 502
    assert exc_info.value.message == "Empty Response getting from AI"
    assert str(exc_info.value) == "Empty Response getting from AI"
    assert "Gemini returned an empty response." in caplog.text
    mock_generate.assert_called_once()


def test_extract_expense_data_raises_validation_error_on_malformed_json():
    """Verify ValidationError when mock_helper supplies malformed JSON text."""
    image_bytes = read_as_bytes(_VALID_IMAGE_PATH)

    with mock_helper.mock_generate_content(
        text="{invalid_json_format"
    ) as mock_generate:
        with pytest.raises(ValidationError):
            extract_expense_data(image_bytes, "image/png")

    mock_generate.assert_called_once()


def test_extract_expense_data_raises_validation_error_on_missing_required_fields():
    """Verify ValidationError when data is missing required is_financial."""
    image_bytes = read_as_bytes(_VALID_IMAGE_PATH)
    incomplete_data = {"merchant_name": "Incomplete Store"}

    with mock_helper.mock_generate_content(data=incomplete_data) as mock_generate:
        with pytest.raises(ValidationError) as exc_info:
            extract_expense_data(image_bytes, "image/png")

    mock_generate.assert_called_once()
    missing_fields = {error["loc"][0] for error in exc_info.value.errors()}
    assert missing_fields == {"is_financial"}


def test_extract_expense_data_propagates_gemini_api_exception():
    """Verify unexpected Gemini client exceptions propagate using mock_helper."""
    image_bytes = read_as_bytes(_VALID_IMAGE_PATH)
    api_error = RuntimeError("Google GenAI service unavailable")

    with mock_helper.mock_extractor_exception(api_error) as mock_generate:
        with pytest.raises(RuntimeError, match=r"^Google GenAI service unavailable$"):
            extract_expense_data(image_bytes, "image/png")

    mock_generate.assert_called_once()
