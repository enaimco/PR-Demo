"""Pure complexity scoring logic for pull requests."""

import math

ADDITIONS_WEIGHT = 0.3
DELETIONS_WEIGHT = 0.2
CHANGED_FILES_WEIGHT = 0.25
COMMITS_WEIGHT = 0.15
REVIEW_THREADS_WEIGHT = 0.1

MAX_SCORE = 100.0
NORMALIZATION_DIVISOR = 10.0


def compute_complexity_score(
    additions: int,
    deletions: int,
    changed_files: int,
    commit_count: int,
    review_thread_count: int,
) -> float:
    """Compute a 0–100 complexity score from PR signals.

    Uses log-scaled weighted sum to prevent extreme outliers
    from dominating the score.
    """
    raw = (
        ADDITIONS_WEIGHT * math.log1p(additions)
        + DELETIONS_WEIGHT * math.log1p(deletions)
        + CHANGED_FILES_WEIGHT * math.log1p(changed_files)
        + COMMITS_WEIGHT * math.log1p(commit_count)
        + REVIEW_THREADS_WEIGHT * math.log1p(review_thread_count)
    )
    normalized = (raw / NORMALIZATION_DIVISOR) * MAX_SCORE
    return round(min(normalized, MAX_SCORE), 1)
