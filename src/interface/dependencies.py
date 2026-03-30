"""FastAPI dependency injection helpers for the interface layer."""

from fastapi import HTTPException, Request

from src.application.fetch_org_pull_requests import FetchOrgPullRequestsUseCase
from src.domain.ports import SessionPort
from src.infrastructure.github_client import GitHubGraphQLClient
from src.infrastructure.session import GITHUB_ACCESS_TOKEN_KEY, StarletteSessionAdapter


def get_session(request: Request) -> SessionPort:
    """Provide a SessionPort backed by Starlette's session middleware."""
    return StarletteSessionAdapter(request)


def get_fetch_org_pull_requests_use_case(
    request: Request,
) -> FetchOrgPullRequestsUseCase:
    """Build a FetchOrgPullRequestsUseCase wired to the current user's token."""
    session = StarletteSessionAdapter(request)
    access_token = session.get(GITHUB_ACCESS_TOKEN_KEY)
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    github_client = GitHubGraphQLClient(access_token=access_token)
    return FetchOrgPullRequestsUseCase(github_port=github_client)
