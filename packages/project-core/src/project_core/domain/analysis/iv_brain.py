"""Agent IV LLM reasoning brain — tool-catalog ops only (no sandbox scripts).

    DatasetWorkingSet -> AnalysisPlanner(LLM) -> execute_op -> loop
                     -> sufficiency/critic -> ResponseAssembler
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from project_core.domain.analysis.feedback_coerce import try_validate_data_feedback
from project_core.domain.analysis.iv_analyzer import (
    _empty_feedback,
    _identifier_mismatch_feedback,
    _merge_external_paths,
    _probe_success_needs_fact_feedback,
)
from project_core.domain.analysis.iv_sufficiency import (
    assess_sufficiency,
    insufficiency_data_feedback,
)
from project_core.domain.analysis.ops import DatasetWorkingSet, execute_op
from project_core.domain.analysis.ops.registry import catalog_for_prompt
from project_core.domain.analysis.query_role_classifier import classify_query_roles
from project_core.domain.contracts.brief import AnalysisBrief

if TYPE_CHECKING:
    from project_core.domain.access.context_policy import ContextPolicy
    from project_core.domain.contracts.workflow import PermissionsSnapshot
    from project_core.llm.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)


class AnalysisPlanner:
    """One LLM turn: decide the next op or a terminal action."""

    def __init__(self, llm: "OpenRouterClient", profile_name: str, system_prompt: str) -> None:
        self._llm = llm
        self._profile_name = profile_name
        self._system_prompt = system_prompt
        self.tokens = 0

    def next_decision(self, state: dict[str, Any]) -> dict[str, Any]:
        result = self._llm.chat(
            profile_name=self._profile_name,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": json.dumps(state, ensure_ascii=False, default=str)},
            ],
            response_format={"type": "json_object"},
        )
        self.tokens += int(getattr(result, "usage_tokens", 0) or 0)
        content = str(getattr(result, "content", "") or "")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning(
                "IV planner returned invalid JSON content preview=%r",
                content[:300],
            )
            raise


def run_analysis_brain(
    *,
    brief: AnalysisBrief,
    manifest: dict[str, Any],
    profile: dict[str, Any],
    out_dir: str,
    max_steps: int,
    query_meta: list[dict[str, Any]] | None,
    recipe_candidates: list[dict[str, Any]] | None,
    domain_rules_excerpt: str,
    permissions: "PermissionsSnapshot",
    context_policy: "ContextPolicy",
    llm: "OpenRouterClient",
    profile_name: str,
    system_prompt: str,
    output_table_semantics: list[dict[str, Any]] | None = None,
    output_column_semantics: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Bounded LLM loop that only invokes catalog ops (never free-form scripts)."""
    paths = [q.get("path") for q in manifest.get("queries", []) if q.get("path")]
    paths, meta = _merge_external_paths(brief, paths, query_meta or [])
    # Rebuild manifest paths after external merge
    queries = []
    for i, p in enumerate(paths):
        m = meta[i] if i < len(meta) else {}
        queries.append(
            {
                "path": p,
                "ref": f"q{i}",
                "role": m.get("role"),
                "purpose": m.get("purpose"),
                "row_count": (manifest.get("queries") or [{}])[i].get("row_count")
                if i < len(manifest.get("queries") or [])
                else None,
            }
        )
    row_counts = {
        i: int((manifest.get("queries") or [{}])[i].get("row_count", 0) or 0)
        if i < len(manifest.get("queries") or [])
        else 0
        for i in range(len(paths))
    }
    # Prefer explicit row counts from merged query entries when present
    for i, q in enumerate(manifest.get("queries") or []):
        if i < len(paths) and q.get("row_count") is not None:
            row_counts[i] = int(q.get("row_count") or 0)

    mode, main_rows, probe_rows, _main_idxs, probe_idxs = classify_query_roles(
        meta, row_counts, num_queries=len(paths)
    )
    product_code = (brief.filters or {}).get("product_code") or (brief.filters or {}).get("sku")

    if mode == "probe_only_success":
        return _probe_success_needs_fact_feedback(brief, probe_idxs, row_counts, paths)
    if mode == "main_empty_probe_hit" and product_code:
        return _identifier_mismatch_feedback(str(product_code), probe_idxs, row_counts, paths)
    if profile.get("row_count", 0) == 0:
        return _empty_feedback(brief, product_code)

    work_dir = Path(out_dir) / "_ws"
    ws = DatasetWorkingSet.from_manifest(
        {"queries": queries},
        meta,
        work_dir=work_dir,
    )
    planner = AnalysisPlanner(llm, profile_name, system_prompt)

    observations: list[dict[str, Any]] = []
    steps_trace: list[dict[str, Any]] = []
    caveats: list[str] = []
    headline_metrics: dict[str, Any] = {"row_count": profile.get("row_count", 0)}
    steps_run = 0

    recipe_summaries = [
        {
            "tool_id": c.get("tool_id"),
            "name": c.get("name"),
            "intent_pattern": c.get("intent_pattern"),
            "score": c.get("score"),
            "steps": c.get("steps") or c.get("op_chain"),
        }
        for c in (recipe_candidates or [])
    ]

    terminal: dict[str, Any] | None = None
    while steps_run < max_steps:
        state = {
            "brief": brief.model_dump(),
            "domain_rules_excerpt": domain_rules_excerpt or "",
            "datasets": ws.list_profiles(),
            "op_catalog": catalog_for_prompt(),
            "output_table_semantics": list(output_table_semantics or []),
            "output_column_semantics": list(output_column_semantics or []),
            "recipe_candidates": recipe_summaries,
            "output_format": brief.output_format,
            "chart_spec": brief.chart_spec,
            "observations": observations,
            "steps_run": steps_run,
            "max_steps": max_steps,
            "remaining_steps": max_steps - steps_run,
            "artifacts": list(ws.artifact_paths),
        }
        try:
            decision = planner.next_decision(state)
        except Exception:
            logger.warning("IV planner LLM call failed at step %s", steps_run, exc_info=True)
            caveats.append("planner_failed")
            break

        action = str(decision.get("decision") or decision.get("action") or "finalize")

        if action == "data_feedback":
            fb_raw = decision.get("data_feedback") or {}
            fb, err = try_validate_data_feedback(fb_raw)
            if fb is None:
                logger.warning("IV brain data_feedback invalid: %s raw=%r", err, str(fb_raw)[:300])
                if mode == "all_empty" or profile.get("row_count", 0) == 0:
                    return _empty_feedback(brief, product_code)
                return _probe_success_needs_fact_feedback(brief, probe_idxs, row_counts, paths)
            payload: dict[str, Any] = {"action": "data_feedback", "data_feedback": fb.model_dump()}
            if decision.get("suggest_clarify"):
                payload["suggest_clarify"] = decision["suggest_clarify"]
            payload["steps_trace"] = steps_trace
            if ws.artifact_paths:
                payload["artifact_paths"] = list(ws.artifact_paths)
                payload["chart_artifacts"] = list(ws.chart_artifacts)
                payload["excel_artifacts"] = list(ws.excel_artifacts)
                payload["sandbox_steps"] = steps_run
            return payload

        if action == "suggest_clarify":
            return {
                "action": "suggest_clarify",
                "clarification_request": decision.get("clarification_request")
                or decision.get("suggest_clarify")
                or {},
                "steps_trace": steps_trace,
            }
        if action == "impossible":
            return {
                "action": "impossible",
                "reason": decision.get("reason") or "metric_not_mappable",
                "impossible_reason": decision.get("impossible_reason") or "not_solvable_with_data",
                "explanation_vi": decision.get("insight_vi") or decision.get("explanation_vi"),
                "steps_trace": steps_trace,
            }
        if action in ("finalize", "complete", "partial"):
            # Auto critic: brief coverage
            cov = execute_op(
                ws,
                "match_brief_coverage",
                {"brief": brief.model_dump()},
                out_dir=out_dir,
            )
            if cov.status == "ok" and cov.result.get("issue") == "insufficient_deliverable":
                caveats.append("brief_coverage_gap")
            _ensure_deliverable_exports(ws, brief, out_dir=out_dir, caveats=caveats)
            claimed = str(decision.get("status") or action)
            if claimed not in ("complete", "partial"):
                claimed = "complete" if action != "partial" else "partial"
            arts = list(ws.primary_artifacts or ws.artifact_paths)
            check = assess_sufficiency(
                brief,
                row_count=int(profile.get("row_count", 0) or 0),
                artifacts=arts,
                chart_artifacts=ws.chart_artifacts,
                excel_artifacts=ws.excel_artifacts,
                headline_metrics={
                    **headline_metrics,
                    **(decision.get("headline_metrics") or {}),
                },
                claimed_status=claimed,
            )
            if check.force_feedback:
                fb_payload = insufficiency_data_feedback(
                    brief,
                    check,
                    row_count=int(profile.get("row_count", 0) or 0),
                    artifacts=arts,
                )
                fb_payload["steps_trace"] = steps_trace
                fb_payload["sandbox_steps"] = steps_run
                if caveats:
                    fb_payload["caveats"] = list(
                        dict.fromkeys([*(fb_payload.get("caveats") or []), *caveats])
                    )[:8]
                return fb_payload
            if check.gaps:
                decision = {**decision, "status": "partial"}
                caveats.extend(check.gaps)
            terminal = decision
            break

        # run_op (or legacy run_step with op payload)
        if action in ("run_op", "run_step"):
            op = decision.get("op") or decision.get("step") or {}
            # Reject any attempt to run free-form scripts
            if op.get("script") or op.get("kind") == "script":
                steps_run += 1
                err_msg = "script_ops_disabled:use_catalog_ops"
                caveats.append(err_msg)
                observations.append({"op_id": "forbidden", "status": "error", "error": err_msg})
                steps_trace.append({"step_id": f"iv-step-{steps_run}", "status": "error", "error": err_msg})
                continue

            # Recipe chain: execute listed ops sequentially as one budgeted step group
            if op.get("kind") == "recipe" or (op.get("tool_id") and op.get("steps")):
                chain = op.get("steps") or []
                for cand in recipe_candidates or []:
                    if cand.get("tool_id") == op.get("tool_id"):
                        chain = cand.get("steps") or cand.get("op_chain") or chain
                        break
                for step_op in chain:
                    oid = str(step_op.get("op_id") or "")
                    oargs = dict(step_op.get("args") or {})
                    if step_op.get("dataset") and "dataset" not in oargs:
                        oargs["dataset"] = step_op["dataset"]
                    if step_op.get("save_as"):
                        oargs["save_as"] = step_op["save_as"]
                    res = execute_op(ws, oid, oargs, out_dir=out_dir)
                    steps_run += 1
                    observations.append(res.as_observation())
                    steps_trace.append(
                        {
                            "step_id": f"iv-step-{steps_run}",
                            "op_id": oid,
                            "status": res.status,
                            "error": res.error,
                            "thought": decision.get("thought"),
                        }
                    )
                    if res.status != "ok":
                        caveats.append(f"{oid}:{res.error or 'error'}")
                        break
                    if steps_run >= max_steps:
                        break
                continue

            op_id = str(op.get("op_id") or op.get("kind") or "")
            # Map legacy chart/excel kinds to catalog ops
            if op_id in {"chart", "plot"}:
                op_id = "plot_chart"
                oargs = dict(op.get("chart") or op.get("args") or {})
                oargs.setdefault("dataset", op.get("dataset") or op.get("dataset_index", "q0"))
                if isinstance(oargs.get("dataset"), int):
                    oargs["dataset"] = f"q{oargs['dataset']}"
            elif op_id == "excel":
                op_id = "export_excel"
                oargs = dict(op.get("args") or {})
                oargs.setdefault("dataset", op.get("dataset") or "q0")
            else:
                oargs = dict(op.get("args") or {})
                if op.get("dataset") is not None and "dataset" not in oargs:
                    ds = op.get("dataset")
                    oargs["dataset"] = f"q{ds}" if isinstance(ds, int) else str(ds)
                if op.get("dataset_index") is not None and "dataset" not in oargs:
                    oargs["dataset"] = f"q{int(op['dataset_index'])}"
                if op.get("save_as"):
                    oargs["save_as"] = op["save_as"]

            if not context_policy.can_invoke_tool(permissions, "IV", "run_analysis_op"):
                return {
                    "action": "data_feedback",
                    "data_feedback": {
                        "needs_sql_retry": False,
                        "issue": "tool_not_granted",
                        "summary": "run_analysis_op not granted",
                        "diagnosis": "impossible",
                    },
                    "impossible_reason": "tool_not_granted:run_analysis_op",
                }

            res = execute_op(ws, op_id, oargs, out_dir=out_dir)
            steps_run += 1
            obs = res.as_observation()
            observations.append(obs)
            steps_trace.append(
                {
                    "step_id": f"iv-step-{steps_run}",
                    "op_id": op_id,
                    "status": res.status,
                    "error": res.error,
                    "thought": decision.get("thought"),
                }
            )
            if res.status != "ok":
                caveats.append(f"{op_id}:{res.error or 'error'}")
            elif obs.get("empty_after_op"):
                caveats.append("empty_after_op")
            continue

        caveats.append(f"unknown_decision:{action}")
        break
    else:
        caveats.append("budget_exceeded")

    _ensure_deliverable_exports(ws, brief, out_dir=out_dir, caveats=caveats)
    arts = list(ws.primary_artifacts or ws.artifact_paths)
    assembled = _assemble_response(
        terminal=terminal,
        artifacts=arts,
        chart_artifacts=ws.chart_artifacts,
        excel_artifacts=ws.excel_artifacts,
        steps_trace=steps_trace,
        caveats=caveats,
        headline_metrics=headline_metrics,
        steps_run=steps_run,
        planner_tokens=planner.tokens,
    )
    post = assess_sufficiency(
        brief,
        row_count=int(profile.get("row_count", 0) or 0),
        artifacts=arts,
        chart_artifacts=ws.chart_artifacts,
        excel_artifacts=ws.excel_artifacts,
        headline_metrics=assembled.get("headline_metrics") or headline_metrics,
        claimed_status=str(assembled.get("action") or "partial"),
    )
    if post.force_feedback:
        fb_payload = insufficiency_data_feedback(
            brief,
            post,
            row_count=int(profile.get("row_count", 0) or 0),
            artifacts=arts,
        )
        fb_payload["steps_trace"] = steps_trace
        fb_payload["sandbox_steps"] = steps_run
        if caveats:
            fb_payload["caveats"] = list(dict.fromkeys([*(fb_payload.get("caveats") or []), *caveats]))[:8]
        if planner.tokens:
            fb_payload["usage_tokens"] = planner.tokens
        return fb_payload
    if post.gaps and assembled.get("action") == "complete":
        assembled["action"] = "partial"
        assembled["caveats"] = list(assembled.get("caveats") or []) + list(post.gaps)
        assembled["coverage"] = {"diagnosis": "partial", "gaps": list(post.gaps)[:5]}
    return assembled


