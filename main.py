"""Application composition root."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.infrastructure.oauth import GitHubOAuthAdapter
from src.interface.routers import dashboard, pull_requests
from src.interface.routers.auth import build_auth_router

load_dotenv()


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Required environment variable '{key}' is not set.")
    return value


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    session_secret = _require_env("SESSION_SECRET")
    client_id = _require_env("GITHUB_CLIENT_ID")
    client_secret = _require_env("GITHUB_CLIENT_SECRET")

    app = FastAPI(
        title="PR Dashboard",
        version="0.1.0",
        swagger_ui_init_oauth={},
        openapi_tags=[{"name": "pull-requests"}],
    )

    # Register Bearer auth in OpenAPI so Swagger UI shows the Authorize button.
    from fastapi.openapi.utils import get_openapi

    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )
        schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "Paste your GitHub access token (shown on the dashboard).",
            }
        }
        schema["security"] = [{"BearerAuth": []}]
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi

    # SessionMiddleware must be registered before any route that uses the session.
    app.add_middleware(SessionMiddleware, secret_key=session_secret)

    oauth_adapter = GitHubOAuthAdapter(
        client_id=client_id,
        client_secret=client_secret,
    )

    app.include_router(build_auth_router(oauth_adapter))
    app.include_router(dashboard.router)
    app.include_router(pull_requests.router)

    return app


app = create_app()
