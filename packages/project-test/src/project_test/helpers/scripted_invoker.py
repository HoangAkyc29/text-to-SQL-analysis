from __future__ import annotations

import copy
from typing import Any


class ScriptedAgentInvoker:
    """Records every agent call and returns scripted payloads per agent/attempt.

    For Agent II, when metadata.mode == \"select_tables\" and the next scripted
    item is a plan/probe SQL (legacy tests), auto-respond with select_tables
    without consuming the plan payload.
    """

    def __init__(self, scripts: dict[str, list[dict[str, Any]]] | None = None) -> None:
        self.scripts = scripts or {}
        self.calls: list[dict[str, Any]] = []

    def invoke(self, agent: str, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(
            {
                "agent": agent,
                "payload": copy.deepcopy(payload),
                "metadata": dict(metadata or {}),
            }
        )
        queue = self.scripts.get(agent, [])
        mode = str((metadata or {}).get("mode") or "")

        if agent == "II" and mode == "select_tables":
            if queue and queue[0].get("action") in {"select_tables", "clarify", "impossible"}:
                return queue.pop(0)
            tables = ["STRANS"]
            brief = (payload or {}).get("brief") or {}
            filters = brief.get("filters") or {}
            if filters.get("product_code") or filters.get("sku"):
                tables = ["SKU_DEF", "STRANS"]
            return {
                "action": "select_tables",
                "selected_tables": tables,
                "selected_target_dbs": ["db2"] * len(tables),
                "reasoning": "scripted auto select_tables",
            }

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
