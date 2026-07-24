"""Tool-Selector — suggest MCP tools for one Data Agent chunk goal."""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import DecisionContext

from project_core.domain.analysis.ops.registry import OP_CATALOG
from project_core.domain.audit.logger import AuditLogger
from project_core.domain.data_fetch.catalog import FETCH_CATALOG
from project_core.llm.json_parse import parse_llm_json
from project_core.llm.openrouter_client import OpenRouterClient
from project_core.models.loader import agent_profile
from project_core.service.supermarket_agent import SupermarketAgentService

logger = logging.getLogger(__name__)

_SERVER_FOR_FETCH = {
    "resolve_products": "product-lookup",
    "preview_table": "data-query",
    "query_rows": "data-query",
    "aggregate_rows": "data-query",
    "lookup_distinct": "data-query",
}
_DELIVERABLE_OPS = {
    "export_csv",
    "export_excel",
    "plot_chart",
    "bundle_deliverables",
    "inspect_excel",
    "validate_export",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _load_skill_corpus() -> str:
    parts: list[str] = []
    root = _repo_root() / "mcp-servers"
    if not root.is_dir():
        return ""
    for skills_dir in sorted(root.glob("*/skills")):
        for md in sorted(skills_dir.glob("*.md")):
            try:
                body = md.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if body:
                parts.append(f"### {md.parent.parent.name}/{md.stem}\n\n{body}")
    return "\n\n---\n\n".join(parts)


def _tool_catalog_json() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for tool_id, desc in FETCH_CATALOG.items():
        items.append(
            {
                "server": _SERVER_FOR_FETCH.get(tool_id, "data-query"),
                "tool_id": tool_id,
                "description": desc,
            }
        )
    for op_id, desc in OP_CATALOG.items():
        server = "deliverables" if op_id in _DELIVERABLE_OPS else "dataframe-ops"
        items.append({"server": server, "tool_id": op_id, "description": desc})
    return items


class ToolSelectorService(SupermarketAgentService):
    def decide(self, ctx: DecisionContext) -> Any:
        payload_in, meta = self.parse_payload(ctx)
        chunk_goal = str(
            payload_in.get("chunk_goal")
            or meta.get("chunk_goal")
            or payload_in.get("stage_goal")
            or ""
        ).strip()
        trace_id = str(payload_in.get("trace_id") or meta.get("trace_id") or "").strip()
        analysis_id = str(payload_in.get("analysis_id") or meta.get("analysis_id") or "").strip()
        actor_id = str(meta.get("actor_id") or ctx.request.actor_id or "tool-selector")
        turn = payload_in.get("turn") if payload_in.get("turn") is not None else meta.get("turn")
        started = time.perf_counter()

        if not chunk_goal:
            out = {"tools": [], "none_available": True, "reason": "empty_chunk_goal"}
            self._audit(trace_id, actor_id, analysis_id, chunk_goal, out, started, turn=turn, use_stub=False)
            return self.json_response(ctx, out)

        state = {
            "chunk_goal": chunk_goal,
            "brief_slice": payload_in.get("brief_slice") or meta.get("brief_slice") or {},
            "available_datasets": payload_in.get("available_datasets")
            or meta.get("available_datasets")
            or [],
            "prior_observations_summary": payload_in.get("prior_observations_summary")
            or meta.get("prior_observations_summary")
            or [],
            "case_hints": payload_in.get("case_hints") or meta.get("case_hints") or [],
            "tool_catalog": _tool_catalog_json(),
        }

        if os.getenv("ALLOW_LLM_STUB") == "1":
            out = self._stub(chunk_goal, state)
            self._audit(
                trace_id, actor_id, analysis_id, chunk_goal, out, started, turn=turn, use_stub=True
            )
            return self.json_response(ctx, out)

        system = self.llm_system_prompt(guide="select_guide")
        corpus = _load_skill_corpus()
        if corpus:
            system = system + "\n\n---\n\n## MCP skill corpus\n\n" + corpus[:120000]

        client = OpenRouterClient()
        result = client.chat(
            profile_name=agent_profile("tool_selector"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(state, ensure_ascii=False, default=str)},
            ],
            response_format={"type": "json_object"},
        )
        usage = int(getattr(result, "usage_tokens", 0) or 0)
        try:
            payload = parse_llm_json(result)
        except Exception as exc:  # noqa: BLE001
            logger.warning("tool_selector parse failed: %s", exc)
            out = {"tools": [], "none_available": True, "reason": f"parse_failed:{exc}"}
            self._audit(
                trace_id,
                actor_id,
                analysis_id,
                chunk_goal,
                out,
                started,
                turn=turn,
                use_stub=False,
                usage_tokens=usage,
            )
            return self.json_response(ctx, out, usage_tokens=usage)
        if not isinstance(payload, dict):
            payload = {"tools": [], "none_available": True, "reason": "non_object"}
        self._audit(
            trace_id,
            actor_id,
            analysis_id,
            chunk_goal,
            payload,
            started,
            turn=turn,
            use_stub=False,
            usage_tokens=usage,
        )
        return self.json_response(ctx, payload, usage_tokens=usage)

    def _audit(
        self,
        trace_id: str,
        actor_id: str,
        analysis_id: str,
        chunk_goal: str,
        payload: dict[str, Any],
        started: float,
        *,
        turn: Any = None,
        use_stub: bool,
        usage_tokens: int = 0,
    ) -> None:
        if not trace_id:
            return
        try:
            turn_i = int(turn) if turn is not None else None
        except (TypeError, ValueError):
            turn_i = None
        try:
            AuditLogger().log_tool_selector_suggest(
                trace_id=trace_id,
                actor_id=actor_id,
                analysis_id=analysis_id or None,
                chunk_goal=chunk_goal,
                tools=list(payload.get("tools") or []),
                none_available=bool(payload.get("none_available")),
                reason=str(payload.get("reason") or "") or None,
                duration_ms=int((time.perf_counter() - started) * 1000),
                use_stub=use_stub,
                usage_tokens=usage_tokens,
                turn=turn_i,
            )
        except Exception:  # noqa: BLE001
            logger.exception("tool_selector audit failed")

    def _stub(self, chunk_goal: str, state: dict[str, Any]) -> dict[str, Any]:
        goal = chunk_goal.lower()
        tools: list[dict[str, Any]] = []
        if "sku" in goal or "product" in goal or "mã" in goal or "resolve" in goal:
            tools.append(
                {
                    "server": "product-lookup",
                    "tool_id": "resolve_products",
                    "reason": "stub: product resolve",
                    "args_hints": {"codes": "from brief.filters.product_code"},
                }
            )
        if any(k in goal for k in ("fetch", "query", "bill", "sale", "strans", "transhdr", "dòng", "header")):
            tools.append(
                {
                    "server": "data-query",
                    "tool_id": "query_rows",
                    "reason": "stub: flexible query",
                    "args_hints": {"table": "STRANS|TRANSHDR", "filters": [], "time_range": "from brief"},
                }
            )
        if any(k in goal for k in ("export", "excel", "deliver")):
            tools.append(
                {
                    "server": "deliverables",
                    "tool_id": "export_excel",
                    "reason": "stub: export",
                    "args_hints": {"dataset": "latest analytical frame"},
                }
            )
        if any(k in goal for k in ("join", "filter", "top", "group", "rank")):
            tools.append(
                {
                    "server": "dataframe-ops",
                    "tool_id": "filter_rows" if "filter" in goal else "top_n_per_group",
                    "reason": "stub: transform",
                    "args_hints": {},
                }
            )
        if not tools:
            return {"tools": [], "none_available": True, "reason": "stub_no_match"}
        return {"tools": tools, "none_available": False}


def build_service(config: PlatformConfig, spec: AgentSpec) -> ToolSelectorService:
    root = Path(__file__).resolve().parent / "skills"
    return ToolSelectorService(config, spec, skills_root=root, agent_key="TOOL_SELECTOR")
