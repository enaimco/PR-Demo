"""Unit tests for age bracket classification — pure, no I/O."""

from datetime import datetime, timedelta, timezone

from src.domain.pr import AgeBracket
from src.domain.pr_age import classify_age

NOW = datetime(2026, 3, 25, 12, 0, 0, tzinfo=timezone.utc)


def test_fresh_under_one_day() -> None:
    created = NOW - timedelta(hours=6)
    assert classify_age(created, NOW) == AgeBracket.FRESH


def test_recent_between_one_and_three_days() -> None:
    created = NOW - timedelta(days=2)
    assert classify_age(created, NOW) == AgeBracket.RECENT


def test_aging_between_three_and_seven_days() -> None:
    created = NOW - timedelta(days=5)
    assert classify_age(created, NOW) == AgeBracket.AGING


def test_stale_between_seven_and_fourteen_days() -> None:
    created = NOW - timedelta(days=10)
    assert classify_age(created, NOW) == AgeBracket.STALE


def test_ancient_over_fourteen_days() -> None:
    created = NOW - timedelta(days=20)
    assert classify_age(created, NOW) == AgeBracket.ANCIENT


def test_boundary_exactly_one_day() -> None:
    created = NOW - timedelta(days=1)
    assert classify_age(created, NOW) == AgeBracket.RECENT


def test_boundary_exactly_three_days() -> None:
    created = NOW - timedelta(days=3)
    assert classify_age(created, NOW) == AgeBracket.AGING


def test_boundary_exactly_seven_days() -> None:
    created = NOW - timedelta(days=7)
    assert classify_age(created, NOW) == AgeBracket.STALE


def test_boundary_exactly_fourteen_days() -> None:
    created = NOW - timedelta(days=14)
    assert classify_age(created, NOW) == AgeBracket.ANCIENT


def test_just_created() -> None:
    assert classify_age(NOW, NOW) == AgeBracket.FRESH
