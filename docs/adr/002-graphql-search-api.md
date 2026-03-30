# ADR 002: Use GitHub GraphQL Search API for PR fetching

## Status

Accepted

## Context

We need to fetch all open pull requests for a GitHub organisation. Two approaches exist:

1. **Per-repo traversal:** List all org repos, then query each repo's open PRs in parallel.
2. **GraphQL search API:** Single paginated query using `org:<org> is:pr is:open`.

## Decision

Use the GraphQL search API (`search` query type).

## Rationale

- **Fewer round trips.** One paginated query vs. potentially hundreds of per-repo queries.
- **Simpler code.** No need to manage parallel requests, rate limiting across repos, or repo-level pagination.
- **All fields in one request.** `additions`, `deletions`, `changedFiles`, `commits.totalCount`, and `reviewThreads.totalCount` are all available on the `PullRequest` fragment.

## Trade-offs

- The search API has a **1,000 result limit**. Organisations with more than 1,000 open PRs would need the per-repo approach.
- For the current use case (internal dashboards for typical orgs), this limit is acceptable.

## Consequences

- If the 1,000-result cap becomes a problem, we will need to refactor `GitHubGraphQLClient` to use per-repo traversal. The `GitHubPort` interface will not change — only the infrastructure implementation.
