from __future__ import annotations

from typing import Any, Literal

from pydantic import ValidationError

from project_core.domain.contracts.agent_outputs import AnalystResponse, RiskReviewResponse, SqlPlannerResponse
from project_core.domain.errors.codes import ContractInvalidError

AgentKey = Literal["II", "III", "IV"]


def parse_agent_response(agent: AgentKey, raw: dict[str, Any]) -> SqlPlannerResponse | RiskReviewResponse | AnalystResponse:
    try:
        if agent == "II":
            return SqlPlannerResponse.model_validate(raw)
        if agent == "III":
            return RiskReviewResponse.model_validate(raw)
        return AnalystResponse.model_validate(raw)
    except ValidationError as exc:
        raise ContractInvalidError(f"Agent {agent} response invalid: {exc}") from exc
