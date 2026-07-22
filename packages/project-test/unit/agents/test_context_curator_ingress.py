from __future__ import annotations

from conversational_router.service import ConversationalRouterService


def test_ingress_stub_follow_up_with_context_pack(monkeypatch):
    monkeypatch.setenv("ALLOW_LLM_STUB", "1")
    svc = ConversationalRouterService.__new__(ConversationalRouterService)

    class FakeCtx:
        def __init__(self):
            self.request = type(
                "R",
                (),
                {
                    "session_id": "s",
                    "actor_id": "a",
                    "message": "làm tương tự với mã 30323",
                    "metadata": {
                        "mode": "ingress",
                        "context_pack": {
                            "current_message": "làm tương tự với mã 30323",
                            "last_resolved_brief": {
                                "intent": "Phân tích quà tặng 0030344",
                                "metrics": ["quantity"],
                                "filters": {
                                    "product_code": ["0030344"],
                                    "min_bill_value": 600000,
                                },
                                "time_range": {
                                    "start": "2026-07-01",
                                    "end": "2026-07-06",
                                    "grain": "day",
                                },
                                "output_format": ["excel", "table"],
                            },
                            "working_memory": {"current_goal": "gift analysis"},
                            "selected_turns": [],
                            "sticky_rules": [],
                        },
                    },
                },
            )()

    out = ConversationalRouterService._ingress(svc, FakeCtx())
    payload = out.payload
    assert payload["dialogue_act"] == "follow_up_same_task"
    assert payload["route"] == "analysis"
    assert payload["brief"]["filters"]["product_code"] == "30323"


def test_curator_stub(monkeypatch):
    monkeypatch.setenv("ALLOW_LLM_STUB", "1")
    svc = ConversationalRouterService.__new__(ConversationalRouterService)

    class FakeCtx:
        def __init__(self):
            self.request = type(
                "R",
                (),
                {
                    "session_id": "s",
                    "actor_id": "a",
                    "message": '{"current_message":"x","candidates":[{"id":"1","kind":"analysis"},{"id":"2","kind":"satisfaction"}]}',
                    "metadata": {"mode": "context_curator"},
                },
            )()

    out = ConversationalRouterService._context_curator(svc, FakeCtx())
    payload = out.payload
    assert "1" in payload["selected_turn_ids"]
    assert "2" in payload["drop_turn_ids"]
