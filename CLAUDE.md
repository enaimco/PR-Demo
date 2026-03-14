# CLAUDE.md — Agent Instructions for PR Dashboard

## Stack
- **Backend:** Python 3.12, FastAPI (with Swagger docs at `/docs`)
- **Frontend:** HTMX + Jinja2 templates (no JS framework)
- **Auth:** GitHub OAuth (via `authlib` or `httpx-oauth`)
- **GitHub API:** `httpx` with GraphQL queries
- **Testing:** `pytest` + `pytest-asyncio`
- **Deployment:** Vercel (or Railway for Python)

---

## Architecture: Onion (Clean Architecture)

Layers from innermost to outermost. **Each layer may only depend on layers inward — never outward.**

```
Domain (entities, value objects, interfaces)
  └── Application (use cases — orchestrates domain)
        └── Infrastructure (GitHub API, session store, OAuth)
              └── Interface (FastAPI routes, HTMX templates)
```

### Layer responsibilities

| Layer | Location | Contains |
|-------|----------|----------|
| Domain | `src/domain/` | `PRData`, `AgeBracket`, pure functions, abstract interfaces (no I/O) |
| Application | `src/application/` | Use cases: `FetchOrgPRsUseCase`, `ClassifyPRAgeUseCase` |
| Infrastructure | `src/infrastructure/` | GitHub GraphQL client, OAuth adapter, session adapter |
| Interface | `src/interface/` | FastAPI routers, Jinja2 template responses, request/response models |

### Rules
- **Composition over inheritance.** Prefer injecting collaborators via constructor/function args rather than subclassing. This makes units independently testable.
- **Dependency inversion.** Application layer depends on abstract interfaces (`GitHubPort`, `SessionPort`) defined in `domain/`. Infrastructure implements them.
- **No cross-layer imports.** `domain/` must never import from `application/`, `infrastructure/`, or `interface/`. `application/` must never import from `infrastructure/` directly.

---

## Code Standards (Clean Code — Uncle Bob)

- **Names reveal intent.** No abbreviations (`prs_data` → `open_pull_requests`).
- **Functions do one thing.** If a function needs a comment to explain what it does, rename or split it.
- **Small functions.** Aim for < 20 lines. If it's longer, extract.
- **No magic numbers/strings.** Use named constants or enums (e.g., `AgeBracket.STALE` not `14`).
- **Avoid side effects.** Pure functions wherever possible, especially in `domain/`.
- **Fail fast.** Validate inputs at the boundary (interface layer). Trust internal layers.
- **Type everything.** All function signatures must have full type annotations.
- **Docstrings on public interfaces only.** Not on private helpers unless logic is non-obvious.

---

## Testing

- Unit tests for all `domain/` and `application/` code — no I/O, no mocks needed if architecture is clean.
- Integration tests for `infrastructure/` with real or stubbed HTTP.
- Use dependency injection to swap real GitHub client for a fake in tests.
- Test file mirrors source: `tests/domain/test_pr_age.py` for `src/domain/pr_age.py`.
- Run tests before every commit: `pytest`.

---

## Documentation

Keep the following up to date as you work:

- **`docs/architecture.md`** — update if any layer boundaries change or new components are added.
- **`docs/api.md`** — auto-generated via Swagger (`/docs`), but note any non-obvious decisions.
- **`docs/adr/`** — add an Architecture Decision Record for any significant technology or design choice.
- **Inline docstrings** on all public use cases and domain interfaces.

---

## Git Workflow

- **Small commits, often.** One logical change per commit. Do not batch unrelated changes.
- Commit message format: `<type>(<scope>): <short description>` — e.g., `feat(domain): add AgeBracket enum`, `fix(infra): handle GitHub rate limit response`.
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`.
- Always run `pytest` before committing.
- Never commit directly to `main`. Use feature branches named `issue/<number>-<slug>` (e.g., `issue/1-scaffolding-auth`).

---

## GitHub Issues Workflow

- **Before starting work**, check which issue is being addressed. Post a comment on the issue:
  > "Starting work on this issue. Branch: `issue/<n>-<slug>`"
- **While working**, post progress comments on the issue after each meaningful milestone (e.g., after a layer is complete, after tests pass).
- **If context is lost or the session ends**, post a comment on the issue summarising:
  - What has been completed
  - What remains
  - Any blockers or open decisions
  - The current branch name
  This allows the next session to resume without re-reading all code from scratch.
- **When feature is complete**, close the issue via the PR (use `Closes #<n>` in PR body).

---

## Pull Request Workflow

When a feature (issue) is complete:

1. Push the feature branch.
2. Create a PR targeting `main` with:
   - Title: mirrors the issue title
   - Body includes: summary of changes, `Closes #<n>`, testing notes
3. **Self-review the PR** — leave inline comments on the PR for:
   - Any non-obvious design decisions
   - Trade-offs made under time/complexity constraints
   - Anything that should be revisited or that deviates from the architecture
4. Request review from the user.
5. Do **not** merge — the user will review and merge.

---

## Environment Variables

```
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
GITHUB_ORG=           # default org (optional, can be set per-request)
SESSION_SECRET=       # random string for signing sessions
```

---

## Directory Structure

```
pr-demo/
├── CLAUDE.md
├── docs/
│   ├── architecture.md
│   └── adr/
├── src/
│   ├── domain/          # entities, interfaces, pure logic
│   ├── application/     # use cases
│   ├── infrastructure/  # GitHub client, OAuth, session
│   └── interface/       # FastAPI routers, Jinja2 templates
├── templates/           # HTMX/Jinja2 HTML templates
├── tests/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── main.py              # FastAPI app entrypoint
├── pyproject.toml
└── .env.example
```
