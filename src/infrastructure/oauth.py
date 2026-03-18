"""GitHub OAuth adapter using authlib."""

from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.requests import Request
from starlette.responses import RedirectResponse

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_SCOPE = "read:org,repo"


class GitHubOAuthAdapter:
    """Composes authlib OAuth to handle the GitHub OAuth 2.0 flow."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        oauth = OAuth()
        oauth.register(
            name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=GITHUB_AUTHORIZE_URL,
            access_token_url=GITHUB_TOKEN_URL,
            client_kwargs={"scope": GITHUB_SCOPE},
        )
        self._github = oauth.github

    async def redirect_to_authorization(
        self, request: Request, redirect_uri: str
    ) -> RedirectResponse:
        """Redirect the user to GitHub's authorization page."""
        return await self._github.authorize_redirect(request, redirect_uri)

    async def exchange_code_for_token(self, request: Request) -> dict:
        """Exchange the authorization code for an access token."""
        token = await self._github.authorize_access_token(request)
        return dict(token)


__all__ = ["GitHubOAuthAdapter", "OAuthError"]
