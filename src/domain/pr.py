"""Domain entities for pull request data."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

FRESH_THRESHOLD_DAYS = 1
RECENT_THRESHOLD_DAYS = 3
AGING_THRESHOLD_DAYS = 7
STALE_THRESHOLD_DAYS = 14


class AgeBracket(Enum):
    """Classification of a pull request's age."""

    FRESH = "fresh"
    RECENT = "recent"
    AGING = "aging"
    STALE = "stale"
    ANCIENT = "ancient"


@dataclass(frozen=True)
class PRData:
    """Immutable value object representing a classified pull request."""

    node_id: str
    title: str
    url: str
    author: str
    created_at: datetime
    is_draft: bool
    additions: int
    deletions: int
    changed_files: int
    commit_count: int
    review_thread_count: int
    age_bracket: AgeBracket
    complexity_score: float
