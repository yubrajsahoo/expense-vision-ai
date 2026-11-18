"""Top-level router configuration and aggregation for actuators and API v1 endpoints."""

from fastapi import APIRouter

from router.actuators.health import health_router
from router.v1.expense import expense_router

actuators_router = APIRouter(prefix="/actuators", tags=["Actuators"])
api_v1_router = APIRouter(prefix="/api/v1", tags=["API v1"])


# Actuator routes
actuators_router.include_router(health_router)


# API v1 routes
api_v1_router.include_router(expense_router)
