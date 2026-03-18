"""FastAPI dependency injection helpers for the interface layer."""

from fastapi import Request

from src.domain.ports import SessionPort
from src.infrastructure.session import StarletteSessionAdapter


def get_session(request: Request) -> SessionPort:
    """Provide a SessionPort backed by Starlette's session middleware."""
    return StarletteSessionAdapter(request)
