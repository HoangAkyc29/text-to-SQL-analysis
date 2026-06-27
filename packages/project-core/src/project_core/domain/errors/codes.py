"""Application error codes."""

from __future__ import annotations


class ProjectError(Exception):
    code: str = "PROJECT_ERROR"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


class LLMProviderError(ProjectError):
    code = "LLM_PROVIDER_ERROR"


class PolicyViolationError(ProjectError):
    code = "POLICY_VIOLATION"


class BudgetExceededError(ProjectError):
    code = "BUDGET_EXCEEDED"


class ClarifyRoundsExceededError(ProjectError):
    code = "CLARIFY_ROUNDS_EXCEEDED"


class AgentUnavailableError(ProjectError):
    code = "AGENT_UNAVAILABLE"


class ContractInvalidError(ProjectError):
    code = "CONTRACT_INVALID"


class WorkflowStaleError(ProjectError):
    code = "WORKFLOW_STALE"
