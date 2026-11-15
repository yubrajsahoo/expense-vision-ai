import pytest

from router.actuators.health import health_check


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
