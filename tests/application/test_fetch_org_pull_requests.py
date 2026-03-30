"""Use case tests with a fake GitHubPort — no real HTTP."""

from datetime import datetime, timedelta, timezone
from typing import Any

from src.application.fetch_org_pull_requests import FetchOrgPullRequestsUseCase
from src.domain.ports import GitHubPort
from src.domain.pr import AgeBracket

NOW = datetime(2026, 3, 25, 12, 0, 0, tzinfo=timezone.utc)


class FakeGitHubPort(GitHubPort):
    """In-memory fake returning canned PR data."""

    def __init__(self, pull_requests: list[dict[str, Any]]) -> None:
        self._pull_requests = pull_requests

    async def fetch_open_pull_requests(
        self, organization: str
    ) -> list[dict[str, Any]]:
        return self._pull_requests


def _make_raw_pr(
    *,
    title: str = "Fix bug",
    created_at: str = "2026-03-25T06:00:00Z",
    additions: int = 10,
    deletions: int = 5,
    changed_files: int = 2,
    commit_count: int = 1,
    review_thread_count: int = 0,
) -> dict[str, Any]:
    return {
        "node_id": "PR_abc123",
        "title": title,
        "url": "https://github.com/org/repo/pull/1",
        "author": "dev",
        "created_at": created_at,
        "is_draft": False,
        "additions": additions,
        "deletions": deletions,
        "changed_files": changed_files,
        "commit_count": commit_count,
        "review_thread_count": review_thread_count,
    }


async def test_returns_classified_pull_requests() -> None:
    six_hours_ago = (NOW - timedelta(hours=6)).isoformat()
    ten_days_ago = (NOW - timedelta(days=10)).isoformat()

    fake_port = FakeGitHubPort([
        _make_raw_pr(title="Fresh PR", created_at=six_hours_ago),
        _make_raw_pr(title="Stale PR", created_at=ten_days_ago),
    ])
    use_case = FetchOrgPullRequestsUseCase(github_port=fake_port)
    result = await use_case.execute(organization="test-org", now=NOW)

    assert len(result) == 2
    brackets = {pr.title: pr.age_bracket for pr in result}
    assert brackets["Fresh PR"] == AgeBracket.FRESH
    assert brackets["Stale PR"] == AgeBracket.STALE


async def test_empty_org_returns_empty_list() -> None:
    fake_port = FakeGitHubPort([])
    use_case = FetchOrgPullRequestsUseCase(github_port=fake_port)
    result = await use_case.execute(organization="empty-org", now=NOW)
    assert result == []


async def test_results_sorted_by_complexity_descending() -> None:
    fake_port = FakeGitHubPort([
        _make_raw_pr(title="Small", additions=1, deletions=0, changed_files=1),
        _make_raw_pr(title="Large", additions=5000, deletions=2000, changed_files=50, commit_count=30, review_thread_count=10),
    ])
    use_case = FetchOrgPullRequestsUseCase(github_port=fake_port)
    result = await use_case.execute(organization="test-org", now=NOW)

    assert result[0].title == "Large"
    assert result[1].title == "Small"
    assert result[0].complexity_score > result[1].complexity_score
