import pytest

from router.actuators.health import health_check, health_router


def test_health_router_configuration():
    """Test that health_router is configured with GET /health."""
    routes = [r for r in health_router.routes if hasattr(r, "path")]
    assert len(routes) == 1
    route = routes[0]
    assert route.path == "/health"
    assert "GET" in route.methods
    assert route.description == "Actuator to check health"


@pytest.mark.anyio
async def test_health_check_function():
    """Test calling the health_check endpoint function directly."""
    response = await health_check()
    assert response == {
        "name": "expense-vision-service",
        "status": "healthy",
    }


def test_health_check_endpoint(client):
    """Test calling GET /actuators/health via TestClient."""
    response = client.get("/actuators/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert data["name"] == "expense-vision-service"
    assert data["status"] == "healthy"
