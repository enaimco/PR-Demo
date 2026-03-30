"""Integration tests for the /api/prs endpoint."""

from starlette.testclient import TestClient

from main import create_app


def test_prs_endpoint_requires_authentication() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/prs", params={"org": "test-org"})
    assert response.status_code == 401


def test_prs_endpoint_without_org_still_requires_auth() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/prs")
    assert response.status_code == 401
