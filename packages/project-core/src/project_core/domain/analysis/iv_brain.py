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
from project_core.domain.analysis.chart_reviewer import ChartReviewer
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
from project_core.domain.analysis.ops import DatasetWorkingSet, execute_op, list_op_ids
from project_core.domain.analysis.ops.registry import (
    catalog_for_prompt,
    missing_required_args,
    normalize_op_args,
)
from project_core.domain.analysis.query_role_classifier import classify_query_roles
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.iv_reasoning import (
    IVChecklistStatus,
    IVReasoningPhase,
    IVReasoningState,
)
from project_core.config.loader import load_project_config

if TYPE_CHECKING:
    from project_core.domain.access.context_policy import ContextPolicy
    from project_core.domain.contracts.workflow import PermissionsSnapshot
    from project_core.llm.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

_NON_MUTATING_OPS = {
    "list_datasets",
    "describe_columns",
    "head_rows",
    "sample_rows",
    "value_counts",
    "null_report",
    "assert_nonempty",
    "assert_columns_present",
    "match_brief_coverage",
    "detect_empty_after_filter",
    "grain_check",
}


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
    analysis_plan: dict[str, Any] | None = None,
    execution_plan: dict[str, Any] | None = None,
    max_planner_turns: int | None = None,
) -> dict[str, Any]:
    """Bounded LLM loop that only invokes catalog ops (never free-form scripts)."""
    manifest_queries = [q for q in manifest.get("queries", []) if q.get("path")]
    paths = [q["path"] for q in manifest_queries]
    planned_meta = query_meta or []
    aligned_meta: list[dict[str, Any]] = []
    for ordinal, query in enumerate(manifest_queries):
        query_index = int(query.get("query_index", ordinal) or 0)
        aligned_meta.append(
            dict(planned_meta[query_index])
            if query_index < len(planned_meta)
            else {"role": "main"}
        )
    paths, meta = _merge_external_paths(brief, paths, aligned_meta)
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
                "row_count": manifest_queries[i].get("row_count")
                if i < len(manifest_queries)
                else None,
                "requirement_ids": list(m.get("requirement_ids") or []),
            }
        )
    row_counts = {
        i: int(manifest_queries[i].get("row_count", 0) or 0)
        if i < len(manifest_queries)
        else 0
        for i in range(len(paths))
    }
    # Prefer explicit row counts from merged query entries when present
    for i, q in enumerate(manifest_queries):
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
    reasoning = IVReasoningState.from_brief(brief)
    op_budget = max(1, int(max_steps))
    planner_budget = max(
        5,
        int(
            max_planner_turns
            or load_project_config().pipeline.iv_max_planner_turns
        ),
    )
    effective_analysis_plan = analysis_plan or {
        "source": "deterministic_brief_checklist",
        "subtasks": [
            {
                "subtask_id": item.item_id,
                "requirement": item.requirement,
                "category": item.category,
            }
            for item in reasoning.checklist
        ],
    }
    visual_reviews: list[dict[str, Any]] = []
    reviewed_images: set[str] = set()
    reviewer = ChartReviewer(llm=llm) if load_project_config().pipeline.review_all_images else None
    if reviewer is not None:
        for ext in brief.external_sources or []:
            if not str(getattr(ext, "mime", "")).startswith("image/"):
                continue
            image_path = Path(str(ext.path))
            if not image_path.exists():
                continue
            review = reviewer.review(
                image_path,
                allowed_root=image_path.parent,
                chart_context={"intent": brief.intent, "title": ext.original_name},
            ).model_copy(update={"artifact_role": "uploaded_image"})
            visual_reviews.append(review.model_dump(mode="json"))
            reviewed_images.add(str(image_path.resolve()))
            if review.verdict != "pass":
                caveats.append(f"uploaded_image_review:{review.verdict}")

    def _review_pending_charts() -> None:
        if reviewer is None:
            return
        for chart_value in ws.chart_artifacts:
            chart_path = Path(chart_value)
            resolved_chart = str(chart_path.resolve())
            if resolved_chart in reviewed_images or not chart_path.exists():
                continue
            record = ws.artifact_for_path(chart_value)
            source_ref = record.source_refs[0] if record and record.source_refs else ""
            source_frame = ws.get(source_ref).frame() if source_ref and ws.has(source_ref) else None
            context = dict((record.metadata if record else {}).get("chart_spec") or {})
            context.update(
                {
                    "intent": brief.intent,
                    "row_count": len(source_frame) if source_frame is not None else 0,
                    "columns": list(source_frame.columns.astype(str))
                    if source_frame is not None
                    else [],
                }
            )
            review_path = chart_path
            for attempt in range(3):
                review = reviewer.review(
                    review_path,
                    allowed_root=out_dir,
                    source_data=source_frame,
                    chart_context=context,
                ).model_copy(update={"review_attempts": attempt + 1})
                visual_reviews.append(review.model_dump(mode="json"))
                reviewed_images.add(str(review_path.resolve()))
                if review.verdict == "pass" and attempt > 0:
                    for prior in visual_reviews[-(attempt + 1) : -1]:
                        prior["resolved"] = True
                if (
                    review.verdict != "replot"
                    or review.fix_args is None
                    or attempt >= 2
                    or source_frame is None
                    or not source_ref
                ):
                    if review.verdict != "pass":
                        caveats.append(f"chart_review:{review.verdict}")
                    break
                fix = review.fix_args.model_dump(exclude_none=True)
                plot_args = {
                    **context,
                    **{k: v for k, v in fix.items() if k not in {"width", "height", "orientation", "show_legend"}},
                    "dataset": source_ref,
                    "filename": f"{chart_path.stem}_reviewed_{attempt + 1}.png",
                    "primary": True,
                }
                if fix.get("width") and fix.get("height"):
                    plot_args["figsize"] = [fix["width"], fix["height"]]
                if plot_args.get("kind") == "scatter":
                    plot_args["kind"] = "line"
                rerender = execute_op(ws, "plot_chart", plot_args, out_dir=out_dir)
                reasoning.record_mutation("plot_chart")
                observations.append(rerender.as_observation())
                steps_trace.append(
                    {
                        "step_id": f"iv-step-{reasoning.op_count}",
                        "op_id": "plot_chart",
                        "status": rerender.status,
                        "error": rerender.error,
                        "reason": "visual_review_replot",
                    }
                )
                if rerender.status != "ok" or not rerender.result.get("path"):
                    caveats.append("chart_replot_failed")
                    break
                if record:
                    record.primary = False
                    if record.path in ws.primary_artifacts:
                        ws.primary_artifacts.remove(record.path)
                review_path = Path(str(rerender.result["path"]))
                record = ws.artifact_for_path(str(review_path))
                context = dict((record.metadata if record else {}).get("chart_spec") or context)
                context.update(
                    {
                        "intent": brief.intent,
                        "row_count": len(source_frame),
                        "columns": list(source_frame.columns.astype(str)),
                    }
                )

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
    invalid_op_counts: dict[str, int] = {}
    while reasoning.planner_turns < planner_budget:
        state = {
            "brief": brief.model_dump(),
            "domain_rules_excerpt": domain_rules_excerpt or "",
            "datasets": ws.list_profiles(),
            "op_catalog": catalog_for_prompt(),
            "output_table_semantics": list(output_table_semantics or []),
            "output_column_semantics": list(output_column_semantics or []),
            "recipe_candidates": recipe_summaries,
            "analysis_plan": effective_analysis_plan,
            "execution_plan": execution_plan or {},
            "output_format": brief.output_format,
            "chart_spec": brief.chart_spec,
            "observations": observations,
            "reasoning": reasoning.for_prompt(),
            "planner_turns": reasoning.planner_turns,
            "op_count": reasoning.op_count,
            "steps_run": reasoning.op_count,
            "max_steps": max_steps,
            "max_planner_turns": planner_budget,
            "remaining_planner_turns": planner_budget - reasoning.planner_turns,
            "remaining_steps": max(0, op_budget - reasoning.analysis_ops),
            "artifacts": list(ws.artifact_paths),
            "artifact_manifests": [
                record.model_dump(mode="json") for record in ws.artifacts.values()
            ],
            "visual_reviews": visual_reviews,
        }
        try:
            reasoning.planner_turns += 1
            decision = planner.next_decision(state)
        except Exception:
            logger.warning(
                "IV planner LLM call failed at turn %s",
                reasoning.planner_turns,
                exc_info=True,
            )
            caveats.append("planner_failed")
            break

        action = str(decision.get("decision") or decision.get("action") or "finalize")
        if action in set(list_op_ids()):
            direct_args = dict(decision.get("args") or {})
            for key, value in decision.items():
                if (
                    key not in {"decision", "action", "args", "op", "thought", "reason"}
                    and value is not None
                    and key not in direct_args
                ):
                    direct_args[key] = value
            decision = {
                **decision,
                "decision": "run_op",
                "op": {
                    "op_id": action,
                    "args": direct_args,
                },
            }
            action = "run_op"

        if action == "assess":
            reasoning.advance_to(IVReasoningPhase.PLAN)
            continue
        if action == "plan":
            reasoning.advance_to(IVReasoningPhase.EXECUTE)
            continue

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
                payload["sandbox_steps"] = reasoning.op_count
            payload["planner_turns"] = reasoning.planner_turns
            payload["reasoning_state"] = reasoning.for_prompt()
            payload["visual_reviews"] = visual_reviews
            payload["artifact_manifests"] = [
                record.model_dump(mode="json") for record in ws.artifacts.values()
            ]
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
        if action in ("verify", "finalize", "complete", "partial"):
            _review_pending_charts()
            reasoning.advance_to(IVReasoningPhase.VERIFY)
            claimed = str(decision.get("status") or action)
            if claimed not in ("complete", "partial"):
                claimed = "complete" if action != "partial" else "partial"
            verification_metrics = {
                **headline_metrics,
                **(decision.get("headline_metrics") or {}),
            }
            check, arts = _verify_deliverable(
                reasoning=reasoning,
                ws=ws,
                brief=brief,
                out_dir=out_dir,
                caveats=caveats,
                row_count=int(profile.get("row_count", 0) or 0),
                headline_metrics=verification_metrics,
                claimed_status=claimed,
                semantic_labels=[
                    *(output_column_semantics or []),
                    *[
                        {"purpose": item.get("purpose")}
                        for item in meta
                        if isinstance(item, dict) and item.get("purpose")
                    ],
                ],
                mapped_requirement_ids={
                    str(requirement_id)
                    for item in meta
                    if isinstance(item, dict) and item.get("role") != "probe"
                    for requirement_id in (item.get("requirement_ids") or [])
                },
            )
            headline_metrics.update(verification_metrics)
            if check.force_feedback:
                fb_payload = insufficiency_data_feedback(
                    brief,
                    check,
                    row_count=int(profile.get("row_count", 0) or 0),
                    artifacts=arts,
                )
                fb_payload["steps_trace"] = steps_trace
                fb_payload["sandbox_steps"] = reasoning.op_count
                fb_payload["planner_turns"] = reasoning.planner_turns
                fb_payload["reasoning_state"] = reasoning.for_prompt()
                fb_payload["headline_metrics"] = verification_metrics
                fb_payload["coverage"] = {
                    "diagnosis": "partial",
                    "gaps": list(check.gaps),
                }
                fb_payload["verification"] = reasoning.verification.model_dump(mode="json")
                fb_payload["artifact_manifests"] = [
                    record.model_dump(mode="json") for record in ws.artifacts.values()
                ]
                fb_payload["visual_reviews"] = visual_reviews
                if caveats:
                    fb_payload["caveats"] = list(
                        dict.fromkeys([*(fb_payload.get("caveats") or []), *caveats])
                    )[:8]
                return fb_payload
            if action == "verify":
                continue
            if check.gaps:
                decision = {**decision, "status": "partial"}
                caveats.extend(check.gaps)
            if "auto_export_fallback_partial" in caveats:
                decision = {**decision, "status": "partial"}
            if any(
                r.get("verdict") != "pass" and not r.get("resolved")
                for r in visual_reviews
            ):
                decision = {**decision, "status": "partial"}
                caveats.append("visual_review_not_passed")
            reasoning.advance_to(IVReasoningPhase.FINALIZE)
            terminal = decision
            break

        # run_op (or legacy run_step with op payload)
        if action in ("run_op", "run_step"):
            if reasoning.phase in {IVReasoningPhase.VERIFY, IVReasoningPhase.FINALIZE}:
                reasoning.phase = IVReasoningPhase.EXECUTE
                reasoning.phase_history.append(IVReasoningPhase.EXECUTE)
            else:
                reasoning.advance_to(IVReasoningPhase.EXECUTE)
            op = decision.get("op") or decision.get("step") or {}
            # Reject any attempt to run free-form scripts
            if op.get("script") or op.get("kind") == "script":
                reasoning.record_observation()
                err_msg = "script_ops_disabled:use_catalog_ops"
                caveats.append(err_msg)
                observations.append({"op_id": "forbidden", "status": "error", "error": err_msg})
                steps_trace.append(
                    {
                        "step_id": f"iv-step-{reasoning.op_count}",
                        "status": "error",
                        "error": err_msg,
                    }
                )
                continue

            # Recipe chain: execute listed ops sequentially as one budgeted step group
            if op.get("kind") == "recipe" or (op.get("tool_id") and op.get("steps")):
                chain = op.get("steps") or []
                for cand in recipe_candidates or []:
                    if cand.get("tool_id") == op.get("tool_id"):
                        chain = cand.get("steps") or cand.get("op_chain") or chain
                        break
                for step_op in chain:
                    if reasoning.analysis_ops >= op_budget:
                        caveats.append("op_budget_exceeded")
                        break
                    oid = str(step_op.get("op_id") or "")
                    oargs = dict(step_op.get("args") or {})
                    if step_op.get("dataset") and "dataset" not in oargs:
                        oargs["dataset"] = step_op["dataset"]
                    if step_op.get("save_as"):
                        oargs["save_as"] = step_op["save_as"]
                    res = execute_op(ws, oid, oargs, out_dir=out_dir)
                    reasoning.analysis_ops += 1
                    if res.status == "ok" and oid not in _NON_MUTATING_OPS:
                        reasoning.record_mutation(oid)
                    else:
                        reasoning.record_observation()
                    observations.append(res.as_observation())
                    steps_trace.append(
                        {
                            "step_id": f"iv-step-{reasoning.op_count}",
                            "op_id": oid,
                            "args": oargs,
                            "dataset": oargs.get("dataset"),
                            "save_as": oargs.get("save_as"),
                            "status": res.status,
                            "error": res.error,
                            "thought": decision.get("thought"),
                        }
                    )
                    if res.status != "ok":
                        caveats.append(f"{oid}:{res.error or 'error'}")
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
            oargs, arg_repairs = normalize_op_args(op_id, oargs)

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

            missing_args = missing_required_args(op_id, oargs)
            if not missing_args and reasoning.analysis_ops >= op_budget:
                caveats.append("op_budget_exceeded")
                break
            res = execute_op(ws, op_id, oargs, out_dir=out_dir)
            if missing_args:
                reasoning.record_observation()
            else:
                reasoning.analysis_ops += 1
            if not missing_args and res.status == "ok" and op_id not in _NON_MUTATING_OPS:
                reasoning.record_mutation(op_id)
            elif not missing_args:
                reasoning.record_observation()
            obs = res.as_observation()
            if arg_repairs:
                obs["arg_repairs"] = arg_repairs
            observations.append(obs)
            steps_trace.append(
                {
                    "step_id": f"iv-step-{reasoning.op_count}",
                    "op_id": op_id,
                    "args": oargs,
                    "dataset": oargs.get("dataset"),
                    "save_as": oargs.get("save_as"),
                    "status": res.status,
                    "error": res.error,
                    "arg_repairs": arg_repairs,
                    "thought": decision.get("thought"),
                }
            )
            if res.status != "ok":
                if missing_args:
                    invalid_key = json.dumps(
                        {"op_id": op_id, "args": oargs},
                        sort_keys=True,
                        default=str,
                    )
                    invalid_op_counts[invalid_key] = invalid_op_counts.get(invalid_key, 0) + 1
                    if invalid_op_counts[invalid_key] >= 2:
                        steps_trace[-1]["repair_action"] = (
                            "abandon_schema_invalid_op_and_verify"
                        )
                        terminal = {
                            "status": "complete",
                            "reason": "schema_invalid_optional_op_abandoned",
                        }
                        break
                else:
                    caveats.append(f"{op_id}:{res.error or 'error'}")
            elif obs.get("empty_after_op"):
                caveats.append("empty_after_op")
            continue

        caveats.append(f"unknown_decision:{action}")
        break
    else:
        caveats.append("budget_exceeded")

    _review_pending_charts()
    if reasoning.phase == IVReasoningPhase.FINALIZE:
        arts = list(ws.primary_artifacts or ws.artifact_paths)
        post = assess_sufficiency(
            brief,
            row_count=int(profile.get("row_count", 0) or 0),
            artifacts=arts,
            chart_artifacts=ws.chart_artifacts,
            excel_artifacts=ws.excel_artifacts,
            headline_metrics=headline_metrics,
            claimed_status=str((terminal or {}).get("status") or "complete"),
            verify_artifact_files=True,
            coverage_gaps=list(reasoning.verification.coverage_gaps),
        )
    else:
        reasoning.advance_to(IVReasoningPhase.VERIFY)
        post, arts = _verify_deliverable(
            reasoning=reasoning,
            ws=ws,
            brief=brief,
            out_dir=out_dir,
            caveats=caveats,
            row_count=int(profile.get("row_count", 0) or 0),
            headline_metrics=headline_metrics,
            claimed_status="partial"
            if terminal is None
            else str(terminal.get("status") or "complete"),
            semantic_labels=[
                *(output_column_semantics or []),
                *[
                    {"purpose": item.get("purpose")}
                    for item in meta
                    if isinstance(item, dict) and item.get("purpose")
                ],
            ],
            mapped_requirement_ids={
                str(requirement_id)
                for item in meta
                if isinstance(item, dict) and item.get("role") != "probe"
                for requirement_id in (item.get("requirement_ids") or [])
            },
        )
    assembled = _assemble_response(
        terminal=terminal,
        artifacts=arts,
        chart_artifacts=ws.chart_artifacts,
        excel_artifacts=ws.excel_artifacts,
        steps_trace=steps_trace,
        caveats=caveats,
        headline_metrics=headline_metrics,
        steps_run=reasoning.op_count,
        planner_tokens=planner.tokens,
    )
    assembled["planner_turns"] = reasoning.planner_turns
    assembled["reasoning_state"] = reasoning.for_prompt()
    assembled["verification"] = reasoning.verification.model_dump(mode="json")
    assembled["visual_reviews"] = visual_reviews
    assembled["artifact_manifests"] = [
        record.model_dump(mode="json") for record in ws.artifacts.values()
    ]
    if post.force_feedback:
        fb_payload = insufficiency_data_feedback(
            brief,
            post,
            row_count=int(profile.get("row_count", 0) or 0),
            artifacts=arts,
        )
        fb_payload["steps_trace"] = steps_trace
        fb_payload["sandbox_steps"] = reasoning.op_count
        fb_payload["planner_turns"] = reasoning.planner_turns
        fb_payload["reasoning_state"] = reasoning.for_prompt()
        fb_payload["headline_metrics"] = headline_metrics
        fb_payload["coverage"] = {
            "diagnosis": "partial",
            "gaps": list(post.gaps),
        }
        fb_payload["verification"] = reasoning.verification.model_dump(mode="json")
        fb_payload["artifact_manifests"] = [
            record.model_dump(mode="json") for record in ws.artifacts.values()
        ]
        fb_payload["visual_reviews"] = visual_reviews
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