def _ensure_deliverable_exports(
    ws: DatasetWorkingSet,
    brief: AnalysisBrief,
    *,
    out_dir: str,
    caveats: list[str],
) -> None:
    """If the planner forgot to export, write CSV/Excel from the richest dataset."""
    if ws.artifact_paths:
        return
    refs = ws.refs()
    if not refs:
        return
    preferred = [r for r in refs if not r.startswith("q") or "_" in r] or refs
    best_ref = preferred[-1]
    best_n = -1
    for ref in preferred:
        try:
            n = len(ws.get(ref).frame())
        except Exception:  # noqa: BLE001
            continue
        if n > best_n:
            best_n = n
            best_ref = ref
    if best_n <= 0:
        return
    formats = {str(x).strip().lower() for x in (brief.output_format or []) if str(x).strip()}
    want_excel = bool(formats & {"excel", "xlsx", "spreadsheet"})
    csv_res = execute_op(
        ws,
        "export_csv",
        {"dataset": best_ref, "filename": "analysis_result.csv", "primary": True},
        out_dir=out_dir,
    )
    if csv_res.status != "ok":
        caveats.append(f"auto_export_csv:{csv_res.error or 'error'}")
    elif not want_excel:
        caveats.append("auto_exported_csv")
    if want_excel:
        x_res = execute_op(
            ws,
            "export_excel",
            {"dataset": best_ref, "filename": "analysis_result.xlsx", "primary": True},
            out_dir=out_dir,
        )
        if x_res.status != "ok":
            caveats.append(f"auto_export_excel:{x_res.error or 'error'}")
        else:
            caveats.append("auto_exported_excel")


