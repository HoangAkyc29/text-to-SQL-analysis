from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import DecisionContext

from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.sql.policy_engine import PolicyEngine
from project_core.service.supermarket_agent import SupermarketAgentService

_CATALOG = SchemaCatalog.from_dictionary_dir()


class RiskReviewerService(SupermarketAgentService):
    def decide(self, ctx: DecisionContext) -> Any:
        meta = ctx.request.metadata or {}
        payload_in = json.loads(ctx.request.message or "{}") if ctx.request.message else {}
        sql = payload_in.get("sql") or meta.get("sql") or ""
        allowed_tables = list(payload_in.get("allowed_tables") or meta.get("allowed_tables") or [])
        schema_context = payload_in.get("schema_context") or meta.get("schema_context") or {}

        policy = PolicyEngine(_CATALOG, allowed_tables=allowed_tables or None)
        verdict = policy.validate(sql)

        if os.getenv("ALLOW_LLM_STUB") == "1":
            blocked = not verdict.allowed or any(
                tok in sql.lower() for tok in ("drop", "delete", "insert", "update", "exec ")
            )
            concerns = list(verdict.violations)
            if blocked and not concerns:
                concerns = ["forbidden_statement"]
            payload = {
                "verdict": "reject" if blocked else "approve",
                "concerns": concerns,
                "risk_feedback": None if not blocked else {"issue": concerns[0] if concerns else "blocked"},
                "schema_context_summary": {
                    "table_count": len(schema_context.get("tables") or []),
                    "has_domain_definitions": bool(schema_context.get("domain_definitions_excerpt")),
                },
            }
            return self.json_response(ctx, payload)

        return self.json_response(
            ctx,
            {
                "verdict": "approve" if verdict.allowed else "reject",
                "concerns": verdict.violations,
                "schema_context_summary": {"table_count": len(schema_context.get("tables") or [])},
            },
        )


def build_service(config: PlatformConfig, spec: AgentSpec) -> RiskReviewerService:
    skills_root = Path(__file__).resolve().parent / "skills"
    return RiskReviewerService(config, spec, skills_root=skills_root, agent_key="III")
