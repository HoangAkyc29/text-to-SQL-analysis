from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import DecisionContext

from project_core.config.loader import load_project_config
from project_core.domain.analysis.iv_analyzer import analyze_datasets
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.service.supermarket_agent import SupermarketAgentService

logger = logging.getLogger(__name__)


class DataAnalystService(SupermarketAgentService):
    def skill_reference(self) -> str:
        """Expose analyst skill docs for tooling/tests."""
        return self.llm_system_prompt(guide="analyze_guide")

    def decide(self, ctx: DecisionContext) -> Any:
        payload_in, meta = self.parse_payload(ctx)
        manifest = payload_in.get("dataset_manifest") or meta.get("dataset_manifest") or {}
        profile = payload_in.get("result_profile") or meta.get("result_profile") or {}
        brief_data = payload_in.get("brief") or meta.get("brief") or {}
        brief = AnalysisBrief.model_validate(brief_data)
        query_meta = payload_in.get("query_meta") or meta.get("query_meta") or []
        out_dir = payload_in.get("out_dir") or meta.get("out_dir") or "data/artifacts/out"
        max_steps = int(
            payload_in.get("max_steps")
            or meta.get("max_steps")
            or load_project_config().pipeline.iv_max_steps
        )
        analysis_tools = payload_in.get("analysis_tools") or meta.get("analysis_tools") or []
        recipe_candidates = payload_in.get("recipe_candidates") or meta.get("recipe_candidates") or []

        permissions = self.resolve_permissions(payload_in, meta)
        cp = self.context_policy
        if permissions is None or not cp.can_invoke_tool(permissions, "IV", "run_analysis_script"):
            return self.json_response(
                ctx,
                {
                    "action": "data_feedback",
                    "data_feedback": {
                        "needs_sql_retry": False,
                        "issue": "tool_not_granted",
                        "summary": "run_analysis_script not granted",
                        "diagnosis": "impossible",
                    },
                    "impossible_reason": "tool_not_granted:python-sandbox:run_analysis_script",
                },
            )
        recipe_candidates = [
            c
            for c in recipe_candidates
            if not c.get("tool_id") or cp.can_invoke_function(permissions, c.get("tool_id", ""))
        ]

        analysis_plan = payload_in.get("analysis_plan") or meta.get("analysis_plan")
        execution_plan = payload_in.get("execution_plan") or meta.get("execution_plan")
        domain_rules_excerpt = payload_in.get("domain_rules_excerpt") or meta.get("domain_rules_excerpt") or ""

        cfg = load_project_config()
        if self._should_use_brain(cfg):
            brain_payload = self._run_brain(
                brief=brief,
                manifest=manifest,
                profile=profile,
                out_dir=out_dir,
                max_steps=max_steps,
                query_meta=query_meta,
                recipe_candidates=recipe_candidates,
                domain_rules_excerpt=domain_rules_excerpt,
                permissions=permissions,
            )
            if brain_payload is not None:
                return self.json_response(ctx, brain_payload)

        payload = analyze_datasets(
            brief=brief,
            manifest=manifest,
            profile=profile,
            out_dir=out_dir,
            max_steps=max_steps,
            query_meta=query_meta,
            analysis_tools=analysis_tools,
            recipe_candidates=recipe_candidates,
            analysis_plan=analysis_plan,
            execution_plan=execution_plan,
            domain_rules_excerpt=domain_rules_excerpt,
        )
        return self.json_response(ctx, payload)

    @staticmethod
    def _should_use_brain(cfg: Any) -> bool:
        """LLM reasoning brain is used only when enabled and a real LLM is available."""
        if os.getenv("ALLOW_LLM_STUB") == "1":
            return False
        return bool(getattr(cfg.pipeline, "iv_llm_enabled", False))

    def _run_brain(
        self,
        *,
        brief: AnalysisBrief,
        manifest: dict[str, Any],
        profile: dict[str, Any],
        out_dir: str,
        max_steps: int,
        query_meta: list[dict[str, Any]],
        recipe_candidates: list[dict[str, Any]],
        domain_rules_excerpt: str,
        permissions: Any,
    ) -> dict[str, Any] | None:
        """Run the Agent IV reasoning loop; return None to trigger fallback."""
        try:
            from project_core.domain.analysis.iv_brain import run_analysis_brain
            from project_core.llm.openrouter_client import OpenRouterClient
            from project_core.models.loader import agent_profile

            return run_analysis_brain(
                brief=brief,
                manifest=manifest,
                profile=profile,
                out_dir=out_dir,
                max_steps=max_steps,
                query_meta=query_meta,
                recipe_candidates=recipe_candidates,
                domain_rules_excerpt=domain_rules_excerpt,
                permissions=permissions,
                context_policy=self.context_policy,
                llm=OpenRouterClient(),
                profile_name=agent_profile("analyst"),
                system_prompt=self.llm_system_prompt(guide="reason_loop_guide"),
            )
        except Exception:
            logger.warning("Agent IV brain failed; falling back to analyze_datasets", exc_info=True)
            return None


def build_service(config: PlatformConfig, spec: AgentSpec) -> DataAnalystService:
    skills_root = Path(__file__).resolve().parent / "skills"
    return DataAnalystService(config, spec, skills_root=skills_root, agent_key="IV")
