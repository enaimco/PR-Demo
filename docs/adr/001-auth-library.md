# ADR 001 — Auth Library: authlib over httpx-oauth

**Date:** 2026-03-18
**Status:** Accepted

## Context

We need a Python library to handle the GitHub OAuth 2.0 Authorization Code flow within a Starlette/FastAPI application.

## Decision

Use **authlib** (`authlib.integrations.starlette_client`).

## Rationale

| Criterion | authlib | httpx-oauth |
|-----------|---------|-------------|
| Starlette integration | First-class (`StarletteOAuth2App`) | Manual |
| State/PKCE handling | Automatic (stores state in session) | Manual |
| Maintenance | Active, well-documented | Less active |
| Token exchange | Single call (`authorize_access_token`) | Manual HTTP + parsing |

`authlib` handles the OAuth `state` parameter automatically using the session — this is critical for CSRF protection and aligns with `SessionMiddleware` already required by the app.

`httpx-oauth` would require manual state generation, storage, and verification — more code and more surface area for bugs.

## Consequences

- `authlib` must be listed as an explicit dependency.
- `itsdangerous` must also be explicit (required by `SessionMiddleware` — not reliably pulled in transitively).
- `GitHubOAuthAdapter` composes `authlib`'s client rather than subclassing it, keeping the dependency swappable for tests.
