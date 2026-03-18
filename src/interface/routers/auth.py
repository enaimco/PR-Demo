"""Authentication routes: login, OAuth callback, logout."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from src.domain.ports import SessionPort
from src.infrastructure.oauth import GitHubOAuthAdapter, OAuthError
from src.infrastructure.session import GITHUB_ACCESS_TOKEN_KEY
from src.interface.dependencies import get_session


def build_auth_router(oauth_adapter: GitHubOAuthAdapter) -> APIRouter:
    """Factory that creates the auth router with the given OAuth adapter injected."""
    router = APIRouter()

    @router.get("/login")
    async def login(request: Request) -> RedirectResponse:
        redirect_uri = str(request.url_for("callback"))
        return await oauth_adapter.redirect_to_authorization(request, redirect_uri)

    @router.get("/auth/callback", name="callback")
    async def callback(
        request: Request,
        session: SessionPort = Depends(get_session),
    ) -> RedirectResponse:
        try:
            token = await oauth_adapter.exchange_code_for_token(request)
        except OAuthError:
            return RedirectResponse(url="/login")

        session.set(GITHUB_ACCESS_TOKEN_KEY, token.get("access_token"))
        return RedirectResponse(url="/")

    @router.get("/logout")
    async def logout(
        session: SessionPort = Depends(get_session),
    ) -> RedirectResponse:
        session.clear()
        return RedirectResponse(url="/login")

    return router
