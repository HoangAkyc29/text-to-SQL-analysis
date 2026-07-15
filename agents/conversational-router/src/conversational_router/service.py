from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import DecisionContext

from project_core.config.loader import load_project_config
from project_core.domain.clarification.bridge import ClarificationBridge
from project_core.domain.contracts.brief import AnalysisBrief
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
            brief = AnalysisBrief(intent=text, metrics=["revenue"], output_format=["table"])
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
        if os.getenv("ALLOW_LLM_STUB") == "1":
            payload = {
                "user_message": f"Kết quả: {summary.get('outcome', 'done')}.",
                "artifacts": summary.get("artifact_urls") or [],
            }
            return self.json_response(ctx, payload)
        client = OpenRouterClient()
        result = client.chat(
            profile_name=agent_profile("router"),
            messages=[
                {"role": "system", "content": self.llm_system_prompt(guide="synthesize_guide")},
                {"role": "user", "content": json.dumps(summary, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
        )
        return self.json_response(ctx, parse_llm_json(result))


def build_service(config: PlatformConfig, spec: AgentSpec) -> ConversationalRouterService:
    skills_root = Path(__file__).resolve().parent / "skills"
    return ConversationalRouterService(config, spec, skills_root=skills_root, agent_key="I")
