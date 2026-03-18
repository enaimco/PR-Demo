"""Unit tests for StarletteSessionAdapter (zero I/O)."""

from unittest.mock import MagicMock

from src.infrastructure.session import GITHUB_ACCESS_TOKEN_KEY, StarletteSessionAdapter


def _make_adapter(initial: dict | None = None) -> StarletteSessionAdapter:
    request = MagicMock()
    request.session = dict(initial or {})
    return StarletteSessionAdapter(request)


def test_set_and_get_round_trip():
    adapter = _make_adapter()
    adapter.set("key", "value")
    assert adapter.get("key") == "value"


def test_get_returns_none_for_missing_key():
    adapter = _make_adapter()
    assert adapter.get("nonexistent") is None


def test_clear_removes_all_entries():
    adapter = _make_adapter({"a": 1, "b": 2})
    adapter.clear()
    assert adapter.get("a") is None
    assert adapter.get("b") is None


def test_is_authenticated_when_token_present():
    adapter = _make_adapter({GITHUB_ACCESS_TOKEN_KEY: "some-token"})
    assert adapter.is_authenticated() is True


def test_is_not_authenticated_when_token_absent():
    adapter = _make_adapter()
    assert adapter.is_authenticated() is False
