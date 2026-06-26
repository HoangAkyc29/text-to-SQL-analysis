"""Item 15 - Shared / Global State (blackboard)."""

from agent_core.state.shared_state.base import Blackboard
from agent_core.state.shared_state.in_memory import InMemoryBlackboard

__all__ = ["Blackboard", "InMemoryBlackboard"]
