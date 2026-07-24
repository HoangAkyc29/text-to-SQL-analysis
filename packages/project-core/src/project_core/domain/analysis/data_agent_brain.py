"""Data Agent brain — CoT phases with fetch tools + catalog ops (no free SQL)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from project_core.config.loader import load_project_config
from project_core.domain.analysis.data_agent_guards import (
    assess_deliverable_coverage,
    coverage_forces_partial,
    dataset_looks_like_product_catalog,
    infer_top_n,
    is_blocked_name_type_guess,
    is_blocked_premature_export,
    is_nonblocking_type_clarify,
    soft_product_type,
)
from project_core.domain.analysis.iv_sufficiency import assess_sufficiency
from project_core.domain.analysis.ops import DatasetWorkingSet, execute_op, list_op_ids
from project_core.domain.analysis.ops.registry import (
    catalog_for_prompt as op_catalog_for_prompt,
    missing_required_args,
)
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.data_fetch.toolkit import DataFetchToolkit
from project_core.llm.json_parse import parse_llm_json

if TYPE_CHECKING:
    from project_core.llm.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

DATA_AGENT_PHASES = (
    "orient",
    "ground",
    "probe",
    "narrow",
    "assemble",
    "verify",
    "deliver",
)

_DEFAULT_SYSTEM = """You are the supermarket Data Agent (fetch + analyze). Never write SQL.
Return JSON only with fields: phase, thought, decision, and tool/op/status as needed.

Phases (follow in order; you may briefly revisit earlier phases after evidence):
orient → ground → probe → narrow → assemble → verify → deliver

Decisions:
- fetch: call a parameterized fetch tool {tool_id, args, save_as}
- run_op: call a catalog op {op_id, dataset?, save_as?, args?}
  Put column/op/operator/value/to/by/aggs inside args (or flat on op — both work).
  filter_rows: args.conditions|clauses=[{column, op|operator, value}] OR column+op+value.
  cast_column: args.column + optional args.to (float|int|str|datetime).
- verify: ask runtime to run coverage/grain checks
- finalize: {status: complete|partial, insight_vi, headline_metrics, caveats}
- clarify / impossible: only for true blockers that change which rows/metrics to fetch
  (missing identifier, ambiguous time/store, unresolved entity). Do not invent filters
  from display-name text when product_codes already select SKUs.

Hard rules:
1. If brief has product_code, call resolve_products before query_rows on fact tables.
2. Fact fetches require time_range; never pull unfiltered STRANS/TRANSHDR.
3. Do not pass trans_code/TRANS_CODE unless brief filters request a document type.
4. For min_bill_value, use query_rows on TRANSHDR with min_amount / AMOUNT filter,
   not SUM of one SKU's line amounts.
5. Probe with small limits first; then narrow; then assemble joins/aggs; verify before finalize.
6. thought must name the checklist item and hypothesis from latest samples.
7. sku_ids / trans_nums may be either concrete ID lists OR a working-set dataset name
   (toolkit expands SKU_ID / TRANS_NUM). Prefer dataset refs after resolve/select_columns.
8. When product_codes are present they are the source of truth:
   - Do not invent extra filters on display-name columns (FULL_NAME/NAME) to "confirm" type.
   - product_type_soft is optional context only — continue the pipeline; finalize may caveat
     product_type_unverified. Do not stop to clarify type/name when codes already pin SKUs.
   - Clarify product_type only when there are no product_codes (or resolve is ambiguous) and
     schema/dictionary does not provide a type column.
9. Final export MUST keep SKU_CODE (or SKU_ID) when product_codes were requested.
10. If checklist.top_n is set (e.g. 5 nearest bills), final table rows must be <= top_n;
    call verify before finalize. Prefer status=partial when fewer rows than requested.
