"""Item 29 - Human-in-the-loop / Approval.

Interrupt points where the system pauses for human review/feedback before
continuing (e.g. before executing a side-effecting action).

    request_approval(request) -> ApprovalResponse
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ApprovalRequest:
    """A request for a human decision."""

    summary: str
    payload: dict[str, Any] = field(default_factory=dict)
    options: list[str] = field(default_factory=lambda: ["approve", "reject"])
    risk: str = "medium"


@dataclass(slots=True)
class ApprovalResponse:
    """The human's decision."""

    approved: bool
    choice: str = ""
    feedback: str = ""


class HumanInLoop(ABC):
    """Pause execution and obtain human approval/feedback."""

    @abstractmethod
    def request_approval(self, request: ApprovalRequest) -> ApprovalResponse: ...


class AutoApprove(HumanInLoop):
    """Non-interactive default that approves everything (for tests / demos)."""

    def request_approval(self, request: ApprovalRequest) -> ApprovalResponse:
        return ApprovalResponse(approved=True, choice="approve", feedback="auto-approved")
