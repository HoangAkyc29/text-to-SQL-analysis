from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import DecisionContext

from project_core.config.loader import load_project_config
from project_core.domain.clarification.bridge import ClarificationBridge
from project_core.domain.contracts.brief import AnalysisBrief, BriefRequirement
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.brief.templates import brief_templates_excerpt
from project_core.domain.errors.codes import LLMProviderError
from project_core.domain.feedback.satisfaction_rules import detect_satisfaction
from project_core.llm.json_parse import completion_text, parse_llm_json
from project_core.llm.openrouter_client import ChatCompletionResult, OpenRouterClient
from project_core.models.loader import agent_profile
from project_core.service.supermarket_agent import SupermarketAgentService

logger = logging.getLogger(__name__)

_ANALYSIS_HINTS = ("vip", "doanh", "bán", "chart", "điểm", "revenue", "tồn kho", "inventory")


_TECH_TERMS = ("sku_id", "trans_num", "transhdr", "strans", "barcode", "mã vạch đầy đủ")


def _downgrade_knowledge_if_informal(text: str, brief_data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Post-LLM guard: informal multi-SKU requests should not default to expert."""
    if not brief_data:
        return brief_data
    lowered = text.lower()
    if any(t in lowered for t in _TECH_TERMS):
        return brief_data
    filters = brief_data.get("filters") or {}
    codes = filters.get("product_code") or filters.get("sku")
    multi = isinstance(codes, list) and len(codes) >= 2
    has_bill = filters.get("min_bill_value") or filters.get("min_transaction_value")
    if multi or (codes and has_bill):
        brief_data = dict(brief_data)
        brief_data["user_knowledge_level"] = "unknown"
        brief_data["exploration_mode"] = True
    return brief_data


def _normalize_requirement_provenance(
    text: str,
    brief_data: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Keep inferred fields usable, but only quoted user asks are blocking."""
    if not brief_data:
        return brief_data

    def _norm(value: Any) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip().lower())

    normalized_text = _norm(text)
    supplied: dict[tuple[str, str], BriefRequirement] = {}
    ranking: list[BriefRequirement] = []
    for raw in brief_data.get("requirements") or []:
        if not isinstance(raw, dict):
            continue
        try:
            item = BriefRequirement.model_validate(raw)
        except Exception:  # noqa: BLE001
            continue
        quote = _norm(item.evidence_quote)
        is_explicit = bool(quote and quote in normalized_text and item.source == "explicit")
        item = item.model_copy(
            update={
                "source": "explicit" if is_explicit else "inferred",
                "required": bool(item.required and is_explicit),
            }
        )
        if item.kind == "ranking":
            ranking.append(item)
        else:
            supplied[(item.kind, _norm(item.key))] = item

    generated: list[BriefRequirement] = []

    def _append(kind: str, key: str, value: Any, index: int) -> None:
        lookup = (kind, _norm(key))
        existing = supplied.get(lookup)
        if existing is not None:
            generated.append(existing.model_copy(update={"value": value}))
            return
        generated.append(
            BriefRequirement(
                requirement_id=f"{kind}:{index}",
                kind=kind,
                key=str(key),
                source="inferred",
                required=False,
                value=value,
            )
        )

    for index, value in enumerate(brief_data.get("metrics") or []):
        _append("metric", str(value), value, index)
    for index, value in enumerate(brief_data.get("dimensions") or []):
        _append("dimension", str(value), value, index)
    for index, (key, value) in enumerate((brief_data.get("filters") or {}).items()):
        _append("filter", str(key), value, index)
    time_range = brief_data.get("time_range") or {}
    if time_range.get("start") or time_range.get("end") or time_range.get("grain"):
        _append("time", "time_range", dict(time_range), 0)
    for index, value in enumerate(brief_data.get("output_format") or []):
        _append("output", str(value), value, index)
    generated.extend(ranking)

    explicit_time_dimension = next(
        (
            item
            for item in generated
            if item.kind == "dimension"
            and _norm(item.key) in {"time", "date", "period"}
            and item.source == "explicit"
            and item.required
        ),
        None,
    )
    date_mentions = list(
        re.finditer(r"\b\d{1,4}[-/]\d{1,2}[-/]\d{1,4}\b", text)
    )
    time_evidence = (
        explicit_time_dimension.evidence_quote
        if explicit_time_dimension is not None
        else text[date_mentions[0].start() : date_mentions[1].end()]
        if len(date_mentions) >= 2
        else ""
    )
    if time_evidence:
        generated = [
            item.model_copy(
                update={
                    "source": "explicit",
                    "required": True,
                    "evidence_quote": time_evidence,
                }
            )
            if item.kind == "time" and item.source == "inferred"
            else item
            for item in generated
        ]

    if not any(item.kind == "ranking" for item in generated):
        ranking_match = re.search(
            r"(?P<quote>(?:top|list|danh\s+sách)\s*(?P<limit>\d+)"
            r"[^.!?\n]{0,80}?(?:gần\s+nhất|latest|most\s+recent|recent))",
            text,
            flags=re.IGNORECASE,
        )
        if ranking_match:
            partition_candidates = [
                item.key
                for item in generated
                if item.kind == "dimension"
                and item.source == "explicit"
                and _norm(item.key) not in {"time", "date", "period", "transaction"}
            ]
            generated.append(
                BriefRequirement(
                    requirement_id="ranking:0",
                    kind="ranking",
                    key="top_n",
                    source="explicit",
                    required=True,
                    evidence_quote=ranking_match.group("quote").strip(),
                    value={
                        "limit": int(ranking_match.group("limit")),
                        "partition_by": partition_candidates[0]
                        if len(partition_candidates) == 1
                        else None,
                        "order_by": "time",
                        "direction": "desc",
                    },
                )
            )

    result = dict(brief_data)
    result["requirements"] = [item.model_dump(mode="json") for item in generated]
    return result