"""


class DataAgentPlanner:
    def __init__(self, llm: "OpenRouterClient", profile_name: str, system_prompt: str) -> None:
        self._llm = llm
        self._profile_name = profile_name
        self._system_prompt = system_prompt
        self.tokens = 0

    def next_decision(self, state: dict[str, Any]) -> dict[str, Any]:
        last_err: Exception | None = None
        for attempt in range(1, 4):
            result = self._llm.chat(
                profile_name=self._profile_name,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": json.dumps(state, ensure_ascii=False, default=str)},
                ],
                response_format={"type": "json_object"},
            )
            self.tokens += int(getattr(result, "usage_tokens", 0) or 0)
            try:
                payload = parse_llm_json(result)
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                preview = str(getattr(result, "content", "") or "")[:300]
                logger.warning(
                    "data_agent planner JSON parse failed attempt=%s err=%s preview=%r",
                    attempt,
                    exc,
                    preview,
                )
                continue
            if not isinstance(payload, dict):
                last_err = ValueError("planner_payload_not_object")
                logger.warning(
                    "data_agent planner non-object payload attempt=%s type=%s",
                    attempt,
                    type(payload).__name__,
                )
                continue
            return payload
        assert last_err is not None
        raise last_err


def _product_codes(brief: AnalysisBrief) -> list[str]:
    raw = (brief.filters or {}).get("product_code")
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    return [str(raw).strip()] if str(raw).strip() else []


_OP_META_KEYS = frozenset({"op_id", "kind", "tool_id", "steps", "args", "recipe_id"})


def _merge_op_args(op: dict[str, Any]) -> dict[str, Any]:
    """Merge nested args with flat op fields (LLM often puts column/to at top level)."""
    oargs = dict(op.get("args") or {})
    for key, value in op.items():
        if key in _OP_META_KEYS or value is None:
            continue
        oargs.setdefault(key, value)
    return oargs


def _time_range(brief: AnalysisBrief) -> dict[str, str]:
    tr = brief.time_range
    if tr is None:
        return {}
    return {
        "start": str(getattr(tr, "start", None) or ""),
        "end": str(getattr(tr, "end", None) or ""),
        "grain": str(getattr(tr, "grain", None) or ""),
    }


def _needs_bill_deliverable(brief: AnalysisBrief) -> bool:
    return infer_top_n(brief) is not None or (brief.filters or {}).get("min_bill_value") is not None


def _frame_has_bill_id(df: Any) -> bool:
    cols = {str(c).upper() for c in getattr(df, "columns", [])}
    return bool(cols & {"TRANS_NUM", "BILL_NO", "TRANS_ID"})


def _prefer_export_dataset(
    working_set: DatasetWorkingSet,
    *,
    needs_bill: bool,
) -> str | None:
    """Pick an export ref by grain/shape only — never force a domain recipe."""
    ranked: list[tuple[int, str]] = []
    for ref in working_set.refs():
        try:
            df = working_set.get(ref).frame()
        except Exception:  # noqa: BLE001
            continue
        if needs_bill and dataset_looks_like_product_catalog(df):
            continue
        score = 0
        if needs_bill and _frame_has_bill_id(df):
            score += 100
        # Prefer smaller analytical frames over huge probes.
        score += max(0, 50 - min(len(df), 50))
        ranked.append((score, ref))
    if not ranked:
        return None
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return ranked[0][1]


def _stub_decision(brief: AnalysisBrief, phase: str, observations: list[dict[str, Any]], working_set: DatasetWorkingSet) -> dict[str, Any]:
    """Deterministic path for ALLOW_LLM_STUB / unit tests."""
    codes = _product_codes(brief)
    tr = _time_range(brief)
    min_bill = (brief.filters or {}).get("min_bill_value")
    needs_bill = _needs_bill_deliverable(brief)

    if not any(o.get("tool_id") == "resolve_products" and o.get("ok") for o in observations):
        return {
            "phase": "ground",
            "thought": "Resolve product codes on SKU_DEF before fact fetch",
            "decision": "fetch",
            "tool": {
                "tool_id": "resolve_products",
                "args": {"codes": codes or ["0000"], "limit": 20},
                "save_as": "products",
            },
        }

    sku_ids: list[str] = []
    for ref in ("products", "resolved_skus", "resolved_sku"):
        if not working_set.has(ref):
            continue
        pdf = working_set.get(ref).frame()
        if "SKU_ID" in pdf.columns:
            sku_ids = [str(x) for x in pdf["SKU_ID"].dropna().astype(str).tolist()]
            break

    if not any(
        o.get("tool_id") == "query_rows"
        and o.get("ok")
        and str((o.get("lineage") or {}).get("params", {}).get("table") or "").upper() == "STRANS"
        for o in observations
    ) and not any(
        o.get("tool_id") == "query_rows" and o.get("ok") and o.get("save_as") in {"lines_probe", "sale_lines"}
        for o in observations
    ):
        return {
            "phase": "probe",
            "thought": "Probe sale lines for resolved SKUs in time range",
            "decision": "fetch",
            "tool": {
                "tool_id": "query_rows",
                "args": {
                    "table": "STRANS",
                    "sku_ids": sku_ids[:20] or ["MISSING"],
                    "time_range": tr,
                    "limit": 200,
                },
                "save_as": "lines_probe",
            },
        }

    if min_bill is not None and not any(
        o.get("tool_id") == "query_rows"
        and o.get("ok")
        and (
            o.get("save_as") == "bill_headers"
            or str((o.get("lineage") or {}).get("params", {}).get("table") or "").upper() == "TRANSHDR"
        )
        for o in observations
    ):
        trans_nums: list[str] = []
        for ref in working_set.refs():
            try:
                ldf = working_set.get(ref).frame()
            except Exception:  # noqa: BLE001
                continue
            if "TRANS_NUM" not in ldf.columns:
                continue
            trans_nums = [
                str(x) for x in ldf["TRANS_NUM"].dropna().astype(str).unique().tolist()
            ][:50]
            if trans_nums:
                break
        return {
            "phase": "narrow",
            "thought": "Fetch bill headers with min_amount for bill-value filter",
            "decision": "fetch",
            "tool": {
                "tool_id": "query_rows",
                "args": {
                    "table": "TRANSHDR",
                    "time_range": tr,
                    "trans_nums": trans_nums or None,
                    "min_amount": min_bill,
                    "limit": 200,
                },
                "save_as": "bill_headers",
            },
        }

    if not any(o.get("op_id") == "export_excel" and o.get("ok") for o in observations):
        dataset = _prefer_export_dataset(working_set, needs_bill=needs_bill)
        if dataset is None:
            return {
                "phase": "assemble",
                "thought": "No non-catalog frame ready for export; keep assembling",
                "decision": "finalize",
                "status": "partial",
                "insight_vi": "Chưa có bảng deliverable đúng grain để xuất.",
                "caveats": ["export_blocked_no_suitable_dataset"],
            }
        return {
            "phase": "deliver",
            "thought": f"Export dataset={dataset}",
            "decision": "run_op",
            "op": {
                "op_id": "export_excel",
                "dataset": dataset,
                "args": {"filename": "analysis_result.xlsx"},
            },
        }

    return {
        "phase": "deliver",
        "thought": "Done",
        "decision": "finalize",
        "status": "complete",
        "insight_vi": "Đã hoàn tất phân tích qua Data Agent (stub).",
        "headline_metrics": {},
        "caveats": [],
    }


def run_data_agent_brain(
    *,
    brief: AnalysisBrief,
    out_dir: str,
    fetch_toolkit: DataFetchToolkit,
    working_set: DatasetWorkingSet,
    domain_rules_excerpt: str = "",
    schema_context: dict[str, Any] | None = None,
    retrieval_context: Any = None,
    recipe_candidates: list[dict[str, Any]] | None = None,
    max_steps: int = 20,
    max_planner_turns: int = 16,
    llm: "OpenRouterClient | None" = None,
    profile_name: str = "data_analyst",
    system_prompt: str | None = None,
    use_stub: bool = False,
    planner: Any | None = None,
    trace_id: str | None = None,
    actor_id: str | None = None,
    audit: Any | None = None,
) -> dict[str, Any]:
    """Run CoT loop until finalize / clarify / impossible / budget."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    working_set.set_output_root(out_dir)

    observations: list[dict[str, Any]] = []
    steps_trace: list[dict[str, Any]] = []
    phase = "orient"
    verified = False
    tokens = 0
    if planner is None and llm is not None and not use_stub:
        planner = DataAgentPlanner(
            llm, profile_name, system_prompt or _DEFAULT_SYSTEM
        )

    brief_dump = brief.model_dump(mode="json")
    checklist = {
        "product_codes": _product_codes(brief),
        "time_range": _time_range(brief),
        "min_bill_value": (brief.filters or {}).get("min_bill_value"),
        "product_type_soft": soft_product_type(brief),
        "top_n": infer_top_n(brief),
        "require_sku_evidence": bool(_product_codes(brief)),
        "metrics": list(brief.metrics or []),
        "output_format": list(brief.output_format or []),
    }

    def _audit_turn(**kwargs: Any) -> None:
        logger.info(
            "data_agent_turn trace=%s turn=%s phase=%s decision=%s ok=%s error=%s tool=%s",
            trace_id,
            kwargs.get("turn"),
            kwargs.get("phase"),
            kwargs.get("decision"),
            kwargs.get("ok"),
            kwargs.get("error"),
            kwargs.get("tool_id") or kwargs.get("op_id"),
        )
        if audit is None or not trace_id:
            return
        try:
            audit.log_data_agent_turn(
                trace_id=trace_id,
                actor_id=actor_id or "unknown",
                **kwargs,
            )
        except Exception:  # noqa: BLE001
            logger.exception("data_agent audit turn failed")

    def _persist_trace(extra: dict[str, Any] | None = None) -> None:
        path = Path(out_dir) / "data_agent_trace.json"
        body = {
            "trace_id": trace_id,
            "use_stub": use_stub,
            "checklist": checklist,
            "steps_trace": steps_trace,
            "observations": [
                {k: v for k, v in o.items() if k != "sample"}
                for o in observations
            ],
            "fetch_ok": getattr(fetch_toolkit, "fetch_calls", 0),
            "fetch_attempts": getattr(fetch_toolkit, "fetch_attempts", 0),
            "fetch_errors": list(getattr(fetch_toolkit, "fetch_errors", []) or []),
            **(extra or {}),
        }
        try:
            path.write_text(json.dumps(body, ensure_ascii=False, default=str, indent=2), encoding="utf-8")
        except OSError:
            logger.exception("failed writing data_agent_trace.json")

    for turn in range(max(1, max_planner_turns)):
        state = {
            "phase": phase,
            "brief": brief_dump,
            "checklist": checklist,
            "domain_rules_excerpt": domain_rules_excerpt or "",
            "schema_context_keys": list((schema_context or {}).keys())[:40],
            "retrieval_present": retrieval_context is not None,
            "fetch_catalog": fetch_toolkit.catalog(),
            "op_catalog": op_catalog_for_prompt(),
            "datasets": working_set.list_profiles(),
            "observations": observations[-12:],
            "recipe_candidates": recipe_candidates or [],
            "remaining_turns": max_planner_turns - turn,
            "verified": verified,
        }
        try:
            if planner is None:
                decision = _stub_decision(brief, phase, observations, working_set)
            else:
                decision = planner.next_decision(state)
                tokens = planner.tokens
        except Exception as exc:  # noqa: BLE001
            logger.exception("data agent planner failed")
            if observations:
                # Keep going with deterministic stub instead of aborting a grounded run.
                logger.warning(
                    "data_agent planner resume via stub after failure: %s",
                    exc,
                )
                decision = _stub_decision(brief, phase, observations, working_set)
                steps_trace.append(
                    {
                        "turn": turn + 1,
                        "phase": str(decision.get("phase") or phase),
                        "decision": str(decision.get("decision") or ""),
                        "thought": f"planner_resume_stub:{exc}"[:400],
                    }
                )
            else:
                out = {
                    "action": "partial",
                    "insight_vi": "Data Agent không hoàn tất vòng suy luận.",
                    "caveats": [f"planner_failed:{exc}"],
                    "artifact_paths": list(working_set.artifact_paths),
                    "steps_trace": steps_trace,
                    "observations": observations,
                    "planner_turns": turn + 1,
                    "usage_tokens": tokens,
                }
                _persist_trace({"action": "partial", "caveats": out["caveats"]})
                return out

        decision_name = str(decision.get("decision") or "").strip()
        phase = str(decision.get("phase") or phase)
        thought = str(decision.get("thought") or "")
        steps_trace.append(
            {"turn": turn + 1, "phase": phase, "decision": decision_name, "thought": thought[:400]}
        )
        _audit_turn(
            turn=turn + 1,
            phase=phase,
            decision=decision_name,
            thought=thought,
            tool_id=(decision.get("tool") or {}).get("tool_id")
            if isinstance(decision.get("tool"), dict)
            else None,
            op_id=(decision.get("op") or {}).get("op_id")
            if isinstance(decision.get("op"), dict)
            else None,
        )

        if decision_name == "clarify":
            # Clarify is for true blockers — not soft type/name debates when codes exist.
            if is_nonblocking_type_clarify(
                product_codes=list(checklist.get("product_codes") or []),
                thought=thought,
                decision=decision if isinstance(decision, dict) else {},
                product_type_soft=checklist.get("product_type_soft"),
            ):
                observations.append(
                    {
                        "ok": False,
                        "error": "clarify_rejected_codes_sufficient",
                        "hint": (
                            "product_codes already select SKUs — do not clarify about "
                            "soft product_type / display-name. Continue fetch/analyze; "
                            "finalize may caveat product_type_unverified."
                        ),
                    }
                )
                _audit_turn(
                    turn=turn + 1,
                    phase=phase,
                    decision="clarify",
                    thought=thought,
                    ok=False,
                    error="clarify_rejected_codes_sufficient",
                )
                # Resume deterministic next fetch/op instead of stopping the run.
                decision = _stub_decision(brief, phase, observations, working_set)
                decision_name = str(decision.get("decision") or "")
                phase = str(decision.get("phase") or phase)
                thought = str(
                    decision.get("thought")
                    or "continue after rejected non-blocking type clarify"
                )
                steps_trace.append(
                    {
                        "turn": turn + 1,
                        "phase": phase,
                        "decision": decision_name,
                        "thought": f"override_type_clarify:{thought}"[:400],
                    }
                )
                # Fall through to handle rewritten decision in this same iteration.
            else:
                out = {
                    "action": "suggest_clarify",
                    "suggest_clarify": decision.get("clarification_request")
                    or decision.get("suggest_clarify")
                    or {
                        "reason": decision.get("reason") or thought or "clarify",
                        "questions": [],
                    },
                    "steps_trace": steps_trace,
                    "observations": observations,
                    "planner_turns": turn + 1,
                    "usage_tokens": tokens,
                }
                _persist_trace({"action": "suggest_clarify"})
                return out
        if decision_name == "impossible":
            return {
                "action": "impossible",
                "impossible_reason": decision.get("reason") or thought or "impossible",
                "steps_trace": steps_trace,
                "planner_turns": turn + 1,
                "usage_tokens": tokens,
            }
        if decision_name == "finalize":
            # Hard stop: never finalize empty when brief still needs fact grounding.
            needs_data = bool(checklist.get("product_codes") or checklist.get("time_range", {}).get("start"))
            if needs_data and not working_set.refs():
                observations.append(
                    {
                        "ok": False,
                        "error": "finalize_blocked_empty_working_set",
                        "hint": "Must resolve_products / fetch before finalize",
                    }
                )
                # Bootstrap deterministic resolve so live LLM cannot skip ground.
                decision = _stub_decision(brief, "ground", observations, working_set)
                decision_name = str(decision.get("decision") or "")
                phase = str(decision.get("phase") or "ground")
                thought = str(decision.get("thought") or "bootstrap after empty finalize")
                steps_trace.append(
                    {
                        "turn": turn + 1,
                        "phase": phase,
                        "decision": decision_name,
                        "thought": f"override_empty_finalize:{thought}"[:400],
                    }
                )
                if decision_name != "fetch":
                    return {
                        "action": "partial",
                        "insight_vi": "Data Agent bị chặn finalize khi chưa có dữ liệu.",
                        "caveats": ["finalize_blocked_empty_working_set"],
                        "artifact_paths": [],
                        "steps_trace": steps_trace,
                        "observations": observations,
                        "planner_turns": turn + 1,
                        "usage_tokens": tokens,
                    }
                # Fall through to fetch handling below.
            else:
                status = str(decision.get("status") or "complete")
                arts = list(working_set.artifact_paths)
                if not arts and working_set.refs():
                    ref0 = _prefer_export_dataset(
                        working_set,
                        needs_bill=_needs_bill_deliverable(brief),
                    )
                    if ref0:
                        execute_op(
                            working_set,
                            "export_excel",
                            {"dataset": ref0, "filename": "analysis_result.xlsx"},
                            out_dir=out_dir,
                        )
                        arts = list(working_set.artifact_paths)
                coverage = assess_deliverable_coverage(
                    brief,
                    working_set,
                    product_codes=list(checklist.get("product_codes") or []),
                    top_n=checklist.get("top_n"),
                )
                caveats = list(decision.get("caveats") or [])
                caveats.extend(list(coverage.get("caveats") or []))
                for gap in coverage.get("gaps") or []:
                    if gap not in caveats:
                        caveats.append(gap)
                if soft_product_type(brief) and checklist.get("product_codes"):
                    if "product_type_unverified" not in caveats:
                        caveats.append("product_type_unverified")
                action = "complete" if status == "complete" else "partial"
                if not arts:
                    action = "partial"
                if coverage_forces_partial(list(coverage.get("gaps") or [])):
                    action = "partial"
                    verified = False
                elif status == "complete" and not coverage.get("ok", True):
                    action = "partial"
                observations.append(
                    {
                        "decision": "finalize_coverage",
                        "ok": bool(coverage.get("ok")),
                        "gaps": list(coverage.get("gaps") or []),
                        "caveats": list(coverage.get("caveats") or []),
                        "row_count": coverage.get("row_count"),
                        "columns": coverage.get("columns"),
                        "top_n": coverage.get("top_n"),
                        "source": coverage.get("source"),
                    }
                )
                out = {
                    "action": action,
                    "insight_vi": decision.get("insight_vi")
                    or decision.get("explanation_vi")
                    or "",
                    "headline_metrics": decision.get("headline_metrics") or {},
                    "caveats": caveats,
                    "artifact_paths": arts,
                    "excel_artifacts": list(working_set.excel_artifacts),
                    "chart_artifacts": list(working_set.chart_artifacts),
                    "coverage": {
                        "verified": verified,
                        "deliverable": coverage,
                    },
                    "steps_trace": steps_trace,
                    "observations": observations,
                    "planner_turns": turn + 1,
                    "usage_tokens": tokens,
                    "verification": {
                        "passed": verified and bool(coverage.get("ok")),
                        "deliverable_gaps": list(coverage.get("gaps") or []),
                    },
                    "fetch_ok": getattr(fetch_toolkit, "fetch_calls", 0),
                    "fetch_attempts": getattr(fetch_toolkit, "fetch_attempts", 0),
                    "fetch_errors": list(getattr(fetch_toolkit, "fetch_errors", []) or []),
                }
                _persist_trace({"action": action, "caveats": out["caveats"]})
                return out

        # Accept legacy IV-style action names from mis-prompted models.
        if decision_name in {"", "complete", "partial", "action"}:
            legacy = str(decision.get("action") or decision_name or "").strip()
            if legacy in {"complete", "partial", "finalize"}:
                decision_name = "finalize"
                if "status" not in decision:
                    decision["status"] = "complete" if legacy == "complete" else "partial"
                # Re-enter finalize handling via continue with rewritten decision.
                # Simpler: treat as blocked empty if no data.
                if not working_set.refs():
                    decision = _stub_decision(brief, phase, observations, working_set)
                    decision_name = str(decision.get("decision") or "")
                    steps_trace.append(
                        {
                            "turn": turn + 1,
                            "phase": str(decision.get("phase") or phase),
                            "decision": decision_name,
                            "thought": "override_legacy_iv_action",
                        }
                    )
                else:
                    decision_name = "finalize"
                    # fall through by recursive-style: jump to finalize return
                    status = "partial" if legacy == "partial" else "complete"
                    arts = list(working_set.artifact_paths)
                    if not arts:
                        ref0 = _prefer_export_dataset(
                            working_set,
                            needs_bill=_needs_bill_deliverable(brief),
                        )
                        if ref0:
                            execute_op(
                                working_set,
                                "export_excel",
                                {"dataset": ref0, "filename": "analysis_result.xlsx"},
                                out_dir=out_dir,
                            )
                            arts = list(working_set.artifact_paths)
                    return {
                        "action": "complete" if status == "complete" and arts else "partial",
                        "insight_vi": decision.get("insight_vi") or "",
                        "headline_metrics": decision.get("headline_metrics") or {},
                        "caveats": list(decision.get("caveats") or ["legacy_action_mapped"]),
                        "artifact_paths": arts,
                        "steps_trace": steps_trace,
                        "observations": observations,
                        "planner_turns": turn + 1,
                        "usage_tokens": tokens,
                    }

        if decision_name == "verify":
            row_total = 0
            for prof in working_set.list_profiles():
                row_total += int(prof.get("row_count") or 0)
            cov = assess_sufficiency(
                brief,
                row_count=row_total,
                artifacts=list(working_set.artifact_paths),
                chart_artifacts=list(working_set.chart_artifacts),
                excel_artifacts=list(working_set.excel_artifacts),
            )
            deliverable = assess_deliverable_coverage(
                brief,
                working_set,
                product_codes=list(checklist.get("product_codes") or []),
                top_n=checklist.get("top_n"),
            )
            verified = bool(cov.sufficient) and bool(deliverable.get("ok"))
            observations.append(
                {
                    "decision": "verify",
                    "ok": verified,
                    "gaps": list(dict.fromkeys(list(cov.gaps) + list(deliverable.get("gaps") or []))),
                    "issue": cov.issue or (",".join(deliverable.get("gaps") or []) if not deliverable.get("ok") else ""),
                    "summary": cov.summary
                    or (
                        "Deliverable coverage gaps: " + ", ".join(deliverable.get("gaps") or [])
                        if deliverable.get("gaps")
                        else ""
                    ),
                    "deliverable": deliverable,
                }
            )
            phase = "deliver" if verified else "assemble"
            continue

        if decision_name == "fetch":
            tool = decision.get("tool") or {}
            tool_id = str(tool.get("tool_id") or "")
            args = dict(tool.get("args") or {})
            # Inject brief time_range if missing on fact tools
            if "time_range" not in args and _time_range(brief).get("start"):
                args["time_range"] = _time_range(brief)
            result = fetch_toolkit.execute(
                tool_id,
                args,
                save_as=tool.get("save_as"),
                brief=brief_dump,
            )
            observations.append(result)
            _audit_turn(
                turn=turn + 1,
                phase=phase,
                decision="fetch",
                thought=thought,
                tool_id=tool_id,
                ok=bool(result.get("ok")),
                error=str(result.get("error") or "") or None,
                arg_keys=list(result.get("arg_keys") or sorted(args.keys())),
                row_count=result.get("row_count") if result.get("ok") else None,
                save_as=result.get("save_as") or tool.get("save_as"),
            )
            if len(observations) > max_steps:
                break
            if result.get("ok"):
                if tool_id == "resolve_products":
                    phase = "probe"
                elif tool_id in {"query_rows", "preview_table", "lookup_distinct", "aggregate_rows"}:
                    phase = "narrow" if phase in {"probe", "ground"} else phase
                    if tool.get("save_as") == "bill_headers":
                        phase = "assemble"
            continue

        if decision_name == "run_op":
            op = decision.get("op") or {}
            op_id = str(op.get("op_id") or "")
            if op_id not in set(list_op_ids()):
                observations.append({"ok": False, "error": f"unknown_op:{op_id}", "op_id": op_id})
                _audit_turn(
                    turn=turn + 1,
                    phase=phase,
                    decision="run_op",
                    thought=thought,
                    op_id=op_id,
                    ok=False,
                    error=f"unknown_op:{op_id}",
                )
                continue
            oargs = _merge_op_args(op if isinstance(op, dict) else {})
            blocked = is_blocked_name_type_guess(
                product_codes=list(checklist.get("product_codes") or []),
                op_id=op_id,
                args=oargs,
            )
            if not blocked and op_id == "export_excel":
                blocked = is_blocked_premature_export(
                    checklist=checklist,
                    dataset=str(oargs.get("dataset") or "") or None,
                    working_set=working_set,
                )
            if blocked:
                observations.append(
                    {
                        "ok": False,
                        "error": blocked,
                        "op_id": op_id,
                        "args": oargs,
                        "hint": (
                            "product_codes already identify SKUs — do not guess type from "
                            "display-name columns when product_codes exist. Keep SKU_CODE "
                            "in the final export; use clarify only for true blockers, or "
                            "caveat product_type_unverified if needed."
                            if blocked == "blocked_name_type_guess"
                            else (
                                "checklist asks for bill-grained deliverable (top_n / "
                                "min_bill_value) — do not export product-catalog frames "
                                "(resolved_skus). Assemble TRANS_NUM rows first, then export."
                            )
                        ),
                    }
                )
                logger.info(
                    "data_agent blocked op=%s error=%s dataset=%s",
                    op_id,
                    blocked,
                    oargs.get("dataset"),
                )
                _audit_turn(
                    turn=turn + 1,
                    phase=phase,
                    decision="run_op",
                    thought=thought,
                    op_id=op_id,
                    ok=False,
                    error=blocked,
                    arg_keys=sorted(oargs.keys()),
                )
                continue
            missing = missing_required_args(op_id, oargs)
            if missing:
                same_fail = sum(
                    1
                    for o in observations[-4:]
                    if o.get("op_id") == op_id and o.get("error") in {"missing_args", "repeated_missing_args"}
                )
                err = "repeated_missing_args" if same_fail >= 2 else "missing_args"
                obs: dict[str, Any] = {
                    "ok": False,
                    "error": err,
                    "missing": missing,
                    "op_id": op_id,
                    "received_args": sorted(oargs.keys()),
                }
                if err == "repeated_missing_args":
                    obs["hint"] = (
                        f"Stop retrying {op_id} without {missing}. "
                        "Put required fields in op.args (or flat on op), "
                        "or switch to join_datasets / filter_rows / export_excel."
                    )
                observations.append(obs)
                _audit_turn(
                    turn=turn + 1,
                    phase=phase,
                    decision="run_op",
                    thought=thought,
                    op_id=op_id,
                    ok=False,
                    error=err,
                    arg_keys=sorted(oargs.keys()),
                )
                continue
            try:
                op_result = execute_op(working_set, op_id, oargs, out_dir=out_dir)
                obs = {
                    "ok": op_result.status == "ok",
                    "op_id": op_id,
                    "args": oargs,
                    "dataset": oargs.get("dataset"),
                    "save_as": oargs.get("save_as"),
                    **op_result.as_observation(),
                }
                observations.append(obs)
                _audit_turn(
                    turn=turn + 1,
                    phase=phase,
                    decision="run_op",
                    thought=thought,
                    op_id=op_id,
                    ok=obs["ok"],
                    error=None if obs["ok"] else str(obs.get("error") or op_result.status),
                    arg_keys=sorted(oargs.keys()),
                    save_as=oargs.get("save_as"),
                )
            except Exception as exc:  # noqa: BLE001
                observations.append({"ok": False, "op_id": op_id, "error": str(exc)})
                _audit_turn(
                    turn=turn + 1,
                    phase=phase,
                    decision="run_op",
                    thought=thought,
                    op_id=op_id,
                    ok=False,
                    error=str(exc),
                )
            continue

        observations.append({"ok": False, "error": f"unknown_decision:{decision_name}"})
        _audit_turn(
            turn=turn + 1,
            phase=phase,
            decision=decision_name or "unknown",
            thought=thought,
            ok=False,
            error=f"unknown_decision:{decision_name}",
        )

    out = {
        "action": "partial",
        "insight_vi": "Data Agent hết ngân sách vòng lặp trước khi finalize.",
        "caveats": ["max_planner_turns"],
        "artifact_paths": list(working_set.artifact_paths),
        "steps_trace": steps_trace,
        "observations": observations,
        "planner_turns": max_planner_turns,
        "usage_tokens": tokens,
        "fetch_ok": getattr(fetch_toolkit, "fetch_calls", 0),
        "fetch_attempts": getattr(fetch_toolkit, "fetch_attempts", 0),
        "fetch_errors": list(getattr(fetch_toolkit, "fetch_errors", []) or []),
    }
    # Best-effort export so partial runs still leave deliverables when data exists.
    if not working_set.artifact_paths and working_set.refs():
        try:
            export_ref = _prefer_export_dataset(
                working_set,
                needs_bill=_needs_bill_deliverable(brief),
            )
            if export_ref:
                export = execute_op(
                    working_set,
                    "export_excel",
                    {"dataset": export_ref, "filename": "analysis_result.xlsx"},
                    out_dir=out_dir,
                )
                observations.append(
                    {
                        "ok": export.status == "ok",
                        "op_id": "export_excel",
                        "auto_export_on_budget": True,
                        "dataset": export_ref,
                        **export.as_observation(),
                    }
                )
                out["artifact_paths"] = list(working_set.artifact_paths)
                if export.status == "ok" and out["artifact_paths"]:
                    out["caveats"] = list(out["caveats"]) + ["auto_export_on_budget"]
            else:
                observations.append(
                    {
                        "ok": False,
                        "op_id": "export_excel",
                        "auto_export_on_budget": True,
                        "error": "export_blocked_no_suitable_dataset",
                    }
                )
                out["caveats"] = list(out["caveats"]) + ["export_blocked_no_suitable_dataset"]
        except Exception as exc:  # noqa: BLE001
            observations.append(
                {"ok": False, "op_id": "export_excel", "auto_export_on_budget": True, "error": str(exc)}
            )
    coverage = assess_deliverable_coverage(
        brief,
        working_set,
        product_codes=list(checklist.get("product_codes") or []),
        top_n=checklist.get("top_n"),
    )
    out["caveats"] = list(dict.fromkeys(list(out.get("caveats") or []) + list(coverage.get("caveats") or []) + list(coverage.get("gaps") or [])))
    if coverage_forces_partial(list(coverage.get("gaps") or [])):
        out["action"] = "partial"
    out["coverage"] = coverage
    _persist_trace({"action": out["action"], "caveats": out["caveats"], "coverage": coverage})
    return out
