import logging

import pytest

from services.gatekeeper import (
    _EXTRACT_TEXT_CONFIG_CODE,
    _FINANCIAL_PATTERN,
    is_valid_financial_image,
)
from tests.helper import mock_helper, resource_utils


def test_gatekeeper_constants():
    """Verify Gatekeeper OCR config code and regex pattern."""
    assert _EXTRACT_TEXT_CONFIG_CODE == "--psm 11"
    expected_pattern = r"₹|\b(?:rs|inr|upi|total|amount|paid|sent|transaction)\b"
    assert _FINANCIAL_PATTERN.pattern == expected_pattern


@pytest.mark.parametrize(
    "keyword",
    [
        "₹",
        "rs",
        "inr",
        "upi",
        "total",
        "amount",
        "paid",
        "sent",
        "transaction",
        "paid ₹500 via upi",
        "Total Amount: Rs 1500",
        "sent to merchant transaction successful",
    ],
)
def test_financial_pattern_matches_keywords(keyword):
    """Verify that every expected financial keyword or phrase matches the regex."""
    assert bool(_FINANCIAL_PATTERN.search(keyword.lower())) is True


@pytest.mark.parametrize(
    "non_keyword",
    [
        "hello world",
        "paramount pictures",  # contains 'amount' as substring, not whole word
        "script writing",
        "beautiful landscape view",
    ],
)
def test_financial_pattern_rejects_non_keywords(non_keyword):
    """Verify that words without financial keywords or only substrings are rejected."""
    assert bool(_FINANCIAL_PATTERN.search(non_keyword.lower())) is False


def test_is_valid_financial_image_with_invalid_image(caplog):
    """Test that a non-financial document image is rejected and logged."""
    image_bytes = resource_utils.read_as_bytes("images/invalid_financial_image.png")

    with caplog.at_level(logging.INFO):
        result = is_valid_financial_image(image_bytes)

    assert result is False
    assert "Gatekeeper: Rejected image. No financial keywords found." in caplog.text


def test_is_valid_financial_image_with_valid_image():
    """Test that a valid financial document image is accepted."""
    image_bytes = resource_utils.read_as_bytes("images/valid_financial_image.png")

    result = is_valid_financial_image(image_bytes)

    assert result is True


def test_is_valid_financial_image_with_corrupt_bytes(caplog):
    """Test that corrupted byte buffers fail decoding gracefully with warning."""
    corrupt_bytes = b"not_a_valid_image_buffer"

    with caplog.at_level(logging.WARNING):
        result = is_valid_financial_image(corrupt_bytes)

    assert result is False
    assert "Failed to decode image bytes into a valid image." in caplog.text


def test_is_valid_financial_image_when_ocr_fails(caplog):
    """Test that OCR processing failures are caught, logged, and return False."""
    image_bytes = resource_utils.read_as_bytes("images/valid_financial_image.png")

    with caplog.at_level(logging.ERROR):
        with mock_helper.mock_method(
            "services.gatekeeper.pytesseract.image_to_string",
            exception=Exception("OCR engine unavailable"),
        ):
            result = is_valid_financial_image(image_bytes)

    assert result is False
    assert "Error validating financial image: OCR engine unavailable" in caplog.text


def test_is_valid_financial_image_with_invalid_type(caplog):
    """Test that invalid input types are caught by the top-level exception handler."""
    with caplog.at_level(logging.ERROR):
        result = is_valid_financial_image(None)

    assert result is False
    assert "Error validating financial image:" in caplog.text
