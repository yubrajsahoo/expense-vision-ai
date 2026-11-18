"""Application entry point and FastAPI initialization for Expense Vision Service.

Configures application metadata, registers route groups, and manages
the server lifecycle with Uvicorn.
"""

import uvicorn
from fastapi import FastAPI

from config.config import settings
from router.routers import actuators_router, api_v1_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Initializes the FastAPI application with metadata, registers actuator routes,
    and mounts the API v1 route group.

    :return: Configured FastAPI application instance.
    """
    application = FastAPI(
        title="Expense Vision Service",
        description="AI worker for processing receipts and UPI screenshots",
        version="0.1.0",
    )
    application.include_router(actuators_router)
    application.include_router(api_v1_router)

    return application


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host=settings.host, port=settings.port, reload=settings.reload
    )
