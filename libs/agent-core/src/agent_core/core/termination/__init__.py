"""Item 4 - Termination / Stopping condition."""

from agent_core.core.termination.base import (
    CompositeTermination,
    MaxIterations,
    TerminationCondition,
)

__all__ = ["CompositeTermination", "MaxIterations", "TerminationCondition"]
