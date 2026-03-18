"""Tests for the SessionPort abstract interface."""

import pytest

from src.domain.ports import SessionPort


def test_session_port_is_abstract():
    with pytest.raises(TypeError):
        SessionPort()  # type: ignore[abstract]


def test_concrete_implementation_satisfies_contract():
    class FakeSession(SessionPort):
        def __init__(self) -> None:
            self._store: dict = {}

        def get(self, key: str):
            return self._store.get(key)

        def set(self, key: str, value) -> None:
            self._store[key] = value

        def clear(self) -> None:
            self._store.clear()

        def is_authenticated(self) -> bool:
            return "github_access_token" in self._store

    session = FakeSession()
    assert session.get("x") is None
    session.set("x", 42)
    assert session.get("x") == 42
    assert not session.is_authenticated()
    session.set("github_access_token", "tok")
    assert session.is_authenticated()
    session.clear()
    assert session.get("x") is None
    assert not session.is_authenticated()
