"""Pure age classification logic for pull requests."""

from datetime import datetime

from src.domain.pr import (
    AGING_THRESHOLD_DAYS,
    FRESH_THRESHOLD_DAYS,
    RECENT_THRESHOLD_DAYS,
    STALE_THRESHOLD_DAYS,
    AgeBracket,
)


def classify_age(created_at: datetime, now: datetime) -> AgeBracket:
    """Classify a pull request into an age bracket.

    Both timestamps must be timezone-aware or both naive.
    """
    elapsed_days = (now - created_at).total_seconds() / 86400

    if elapsed_days < FRESH_THRESHOLD_DAYS:
        return AgeBracket.FRESH
    if elapsed_days < RECENT_THRESHOLD_DAYS:
        return AgeBracket.RECENT
    if elapsed_days < AGING_THRESHOLD_DAYS:
        return AgeBracket.AGING
    if elapsed_days < STALE_THRESHOLD_DAYS:
        return AgeBracket.STALE
    return AgeBracket.ANCIENT
