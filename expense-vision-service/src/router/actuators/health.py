from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("/health", description= "Actuator to check health")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {
        "name": "expense-vision-service",
        "status": "healthy",
    }
