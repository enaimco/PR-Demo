"""Starlette session adapter implementing the SessionPort interface."""

from typing import Any

from starlette.requests import Request

from src.domain.ports import SessionPort

GITHUB_ACCESS_TOKEN_KEY = "github_access_token"
GITHUB_USERNAME_KEY = "github_username"


class StarletteSessionAdapter(SessionPort):
    """Wraps Starlette's request.session dict to satisfy SessionPort."""

    def __init__(self, request: Request) -> None:
        self._session = request.session

    def get(self, key: str) -> Any | None:
        return self._session.get(key)

    def set(self, key: str, value: Any) -> None:
        self._session[key] = value

    def clear(self) -> None:
        self._session.clear()

    def is_authenticated(self) -> bool:
        return GITHUB_ACCESS_TOKEN_KEY in self._session
