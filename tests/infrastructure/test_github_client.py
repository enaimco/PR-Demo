"""Integration tests for GitHubGraphQLClient using respx to mock HTTP."""

import pytest
import respx
from httpx import Response

from src.infrastructure.github_client import GITHUB_GRAPHQL_URL, GitHubGraphQLClient


def _graphql_response(nodes: list[dict], has_next: bool = False, cursor: str | None = None) -> dict:
    return {
        "data": {
            "search": {
                "pageInfo": {
                    "hasNextPage": has_next,
                    "endCursor": cursor,
                },
                "nodes": nodes,
            }
        }
    }


def _sample_pr_node(*, node_id: str = "PR_1", title: str = "Fix typo") -> dict:
    return {
        "id": node_id,
        "title": title,
        "url": "https://github.com/org/repo/pull/1",
        "author": {"login": "dev"},
        "createdAt": "2026-03-20T10:00:00Z",
        "isDraft": False,
        "additions": 10,
        "deletions": 3,
        "changedFiles": 2,
        "commits": {"totalCount": 1},
        "reviewThreads": {"totalCount": 0},
    }


@respx.mock
async def test_fetch_parses_single_page() -> None:
    respx.post(GITHUB_GRAPHQL_URL).mock(
        return_value=Response(200, json=_graphql_response([_sample_pr_node()]))
    )

    client = GitHubGraphQLClient(access_token="fake-token")
    result = await client.fetch_open_pull_requests("test-org")

    assert len(result) == 1
    assert result[0]["node_id"] == "PR_1"
    assert result[0]["title"] == "Fix typo"
    assert result[0]["author"] == "dev"
    assert result[0]["commit_count"] == 1


@respx.mock
async def test_handles_pagination() -> None:
    route = respx.post(GITHUB_GRAPHQL_URL)
    route.side_effect = [
        Response(200, json=_graphql_response(
            [_sample_pr_node(node_id="PR_1")], has_next=True, cursor="cursor1"
        )),
        Response(200, json=_graphql_response(
            [_sample_pr_node(node_id="PR_2", title="Second PR")]
        )),
    ]

    client = GitHubGraphQLClient(access_token="fake-token")
    result = await client.fetch_open_pull_requests("test-org")

    assert len(result) == 2
    assert result[0]["node_id"] == "PR_1"
    assert result[1]["node_id"] == "PR_2"


@respx.mock
async def test_handles_empty_org() -> None:
    respx.post(GITHUB_GRAPHQL_URL).mock(
        return_value=Response(200, json=_graphql_response([]))
    )

    client = GitHubGraphQLClient(access_token="fake-token")
    result = await client.fetch_open_pull_requests("empty-org")

    assert result == []


@respx.mock
async def test_skips_null_nodes() -> None:
    respx.post(GITHUB_GRAPHQL_URL).mock(
        return_value=Response(200, json=_graphql_response([None, _sample_pr_node()]))
    )

    client = GitHubGraphQLClient(access_token="fake-token")
    result = await client.fetch_open_pull_requests("test-org")

    assert len(result) == 1


def test_rejects_invalid_org_name() -> None:
    client = GitHubGraphQLClient(access_token="fake-token")
    with pytest.raises(ValueError, match="Invalid organization name"):
        import asyncio
        asyncio.run(client.fetch_open_pull_requests("org with spaces"))
