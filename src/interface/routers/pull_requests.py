"""Pull request API routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel

from src.application.fetch_org_pull_requests import FetchOrgPullRequestsUseCase
from src.domain.pr import PRData
from src.interface.dependencies import bearer_scheme, get_fetch_org_pull_requests_use_case

router = APIRouter(prefix="/api", tags=["pull-requests"])


class PullRequestResponse(BaseModel):
    """Swagger-friendly response model for a classified pull request."""

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
    age_bracket: str
    complexity_score: float


def _to_response(pr_data: PRData) -> PullRequestResponse:
    return PullRequestResponse(
        node_id=pr_data.node_id,
        title=pr_data.title,
        url=pr_data.url,
        author=pr_data.author,
        created_at=pr_data.created_at,
        is_draft=pr_data.is_draft,
        additions=pr_data.additions,
        deletions=pr_data.deletions,
        changed_files=pr_data.changed_files,
        commit_count=pr_data.commit_count,
        review_thread_count=pr_data.review_thread_count,
        age_bracket=pr_data.age_bracket.value,
        complexity_score=pr_data.complexity_score,
    )


@router.get("/prs", response_model=list[PullRequestResponse], dependencies=[Security(bearer_scheme)])
async def list_organization_pull_requests(
    org: str,
    use_case: FetchOrgPullRequestsUseCase = Depends(
        get_fetch_org_pull_requests_use_case
    ),
) -> list[PullRequestResponse]:
    """Fetch and classify all open PRs for the given GitHub organisation."""
    pull_requests = await use_case.execute(organization=org)
    return [_to_response(pr) for pr in pull_requests]
