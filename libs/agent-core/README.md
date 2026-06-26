# agent-core

Shared, abstract building blocks for every agent in the monorepo (items 1-36 of
the abstraction map). The only framework assumption is **Strands Agents**.

Each concept has its own folder with a `base.py` defining an ABC / Protocol plus
its config model. Concrete implementations subclass these and are wired together
through `agent_core.infra.di`.

Sub-packages:

- `core/` - Agent, Persona, Reasoning, Termination, Evaluation (A: 1-5)
- `capabilities/` - Model, Prompt, Context, Tool, ToolRegistry, OutputParser,
  Memory, Retrieval (B: 6-13)
- `state/` - Agent/Shared/Session/Workflow state, Schema, Persistence,
  Transition (C: 14-20)
- `tasks/` - Task, Decomposition, Aggregation (D: 21-23)
- `multiagent/` - Communication, Orchestration, Registry, EventBus, Runtime,
  HumanInLoop (E: 24-29)
- `infra/` - Errors, Observability, Guardrails, Budget, Caching, Hooks, DI
  (F: 30-36)