def _deterministic_synthesis(summary: dict[str, Any]) -> dict[str, Any]:
    """Render only verified pipeline facts; never ask an LLM to invent prose."""
    outcome = str(summary.get("outcome") or "partial")
    metrics = dict(summary.get("headline_metrics") or {})
    artifacts = [str(item) for item in (summary.get("artifact_urls") or [])]
    verification = dict(summary.get("verification") or {})
    coverage = dict(summary.get("coverage") or {})
    gaps = [str(item) for item in (coverage.get("gaps") or [])]
    row_count = int(metrics.get("row_count") or 0)
    if not row_count and isinstance(metrics.get("artifact_rows"), dict):
        row_count = max(
            (int(value or 0) for value in metrics["artifact_rows"].values()),
            default=0,
        )

    sentences: list[str] = []
    if outcome == "success":
        if verification.get("status") == "passed":
            sentences.append(
                "Phân tích đã hoàn tất và kết quả đầu ra đã vượt qua kiểm tra dữ liệu."
            )
        else:
            sentences.append("Phân tích đã hoàn tất.")
    elif outcome == "partial":
        sentences.append("Phân tích đã hoàn thành một phần.")
    elif outcome == "empty":
        sentences.append("Không tìm thấy dữ liệu phù hợp với các điều kiện đã yêu cầu.")
    elif outcome == "policy_blocked":
        sentences.append("Yêu cầu chưa thể thực hiện do giới hạn quyền truy cập dữ liệu.")
    else:
        sentences.append("Phân tích chưa thể hoàn tất.")

    if row_count > 0 and outcome in {"success", "partial"}:
        sentences.append(f"Kết quả chi tiết gồm {row_count} dòng dữ liệu.")

    if outcome == "partial" and gaps:
        readable: list[str] = []
        for gap in gaps[:4]:
            prefix, _, detail = gap.partition(":")
            label = {
                "missing_filter": "bằng chứng bộ lọc",
                "missing_ranking": "kiểm tra xếp hạng",
                "missing_time_evidence": "bằng chứng thời gian",
                "missing_metric": "chỉ số",
                "missing_dimension": "chiều phân tích",
                "unmapped_requirement": "liên kết yêu cầu",
            }.get(prefix, "một yêu cầu đầu ra")
            readable.append(f"{label}{f' ({detail})' if detail else ''}")
        sentences.append("Chưa xác minh được: " + ", ".join(readable) + ".")

    if artifacts:
        sentences.append("File kết quả đã sẵn sàng để tải xuống.")
    return {
        "user_message": " ".join(sentences),
        "artifacts": artifacts,
    }


