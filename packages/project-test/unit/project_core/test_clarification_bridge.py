from __future__ import annotations

from project_core.domain.clarification.bridge import ClarificationBridge
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.memory.session_bundle import TranscriptTurn


def test_bridge_resolves_vip_from_transcript():
    request = ClarificationRequest(
        reason="missing",
        partial_brief=AnalysisBrief(intent="VIP points"),
        questions=[
            {
                "id": "vip_card_prefix",
                "prompt": "VIP?",
                "options": [],
                "maps_to_brief_field": "filters.card_prefix",
            }
        ],
    )
    transcript = [
        TranscriptTurn(id="1", role="user", content="VIP card prefix E trans_code 221", at="now"),
    ]
    result = ClarificationBridge().from_transcript_heuristic(request, transcript)
    assert result.action == "resolve_from_transcript"
    assert result.confidence >= 0.75
