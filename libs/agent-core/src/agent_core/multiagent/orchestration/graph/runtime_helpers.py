"""Graph execution helpers: response parsing, debate rotation."""

from __future__ import annotations

from typing import Any

from agent_core.multiagent.orchestration.graph.model import DebateRotation, GraphNodeSpec


def parse_executor_result(result: Any) -> tuple[Any, dict[str, Any]]:
    """Extract ``(payload, state_updates)`` from an executor return value."""
    state_updates: dict[str, Any] = {}
    if hasattr(result, "payload"):
        payload = result.payload
        state_updates = dict(getattr(result, "state_updates", None) or {})
        if not state_updates and isinstance(payload, dict):
            nested = payload.get("state_updates")
            if isinstance(nested, dict):
                state_updates = nested
        return payload, state_updates
    if isinstance(result, dict):
        updates = result.get("state_updates")
        if isinstance(updates, dict):
            state_updates = updates
        return result, state_updates
    return result, state_updates


def speakers_for_round(spec: GraphNodeSpec, round_idx: int) -> list[str]:
    """Return participant order for a debate round."""
    participants = list(spec.participants)
    if not participants:
        return []
    rotation: DebateRotation = spec.rotation
    if rotation == "round_robin":
        return participants
    if round_idx % 2 == 1:
        return list(reversed(participants))
    return participants


def debate_turn_metadata(
    *,
    node_id: str,
    round_idx: int,
    speaker: str,
    participants: list[str],
    transcript: list[Any],
    role: str = "participant",
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "round": round_idx,
        "speaker": speaker,
        "participants": list(participants),
        "transcript": list(transcript),
        "role": role,
    }
