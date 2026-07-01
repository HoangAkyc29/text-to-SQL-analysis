from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from agent_core.infra.budget.base import BudgetExceeded, BudgetGuard, BudgetLimits

from project_core.config.loader import load_project_config
from project_core.domain.errors.codes import BudgetExceededError


@dataclass
class TraceBudget:
    spent: dict[str, int] = field(default_factory=lambda: {"I": 0, "II": 0, "III": 0, "IV": 0, "tokens": 0})

    def charge(self, agent: str, *, calls: int = 1, tokens: int = 0) -> None:
        self.spent[agent] = self.spent.get(agent, 0) + calls
        self.spent["tokens"] = self.spent.get("tokens", 0) + tokens


class SessionTraceBudget:
    """Shared trace budget for gateway Agent I calls + pipeline agents II–IV."""

    def __init__(self, trace_budget: TraceBudget | None = None) -> None:
        self.trace_budget = trace_budget or TraceBudget()
        self.guard = SupermarketBudgetGuard(self.trace_budget)

    def check_agent(self, agent: str) -> None:
        self.guard.check_agent(agent)

    def record(self, agent: str, *, tokens: int = 0) -> None:
        self.guard.record(agent, tokens=tokens)


class SupermarketBudgetGuard(BudgetGuard):
    def __init__(self, trace_budget: TraceBudget) -> None:
        cfg = load_project_config().budget
        limits = BudgetLimits(max_tokens=cfg.max_tokens_per_trace)
        super().__init__(limits)
        self.trace_budget = trace_budget
        self.agent_caps = cfg.agent_caps

    def check_agent(self, agent: str) -> None:
        cap = self.agent_caps.get(agent, 99)
        if self.trace_budget.spent.get(agent, 0) >= cap:
            raise BudgetExceededError(f"Agent {agent} call cap exceeded")

    def record(self, agent: str, *, tokens: int = 0) -> None:
        self.check_agent(agent)
        self.trace_budget.charge(agent, calls=1, tokens=tokens)
        if self.trace_budget.spent["tokens"] > (self.limits.max_tokens or 0):
            raise BudgetExceededError("Token budget exceeded for trace")

    def charge(self, *, tokens: int = 0, cost_usd: float = 0.0, tool_calls: int = 0) -> None:
        self.trace_budget.charge("tokens", calls=0, tokens=tokens)
        if self.limits.max_tokens and self.trace_budget.spent["tokens"] > self.limits.max_tokens:
            raise BudgetExceeded()

    def remaining(self) -> BudgetLimits:
        used = self.trace_budget.spent.get("tokens", 0)
        max_t = self.limits.max_tokens
        return BudgetLimits(max_tokens=(max_t - used) if max_t else None)


class AgentInvoker(Protocol):
    def invoke(self, agent: str, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]: ...


class SqlGatewayClient(Protocol):
    def validate_sql(self, sql: str, actor_id: str) -> dict[str, Any]: ...
    def explain_sql(self, sql: str, actor_id: str) -> dict[str, Any]: ...
    def execute_readonly(self, sql: str, actor_id: str, *, target_db: str = "db2") -> dict[str, Any]: ...


class SandboxClient(Protocol):
    def run_tool(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]: ...
