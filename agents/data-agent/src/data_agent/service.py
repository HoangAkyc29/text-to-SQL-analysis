"""Data Agent — adaptive chunk loop + Tool-Selector + fetch/ops execution."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import DecisionContext

from project_core.domain.audit.logger import AuditLogger
from project_core.domain.analysis.data_agent_guards import (
    assess_deliverable_coverage,
    coverage_forces_partial,
    infer_top_n,
)
from project_core.domain.analysis.ops import DatasetWorkingSet, execute_op
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.data_fetch.arg_coerce import (
    coerce_product_codes,
    coerce_table_name,
    coerce_time_range,
    looks_like_prose_placeholder,
    sanitize_filter_clauses,
)
from project_core.domain.data_fetch.toolkit import DataFetchToolkit
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.sql.policy_engine import PolicyEngine
from project_core.infra.auth_internal import internal_auth_headers
from project_core.llm.json_parse import parse_llm_json
from project_core.llm.openrouter_client import OpenRouterClient
from project_core.models.loader import agent_profile
from project_core.service.supermarket_agent import SupermarketAgentService

logger = logging.getLogger(__name__)


def _product_codes(brief: AnalysisBrief) -> list[str]:
    raw = (brief.filters or {}).get("product_code")
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    return [str(raw).strip()] if str(raw).strip() else []


def _time_range(brief: AnalysisBrief) -> dict[str, str]:
    tr = brief.time_range
    if tr is None:
        return {}
    return {
        "start": str(getattr(tr, "start", None) or ""),
        "end": str(getattr(tr, "end", None) or ""),
        "grain": str(getattr(tr, "grain", None) or ""),
    }


def _server_for_tool(tool_id: str) -> str:
    if tool_id == "resolve_products":
        return "product-lookup"
    if tool_id in {"preview_table", "query_rows", "aggregate_rows", "lookup_distinct"}:
        return "data-query"
    if tool_id in {
        "export_csv",
        "export_excel",
        "plot_chart",
        "bundle_deliverables",
        "inspect_excel",
        "validate_export",
    }:
        return "deliverables"
    return "dataframe-ops"


def _correlation_ids(payload_in: dict[str, Any], meta: dict[str, Any]) -> tuple[str, str, str]:
    trace_id = str(
        payload_in.get("trace_id")
        or meta.get("trace_id")
        or os.getenv("X_TRACE_ID")
        or ""
    ).strip()
    analysis_id = str(
        payload_in.get("analysis_id")
        or meta.get("analysis_id")
        or os.getenv("X_ANALYSIS_ID")
        or ""
    ).strip()
    actor_id = str(
        payload_in.get("actor_id")
        or meta.get("actor_id")
        or "data-agent"
    ).strip()
    return trace_id, analysis_id, actor_id


class _HttpGw:
    def __init__(self, base_url: str) -> None:
        self.base = base_url.rstrip("/")

    def execute_readonly(self, sql: str, acl: SqlAclContext, *, target_db: str = "db2") -> dict[str, Any]:
        payload = {"sql": sql, "target_db": target_db, **acl.to_gateway_args()}
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(
                f"{self.base}/tools/execute_readonly",
                json=payload,
                headers=internal_auth_headers(),
            )
            resp.raise_for_status()
            return resp.json()


class DataAgentService(SupermarketAgentService):
    def decide(self, ctx: DecisionContext) -> Any:
        payload_in, meta = self.parse_payload(ctx)
        brief = AnalysisBrief.model_validate(payload_in.get("brief") or meta.get("brief") or {})
        permissions = self.resolve_permissions(payload_in, meta)
        if permissions is None:
            return self.json_response(
                ctx, {"action": "impossible", "impossible_reason": "permissions_missing"}
            )

        out_dir = str(payload_in.get("out_dir") or meta.get("out_dir") or "data/artifacts/out")
        work_dir = str(payload_in.get("work_dir") or meta.get("work_dir") or out_dir)
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        Path(work_dir).mkdir(parents=True, exist_ok=True)
        os.environ["DATA_AGENT_WORK_DIR"] = work_dir
        os.environ["DATA_AGENT_OUT_DIR"] = out_dir
        os.environ["DATA_AGENT_BRIEF_JSON"] = json.dumps(brief.model_dump(mode="json"), default=str)
        os.environ["DATA_AGENT_ACL_JSON"] = json.dumps(permissions.model_dump(mode="json"), default=str)

        acl = SqlAclContext.from_permissions(permissions)
        catalog = SchemaCatalog.from_dictionary_dir()
        policy = PolicyEngine(
            catalog,
            allowed_tables=permissions.allowed_tables,
            denied_columns=permissions.denied_columns,
            store_ids=permissions.store_ids,
            store_filter_required=permissions.store_filter_required,
        )
        working_set = DatasetWorkingSet(work_dir=Path(work_dir))
        working_set.set_output_root(out_dir)
        sql_url = os.getenv("SQL_GATEWAY_URL", "http://localhost:18101")
        fetch = DataFetchToolkit(
            sql_gateway=_HttpGw(sql_url),
            policy=policy,
            acl=acl,
            working_set=working_set,
        )

        max_turns = int(payload_in.get("max_planner_turns") or meta.get("max_planner_turns") or 16)
        case_hints = payload_in.get("case_hints") or meta.get("case_hints") or []
        domain_excerpt = payload_in.get("domain_rules_excerpt") or meta.get("domain_rules_excerpt") or ""

        checklist = {
            "product_codes": _product_codes(brief),
            "time_range": _time_range(brief),
            "min_bill_value": (brief.filters or {}).get("min_bill_value"),
            "top_n": infer_top_n(brief),
            "metrics": list(brief.metrics or []),
        }
        observations: list[dict[str, Any]] = []
        steps_trace: list[dict[str, Any]] = []
        stages_trail: list[dict[str, Any]] = []
        tokens = 0
        use_stub = os.getenv("ALLOW_LLM_STUB", "").strip() in {"1", "true", "TRUE"}
        trace_id, analysis_id, actor_id = _correlation_ids(payload_in, meta)
        audit = AuditLogger()

        def _audit_turn(**kwargs: Any) -> None:
            if not trace_id:
                return
            try:
                audit.log_data_agent_turn(
                    trace_id=trace_id,
                    actor_id=actor_id,
                    analysis_id=analysis_id or None,
                    **kwargs,
                )
            except Exception:  # noqa: BLE001
                logger.exception("data_agent audit turn failed")

        def _persist_trace(extra: dict[str, Any] | None = None) -> None:
            path = Path(out_dir) / "data_agent_trace.json"
            body = {
                "trace_id": trace_id,
                "analysis_id": analysis_id,
                "use_stub": use_stub,
                "checklist": checklist,
                "steps_trace": steps_trace,
                "stages": stages_trail,
                "observations": [
                    {k: v for k, v in o.items() if k not in {"sample"}} for o in observations
                ],
                **(extra or {}),
            }
            try:
                path.write_text(
                    json.dumps(body, ensure_ascii=False, default=str, indent=2),
                    encoding="utf-8",
                )
            except OSError:
                logger.exception("failed writing data_agent_trace.json")

        for turn in range(max(1, max_turns)):
            chunk = self._next_chunk(
                brief=brief,
                checklist=checklist,
                observations=observations,
                domain_excerpt=domain_excerpt,
                use_stub=use_stub,
            )
            tokens += int(chunk.get("usage_tokens") or 0)
            decision = str(chunk.get("decision") or "chunk")
            chunk_goal = str(chunk.get("chunk_goal") or chunk.get("thought") or "").strip()
            thought = str(chunk.get("thought") or "")[:400]
            steps_trace.append(
                {
                    "turn": turn + 1,
                    "decision": decision,
                    "chunk_goal": chunk_goal[:400],
                    "thought": thought,
                }
            )
            _audit_turn(
                turn=turn + 1,
                phase="chunk",
                decision=decision,
                thought=thought,
                chunk_goal=chunk_goal,
            )
            _persist_trace()

            if decision == "finalize":
                result = self._finalize(
                    brief, checklist, working_set, observations, steps_trace, stages_trail, tokens, chunk
                )
                _persist_trace({"finalize": {"action": result.get("action"), "caveats": result.get("caveats")}})
                return self.json_response(ctx, result, usage_tokens=tokens)
            if decision in {"clarify", "impossible"}:
                return self.json_response(
                    ctx,
                    {
                        "action": "suggest_clarify" if decision == "clarify" else "impossible",
                        "suggest_clarify": chunk.get("clarification_request")
                        or {"reason": chunk_goal or decision},
                        "impossible_reason": chunk.get("reason") or chunk_goal,
                        "steps_trace": steps_trace,
                        "stages": stages_trail,
                        "usage_tokens": tokens,
                    },
                    usage_tokens=tokens,
                )

            if not chunk_goal:
                observations.append({"ok": False, "error": "empty_chunk_goal"})
                _audit_turn(
                    turn=turn + 1,
                    phase="chunk",
                    decision="skip",
                    thought="empty_chunk_goal",
                    ok=False,
                    error="empty_chunk_goal",
                )
                continue

            selector = self._ask_tool_selector(
                chunk_goal=chunk_goal,
                brief=brief,
                working_set=working_set,
                observations=observations,
                case_hints=case_hints,
                trace_id=trace_id,
                analysis_id=analysis_id,
                actor_id=actor_id,
                turn=turn + 1,
            )
            suggested = list(selector.get("tools") or [])
            selector_ids = [str(t.get("tool_id") or "") for t in suggested if isinstance(t, dict)]
            stages_trail.append(
                {
                    "stage_id": f"t{turn+1}",
                    "goal": chunk_goal,
                    "suggested_tool_ids": selector_ids,
                    "outcome_note": "",
                }
            )
            _audit_turn(
                turn=turn + 1,
                phase="select",
                decision="tool_selector",
                thought=str(selector.get("reason") or "")[:400],
                chunk_goal=chunk_goal,
                selector_tool_ids=selector_ids,
                ok=not bool(selector.get("none_available")),
                error=str(selector.get("reason") or "") if selector.get("none_available") else None,
            )
            if selector.get("none_available") or not suggested:
                observations.append(
                    {
                        "ok": False,
                        "error": "none_available",
                        "reason": selector.get("reason"),
                        "chunk_goal": chunk_goal,
                    }
                )
                stages_trail[-1]["outcome_note"] = "none_available"
                _persist_trace()
                continue

            for tip in suggested[:3]:
                tool_id = str(tip.get("tool_id") or "")
                args = self._args_from_hints(tip, brief, checklist, working_set)
                obs = self._execute_tool(tool_id, args, fetch, working_set, out_dir)
                observations.append(obs)
                stages_trail[-1]["outcome_note"] = "ok" if obs.get("ok") else str(obs.get("error") or "fail")
                is_fetch = bool(obs.get("tool_id"))
                _audit_turn(
                    turn=turn + 1,
                    phase="execute",
                    decision="fetch" if is_fetch else "run_op",
                    thought=chunk_goal[:200],
                    chunk_goal=chunk_goal,
                    tool_id=obs.get("tool_id") if is_fetch else None,
                    op_id=obs.get("op_id") if not is_fetch else None,
                    server=_server_for_tool(tool_id),
                    ok=bool(obs.get("ok")),
                    error=str(obs.get("error") or "") or None,
                    arg_keys=sorted(args.keys()),
                    args_preview=args,
                    row_count=obs.get("row_count"),
                    save_as=obs.get("save_as"),
                    target_dbs=list(obs.get("target_dbs") or []) or None,
                    selector_tool_ids=selector_ids,
                )
            _persist_trace()

        # Budget exhausted — best effort finalize
        result = self._finalize(
            brief,
            checklist,
            working_set,
            observations,
            steps_trace,
            stages_trail,
            tokens,
            {"status": "partial", "insight_vi": "Hết ngân sách vòng lặp.", "caveats": ["max_planner_turns"]},
        )
        _persist_trace({"finalize": {"action": result.get("action"), "caveats": result.get("caveats")}})
        return self.json_response(ctx, result, usage_tokens=tokens)

    def _next_chunk(
        self,
        *,
        brief: AnalysisBrief,
        checklist: dict[str, Any],
        observations: list[dict[str, Any]],
        domain_excerpt: str,
        use_stub: bool,
    ) -> dict[str, Any]:
        if use_stub:
            return self._stub_chunk(brief, checklist, observations)
        client = OpenRouterClient()
        state = {
            "brief": brief.model_dump(mode="json"),
            "checklist": checklist,
            "domain_rules_excerpt": domain_excerpt,
            "observations": [
                {k: v for k, v in o.items() if k != "sample"} for o in observations[-8:]
            ],
            "now": datetime.now(timezone.utc).isoformat(),
        }
        result = client.chat(
            profile_name=agent_profile("data_agent"),
            messages=[
                {"role": "system", "content": self.llm_system_prompt(guide="chunk_guide")},
                {"role": "user", "content": json.dumps(state, ensure_ascii=False, default=str)},
            ],
            response_format={"type": "json_object"},
        )
        try:
            payload = parse_llm_json(result)
        except Exception as exc:  # noqa: BLE001
            logger.warning("data_agent chunk parse failed: %s", exc)
            return self._stub_chunk(brief, checklist, observations) | {
                "usage_tokens": int(getattr(result, "usage_tokens", 0) or 0),
                "thought": f"parse_failed:{exc}",
            }
        if not isinstance(payload, dict):
            payload = self._stub_chunk(brief, checklist, observations)
        payload["usage_tokens"] = int(getattr(result, "usage_tokens", 0) or 0)
        return payload

    def _stub_chunk(
        self, brief: AnalysisBrief, checklist: dict[str, Any], observations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        codes = checklist.get("product_codes") or []
        tr = checklist.get("time_range") or {}
        has_resolve = any(o.get("tool_id") == "resolve_products" and o.get("ok") for o in observations)
        has_sale_lines = any(
            o.get("tool_id") == "query_rows"
            and o.get("ok")
            and o.get("save_as") in {"sale_lines", "lines_probe", "query_rows"}
            and str(((o.get("lineage") or {}).get("params") or {}).get("table") or "STRANS").upper()
            == "STRANS"
            for o in observations
        ) or any(
            o.get("tool_id") == "query_rows"
            and o.get("ok")
            and str(((o.get("lineage") or {}).get("params") or {}).get("table") or "").upper() == "STRANS"
            for o in observations
        )
        has_bills = any(
            o.get("tool_id") == "query_rows"
            and o.get("ok")
            and (
                o.get("save_as") == "bill_headers"
                or str(((o.get("lineage") or {}).get("params") or {}).get("table") or "").upper()
                == "TRANSHDR"
            )
            for o in observations
        )
        has_export = any(
            (o.get("op_id") == "export_excel" or o.get("tool_id") == "export_excel") and o.get("ok")
            for o in observations
        )
        if codes and not has_resolve:
            return {
                "decision": "chunk",
                "chunk_goal": f"Resolve product codes {codes}",
                "thought": "stub ground",
            }
        if tr.get("start") and not has_sale_lines:
            return {
                "decision": "chunk",
                "chunk_goal": "Fetch sale lines via query_rows on STRANS for resolved SKUs",
                "thought": "stub query strans",
            }
        if checklist.get("min_bill_value") is not None and has_sale_lines and not has_bills:
            return {
                "decision": "chunk",
                "chunk_goal": "Fetch TRANSHDR bills with min_bill_value from brief via query_rows",
                "thought": "stub query transhdr",
            }
        if (has_sale_lines or has_bills) and not has_export:
            return {
                "decision": "chunk",
                "chunk_goal": "Assemble deliverable and export excel",
                "thought": "stub deliver",
            }
        return {
            "decision": "finalize",
            "status": "complete" if has_export or has_sale_lines else "partial",
            "insight_vi": "Stub Data Agent hoàn tất.",
            "caveats": [],
        }

    def _ask_tool_selector(
        self,
        *,
        chunk_goal: str,
        brief: AnalysisBrief,
        working_set: DatasetWorkingSet,
        observations: list[dict[str, Any]],
        case_hints: list[Any],
        trace_id: str = "",
        analysis_id: str = "",
        actor_id: str = "data-agent",
        turn: int | None = None,
    ) -> dict[str, Any]:
        url = os.getenv("AGENT_TOOL_SELECTOR_URL", "http://localhost:18205").rstrip("/") + "/run"
        message_body = {
            "chunk_goal": chunk_goal,
            "brief_slice": {
                "intent": brief.intent,
                "filters": brief.filters,
                "time_range": brief.time_range.model_dump() if brief.time_range else {},
                "metrics": brief.metrics,
            },
            "available_datasets": working_set.list_profiles(),
            "prior_observations_summary": [
                {"ok": o.get("ok"), "tool_id": o.get("tool_id") or o.get("op_id"), "error": o.get("error")}
                for o in observations[-6:]
            ],
            "case_hints": case_hints,
            "trace_id": trace_id,
            "analysis_id": analysis_id,
            "turn": turn,
        }
        body = {
            "session_id": analysis_id or "data-agent",
            "actor_id": actor_id or "data-agent",
            "message": json.dumps(message_body, ensure_ascii=False, default=str),
            "metadata": {
                "trace_id": trace_id,
                "analysis_id": analysis_id,
                "turn": turn,
                "actor_id": actor_id,
            },
        }
        headers = internal_auth_headers()
        if trace_id:
            headers["X-Trace-Id"] = trace_id
        if analysis_id:
            headers["X-Analysis-Id"] = analysis_id
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(url, json=body, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            payload = data.get("payload") or {}
            if not payload and data.get("content"):
                payload = json.loads(data["content"])
            return payload if isinstance(payload, dict) else {"none_available": True, "tools": []}
        except Exception as exc:  # noqa: BLE001
            logger.warning("tool_selector invoke failed: %s", exc)
            fallback = ToolSelectorFallback.suggest(chunk_goal)
            # Local audit when selector service unreachable
            if trace_id:
                try:
                    AuditLogger().log_tool_selector_suggest(
                        trace_id=trace_id,
                        actor_id=actor_id,
                        analysis_id=analysis_id or None,
                        chunk_goal=chunk_goal,
                        tools=list(fallback.get("tools") or []),
                        none_available=bool(fallback.get("none_available")),
                        reason=f"fallback:{exc}",
                        turn=turn,
                        use_stub=True,
                    )
                except Exception:  # noqa: BLE001
                    logger.exception("fallback selector audit failed")
            return fallback

    def _args_from_hints(
        self,
        tip: dict[str, Any],
        brief: AnalysisBrief,
        checklist: dict[str, Any],
        working_set: DatasetWorkingSet,
    ) -> dict[str, Any]:
        """Build concrete tool args. Never trust prose placeholders in args_hints."""
        tool_id = str(tip.get("tool_id") or "")
        hints = dict(tip.get("args_hints") or tip.get("args") or {})
        tr = checklist.get("time_range") or {}
        if not isinstance(tr, dict) or not (tr.get("start") or tr.get("end")):
            brief_tr = getattr(brief, "time_range", None)
            if brief_tr is not None:
                tr = brief_tr.model_dump() if hasattr(brief_tr, "model_dump") else dict(brief_tr or {})
        codes = list(checklist.get("product_codes") or [])
        known_refs = list(working_set.refs())

        if tool_id == "resolve_products":
            return {
                "codes": coerce_product_codes(hints.get("codes"), fallback=codes),
                "limit": hints.get("limit", 50) if isinstance(hints.get("limit"), int) else 50,
            }

        if tool_id in {"query_rows", "preview_table", "aggregate_rows", "lookup_distinct"}:
            default_table = "STRANS"
            goal_hint = str(tip.get("reason") or "").lower()
            if "transhdr" in goal_hint or checklist.get("min_bill_value") is not None:
                has_lines = any("strans" in r.lower() or "line" in r.lower() for r in known_refs)
                if has_lines or "transhdr" in goal_hint or "bill" in goal_hint or "header" in goal_hint:
                    default_table = "TRANSHDR"

            limit_raw = hints.get("limit")
            if not isinstance(limit_raw, int) or limit_raw <= 0:
                limit_raw = 5000 if tool_id == "query_rows" else 30

            args: dict[str, Any] = {
                "table": coerce_table_name(hints.get("table"), fallback=default_table),
                "time_range": coerce_time_range(hints.get("time_range"), fallback=tr if isinstance(tr, dict) else None),
                "limit": limit_raw,
            }

            # Only accept typed filter lists; discard prose / bad ops. Prefer sugar below.
            cleaned_filters = sanitize_filter_clauses(hints.get("filters"))
            # Prefer checklist min_bill sugar over invented amount column names.
            if checklist.get("min_bill_value") is not None:
                cleaned_filters = [
                    c
                    for c in cleaned_filters
                    if str(c.get("column") or "").strip().upper()
                    not in {"BILL_AMT", "BILL_AMOUNT", "BILL_VALUE", "TOTAL_AMT", "TOTAL_AMOUNT"}
                ]
            if cleaned_filters:
                args["filters"] = cleaned_filters

            if checklist.get("min_bill_value") is not None and str(args.get("table", "")).upper() == "TRANSHDR":
                args["min_amount"] = checklist["min_bill_value"]

            # SKU_ID exists on line facts (STRANS/PMTRANS), not on TRANSHDR headers.
            table_u = str(args.get("table", "")).upper()
            sku_capable = table_u in {"STRANS", "PMTRANS"} or table_u.startswith("STRANS_") or table_u.startswith("PMTRANS_")
            if sku_capable:
                sku_hint = hints.get("sku_ids")
                if isinstance(sku_hint, str) and sku_hint in known_refs:
                    args["sku_ids"] = sku_hint
                elif isinstance(sku_hint, list) and sku_hint and not any(looks_like_prose_placeholder(x) for x in sku_hint):
                    args["sku_ids"] = sku_hint
                elif codes and working_set.has("resolved_products"):
                    args["sku_ids"] = "resolved_products"
                elif codes and known_refs:
                    for ref in known_refs:
                        if "resolv" in ref.lower() or "product" in ref.lower():
                            args["sku_ids"] = ref
                            break

            if table_u == "TRANSHDR":
                for ref in known_refs:
                    try:
                        frame = working_set.get(ref).frame()
                    except Exception:  # noqa: BLE001
                        continue
                    if "TRANS_NUM" in frame.columns:
                        args["trans_nums"] = ref
                        break

            if tool_id == "aggregate_rows":
                aggs = hints.get("aggs")
                if isinstance(aggs, list) and aggs:
                    args["aggs"] = aggs
                else:
                    args["aggs"] = [{"fn": "sum", "column": "QTY", "as": "sum_qty"}]
                    args["group_by"] = ["SKU_ID"]
                if isinstance(hints.get("group_by"), list):
                    args["group_by"] = hints["group_by"]

            if tool_id == "lookup_distinct":
                col = hints.get("column")
                args["column"] = col if isinstance(col, str) and not looks_like_prose_placeholder(col) else "TRANS_CODE"

            save_raw = hints.get("save_as")
            save_default = "bill_headers" if str(args.get("table", "")).upper() == "TRANSHDR" else "sale_lines"
            args["save_as"] = (
                save_raw
                if isinstance(save_raw, str) and save_raw.strip() and not looks_like_prose_placeholder(save_raw)
                else save_default
            )
            return args

        if tool_id == "export_excel":
            refs = known_refs
            dataset = hints.get("dataset")
            if not isinstance(dataset, str) or looks_like_prose_placeholder(dataset) or (refs and dataset not in refs):
                dataset = refs[-1] if refs else None
            return {"dataset": dataset, "filename": hints.get("filename") or "analysis_result.xlsx"}

        if tool_id in {"filter_rows", "top_n_per_group", "join_datasets", "groupby_agg", "select_columns"}:
            args = {k: v for k, v in hints.items() if not looks_like_prose_placeholder(v)}
            if "dataset" not in args and known_refs:
                args["dataset"] = known_refs[-1]
            elif isinstance(args.get("dataset"), str) and args["dataset"] not in known_refs and known_refs:
                args["dataset"] = known_refs[-1]
            if tool_id == "top_n_per_group":
                args.setdefault("partition_by", "TRANS_NUM")
                args.setdefault("order_by", "TRAN_DATE")
                args.setdefault("n", checklist.get("top_n") or 5)
                args.setdefault("ascending", False)
            return args

        # Drop obvious prose values from residual hints.
        return {k: v for k, v in hints.items() if not looks_like_prose_placeholder(v)}

    def _execute_tool(
        self,
        tool_id: str,
        args: dict[str, Any],
        fetch: DataFetchToolkit,
        working_set: DatasetWorkingSet,
        out_dir: str,
    ) -> dict[str, Any]:
        from project_core.domain.data_fetch.catalog import FETCH_TOOL_IDS
        from project_core.domain.analysis.ops.registry import list_op_ids

        if tool_id in FETCH_TOOL_IDS:
            save_as = args.pop("save_as", tool_id)
            return fetch.execute(tool_id, args, save_as=save_as, brief=json.loads(os.environ.get("DATA_AGENT_BRIEF_JSON") or "{}"))
        if tool_id in set(list_op_ids()):
            # Fix top_n defaults
            if tool_id == "top_n_per_group":
                args.setdefault("partition_by", "TRANS_NUM")
                args.setdefault("order_by", "TRAN_DATE")
                args.setdefault("n", 5)
                args.setdefault("ascending", False)
            try:
                result = execute_op(working_set, tool_id, args, out_dir=out_dir)
                return {"ok": result.status == "ok", "op_id": tool_id, "args": args, **result.as_observation()}
            except Exception as exc:  # noqa: BLE001
                return {"ok": False, "op_id": tool_id, "error": str(exc)}
        return {"ok": False, "error": f"unknown_tool:{tool_id}"}

    def _finalize(
        self,
        brief: AnalysisBrief,
        checklist: dict[str, Any],
        working_set: DatasetWorkingSet,
        observations: list[dict[str, Any]],
        steps_trace: list[dict[str, Any]],
        stages_trail: list[dict[str, Any]],
        tokens: int,
        chunk: dict[str, Any],
    ) -> dict[str, Any]:
        arts = list(working_set.artifact_paths)
        if not arts and working_set.refs():
            ref = working_set.refs()[-1]
            execute_op(
                working_set,
                "export_excel",
                {"dataset": ref, "filename": "analysis_result.xlsx"},
                out_dir=str(working_set.output_root or "data/artifacts/out"),
            )
            arts = list(working_set.artifact_paths)
        coverage = assess_deliverable_coverage(
            brief,
            working_set,
            product_codes=list(checklist.get("product_codes") or []),
            top_n=checklist.get("top_n"),
        )
        caveats = list(chunk.get("caveats") or [])
        caveats.extend(list(coverage.get("caveats") or []))
        caveats.extend(list(coverage.get("gaps") or []))
        status = str(chunk.get("status") or "complete")
        action = "complete" if status == "complete" and arts else "partial"
        if coverage_forces_partial(list(coverage.get("gaps") or [])):
            action = "partial"
        tool_chain: list[dict[str, Any]] = []
        for o in observations:
            if not o.get("ok"):
                continue
            if o.get("tool_id"):
                tool_chain.append(
                    {
                        "kind": "fetch",
                        "server": "data-query" if o.get("tool_id") != "resolve_products" else "product-lookup",
                        "tool_id": o.get("tool_id"),
                        "args": (o.get("lineage") or {}).get("params") or {},
                        "save_as": o.get("save_as"),
                    }
                )
            elif o.get("op_id"):
                tool_chain.append(
                    {
                        "kind": "op",
                        "server": "deliverables" if str(o.get("op_id")).startswith("export") or o.get("op_id") == "plot_chart" else "dataframe-ops",
                        "tool_id": o.get("op_id"),
                        "args": o.get("args") or {},
                        "save_as": o.get("save_as"),
                    }
                )
        return {
            "action": action,
            "insight_vi": chunk.get("insight_vi") or "",
            "headline_metrics": chunk.get("headline_metrics") or {},
            "caveats": list(dict.fromkeys(caveats)),
            "artifact_paths": arts,
            "steps_trace": steps_trace,
            "stages": stages_trail,
            "tool_chain": tool_chain,
            "observations": observations,
            "coverage": coverage,
            "planner_turns": len(steps_trace),
            "usage_tokens": tokens,
            "fetch_ok": sum(1 for o in observations if o.get("tool_id") and o.get("ok")),
            "fetch_attempts": sum(1 for o in observations if o.get("tool_id")),
            "fetch_errors": [str(o.get("error")) for o in observations if o.get("tool_id") and not o.get("ok")],
        }


class ToolSelectorFallback:
    @staticmethod
    def suggest(chunk_goal: str) -> dict[str, Any]:
        goal = chunk_goal.lower()
        tools: list[dict[str, Any]] = []
        if any(k in goal for k in ("resolve", "sku", "product", "mã")):
            tools.append({"server": "product-lookup", "tool_id": "resolve_products", "reason": "fallback"})
        if any(k in goal for k in ("fetch", "query", "bill", "sale", "header", "dòng")):
            tools.append({"server": "data-query", "tool_id": "query_rows", "reason": "fallback"})
        if any(k in goal for k in ("export", "excel", "deliver")):
            tools.append({"server": "deliverables", "tool_id": "export_excel", "reason": "fallback"})
        if any(k in goal for k in ("top", "rank", "gần nhất")):
            tools.append({"server": "dataframe-ops", "tool_id": "top_n_per_group", "reason": "fallback"})
        if not tools:
            return {"tools": [], "none_available": True, "reason": "fallback_empty"}
        return {"tools": tools, "none_available": False}


def build_service(config: PlatformConfig, spec: AgentSpec) -> DataAgentService:
    root = Path(__file__).resolve().parent / "skills"
    return DataAgentService(config, spec, skills_root=root, agent_key="DATA")
