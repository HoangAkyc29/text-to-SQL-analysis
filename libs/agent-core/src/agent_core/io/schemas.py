"""The agent input/output contract.

Every agent service receives an :class:`AgentRequest` and returns an
:class:`AgentResponse`. This is also the wire format for A2A (the router posts
``AgentRequest.model_dump()`` to ``/run`` and parses an ``AgentResponse``).

``metadata['inbox']`` carries structured outputs from upstream agents in a graph;
``payload`` carries this agent's structured output for downstream consumers.
Domain-specific fields (e.g. a symbol, document id, tenant) belong in
``metadata`` and are interpreted by each agent — not by the shared schema.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolCallRecord(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: str | None = None


class AgentRequest(BaseModel):
    """What an agent listens for (the input data)."""

    message: str
    session_id: str = ""
    actor_id: str = "anonymous"
    model_profile: str | None = None
    image_paths: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def inbox(self) -> dict[str, Any]:
        """Structured outputs handed down from upstream agents."""
        return self.metadata.get("inbox", {})

    @property
    def shared_state(self) -> dict[str, Any]:
        """Shared graph blackboard snapshot for this turn."""
        return self.metadata.get("shared_state", {})

    @property
    def debate(self) -> dict[str, Any]:
        """Debate context when the agent is a debate participant or facilitator."""
        return self.metadata.get("debate", {})


class AgentResponse(BaseModel):
    """What an agent returns."""

    session_id: str = ""
    actor_id: str = "anonymous"
    content: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    state_updates: dict[str, Any] = Field(default_factory=dict)
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    memory_refs: list[str] = Field(default_factory=list)
    raw: dict[str, Any] | None = None
