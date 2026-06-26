"""Strands-backed reference implementation of :class:`AbstractAgent`.

This is the one place where the "framework = Strands Agents" assumption is
realised. It maps the abstract observe/plan/step loop onto a single Strands
``Agent`` invocation per step. Agents in the monorepo typically subclass this
and override ``observe``/``plan`` to inject their own context-building logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from commons.logging import get_logger

from agent_core.core.agent.base import (
    AbstractAgent,
    AgentContext,
    Observation,
    Plan,
    StepResult,
)

if TYPE_CHECKING:
    from agent_core.capabilities.context.base import ContextBuilder
    from agent_core.capabilities.models.base import ModelProvider
    from agent_core.capabilities.output_parsers.base import OutputParser
    from agent_core.capabilities.prompts.base import PromptTemplate
    from agent_core.core.reasoning.base import ReasoningStrategy

log = get_logger(__name__)


class StrandsAgent(AbstractAgent):
    """An :class:`AbstractAgent` that delegates a step to ``strands.Agent``.

    Collaborators:
      - ``model``: a :class:`ModelProvider` that yields a Strands model object.
      - ``tools``: list of Strands-compatible tools (native or MCP-adapted).
      - ``system_prompt`` / ``prompt``: static prompt or a PromptTemplate.
      - ``context_builder``: optional ContextBuilder for ``observe``.
      - ``output_parser``: optional parser applied to the final text.
    """

    def __init__(
        self,
        *,
        name: str,
        model: "ModelProvider",
        tools: list[Any] | None = None,
        system_prompt: str = "You are a helpful agent.",
        prompt: "PromptTemplate | None" = None,
        context_builder: "ContextBuilder | None" = None,
        output_parser: "OutputParser | None" = None,
        reasoning: "ReasoningStrategy | None" = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name=name, **kwargs)
        self._model = model
        self._tools = tools or []
        self._system_prompt = system_prompt
        self._prompt = prompt
        self._context_builder = context_builder
        self._output_parser = output_parser
        self._reasoning = reasoning

    def observe(self, context: AgentContext) -> Observation:
        if self._context_builder is not None:
            window = self._context_builder.build(
                goal=context.goal, inputs=context.inputs, session_id=context.session_id
            )
            return Observation(content=window.text, artifacts={"window": window})
        return Observation(content=context.goal, artifacts=dict(context.inputs))

    def plan(self, context: AgentContext, observation: Observation) -> Plan:
        # The Strands agent does its own internal planning/tool-selection, so the
        # outer Plan is a single "invoke the model with this message" action.
        message = observation.content
        if self._prompt is not None:
            message = self._prompt.render({"goal": context.goal, **context.inputs})
        return Plan(rationale="single strands invocation", actions=[{"message": message}], finished=True)

    def step(self, context: AgentContext, plan: Plan) -> StepResult:
        message = plan.actions[0]["message"] if plan.actions else context.goal

        if self._reasoning is not None:
            from agent_core.core.reasoning.loop import ReasoningLoop

            loop = ReasoningLoop(self._reasoning)
            text, trace = loop.run(message, lambda m: self._invoke_strands(m))
            raw: dict[str, Any] = {
                "reasoning_trace": [
                    {"thought": s.thought, "action": s.action, "observation": s.observation}
                    for s in trace
                ]
            }
            if self._output_parser is not None:
                raw["parsed"] = self._output_parser.parse(text)
            return StepResult(output=text, done=True, raw=raw)

        text = self._invoke_strands(message)
        if self._output_parser is not None:
            parsed = self._output_parser.parse(text)
            return StepResult(output=text, done=True, raw={"parsed": parsed})
        return StepResult(output=text, done=True, raw={"strands_result": text})

    def _invoke_strands(self, message: str) -> str:
        from strands import Agent as _StrandsAgent

        agent = _StrandsAgent(
            model=self._model.create(),
            system_prompt=self._render_system_prompt(),
            tools=list(self._tools),
        )
        result = agent(message)
        return str(getattr(result, "content", result))

    def _render_system_prompt(self) -> str:
        parts = [self._system_prompt.strip()]
        if self.persona is not None:
            parts.append(self.persona.to_system_prompt())
        return "\n\n".join(p for p in parts if p)
