"""Health check actuator endpoint for service uptime monitoring."""

from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("/health", description="Actuator to check health")
async def health_check() -> dict[str, str]:
    """Health check endpoint to verify the service is running.

    :return: A dictionary containing the service name and healthy status.
    """
    return {
        "name": "expense-vision-service",
        "status": "healthy",
    }
