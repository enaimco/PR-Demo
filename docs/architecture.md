# Architecture

PR Dashboard follows the **Onion (Clean) Architecture**. Each layer depends only on layers inward — never outward.

```
Domain (entities, value objects, interfaces)
  └── Application (use cases — orchestrates domain)
        └── Infrastructure (GitHub API, session store, OAuth)
              └── Interface (FastAPI routes, HTMX templates)
```

## Layers

### Domain — `src/domain/`

Pure Python. No I/O, no framework imports.

| Component | Purpose |
|-----------|---------|
| `ports.py` | `SessionPort` and `GitHubPort` abstract interfaces |
| `pr.py` | `PRData` frozen dataclass, `AgeBracket` enum, age threshold constants |
| `pr_age.py` | `classify_age()` — pure age bracket classification |
| `pr_complexity.py` | `compute_complexity_score()` — weighted log-scaled scoring |

### Application — `src/application/`

Orchestrates domain logic. Depends only on `domain/`.

| Component | Purpose |
|-----------|---------|
| `fetch_org_pull_requests.py` | `FetchOrgPullRequestsUseCase` — fetches PRs via `GitHubPort`, classifies age and complexity |

### Infrastructure — `src/infrastructure/`

Implements the abstract ports defined in `domain/`.

| Component | Purpose |
|-----------|---------|
| `session.py` | `StarletteSessionAdapter` — wraps `request.session` |
| `oauth.py` | `GitHubOAuthAdapter` — composes `authlib` OAuth client |
| `github_client.py` | `GitHubGraphQLClient` — implements `GitHubPort` via GraphQL search API |

### Interface — `src/interface/`

FastAPI routers and Jinja2 templates. The only layer that imports from `infrastructure/`.

| Component | Purpose |
|-----------|---------|
| `dependencies.py` | `get_session()` and `get_fetch_org_pull_requests_use_case()` FastAPI dependencies |
| `routers/auth.py` | `/login`, `/auth/callback`, `/logout` |
| `routers/dashboard.py` | `/` — protected route |
| `routers/pull_requests.py` | `GET /api/prs?org=<org>` — classified PR data as JSON |

## Composition Root

`main.py` wires all layers together:
1. Reads required env vars (fail fast)
2. Adds `SessionMiddleware` (must be first)
3. Constructs `GitHubOAuthAdapter`
4. Mounts routers
