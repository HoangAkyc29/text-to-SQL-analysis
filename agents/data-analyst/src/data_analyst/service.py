from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import DecisionContext

from project_core.service.supermarket_agent import SupermarketAgentService


class DataAnalystService(SupermarketAgentService):
    def decide(self, ctx: DecisionContext) -> Any:
        meta = ctx.request.metadata or {}
        payload_in = json.loads(ctx.request.goal or "{}") if ctx.request.goal else {}
        manifest = payload_in.get("dataset_manifest") or meta.get("dataset_manifest") or {}
        profile = payload_in.get("result_profile") or meta.get("result_profile") or {}
        if os.getenv("ALLOW_LLM_STUB") == "1":
            if profile.get("row_count", 0) == 0:
                return self.json_response(
                    ctx,
                    {
                        "action": "data_feedback",
                        "data_feedback": {
                            "needs_sql_retry": True,
                            "issue": "empty_result",
                            "summary": "No rows returned",
                            "suggested_intent_fix": "expand filters",
                        },
                    },
                )
            paths = [q.get("path") for q in manifest.get("queries", []) if q.get("path")]
            out_paths = [p.replace("raw", "out").replace(".parquet", ".xlsx") for p in paths]
            return self.json_response(
                ctx,
                {
                    "action": "complete",
                    "headline_metrics": {"row_count": profile.get("row_count", 0)},
                    "artifact_paths": out_paths,
                    "caveats": [],
                },
            )
        return self.json_response(ctx, {"action": "complete", "headline_metrics": {}, "artifact_paths": []})


def build_service(config: PlatformConfig, spec: AgentSpec) -> DataAnalystService:
    skills_root = Path(__file__).resolve().parent / "skills"
    return DataAnalystService(config, spec, skills_root=skills_root, agent_key="IV")
