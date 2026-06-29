from __future__ import annotations

from typing import Any


class ScriptedAgentInvoker:
    """Records every agent call and returns scripted payloads per agent/attempt."""

    def __init__(self, scripts: dict[str, list[dict[str, Any]]] | None = None) -> None:
        self.scripts = scripts or {}
        self.calls: list[dict[str, Any]] = []

    def invoke(self, agent: str, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        self.calls.append({"agent": agent, "payload": payload, "metadata": metadata})
        queue = self.scripts.get(agent, [])
        if queue:
            return queue.pop(0)
        return {}

    def agents_called(self) -> list[str]:
        return [c["agent"] for c in self.calls]

    def last_call(self, agent: str) -> dict[str, Any] | None:
        for c in reversed(self.calls):
            if c["agent"] == agent:
                return c
        return None
