from router.actuators.health import health_router
from router.routers import actuators_router, api_v1_router


def test_actuators_router_configuration():
    """Verify actuators router prefix, tags, and included routes."""
    assert actuators_router.prefix == "/actuators"
    assert "Actuators" in actuators_router.tags

    # Verify that health_router is included
    assert len(actuators_router.routes) > 0
    included_subrouters = [
        getattr(route, "original_router", None) for route in actuators_router.routes
    ]
    assert health_router in included_subrouters


def test_api_v1_router_configuration():
    """Verify api_v1 router prefix and tags."""
    assert api_v1_router.prefix == "/api/v1"
    assert "API v1" in api_v1_router.tags