def _verify_deliverable(
    *,
    reasoning: IVReasoningState,
    ws: DatasetWorkingSet,
    brief: AnalysisBrief,
    out_dir: str,
    caveats: list[str],
    row_count: int,
    headline_metrics: dict[str, Any],
    claimed_status: str,
    semantic_labels: list[dict[str, Any] | str] | None = None,
    mapped_requirement_ids: set[str] | None = None,
) -> tuple[Any, list[str]]:
    """Run deterministic artifact and brief-coverage verification."""
    for op_id in _ensure_deliverable_exports(ws, brief, out_dir=out_dir, caveats=caveats):
        reasoning.record_mutation(op_id)
    if reasoning.phase != IVReasoningPhase.VERIFY:
        reasoning.advance_to(IVReasoningPhase.VERIFY)

    cov = execute_op(
        ws,
        "match_brief_coverage",
        {
            "brief": brief.model_dump(),
            "semantic_labels": list(semantic_labels or []),
        },
        out_dir=out_dir,
    )
    reasoning.record_observation()
    coverage_gaps: list[str] = []
    blocking_ids = {
        item.requirement_id
        for item in brief.blocking_requirements()
        if item.kind != "output"
    }
    if blocking_ids:
        coverage_gaps.extend(
            f"unmapped_requirement:{requirement_id}"
            for requirement_id in sorted(blocking_ids - set(mapped_requirement_ids or set()))
        )
    if cov.status != "ok":
        coverage_gaps.append("coverage_check_failed")
    else:
        coverage_gaps.extend(f"missing_metric:{name}" for name in cov.result.get("metrics_missing", []))
        coverage_gaps.extend(
            f"missing_dimension:{name}" for name in cov.result.get("dimensions_missing", [])
        )
        coverage_gaps.extend(
            f"missing_filter:{name}" for name in cov.result.get("filters_missing", [])
        )
        coverage_gaps.extend(
            f"missing_ranking:{name}" for name in cov.result.get("ranking_missing", [])
        )
        if not cov.result.get("time_covered", True):
            coverage_gaps.append("missing_time_evidence")
        if cov.result.get("issue") == "empty_result":
            coverage_gaps.append("empty_result")

    arts = list(ws.primary_artifacts or ws.artifact_paths)
    artifact_checks: dict[str, bool] = {}
    verified_rows: dict[str, int] = {}
    for record in ws.artifacts.values():
        if record.path not in arts:
            continue
        checks: list[bool] = []
        if record.kind == "excel" and record.sheet_map:
            for sheet, source_ref in record.sheet_map.items():
                result = execute_op(
                    ws,
                    "validate_export",
                    {
                        "artifact_id": record.artifact_id,
                        "expected_dataset": source_ref,
                        "sheet_name": sheet,
                    },
                    out_dir=out_dir,
                )
                reasoning.record_observation()
                checks.append(result.status == "ok" and bool(result.result.get("valid")))
                if result.status == "ok" and result.result.get("valid") and ws.has(source_ref):
                    verified_rows[f"{record.filename}:{sheet}"] = len(ws.get(source_ref).frame())
        elif record.kind in {"csv", "excel"} and record.source_refs:
            source_ref = record.source_refs[0]
            result = execute_op(
                ws,
                "validate_export",
                {"artifact_id": record.artifact_id, "expected_dataset": source_ref},
                out_dir=out_dir,
            )
            reasoning.record_observation()
            checks.append(result.status == "ok" and bool(result.result.get("valid")))
            if checks[-1] and ws.has(source_ref):
                verified_rows[record.filename] = len(ws.get(source_ref).frame())
        else:
            checks.append(
                Path(record.path).is_file()
                and Path(record.path).stat().st_size > 0
                and record.validation_status != "invalid"
            )
        artifact_checks[record.path] = bool(checks) and all(checks)
    for path in arts:
        artifact_checks.setdefault(
            path, Path(path).is_file() and Path(path).stat().st_size > 0
        )
    if verified_rows:
        headline_metrics["row_count"] = max(verified_rows.values())
        headline_metrics["artifact_rows"] = verified_rows
    check = assess_sufficiency(
        brief,
        row_count=row_count,
        artifacts=arts,
        chart_artifacts=ws.chart_artifacts,
        excel_artifacts=ws.excel_artifacts,
        headline_metrics=headline_metrics,
        claimed_status=claimed_status,
        verify_artifact_files=True,
        coverage_gaps=coverage_gaps,
    )

    gap_text = " ".join(check.gaps).lower()
    checked_items: list[str] = []
    for item in reasoning.checklist:
        checked_items.append(item.item_id)
        requirement = item.requirement.lower()
        blocked = (
            (item.category == "metric" and f"missing_metric:{requirement}" in gap_text)
            or (item.category == "dimension" and f"missing_dimension:{requirement}" in gap_text)
            or (item.category == "filter" and "missing_filter:" in gap_text)
            or (item.category == "time" and "missing_time_evidence" in gap_text)
            or (item.category == "format" and any(gap.startswith("missing_") for gap in check.gaps))
            or (item.category == "intent" and (not arts or check.force_feedback))
        )
        item.status = IVChecklistStatus.BLOCKED if blocked else IVChecklistStatus.SATISFIED
        item.evidence = list(arts)[:3] if not blocked else list(check.gaps)[:3]

    reasoning.record_verification(
        passed=check.sufficient and bool(artifact_checks) and all(artifact_checks.values()),
        artifact_checks=artifact_checks,
        coverage_gaps=list(check.gaps),
        checked_items=checked_items,
    )
    if coverage_gaps:
        caveats.append("brief_coverage_gap")
    return check, arts


