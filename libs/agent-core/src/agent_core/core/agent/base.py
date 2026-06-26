"""Item 1 - Agent (core lifecycle).

Defines the canonical agent loop as four overridable steps:

    observe()  -> gather inputs / perceptions into an Observation
    plan()     -> decide next action(s) given the Observation -> Plan
    step()     -> execute one Plan increment -> StepResult
    run()      -> loop observe/plan/step until a Termination condition fires

The base implementation provides the ``run`` driver and leaves the cognitive
steps abstract. A Strands-backed implementation lives in ``strands_agent.py``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from commons.types import JSONValue

if TYPE_CHECKING:
    from agent_core.core.evaluation.base import AbstractEvaluator
    from agent_core.core.persona.base import Persona
    from agent_core.core.reasoning.base import ReasoningStrategy
    from agent_core.core.termination.base import TerminationCondition
    from agent_core.state.agent_state.base import AgentState


@dataclass(slots=True)
class AgentContext:
    """Everything an agent needs for one invocation."""

    goal: str
    inputs: dict[str, JSONValue] = field(default_factory=dict)
    session_id: str = ""
    actor_id: str = "anonymous"
    metadata: dict[str, JSONValue] = field(default_factory=dict)


@dataclass(slots=True)
class Observation:
    """Result of ``observe``: the perceived state for this turn."""

    content: str
    artifacts: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Plan:
    """Result of ``plan``: the intended next action(s)."""

    rationale: str
    actions: list[dict[str, Any]] = field(default_factory=list)
    finished: bool = False


@dataclass(slots=True)
class StepResult:
    """Result of executing one ``step``."""

    output: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    done: bool = False
    raw: dict[str, Any] = field(default_factory=dict)


class AbstractAgent(ABC):
    """Base agent with a pluggable observe/plan/step/run loop.

    Subclasses inject collaborators (persona, reasoning, termination, evaluator,
    state) and implement the three cognitive steps. ``run`` orchestrates them.
    """

    def __init__(
        self,
        *,
        name: str,
        persona: "Persona | None" = None,
        reasoning: "ReasoningStrategy | None" = None,
        termination: "TerminationCondition | None" = None,
        evaluator: "AbstractEvaluator | None" = None,
        state: "AgentState | None" = None,
        max_iterations: int = 8,
    ) -> None:
        self.name = name
        self.persona = persona
        self.reasoning = reasoning
        self.termination = termination
        self.evaluator = evaluator
        self.state = state
        self.max_iterations = max_iterations

    # --- cognitive steps (implement these) --------------------------------
    @abstractmethod
    def observe(self, context: AgentContext) -> Observation:
        """Perceive: assemble the inputs/context for this turn."""

    @abstractmethod
    def plan(self, context: AgentContext, observation: Observation) -> Plan:
        """Decide: choose the next action(s)."""

    @abstractmethod
    def step(self, context: AgentContext, plan: Plan) -> StepResult:
        """Act: execute one increment of the plan."""

    # --- driver loop (usually keep as-is) ---------------------------------
    def run(self, context: AgentContext) -> StepResult:
        """Drive observe/plan/step until termination, then optionally reflect."""
        last: StepResult = StepResult(output="")
        for iteration in range(self.max_iterations):
            observation = self.observe(context)
            plan = self.plan(context, observation)
            last = self.step(context, plan)
            if plan.finished or last.done or self._should_stop(iteration, last):
                break
        return self._reflect(context, last)

    # --- helpers ----------------------------------------------------------
    def _should_stop(self, iteration: int, result: StepResult) -> bool:
        if self.termination is None:
            return False
        return self.termination.should_stop(iteration=iteration, last_output=result.output)

    def _reflect(self, context: AgentContext, result: StepResult) -> StepResult:
        """Optional self-evaluation pass; default is a no-op passthrough."""
        if self.evaluator is None:
            return result
        verdict = self.evaluator.evaluate(result.output, context=context.inputs)
        result.raw["evaluation"] = {"score": verdict.score, "feedback": verdict.feedback}
        return result
