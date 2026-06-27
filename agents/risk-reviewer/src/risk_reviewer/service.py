from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import DecisionContext

from project_core.service.supermarket_agent import SupermarketAgentService


class RiskReviewerService(SupermarketAgentService):
    def decide(self, ctx: DecisionContext) -> Any:
        meta = ctx.request.metadata or {}
        payload_in = json.loads(ctx.request.goal or "{}") if ctx.request.goal else {}
        sql = payload_in.get("sql") or meta.get("sql") or ""
        if os.getenv("ALLOW_LLM_STUB") == "1":
            blocked = any(tok in sql.lower() for tok in ("drop", "delete", "insert"))
            payload = {
                "verdict": "reject" if blocked else "approve",
                "concerns": [] if not blocked else ["forbidden_statement"],
                "risk_feedback": None if not blocked else {"issue": "forbidden_statement"},
            }
            return self.json_response(ctx, payload)
        return self.json_response(ctx, {"verdict": "approve", "concerns": []})


def build_service(config: PlatformConfig, spec: AgentSpec) -> RiskReviewerService:
    skills_root = Path(__file__).resolve().parent / "skills"
    return RiskReviewerService(config, spec, skills_root=skills_root, agent_key="III")
