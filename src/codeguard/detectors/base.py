"""The contract every detector implements."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from codeguard.schemas import Finding


@runtime_checkable
class Detector(Protocol):
    """Anything with a ``name`` and a ``detect(code) -> list[Finding]`` method."""

    name: str

    def detect(self, code: str) -> list[Finding]:
        """Scan Python source code and return every finding (empty list if none)."""
        ...