def _assemble_response(
    *,
    terminal: dict[str, Any] | None,
    artifacts: list[str],
    chart_artifacts: list[str],
    excel_artifacts: list[str],
    steps_trace: list[dict[str, Any]],
    caveats: list[str],
    headline_metrics: dict[str, Any],
    steps_run: int,
    planner_tokens: int,
) -> dict[str, Any]:
    status = "complete"
    insight_vi = None
    if terminal:
        status = str(terminal.get("status") or terminal.get("decision") or terminal.get("action") or "complete")
        if status not in ("complete", "partial"):
            status = "complete"
        fin = terminal.get("finalize") or terminal
        insight_vi = fin.get("insight_vi") or fin.get("explanation_vi") or terminal.get("insight_vi")
        headline_metrics = {**headline_metrics, **(fin.get("headline_metrics") or {})}
        caveats = caveats + list(fin.get("caveats") or [])

    has_success = bool(artifacts)
    if not terminal and not has_success:
        status = "partial"
    if any(c.startswith("planner_failed") for c in caveats) and not has_success:
        status = "partial"

    payload: dict[str, Any] = {
        "action": status,
        "headline_metrics": headline_metrics,
        "artifact_paths": artifacts,
        "chart_artifacts": chart_artifacts,
        "excel_artifacts": excel_artifacts,
        "caveats": caveats[:8],
        "sandbox_steps": steps_run,
        "steps_trace": steps_trace,
        "coverage": {
            "diagnosis": "full" if status == "complete" and has_success else "partial",
            "gaps": [c for c in caveats if ":" in c][:5],
        },
    }
    if insight_vi:
        payload["insight_vi"] = insight_vi
        payload["explanation_vi"] = insight_vi
    if planner_tokens:
        payload["usage_tokens"] = planner_tokens
    payload["op_chain"] = [
        {"op_id": s.get("op_id"), "status": s.get("status")}
        for s in steps_trace
        if s.get("op_id")
    ]
    return payload
