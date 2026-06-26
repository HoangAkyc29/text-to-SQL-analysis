"""Reasoning strategy factory."""

from __future__ import annotations

from typing import Any

from agent_core.core.reasoning.base import ReasoningStrategy
from agent_core.core.reasoning.chain_of_thought import ChainOfThoughtStrategy
from agent_core.core.reasoning.passthrough import PassthroughStrategy
from agent_core.core.reasoning.plan_execute import PlanAndExecuteStrategy
from agent_core.core.reasoning.react import ReActStrategy

_REGISTRY: dict[str, type[ReasoningStrategy]] = {
    "passthrough": PassthroughStrategy,
    "none": PassthroughStrategy,
    "cot": ChainOfThoughtStrategy,
    "chain_of_thought": ChainOfThoughtStrategy,
    "react": ReActStrategy,
    "plan_execute": PlanAndExecuteStrategy,
}


def build_reasoning(name: str | None, **kwargs: Any) -> ReasoningStrategy | None:
    if not name:
        return None
    key = name.lower().strip()
    cls = _REGISTRY.get(key)
    if cls is None:
        raise ValueError(f"Unknown reasoning strategy: {name}")
    return cls(**kwargs)
