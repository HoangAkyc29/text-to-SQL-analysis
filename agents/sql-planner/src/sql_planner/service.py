from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import DecisionContext

from project_core.domain.brief.merge import apply_data_feedback
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.contracts.feedback import DataFeedback
from project_core.domain.product.resolver import resolve_product_code
from project_core.domain.sql.shard_resolver import build_db1_union_sql
from project_core.domain.errors.codes import LLMProviderError
from project_core.llm.json_parse import completion_text, parse_llm_json
from project_core.llm.openrouter_client import OpenRouterClient
from project_core.models.loader import agent_profile
from project_core.service.supermarket_agent import SupermarketAgentService

logger = logging.getLogger(__name__)

# Operational policy: LLM failure must never degrade to heuristic stub SQL.
AGENT_LLM_ABSOLUTE_FAILURE = "AGENT_LLM_ABSOLUTE_FAILURE"


class SqlPlannerService(SupermarketAgentService):
    def decide(self, ctx: DecisionContext) -> Any:
        payload_in, meta = self.parse_payload(ctx)
        brief = AnalysisBrief.model_validate(payload_in.get("brief") or meta.get("brief") or {})
        inbox = payload_in.get("inbox") or meta.get("inbox") or {}
        attempt = int(payload_in.get("attempt") or meta.get("attempt") or 1)
        schema_context = payload_in.get("schema_context") or meta.get("schema_context") or {}
        retrieval_context = payload_in.get("retrieval_context") or meta.get("retrieval_context") or []
        mode = str(meta.get("mode") or payload_in.get("mode") or "plan_sql")

        permissions = self.resolve_permissions(payload_in, meta)
        if permissions is None or not self.context_policy.can_invoke_tool(
            permissions, "II", "validate_sql"
        ):
            return self.json_response(
                ctx,
                {"action": "impossible", "reason": "tool_not_granted:validate_sql"},
            )

        if not retrieval_context and getattr(self, "retriever", None):
            if hasattr(self.retriever, "retrieve_hierarchical"):
                from project_core.domain.retrieval.query_builder import build_retrieval_query

                result = self.retriever.retrieve_hierarchical(
                    build_retrieval_query(brief.intent, brief), top_k=8
                )
                retrieval_context = result.to_payload()
            else:
                chunks = self.retrieve(brief.intent, top_k=5)
                retrieval_context = [c.text for c in chunks]

        if inbox.get("data_feedback"):
            brief = apply_data_feedback(brief, inbox["data_feedback"])

        # Test harness only. Production/ops must keep ALLOW_LLM_STUB=0.
        # Stub in a live agent path is never a valid degradation — see absolute failure below.
        if os.getenv("ALLOW_LLM_STUB") == "1":
            if mode == "select_tables":
                return self._stub_select_tables(ctx, brief, schema_context)
            return self._stub_plan(ctx, brief, inbox, attempt, schema_context)

        guide = "select_tables_guide" if mode == "select_tables" else "plan_sql_guide"
        extra = None
        if mode != "select_tables" and (inbox.get("probe_mode") or inbox.get("data_feedback")):
            probe = self.skill.guide("probe_feedback_guide") if self.skill else ""
            if probe.strip():
                extra = probe

        client = OpenRouterClient()
        result = None
        try:
            result = client.chat(
                profile_name=agent_profile("sql_planner"),
                messages=[
                    {"role": "system", "content": self.llm_system_prompt(guide=guide, extra=extra)},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "brief": brief.model_dump(),
                                "inbox": inbox,
                                "attempt": attempt,
                                "schema_context": schema_context,
                                "retrieval_context": retrieval_context,
                                "mode": mode,
                            },
                            ensure_ascii=False,
                        ),
                    },
                ],
                response_format={"type": "json_object"},
            )
            payload = parse_llm_json(result)
        except LLMProviderError as exc:
            snippet = completion_text(result)[:300] if result is not None else ""
            logger.error(
                "Agent II absolute failure mode=%s: %s content=%r",
                mode,
                exc,
                snippet,
            )
            return self.json_response(
                ctx,
                {
                    "action": "impossible",
                    "reason": AGENT_LLM_ABSOLUTE_FAILURE,
                    "reasoning": f"LLM {mode} failed — stub fallback forbidden: {exc}",
                },
            )
        return self.json_response(ctx, payload, usage_tokens=result.usage_tokens)

    def _stub_select_tables(
        self,
        ctx: DecisionContext,
        brief: AnalysisBrief,
        schema_context: dict,
    ):
        filters = brief.filters or {}
        intent = (brief.intent or "").lower()
        tables: list[str] = []
        if filters.get("product_code") or filters.get("sku") or any(
            k in intent for k in ("sku", "mã hàng", "san pham", "quà", "qua tang", "gift")
        ):
            tables.extend(["SKU_DEF", "STRANS"])
        if any(k in intent for k in ("bill", "hóa đơn", "hoa don", "transhdr")):
            tables.append("TRANSHDR")
        if "vip" in intent or "thẻ" in intent or "the " in intent:
            tables.extend(["CSCARD", "PMTRANS"])
        if any(k in intent for k in ("tồn", "ton kho", "inventory", "onhand")):
            tables.append("STK_DTL")
        if not tables:
            tables = ["STRANS"]
        # Preserve order, cap 6
        ordered: list[str] = []
        for t in tables:
            if t not in ordered:
                ordered.append(t)
        ordered = ordered[:6]
        logical = schema_context.get("logical_tables") or []
        if logical:
            allowed = {str(x).upper() for x in logical}
            filtered = [t for t in ordered if t.upper() in allowed]
            if filtered:
                ordered = filtered
        return self.json_response(
            ctx,
            {
                "action": "select_tables",
                "selected_tables": ordered,
                "selected_target_dbs": ["db2"] * len(ordered),
                "reasoning": "stub select_tables from brief cues",
            },
        )

    def _stub_plan(
        self,
        ctx: DecisionContext,
        brief: AnalysisBrief,
        inbox: dict,
        attempt: int,
        schema_context: dict,
    ):
        filters = brief.filters or {}

        if inbox.get("probe_mode") or inbox.get("data_feedback"):
            probe_result = self._probe_plan(brief, inbox)
            if probe_result:
                return self.json_response(ctx, probe_result)

        if (
            attempt == 1
            and not brief.exploration_mode
            and not filters.get("card_prefix")
            and "vip" in brief.intent.lower()
        ):
            req = ClarificationRequest(
                reason="missing_vip_definition",
                partial_brief=brief,
                questions=[
                    {
                        "id": "vip_card_prefix",
                        "prompt": "VIP được định nghĩa thế nào?",
                        "options": [
                            {
                                "id": "prefix_e",
                                "label": "Card bắt đầu E",
                                "brief_value": {"filters": {"card_prefix": "E"}},
                            },
                            {
                                "id": "tier_vip",
                                "label": "Tier VIP",
                                "brief_value": {"filters": {"loyalty_tier": "VIP"}},
                            },
                            {
                                "id": "unknown",
                                "label": "Tôi không chắc — hãy khám phá dữ liệu",
                                "brief_value": {"exploration_mode": True, "user_knowledge_level": "unknown"},
                            },
                        ],
                        "maps_to_brief_field": "filters.card_prefix",
                    }
                ],
            )
            return self.json_response(ctx, {"action": "clarify", "clarification_request": req.model_dump()})

        if brief.plan and brief.plan.is_decomposed and len(brief.plan.subtasks) > 1:
            return self.json_response(ctx, self._plan_for_subtasks(brief, attempt))

        product_code = filters.get("product_code") or filters.get("sku")
        sql: list[str] = []
        query_meta: list[dict[str, str]] = []
        target_dbs: list[str] = []

        if product_code:
            if isinstance(product_code, list):
                product_code = product_code[0] if product_code else ""
            resolved = resolve_product_code(str(product_code))
            for probe in resolved.probe_sql:
                sql.append(probe)
                query_meta.append({"role": "probe", "purpose": "product_lookup"})
                target_dbs.append("db2")
            best = resolved.candidates[0] if resolved.candidates else None
            predicate = best.sql_predicate if best else f"SKU_ID = '{product_code}'"
            sql.append(
                f"SELECT TOP 50000 SKU_ID, SUM(AMOUNT) AS total_amount FROM STRANS "
                f"WHERE LOWER(TRANS_CODE) LIKE '%' + LOWER('113') + '%' AND {predicate} GROUP BY SKU_ID"
            )
            query_meta.append({"role": "main", "purpose": "product_revenue"})
            target_dbs.append("db2")
        elif brief.exploration_mode or brief.user_knowledge_level == "unknown":
            sql = [
                (
                    "SELECT TOP 50000 FORMAT(s.TRAN_DATE,'yyyy-MM') AS month, "
                    "SUM(s.AMOUNT) AS monthly_amount FROM STRANS s "
                    "WHERE LOWER(s.TRANS_CODE) LIKE '%' + LOWER('113') + '%' GROUP BY FORMAT(s.TRAN_DATE,'yyyy-MM')"
                ),
                (
                    "SELECT TOP 50000 s.STK_ID, SUM(s.AMOUNT) AS store_amount FROM STRANS s "
                    "WHERE LOWER(s.TRANS_CODE) LIKE '%' + LOWER('113') + '%' GROUP BY s.STK_ID"
                ),
                (
                    "SELECT TOP 100 SKU_ID, SKU_CODE, BARCODE FROM SKU_DEF"
                ),
            ]
            query_meta = [
                {"role": "main", "purpose": "monthly_trend"},
                {"role": "main", "purpose": "by_store"},
                {"role": "probe", "purpose": "sku_sample"},
            ]
            target_dbs = ["db2", "db2", "db2"]
        else:
            sql = [
                (
                    f"SELECT TOP 50000 c.CARD_ID, SUM(p.AMOUNT) AS total_amount "
                    f"FROM CSCARD c JOIN PMTRANS p ON p.CARD_ID = c.CARD_ID "
                    f"WHERE LOWER(p.TRANS_CODE) LIKE '%' + LOWER('221') + '%' GROUP BY c.CARD_ID"
                ),
                (
                    "SELECT TOP 50000 FORMAT(s.TRAN_DATE,'yyyy-MM') AS month, SUM(s.AMOUNT) AS monthly_amount "
                    "FROM STRANS s WHERE LOWER(s.TRANS_CODE) LIKE '%' + LOWER('113') + '%' GROUP BY FORMAT(s.TRAN_DATE,'yyyy-MM')"
                ),
            ]
            query_meta = [{"role": "main"}, {"role": "main"}]
            target_dbs = ["db2", "db2"]

        if inbox.get("data_feedback"):
            fb = inbox["data_feedback"]
            issue = fb.get("issue") if isinstance(fb, dict) else ""
            if issue == "grain" and attempt > 1:
                sql = [
                    (
                        "SELECT TOP 50000 s.TRANS_NUM, s.SKU_ID, s.AMOUNT, s.QTY "
                        "FROM STRANS s WHERE LOWER(s.TRANS_CODE) LIKE '%' + LOWER('113') + '%'"
                    )
                ]
                query_meta = [{"role": "main", "purpose": "line_level"}]
                target_dbs = ["db2"]

        shard_plan = (schema_context or {}).get("shard_plan") or {}
        if shard_plan.get("needs_db1") and shard_plan.get("shards"):
            shards = shard_plan["shards"]
            union_sql: list[str] = []
            union_dbs: list[str] = []
            for q in sql:
                union_sql.append(build_db1_union_sql(q, shards))
                union_dbs.append("db1")
            if union_sql:
                sql = union_sql
                target_dbs = union_dbs

        return self.json_response(
            ctx,
            {
                "action": "plan_sql",
                "sql_queries": sql,
                "query_meta": query_meta,
                "target_dbs": target_dbs,
                "target_db": "db2",
                "reasoning": "Plan using data_dictionary tables",
                "attempt": attempt,
                "schema_tables_used": ["CSCARD", "PMTRANS", "STRANS", "SKU_DEF", "BARCODE"],
            },
        )

    def _probe_plan(self, brief: AnalysisBrief, inbox: dict) -> dict[str, Any] | None:
        raw = inbox.get("data_feedback") or {}
        try:
            fb = DataFeedback.model_validate(raw)
        except Exception:
            return None
        if not fb.probe_requests:
            return None
        # Stub harness only: copy SQL if IV/tests explicitly provided it.
        # Production LLM path never relies on this — empty suggested_sql → no stub probe plan.
        sql = [p.suggested_sql for p in fb.probe_requests[:3] if (p.suggested_sql or "").strip()]
        if not sql:
            return None
        return {
            "action": "probe_sql",
            "sql_queries": sql,
            "query_meta": [{"role": "probe", "purpose": p.purpose} for p in fb.probe_requests[:3] if (p.suggested_sql or "").strip()],
            "target_dbs": ["db2"] * len(sql),
            "reasoning": "IV-requested probe SQL",
        }

    def _plan_for_subtasks(self, brief: AnalysisBrief, attempt: int) -> dict[str, Any]:
        sql: list[str] = []
        query_meta: list[dict[str, str]] = []
        target_dbs: list[str] = []
        assert brief.plan is not None
        for subtask in brief.plan.subtasks:
            lower = subtask.intent.lower()
            if "inventory" in lower or "tồn" in lower:
                sql.append("SELECT TOP 50000 STK_ID, SKU_ID, QTY_ONHAND FROM STK_DTL")
                query_meta.append({"role": "main", "purpose": "inventory", "subtask_id": subtask.id})
            elif "vip" in lower:
                sql.append(
                    "SELECT TOP 50000 c.CARD_ID, SUM(p.AMOUNT) AS total_amount "
                    "FROM CSCARD c JOIN PMTRANS p ON p.CARD_ID = c.CARD_ID "
                    "WHERE LOWER(p.TRANS_CODE) LIKE '%' + LOWER('221') + '%' GROUP BY c.CARD_ID"
                )
                query_meta.append({"role": "main", "purpose": "vip_revenue", "subtask_id": subtask.id})
            elif "trend" in lower or "tháng" in lower or "month" in lower:
                sql.append(
                    "SELECT TOP 50000 FORMAT(s.TRAN_DATE,'yyyy-MM') AS month, "
                    "SUM(s.AMOUNT) AS monthly_amount FROM STRANS s "
                    "WHERE LOWER(s.TRANS_CODE) LIKE '%' + LOWER('113') + '%' GROUP BY FORMAT(s.TRAN_DATE,'yyyy-MM')"
                )
                query_meta.append({"role": "main", "purpose": "monthly_trend", "subtask_id": subtask.id})
            else:
                sql.append(
                    "SELECT TOP 50000 s.STK_ID, SUM(s.AMOUNT) AS store_amount FROM STRANS s "
                    "WHERE LOWER(s.TRANS_CODE) LIKE '%' + LOWER('113') + '%' GROUP BY s.STK_ID"
                )
                query_meta.append({"role": "main", "purpose": "revenue", "subtask_id": subtask.id})
            target_dbs.append("db2")
        return {
            "action": "plan_sql",
            "sql_queries": sql,
            "query_meta": query_meta,
            "target_dbs": target_dbs,
            "target_db": "db2",
            "reasoning": f"Decomposed plan with {len(sql)} subtasks",
            "attempt": attempt,
            "schema_tables_used": ["STRANS", "PMTRANS", "CSCARD", "STK_DTL"],
        }


def build_service(config: PlatformConfig, spec: AgentSpec) -> SqlPlannerService:
    from project_core.infra.mongo_factory import try_create_hybrid_retriever

    skills_root = Path(__file__).resolve().parent / "skills"
    retriever = try_create_hybrid_retriever()
    return SqlPlannerService(config, spec, skills_root=skills_root, agent_key="II", retriever=retriever)
