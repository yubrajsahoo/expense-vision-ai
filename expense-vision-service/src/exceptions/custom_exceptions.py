"""Custom application exceptions for Expense Vision Service.

Defines the base application exception hierarchy carrying HTTP status codes
for structured API error handling across service and router layers.
"""


class AppException(Exception):
    """Base application exception carrying an HTTP status code.

    :param message: Human-readable error message describing the failure.
    :param status_code: HTTP status code associated with the error (default: 500).
    """

    def __init__(self, message: str, status_code: int = 500):
        """Initialize AppException with a message and HTTP status code.

        :param message: Error message describing the failure.
        :param status_code: HTTP status code.
        """
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidImageError(AppException):
    """Raised when the uploaded file has an invalid type or is empty.

    :param message: Human-readable error message explaining the validation error.
    """

    def __init__(self, message: str):
        """Initialize InvalidImageError with HTTP 400 Bad Request status.

        :param message: Error message describing the invalid image input.
        """
        super().__init__(message=message, status_code=400)


class ExtractionError(AppException):
    """Raised when the Gemini API fails to extract expense data.

    :param message: Human-readable error message.
    """

    def __init__(self, message: str = "Unable to extract expense data."):
        """Initialize ExtractionError with HTTP 502 Bad Gateway status.

        :param message: Error message describing the extraction failure.
        """
        super().__init__(message=message, status_code=502)
