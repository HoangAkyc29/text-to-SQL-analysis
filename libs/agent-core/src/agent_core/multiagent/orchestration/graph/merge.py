"""Merge strategies for parallel node outputs."""

from __future__ import annotations

from typing import Any

from agent_core.tasks.aggregation.base import ConcatMerge, MajorityVote, ResultAggregator


def merge_results(strategy: str, results: list[Any]) -> Any:
    """Combine parallel branch outputs using *strategy*."""
    if strategy == "state_map":
        raise ValueError("state_map merge is handled by the graph engine, not merge_results")
    aggregator: ResultAggregator
    if strategy == "majority_vote":
        aggregator = MajorityVote()
    elif strategy == "last":
        return results[-1] if results else None
    else:
        aggregator = ConcatMerge()
    return aggregator.aggregate(results)


def merge_state_map(
    state_map: dict[str, str],
    agent_outputs: list[tuple[str, Any, dict[str, Any]]],
) -> dict[str, Any]:
    """Map parallel agent outputs to named state channels (not yet applied)."""
    channels: dict[str, Any] = {}
    for agent_id, payload, updates in agent_outputs:
        channel = state_map.get(agent_id)
        if not channel:
            continue
        value = updates.get(channel)
        if value is None and isinstance(payload, dict):
            value = payload.get(channel, payload)
        if value is not None:
            channels[channel] = value
    return channels
