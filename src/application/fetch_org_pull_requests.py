"""Use case: fetch and classify open pull requests for an organisation."""

from datetime import datetime, timezone
from typing import Any

from src.domain.ports import GitHubPort
from src.domain.pr import PRData
from src.domain.pr_age import classify_age
from src.domain.pr_complexity import compute_complexity_score


def _parse_created_at(raw: str) -> datetime:
    """Parse an ISO-8601 timestamp into a timezone-aware datetime."""
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def _build_pr_data(raw: dict[str, Any], now: datetime) -> PRData:
    """Transform a raw PR dict into a classified PRData entity."""
    created_at = _parse_created_at(raw["created_at"])
    return PRData(
        node_id=raw["node_id"],
        title=raw["title"],
        url=raw["url"],
        author=raw["author"],
        created_at=created_at,
        is_draft=raw["is_draft"],
        additions=raw["additions"],
        deletions=raw["deletions"],
        changed_files=raw["changed_files"],
        commit_count=raw["commit_count"],
        review_thread_count=raw["review_thread_count"],
        age_bracket=classify_age(created_at, now),
        complexity_score=compute_complexity_score(
            additions=raw["additions"],
            deletions=raw["deletions"],
            changed_files=raw["changed_files"],
            commit_count=raw["commit_count"],
            review_thread_count=raw["review_thread_count"],
        ),
    )


class FetchOrgPullRequestsUseCase:
    """Orchestrates fetching PRs from GitHub and applying domain classification."""

    def __init__(self, github_port: GitHubPort) -> None:
        self._github_port = github_port

    async def execute(
        self,
        organization: str,
        now: datetime | None = None,
    ) -> list[PRData]:
        now = now or datetime.now(timezone.utc)
        raw_pull_requests = await self._github_port.fetch_open_pull_requests(
            organization
        )
        classified = [
            _build_pr_data(raw, now) for raw in raw_pull_requests
        ]
        return sorted(
            classified, key=lambda pr: pr.complexity_score, reverse=True
        )
