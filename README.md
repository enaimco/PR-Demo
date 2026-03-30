# PR Dashboard

A lightweight internal tool that gives engineering teams instant visibility into the health of open pull requests across a GitHub organisation — with a focus on surfacing PRs that have gone stale before they become blockers.

---

## The Problem

We have ~45 open PRs across our repos at any given time, spanning a range of states:

- **Draft** — work in progress, not yet ready for review
- **Fresh** — recently opened, in active review
- **Aging** — open for days without meaningful activity
- **Stale** — sitting for weeks, blocking merges, accumulating drift

The long-lived ones are the real cost. They create merge conflicts, lose reviewer context, slow down deploys, and quietly erode team momentum. The challenge isn't that people don't care — it's that there's no single place to see which PRs need attention right now.

---

## The Solution

A dashboard that authenticates with GitHub, pulls all open PRs for the org via the GitHub GraphQL API, and classifies each one by age. The goal is to make the unhealthy PRs impossible to ignore.

**Core features:**

- **Age-based classification** — PRs are bucketed into `Fresh`, `Aging`, `Stale`, and `Draft` so the team can triage at a glance
- **Complexity score** — each PR is scored `Low / Medium / High / Very High` based on signals available from the GitHub API: lines changed, files touched, commit count, and review thread volume. Pure domain logic — no extra API calls required.
- **Org-wide view** — aggregates across all repos, not just one at a time
- **GitHub OAuth login** — no separate credentials, uses the access you already have
- **Lightweight UI** — server-rendered HTMX/Jinja2, no SPA complexity, fast to load and easy to extend

**Complexity scoring model:**

| Signal | What it captures |
|--------|-----------------|
| `additions + deletions` | Raw size of the change |
| `changedFiles` | Breadth — how much of the codebase is touched |
| `commits` | History shape — high commit count often means iterative, complex work |
| `reviewThreads` | Complexity discovered in review — back-and-forth is a signal |

Each signal is normalised to `[0, 1]` against a configurable ceiling, then combined as a weighted sum and bucketed. Weights are named constants in the domain layer and can be tuned without touching infrastructure or UI.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI |
| Frontend | HTMX + Jinja2 (server-rendered) |
| Auth | GitHub OAuth |
| GitHub API | GraphQL via `httpx` |
| Testing | `pytest` + `pytest-asyncio` |

---

## Architecture

The app follows **Clean (Onion) Architecture** — domain logic is isolated from infrastructure and framework concerns, making each layer independently testable and replaceable.

```
Domain        →  PR entities, age classification logic, abstract interfaces
Application   →  Use cases (fetch org PRs, classify by age)
Infrastructure →  GitHub GraphQL client, OAuth adapter, session store
Interface     →  FastAPI routes, HTMX templates
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- A GitHub OAuth App ([create one here](https://github.com/settings/developers))

### Setup

```bash
# Clone and install dependencies
git clone https://github.com/enaimco/PR-Demo.git
cd pr-demo
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Fill in GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_ORG, SESSION_SECRET

# Run the app
python main.py
```

The app will be available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### Running Tests

```bash
pytest
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_CLIENT_ID` | OAuth App client ID |
| `GITHUB_CLIENT_SECRET` | OAuth App client secret |
| `GITHUB_ORG` | Default GitHub organisation to query |
| `SESSION_SECRET` | Random string used to sign sessions |
