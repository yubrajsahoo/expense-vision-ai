from exceptions.custom_exceptions import (
    AppException,
    ExtractionError,
    InvalidImageError,
)


def test_app_exception_default_status_code():
    """Verify AppException stores the message and defaults to status code 500."""
    exc = AppException("Base application error")
    assert exc.message == "Base application error"
    assert exc.status_code == 500
    assert str(exc) == "Base application error"
    assert isinstance(exc, Exception)


def test_app_exception_custom_status_code():
    """Verify AppException correctly stores a custom HTTP status code."""
    exc = AppException("Service unavailable", status_code=503)
    assert exc.message == "Service unavailable"
    assert exc.status_code == 503
    assert str(exc) == "Service unavailable"


def test_invalid_image_error():
    """Verify InvalidImageError sets status code 400 and inherits from AppException."""
    exc = InvalidImageError("Unsupported file type")
    assert exc.message == "Unsupported file type"
    assert exc.status_code == 400
    assert str(exc) == "Unsupported file type"
    assert isinstance(exc, AppException)
    assert isinstance(exc, Exception)


def test_extraction_error_default_message():
    """Verify ExtractionError defaults to 502 and standard error message."""
    exc = ExtractionError()
    assert exc.message == "Unable to extract expense data."
    assert exc.status_code == 502
    assert str(exc) == "Unable to extract expense data."
    assert isinstance(exc, AppException)
    assert isinstance(exc, Exception)


def test_extraction_error_custom_message():
    """Verify ExtractionError sets status code 502 with custom message."""
    exc = ExtractionError("Gemini AI failure")
    assert exc.message == "Gemini AI failure"
    assert exc.status_code == 502
    assert str(exc) == "Gemini AI failure"
    assert isinstance(exc, AppException)
