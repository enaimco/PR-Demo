"""Abstract interfaces (ports) for the domain layer.

These define what the domain needs from the outside world,
without any dependency on infrastructure or framework code.
"""

from abc import ABC, abstractmethod
from typing import Any


class SessionPort(ABC):
    """Abstract session contract used by the application and interface layers."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Return the value stored under key, or None if absent."""

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Store value under key."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all entries from the session."""

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Return True when a GitHub access token is present in the session."""
