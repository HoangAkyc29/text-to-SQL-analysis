"""Concrete context builder (item 8).

Assembles the per-turn window from: skill/tool docs, long-term memory recall,
short-term transcript, current state snapshot, and upstream agent payloads. Then
truncates to a rough token budget (4 chars ~= 1 token heuristic).
"""

from __future__ import annotations

from typing import Any

from agent_core.capabilities.context.base import ContextBuilder, ContextWindow


class DefaultContextBuilder(ContextBuilder):
    """Collect + fit context fragments for a turn."""

    def __init__(
        self,
        *,
        max_tokens: int = 8000,
        skill_docs: str = "",
        ltm_fragments: list[str] | None = None,
        retrieval_fragments: list[str] | None = None,
        stm_history: list[dict[str, str]] | None = None,
        state_snapshot: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(max_tokens=max_tokens)
        self._skill_docs = skill_docs
        self._ltm_fragments = ltm_fragments or []
        self._retrieval_fragments = retrieval_fragments or []
        self._stm_history = stm_history or []
        self._state_snapshot = state_snapshot or {}

    def collect(self, *, goal: str, inputs: dict[str, Any], session_id: str) -> list[str]:
        fragments: list[str] = [f"Goal: {goal}"]
        if self._skill_docs:
            fragments.append("Tool usage guide:\n" + self._skill_docs)
        if self._ltm_fragments:
            fragments.append("Long-term context:\n" + "\n".join(self._ltm_fragments))
        if self._retrieval_fragments:
            fragments.append("Retrieved context:\n" + "\n".join(self._retrieval_fragments))
        if self._stm_history:
            convo = "\n".join(f"{t['role']}: {t['content']}" for t in self._stm_history[-6:])
            fragments.append("Recent conversation:\n" + convo)
        if self._state_snapshot:
            fragments.append("Current state:\n" + str(self._state_snapshot))
        if inputs:
            fragments.append("Inputs:\n" + str(inputs))
        return fragments

    def fit(self, fragments: list[str]) -> ContextWindow:
        budget_chars = self.max_tokens * 4
        kept: list[str] = []
        used = 0
        dropped = 0
        for frag in fragments:
            if used + len(frag) <= budget_chars:
                kept.append(frag)
                used += len(frag)
            else:
                dropped += 1
        text = "\n\n".join(kept)
        return ContextWindow(
            text=text,
            fragments=kept,
            token_estimate=used // 4,
            dropped=dropped,
        )
