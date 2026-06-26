"""Item 32 - Guardrails / Validation / Policy.

Validate inputs/outputs, apply safety filters, and enforce permissions/ACLs:
which agent may call which tool or read which data.

    validate(payload) -> ValidationResult
    can_access(actor, resource, action) -> bool
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ValidationResult:
    """Outcome of a guardrail check."""

    allowed: bool
    reason: str = ""
    transformed: Any = None  # optionally sanitised payload
    violations: list[str] = field(default_factory=list)


class Guardrail(ABC):
    """Validate / sanitise a payload (input or output)."""

    @abstractmethod
    def validate(self, payload: Any, *, context: dict[str, Any] | None = None) -> ValidationResult: ...


class PermissionPolicy(ABC):
    """Authorize an actor to perform an action on a resource (ACL)."""

    @abstractmethod
    def can_access(self, actor: str, resource: str, action: str) -> bool: ...
