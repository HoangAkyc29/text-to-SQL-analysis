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
        max_ops = int(
            payload_in.get("max_steps")
            or meta.get("max_steps")
            or load_project_config().pipeline.iv_max_steps
        )
        max_planner_turns = int(
            payload_in.get("max_planner_turns")
            or meta.get("max_planner_turns")
            or load_project_config().pipeline.iv_max_planner_turns
        )
        analysis_tools = payload_in.get("analysis_tools") or meta.get("analysis_tools") or []
        recipe_candidates = payload_in.get("recipe_candidates") or meta.get("recipe_candidates") or []

        permissions = self.resolve_permissions(payload_in, meta)
        cp = self.context_policy
        if permissions is None or not cp.can_invoke_tool(permissions, "IV", "run_analysis_op"):
            return self.json_response(
                ctx,
                {
                    "action": "data_feedback",
                    "data_feedback": {
                        "needs_sql_retry": False,
                        "issue": "tool_not_granted",
                        "summary": "run_analysis_op not granted",
                        "diagnosis": "impossible",
                    },
                    "impossible_reason": "tool_not_granted:run_analysis_op",
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
        output_table_semantics = (
            payload_in.get("output_table_semantics") or meta.get("output_table_semantics") or []
        )
        output_column_semantics = (
            payload_in.get("output_column_semantics") or meta.get("output_column_semantics") or []
        )

        cfg = load_project_config()
        if self._should_use_brain(cfg):
            brain_payload = self._run_brain(
                brief=brief,
                manifest=manifest,
                profile=profile,
                out_dir=out_dir,
                max_steps=max_ops,
                max_planner_turns=max_planner_turns,
                query_meta=query_meta,
                recipe_candidates=recipe_candidates,
                domain_rules_excerpt=domain_rules_excerpt,
                output_table_semantics=output_table_semantics,
                output_column_semantics=output_column_semantics,
                analysis_plan=analysis_plan,
                execution_plan=execution_plan,
                permissions=permissions,
            )
            if brain_payload is not None:
                # If the LLM loop returns complete/partial without files,
                # fall back to deterministic analysis so users still get exports
                # when SQL data is already present (including planner_failed@step0).
                action = str(brain_payload.get("action") or "")
                arts = brain_payload.get("artifact_paths") or []
                steps = int(brain_payload.get("sandbox_steps") or 0)
                if action in {"complete", "partial"} and not arts:
                    logger.warning(
                        "Agent IV brain returned %s with %s sandbox steps and no artifacts; "
                        "falling back to analyze_datasets",
                        action,
                        steps,
                    )
                else:
                    return self.json_response(ctx, brain_payload)

        payload = analyze_datasets(
            brief=brief,
            manifest=manifest,
            profile=profile,
            out_dir=out_dir,
            max_steps=max_ops,
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
        max_planner_turns: int,
        query_meta: list[dict[str, Any]],
        recipe_candidates: list[dict[str, Any]],
        domain_rules_excerpt: str,
        output_table_semantics: list[dict[str, Any]],
        output_column_semantics: list[dict[str, Any]],
        analysis_plan: dict[str, Any] | None,
        execution_plan: dict[str, Any] | None,
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
                max_planner_turns=max_planner_turns,
                query_meta=query_meta,
                recipe_candidates=recipe_candidates,
                domain_rules_excerpt=domain_rules_excerpt,
                output_table_semantics=output_table_semantics,
                output_column_semantics=output_column_semantics,
                analysis_plan=analysis_plan,
                execution_plan=execution_plan,
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
