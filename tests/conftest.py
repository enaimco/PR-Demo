"""Shared test fixtures."""

import os

import pytest
from fastapi.testclient import TestClient

# Provide required env vars before the app module is imported.
os.environ.setdefault("SESSION_SECRET", "test-secret-key")
os.environ.setdefault("GITHUB_CLIENT_ID", "test-client-id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test-client-secret")

from main import create_app  # noqa: E402


@pytest.fixture()
def app():
    return create_app()


@pytest.fixture()
def client(app):
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
