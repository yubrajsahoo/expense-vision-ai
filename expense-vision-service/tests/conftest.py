from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import create_app


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests under tests/integration.",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if config.getoption("--integration"):
        return

    skip_integration = pytest.mark.skip(
        reason="Skipped by default. Pass --integration to run."
    )
    for item in items:
        if "integration" in Path(item.fspath).parts or "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture
def app():
    """Create and return a new FastAPI test application instance."""
    return create_app()


@pytest.fixture
def client(app):
    """Create and return a TestClient instance for testing API endpoints."""
    return TestClient(app)