class ConversationalRouterService(SupermarketAgentService):
    def decide(self, ctx: DecisionContext) -> Any:
        mode = (ctx.request.metadata or {}).get("mode", "ingress")
        if mode == "clarification_bridge":
            return self._clarification_bridge(ctx)
        if mode == "clarify":
            return self._clarify(ctx)
        if mode == "synthesize":
            return self._synthesize(ctx)
        return self._ingress(ctx)

    def _ingress_heuristic(self, text: str, external_sources: list[Any]) -> dict[str, Any]:
        lowered = text.lower()
        route = "analysis" if any(k in lowered for k in _ANALYSIS_HINTS) else "chitchat"
        brief: AnalysisBrief | None = None
        if route == "analysis":
            metric = (
                "inventory"
                if any(token in lowered for token in ("tồn kho", "inventory"))
                else "revenue"
                if any(token in lowered for token in ("doanh thu", "revenue"))
                else None
            )
            brief = AnalysisBrief(
                intent=text,
                metrics=[metric] if metric else [],
                output_format=["table"],
                requirements=[
                    BriefRequirement(
                        requirement_id="metric:0",
                        kind="metric",
                        key=metric,
                        source="explicit",
                        required=True,
                        evidence_quote=text,
                        value=metric,
                    )
                ]
                if metric
                else [],
            )
            if external_sources:
                from project_core.domain.contracts.external_source import ExternalSource

                brief.external_sources = [ExternalSource.model_validate(s) for s in external_sources]
                excerpts = [s.get("text_excerpt", "")[:500] for s in external_sources if s.get("text_excerpt")]
                if excerpts:
                    brief.intent = f"{text}\n\n[Attachments]\n" + "\n".join(excerpts)
        return {
            "route": route,
            "user_message": "Đã nhận yêu cầu phân tích." if route == "analysis" else "Xin chào, tôi có thể giúp gì?",
            "brief": brief.model_dump() if brief else None,
        }

    def _parse_json_payload(
        self,
        result: ChatCompletionResult,
        *,
        fallback_text: str = "",
        external_sources: list[Any] | None = None,
    ) -> dict[str, Any]:
        try:
            return parse_llm_json(result)
        except LLMProviderError as exc:
            logger.error(
                "Agent I absolute failure (LLM JSON parse): %s; content=%r",
                exc,
                completion_text(result)[:200],
            )
            # Never degrade to ingress heuristic while ALLOW_LLM_STUB=0.
            raise

    def _ingress(self, ctx: DecisionContext):
        meta = ctx.request.metadata or {}
        raw = ctx.request.message or ""
        external_sources = meta.get("external_sources") or []
        text = raw
        if raw.startswith("{"):
            try:
                payload = json.loads(raw)
                text = payload.get("text") or raw
                external_sources = payload.get("external_sources") or external_sources
            except json.JSONDecodeError:
                pass
        satisfaction = detect_satisfaction(text)
        if os.getenv("ALLOW_LLM_STUB") == "1":
            payload_out = self._ingress_heuristic(text, external_sources)
            payload_out["satisfaction_signal"] = satisfaction
            return self.json_response(ctx, payload_out)
        user_content: dict[str, Any] = {"text": text}
        if external_sources:
            user_content["external_sources"] = external_sources
        templates = brief_templates_excerpt()
        if templates:
            user_content["brief_templates_excerpt"] = templates
        client = OpenRouterClient()
        result = client.chat(
            profile_name=agent_profile("router"),
            messages=[
                {
                    "role": "system",
                    "content": self.llm_system_prompt(
                        guide="ingress_guide",
                        extra=f"## Brief templates\n\n{templates}" if templates else None,
                    ),
                },
                {"role": "user", "content": json.dumps(user_content, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
        )
        payload = self._parse_json_payload(result, fallback_text=text, external_sources=external_sources)
        if payload.get("brief"):
            payload["brief"] = _downgrade_knowledge_if_informal(text, payload["brief"])
            payload["brief"] = _normalize_requirement_provenance(text, payload["brief"])
        if satisfaction:
            payload["satisfaction_signal"] = satisfaction
        return self.json_response(ctx, payload, usage_tokens=result.usage_tokens)

    def _clarification_bridge(self, ctx: DecisionContext):
        meta = ctx.request.metadata or {}
        request = ClarificationRequest.model_validate(meta["clarification_request"])
        transcript = meta.get("transcript") or []
        cfg = load_project_config()
        bridge = ClarificationBridge(min_confidence=cfg.clarification.bridge_min_confidence)
        if os.getenv("ALLOW_LLM_STUB") == "1":
            from project_core.domain.memory.session_bundle import TranscriptTurn

            turns = [TranscriptTurn.model_validate(t) if isinstance(t, dict) else t for t in transcript]
            result = bridge.from_transcript_heuristic(request, turns)
        else:
            client = OpenRouterClient()
            llm = client.chat(
                profile_name=agent_profile("router"),
                messages=[
                    {"role": "system", "content": self.llm_system_prompt(guide="clarification_bridge_guide")},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {"request": request.model_dump(), "transcript": transcript},
                            ensure_ascii=False,
                        ),
                    },
                ],
                response_format={"type": "json_object"},
            )
            result = ClarificationBridge.parse_llm_bridge(completion_text(llm), request)
        return self.json_response(ctx, result.model_dump())

    def _clarify(self, ctx: DecisionContext):
        meta = ctx.request.metadata or {}
        request = ClarificationRequest.model_validate(meta["clarification_request"])
        if os.getenv("ALLOW_LLM_STUB") == "1":
            payload = {
                "user_message": "Vui lòng chọn thêm thông tin để tiếp tục phân tích.",
                "clarification": request.model_dump(),
            }
            return self.json_response(ctx, payload)
        client = OpenRouterClient()
        templates = brief_templates_excerpt()
        result = client.chat(
            profile_name=agent_profile("router"),
            messages=[
                {
                    "role": "system",
                    "content": self.llm_system_prompt(
                        guide="clarify_guide",
                        extra=f"## Brief templates\n\n{templates}" if templates else None,
                    ),
                },
                {"role": "user", "content": json.dumps(request.model_dump(), ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
        )
        payload = parse_llm_json(result)
        payload.setdefault("clarification", request.model_dump())
        return self.json_response(ctx, payload)

    def _synthesize(self, ctx: DecisionContext):
        meta = ctx.request.metadata or {}
        summary = meta.get("technical_summary") or {}
        return self.json_response(ctx, _deterministic_synthesis(summary))


def build_service(config: PlatformConfig, spec: AgentSpec) -> ConversationalRouterService:
    skills_root = Path(__file__).resolve().parent / "skills"
    return ConversationalRouterService(config, spec, skills_root=skills_root, agent_key="I")
