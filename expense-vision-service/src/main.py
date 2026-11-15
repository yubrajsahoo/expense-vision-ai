import uvicorn
from fastapi import FastAPI

from config.config import settings
from router.routers import actuators_router, api_v1_router


def create_app():
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
