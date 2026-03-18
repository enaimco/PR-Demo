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
| `ports.py` | `SessionPort` abstract interface |

### Application — `src/application/`

Orchestrates domain logic. Depends only on `domain/`.

_Phase 1: empty. Use cases will be added in Phase 2._

### Infrastructure — `src/infrastructure/`

Implements the abstract ports defined in `domain/`.

| Component | Purpose |
|-----------|---------|
| `session.py` | `StarletteSessionAdapter` — wraps `request.session` |
| `oauth.py` | `GitHubOAuthAdapter` — composes `authlib` OAuth client |

### Interface — `src/interface/`

FastAPI routers and Jinja2 templates. The only layer that imports from `infrastructure/`.

| Component | Purpose |
|-----------|---------|
| `dependencies.py` | `get_session()` FastAPI dependency — single infra import point |
| `routers/auth.py` | `/login`, `/auth/callback`, `/logout` |
| `routers/dashboard.py` | `/` — protected route |

## Composition Root

`main.py` wires all layers together:
1. Reads required env vars (fail fast)
2. Adds `SessionMiddleware` (must be first)
3. Constructs `GitHubOAuthAdapter`
4. Mounts routers
