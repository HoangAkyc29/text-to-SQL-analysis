from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import DecisionContext

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.llm.openrouter_client import OpenRouterClient
from project_core.models.loader import agent_profile
from project_core.service.supermarket_agent import SupermarketAgentService


class SqlPlannerService(SupermarketAgentService):
    def decide(self, ctx: DecisionContext) -> Any:
        meta = ctx.request.metadata or {}
        payload_in = json.loads(ctx.request.message or "{}") if ctx.request.message else {}
        brief = AnalysisBrief.model_validate(payload_in.get("brief") or meta.get("brief") or {})
        inbox = payload_in.get("inbox") or meta.get("inbox") or {}
        attempt = int(payload_in.get("attempt") or meta.get("attempt") or 1)

        if os.getenv("ALLOW_LLM_STUB") == "1":
            return self._stub_plan(ctx, brief, inbox, attempt)

        client = OpenRouterClient()
        result = client.chat(
            profile_name=agent_profile("sql_planner"),
            messages=[
                {"role": "system", "content": "You are Agent II SQL planner."},
                {"role": "user", "content": json.dumps({"brief": brief.model_dump(), "inbox": inbox, "attempt": attempt})},
            ],
            response_format={"type": "json_object"},
        )
        return self.json_response(ctx, json.loads(result.content))

    def _stub_plan(self, ctx: DecisionContext, brief: AnalysisBrief, inbox: dict, attempt: int):
        filters = brief.filters or {}
        if attempt == 1 and not filters.get("card_prefix") and "vip" in brief.intent.lower():
            req = ClarificationRequest(
                reason="missing_vip_definition",
                partial_brief=brief,
                questions=[
                    {
                        "id": "vip_card_prefix",
                        "prompt": "VIP được định nghĩa thế nào?",
                        "options": [
                            {"id": "prefix_e", "label": "Card bắt đầu E", "brief_value": {"filters": {"card_prefix": "E"}}},
                            {"id": "tier_vip", "label": "Tier VIP", "brief_value": {"filters": {"loyalty_tier": "VIP"}}},
                        ],
                        "maps_to_brief_field": "filters.card_prefix",
                    }
                ],
            )
            return self.json_response(ctx, {"action": "clarify", "clarification_request": req.model_dump()})
        sql = [
            "SELECT TOP 50000 c.customer_id, c.card_id, SUM(t.amount) AS total_amount FROM customers c JOIN transactions t ON c.customer_id=t.customer_id WHERE t.trans_code=221 GROUP BY c.customer_id, c.card_id",
            "SELECT TOP 50000 FORMAT(t.trans_date,'yyyy-MM') AS month, SUM(t.amount) AS monthly_amount FROM transactions t WHERE t.trans_code=221 GROUP BY FORMAT(t.trans_date,'yyyy-MM')",
        ]
        return self.json_response(
            ctx,
            {"action": "plan_sql", "sql_queries": sql, "reasoning": "VIP points analysis", "attempt": attempt},
        )


def build_service(config: PlatformConfig, spec: AgentSpec) -> SqlPlannerService:
    skills_root = Path(__file__).resolve().parent / "skills"
    return SqlPlannerService(config, spec, skills_root=skills_root, agent_key="II")
