"""Authentication routes: login, OAuth callback, logout."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from src.domain.ports import SessionPort
import httpx

from src.infrastructure.oauth import GitHubOAuthAdapter, OAuthError
from src.infrastructure.session import GITHUB_ACCESS_TOKEN_KEY, GITHUB_USERNAME_KEY
from src.interface.dependencies import get_session

templates = Jinja2Templates(directory="templates")


def build_auth_router(oauth_adapter: GitHubOAuthAdapter) -> APIRouter:
    """Factory that creates the auth router with the given OAuth adapter injected."""
    router = APIRouter()

    @router.get("/login")
    async def login(request: Request) -> object:
        return templates.TemplateResponse("login.html", {"request": request})

    @router.get("/login/oauth")
    async def login_oauth(request: Request) -> RedirectResponse:
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

        access_token = token.get("access_token")
        session.set(GITHUB_ACCESS_TOKEN_KEY, access_token)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code == 200:
                session.set(GITHUB_USERNAME_KEY, response.json().get("login"))

        return RedirectResponse(url="/")

    @router.get("/logout")
    async def logout(
        session: SessionPort = Depends(get_session),
    ) -> RedirectResponse:
        session.clear()
        return RedirectResponse(url="/login")

    return router
