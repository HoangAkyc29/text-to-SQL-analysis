from __future__ import annotations

from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.contracts.workflow import PermissionsSnapshot, WorkflowState
from project_core.domain.memory.session_bundle import SessionBundle


class ContextPolicy:
    def build_request_context(
        self,
        agent: str,
        actor_id: str,
        session: SessionBundle,
        *,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ctx: dict[str, Any] = {"agent": agent, "actor_id": actor_id}
        if agent == "I":
            ctx.update(
                {
                    "transcript": session.transcript,
                    "workflow_summary": _workflow_summary(session.workflow),
                    "clarification_request": extra.get("clarification_request") if extra else None,
                }
            )
        elif agent == "II":
            ctx.update(
                {
                    "brief": session.workflow.brief.model_dump() if session.workflow and session.workflow.brief else {},
                    "workflow_steps": [s.model_dump() for s in (session.workflow.steps if session.workflow else [])],
                    "inbox": extra or {},
                }
            )
        elif agent == "III":
            ctx.update(extra or {})
        elif agent == "IV":
            ctx.update(extra or {})
        return ctx

    def allowed_mcp_tools(self, agent: str) -> list[str]:
        if agent == "II":
            return ["validate_sql"]
        if agent == "III":
            return ["explain_sql", "get_schema_snapshot"]
        if agent == "IV":
            return ["run_analysis_script", "preview_dataframe", "export_excel", "plot_chart", "load_dataset"]
        return []

    def filter_schema_excerpt(self, agent: str, snapshot: PermissionsSnapshot, catalog_tables: dict[str, Any]) -> dict[str, Any]:
        allowed = {t.lower() for t in snapshot.allowed_tables}
        return {k: v for k, v in catalog_tables.items() if k.lower() in allowed}


def _workflow_summary(workflow: WorkflowState | None) -> dict[str, Any]:
    if workflow is None:
        return {}
    return {
        "status": workflow.status.value,
        "active_analysis_id": workflow.active_analysis_id,
        "last_outcome": workflow.last_outcome,
    }
