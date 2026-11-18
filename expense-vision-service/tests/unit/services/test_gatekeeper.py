from unittest.mock import patch

from services.gatekeeper import is_valid_financial_image
from tests.helper import resource_utils


def test_is_valid_financial_image_with_invalid_image():
    """
    Test that a non-financial document image is rejected.
    """
    image_bytes = resource_utils.read_as_bytes("images/invalid_financial_image.png")

    result = is_valid_financial_image(image_bytes)

    assert result is False


def test_is_valid_financial_image_with_valid_image():
    """
    Test that a valid financial document image is accepted.
    """
    image_bytes = resource_utils.read_as_bytes("images/valid_financial_image.png")

    result = is_valid_financial_image(image_bytes)

    assert result is True


def test_is_valid_financial_image_with_corrupt_bytes():
    """
    Test that corrupted or non-image byte buffers fail decoding gracefully.
    """
    corrupt_bytes = b"not_a_valid_image_buffer"

    result = is_valid_financial_image(corrupt_bytes)

    assert result is False


def test_is_valid_financial_image_when_ocr_fails():
    """
    Test that OCR processing failures are caught and handled gracefully.
    """
    image_bytes = resource_utils.read_as_bytes("images/valid_financial_image.png")

    with patch(
        "services.gatekeeper.pytesseract.image_to_string",
        side_effect=Exception("OCR engine unavailable"),
    ):
        result = is_valid_financial_image(image_bytes)

    assert result is False


def test_is_valid_financial_image_with_invalid_type():
    """
    Test that invalid input types are caught by the top-level exception handler.
    """
    result = is_valid_financial_image(None)

    assert result is False
