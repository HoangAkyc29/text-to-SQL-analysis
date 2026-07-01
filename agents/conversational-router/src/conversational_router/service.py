from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import DecisionContext

from project_core.domain.clarification.bridge import ClarificationBridge
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.feedback.satisfaction_rules import detect_satisfaction
from project_core.llm.openrouter_client import OpenRouterClient
from project_core.models.loader import agent_profile
from project_core.service.supermarket_agent import SupermarketAgentService


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
            route = "analysis" if any(k in text.lower() for k in ("vip", "doanh", "bán", "chart", "điểm")) else "chitchat"
            brief = None
            if route == "analysis":
                brief = AnalysisBrief(intent=text, metrics=["points"], output_format=["chart"])
                if external_sources:
                    from project_core.domain.contracts.external_source import ExternalSource

                    brief.external_sources = [ExternalSource.model_validate(s) for s in external_sources]
                    excerpts = [s.get("text_excerpt", "")[:500] for s in external_sources if s.get("text_excerpt")]
                    if excerpts:
                        brief.intent = f"{text}\n\n[Attachments]\n" + "\n".join(excerpts)
            payload_out = {
                "route": route,
                "user_message": "Đã nhận yêu cầu phân tích." if route == "analysis" else "Xin chào, tôi có thể giúp gì?",
                "brief": brief.model_dump() if brief else None,
                "satisfaction_signal": satisfaction,
            }
            return self.json_response(ctx, payload_out)
        user_content: dict[str, Any] = {"text": text}
        if external_sources:
            user_content["external_sources"] = external_sources
        client = OpenRouterClient()
        result = client.chat(
            profile_name=agent_profile("router"),
            messages=[
                {"role": "system", "content": self.llm_system_prompt(guide="ingress_guide")},
                {"role": "user", "content": json.dumps(user_content, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
        )
        payload = json.loads(result.content)
        if satisfaction:
            payload["satisfaction_signal"] = satisfaction
        return self.json_response(ctx, payload)

    def _clarification_bridge(self, ctx: DecisionContext):
        meta = ctx.request.metadata or {}
        request = ClarificationRequest.model_validate(meta["clarification_request"])
        transcript = meta.get("transcript") or []
        bridge = ClarificationBridge()
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
            result = ClarificationBridge.parse_llm_bridge(llm.content, request)
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
        result = client.chat(
            profile_name=agent_profile("router"),
            messages=[
                {"role": "system", "content": self.llm_system_prompt(guide="clarify_guide")},
                {"role": "user", "content": json.dumps(request.model_dump(), ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
        )
        payload = json.loads(result.content)
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
        return self.json_response(ctx, json.loads(result.content))


def build_service(config: PlatformConfig, spec: AgentSpec) -> ConversationalRouterService:
    skills_root = Path(__file__).resolve().parent / "skills"
    return ConversationalRouterService(config, spec, skills_root=skills_root, agent_key="I")
