"""HTTP health endpoint tests."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_liveness_includes_correlation_id() -> None:
    """The service emits and returns a correlation ID."""
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["X-Request-ID"] == response.json()["request_id"]


def test_liveness_propagates_client_correlation_id() -> None:
    """A client-provided correlation ID remains observable end to end."""
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/health/live", headers={"X-Request-ID": "test-id"})

    assert response.headers["X-Request-ID"] == "test-id"
