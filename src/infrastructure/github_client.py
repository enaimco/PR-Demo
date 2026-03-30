"""GitHub GraphQL client implementing GitHubPort."""

import re
import time
from typing import Any

import httpx

from src.domain.ports import GitHubPort

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
PAGE_SIZE = 50
CACHE_TTL_SECONDS = 60

OPEN_PRS_QUERY = """
query($search_query: String!, $cursor: String) {
  search(query: $search_query, type: ISSUE, first: 50, after: $cursor) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on PullRequest {
        id
        title
        url
        author { login }
        createdAt
        isDraft
        additions
        deletions
        changedFiles
        commits { totalCount }
        reviewThreads { totalCount }
      }
    }
  }
}
"""

ORG_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9\-]+$")


def _validate_organization(organization: str) -> None:
    """Reject org names that could alter the GraphQL search string."""
    if not ORG_NAME_PATTERN.match(organization):
        raise ValueError(f"Invalid organization name: {organization!r}")


def _parse_pull_request_node(node: dict[str, Any]) -> dict[str, Any]:
    """Transform a GraphQL PR node into the flat dict contract."""
    return {
        "node_id": node["id"],
        "title": node["title"],
        "url": node["url"],
        "author": (node.get("author") or {}).get("login", "ghost"),
        "created_at": node["createdAt"],
        "is_draft": node["isDraft"],
        "additions": node["additions"],
        "deletions": node["deletions"],
        "changed_files": node["changedFiles"],
        "commit_count": node["commits"]["totalCount"],
        "review_thread_count": node["reviewThreads"]["totalCount"],
    }


class GitHubGraphQLClient(GitHubPort):
    """Fetches open pull requests from GitHub using the GraphQL search API."""

    def __init__(self, access_token: str) -> None:
        self._access_token = access_token
        self._cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}

    async def fetch_open_pull_requests(
        self, organization: str
    ) -> list[dict[str, Any]]:
        _validate_organization(organization)

        cached = self._cache.get(organization)
        if cached and (time.monotonic() - cached[0]) < CACHE_TTL_SECONDS:
            return cached[1]

        pull_requests = await self._fetch_all_pages(organization)
        self._cache[organization] = (time.monotonic(), pull_requests)
        return pull_requests

    async def _fetch_all_pages(
        self, organization: str
    ) -> list[dict[str, Any]]:
        pull_requests: list[dict[str, Any]] = []
        cursor: str | None = None
        search_query = f"org:{organization} is:pr is:open"

        async with httpx.AsyncClient() as client:
            while True:
                response = await client.post(
                    GITHUB_GRAPHQL_URL,
                    json={
                        "query": OPEN_PRS_QUERY,
                        "variables": {
                            "search_query": search_query,
                            "cursor": cursor,
                        },
                    },
                    headers={
                        "Authorization": f"Bearer {self._access_token}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()

                search_result = data["data"]["search"]
                for node in search_result["nodes"]:
                    if node:
                        pull_requests.append(_parse_pull_request_node(node))

                page_info = search_result["pageInfo"]
                if not page_info["hasNextPage"]:
                    break
                cursor = page_info["endCursor"]

        return pull_requests
