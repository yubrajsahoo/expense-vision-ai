"""Global exception handlers for the FastAPI application.

Catches application-specific and unhandled exceptions, logs them with appropriate
severity, and transforms them into standardized JSON error responses.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from exceptions.custom_exceptions import AppException

_logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom and default exception handlers on the FastAPI application.

    :param app: The FastAPI application instance to attach handlers to.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """Handle domain-specific AppException subclasses and return structured JSON.

        :param request: The incoming HTTP request.
        :param exc: The caught AppException instance.
        :return: JSONResponse with the exception's status code and details.
        """
        _logger.warning(
            "AppException on %s: [%d] %s",
            request.url.path,
            exc.status_code,
            exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle uncaught general exceptions with HTTP 500 and sanitized message.

        :param request: The incoming HTTP request.
        :param exc: The unhandled exception instance.
        :return: JSONResponse with status code 500 and error message.
        """
        _logger.exception("Unhandled error on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred.",
                "path": request.url.path,
            },
        )
