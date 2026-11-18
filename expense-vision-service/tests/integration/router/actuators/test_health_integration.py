from fastapi.testclient import TestClient

from main import create_app


def test_actuators_health_integration_endpoint():
    """Verify live GET /actuators/health returns healthy status code and metadata."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/actuators/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "name": "expense-vision-service",
        "status": "healthy",
    }
