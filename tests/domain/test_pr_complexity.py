"""Unit tests for complexity scoring — pure, no I/O."""

from src.domain.pr_complexity import MAX_SCORE, compute_complexity_score


def test_zero_signals_returns_zero() -> None:
    score = compute_complexity_score(
        additions=0,
        deletions=0,
        changed_files=0,
        commit_count=0,
        review_thread_count=0,
    )
    assert score == 0.0


def test_small_pr_low_score() -> None:
    score = compute_complexity_score(
        additions=5,
        deletions=2,
        changed_files=1,
        commit_count=1,
        review_thread_count=0,
    )
    assert 0 < score < 30


def test_large_pr_high_score() -> None:
    score = compute_complexity_score(
        additions=2000,
        deletions=500,
        changed_files=40,
        commit_count=20,
        review_thread_count=15,
    )
    assert score > 50


def test_score_never_exceeds_max() -> None:
    score = compute_complexity_score(
        additions=100_000,
        deletions=100_000,
        changed_files=1000,
        commit_count=500,
        review_thread_count=200,
    )
    assert score <= MAX_SCORE


def test_additions_increase_score() -> None:
    baseline = compute_complexity_score(10, 0, 1, 1, 0)
    higher = compute_complexity_score(1000, 0, 1, 1, 0)
    assert higher > baseline


def test_all_signals_contribute() -> None:
    base = compute_complexity_score(10, 10, 5, 3, 2)
    assert base > 0
    # Each signal at zero should reduce score
    assert compute_complexity_score(0, 10, 5, 3, 2) < base
    assert compute_complexity_score(10, 0, 5, 3, 2) < base
    assert compute_complexity_score(10, 10, 0, 3, 2) < base
    assert compute_complexity_score(10, 10, 5, 0, 2) < base
    assert compute_complexity_score(10, 10, 5, 3, 0) < base
