import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def app():
    """Create and return a new FastAPI test application instance."""
    return create_app()


@pytest.fixture
def client(app):
    """Create and return a TestClient instance for testing API endpoints."""
    return TestClient(app)