def _ensure_deliverable_exports(
    ws: DatasetWorkingSet,
    brief: AnalysisBrief,
    *,
    out_dir: str,
    caveats: list[str],
) -> list[str]:
    """Export every candidate deliverable; fallback is always marked partial."""
    if ws.artifact_paths:
        return []
    refs = ws.refs()
    if not refs:
        return []
    preferred = [r for r in refs if not r.startswith("q") or "_" in r]
    candidates = preferred or refs
    nonempty: list[tuple[str, int]] = []
    for ref in candidates:
        try:
            n = len(ws.get(ref).frame())
        except Exception:  # noqa: BLE001
            continue
        if n > 0:
            nonempty.append((ref, n))
    if not nonempty:
        return []
    exported: list[str] = []
    formats = {str(x).strip().lower() for x in (brief.output_format or []) if str(x).strip()}
    want_excel = bool(formats & {"excel", "xlsx", "spreadsheet"}) or len(nonempty) > 1
    want_csv = bool(formats & {"csv"}) or not want_excel
    if want_csv:
        for index, (ref, _) in enumerate(nonempty):
            csv_res = execute_op(
                ws,
                "export_csv",
                {
                    "dataset": ref,
                    "filename": "analysis_result.csv"
                    if len(nonempty) == 1
                    else f"analysis_{index + 1}_{ref}.csv",
                    "primary": True,
                },
                out_dir=out_dir,
            )
            if csv_res.status != "ok":
                caveats.append(f"auto_export_csv:{csv_res.error or 'error'}")
            else:
                exported.append("export_csv")
    if want_excel:
        sheets: dict[str, str] = {}
        used: set[str] = set()
        for index, (ref, _) in enumerate(nonempty):
            base = "".join(ch if ch.isalnum() or ch in " _-" else "_" for ch in ref)[:25] or f"data_{index + 1}"
            name = base
            suffix = 2
            while name.lower() in used:
                name = f"{base[:27]}_{suffix}"
                suffix += 1
            used.add(name.lower())
            sheets[name] = ref
        x_res = execute_op(
            ws,
            "export_excel",
            {"sheets": sheets, "filename": "analysis_result.xlsx", "primary": True},
            out_dir=out_dir,
        )
        if x_res.status != "ok":
            caveats.append(f"auto_export_excel:{x_res.error or 'error'}")
        else:
            exported.append("export_excel")
    if exported:
        caveats.append("auto_export_fallback_partial")
    return exported


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
    if not terminal:
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
        {
            "op_id": s.get("op_id"),
            "args": dict(s.get("args") or {}),
            "dataset": s.get("dataset"),
            "save_as": s.get("save_as"),
        }
        for s in steps_trace
        if s.get("op_id") and s.get("status") == "ok"
    ]
    return payload
