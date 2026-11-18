"""Gatekeeper service for local financial image validation.

Performs fast, local OCR validation using OpenCV and Tesseract to verify
that an uploaded image contains financial keywords before forwarding it
to the Gemini API for extraction.
"""

import logging
import re

import cv2
import numpy as np
import pytesseract

_logger = logging.getLogger(__name__)

# Match ₹ anywhere, or financial keywords only as whole words
_FINANCIAL_PATTERN = re.compile(
    r"₹|\b(?:rs|inr|upi|total|amount|paid|sent|transaction)\b"
)

# Extracted text config code
_EXTRACT_TEXT_CONFIG_CODE = "--psm 11"


def is_valid_financial_image(image_bytes: bytes) -> bool:
    """Validate whether the provided image bytes represent a valid financial document.

    Decodes the image bytes, converts to grayscale, and runs OCR to detect
    financial keywords (e.g., ₹, rs, inr, upi, total, amount, paid, sent, transaction).

    :param image_bytes: Raw bytes of the image to validate.
    :return: True if financial keywords are found, False otherwise.
    """
    try:
        np_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        if image is None:
            _logger.warning("Failed to decode image bytes into a valid image.")
            return False

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        extracted_text = (
            pytesseract.image_to_string(gray_image, config=_EXTRACT_TEXT_CONFIG_CODE)
            .strip()
            .lower()
        )

        _logger.debug(f"Extracted text from image is: {extracted_text}")

        is_valid = bool(_FINANCIAL_PATTERN.search(extracted_text))

        if not is_valid:
            _logger.info("Gatekeeper: Rejected image. No financial keywords found.")

        return is_valid

    except Exception as e:
        _logger.error(f"Error validating financial image: {e}")
        return False
