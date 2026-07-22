from __future__ import annotations

from project_core.config.loader import ContextPackConfig
from project_core.domain.contracts.brief import AnalysisBrief, BriefRequirement, TimeRange
from project_core.domain.brief.session_merge import (
    empty_follow_up_message,
    pad_product_codes_to_prior,
    rewrite_anaphora_intent,
    session_merge_brief,
)
from project_core.domain.contracts.workflow import WorkflowState
from project_core.domain.memory.context_pack import (
    apply_curator_selection,
    build_candidates,
    build_context_pack_hard,
    has_follow_up_signal,
    should_invoke_curator,
    trim_turn_content,
)
from project_core.domain.memory.session_bundle import TranscriptTurn
from project_core.domain.memory.working_memory import SelectedTurn, WorkingMemory


def _cfg(**overrides) -> ContextPackConfig:
    base = ContextPackConfig()
    return base.model_copy(update=overrides)


def _turn(i: int, role: str, content: str) -> TranscriptTurn:
    return TranscriptTurn(id=f"t{i}", role=role, content=content, at=f"2026-07-22T00:00:{i:02d}Z")


def test_trim_and_follow_up_signal():
    long = "x" * 900
    trimmed = trim_turn_content(long, 600)
    assert len(trimmed) <= 610
    assert "..." in trimmed
    assert has_follow_up_signal("làm tương tự với mã 30323 cho tôi")
    assert not has_follow_up_signal("doanh thu tháng 7")


def test_sliding_window_drops_satisfaction():
    turns = [
        _turn(1, "user", "Phân tích quà tặng mã 0030344 từ 1/7 đến 6/7"),
        _turn(2, "assistant", "Đã xong."),
        _turn(3, "user", "kết quả tốt lắm"),
        _turn(4, "assistant", "Cảm ơn bạn!"),
        _turn(5, "user", "làm tương tự với mã 30323"),
    ]
    selected = build_candidates(turns, "làm tương tự với mã 30323", _cfg(window_recent_turns=8))
    kinds = {t.kind for t in selected}
    assert "satisfaction" not in kinds
    assert any("0030344" in t.content_trimmed or "quà" in t.content_trimmed for t in selected)


def test_should_invoke_curator_on_follow_up():
    cfg = _cfg()
    assert should_invoke_curator(
        pct=0.1,
        current_message="làm tương tự với mã 30323",
        transcript_len=5,
        has_resolved_brief=True,
        cfg=cfg,
    )
    assert not should_invoke_curator(
        pct=0.1,
        current_message="doanh thu theo cửa hàng",
        transcript_len=3,
        has_resolved_brief=False,
        cfg=cfg,
    )


def test_hard_only_short_session():
    wf = WorkflowState(session_id="s", actor_id="a")
    turns = [
        _turn(1, "user", "doanh thu tháng này"),
        _turn(2, "assistant", "Đã nhận."),
    ]
    pack, _cands, need = build_context_pack_hard(
        transcript=turns,
        workflow=wf,
        current_message="tồn kho theo store",
        cfg=_cfg(),
        current_turn_id=None,
    )
    assert need is False
    assert pack.pack_meta.strategy == "hard_only"
    assert pack.current_message == "tồn kho theo store"


def test_pad_product_codes_and_session_merge_follow_up():
    prior = AnalysisBrief(
        intent="Phân tích quà tặng 0030344, 0030348 trong 2026-07-01..2026-07-06, bill>=600000",
        metrics=["quantity"],
        filters={"product_code": ["0030344", "0030348"], "min_bill_value": 600000},
        time_range=TimeRange(start="2026-07-01", end="2026-07-06", grain="day"),
        output_format=["excel", "table"],
        requirements=[
            BriefRequirement(
                requirement_id="filter:0",
                kind="filter",
                key="product_code",
                source="explicit",
                required=True,
                evidence_quote="0030344",
                value=["0030344", "0030348"],
            )
        ],
    )
    assert pad_product_codes_to_prior("30323", prior.filters["product_code"]) == "0030323"
    thin = AnalysisBrief(
        intent="Phân tích tương tự như trước đó cho mã 30323",
        filters={"product_code": "30323"},
        metrics=[],
        time_range=TimeRange(),
    )
    merged, override = session_merge_brief(
        brief=thin,
        dialogue_act="follow_up_same_task",
        prior_brief=prior,
        current_message="làm tương tự với mã 30323",
    )
    assert override is None
    assert merged is not None
    assert merged.filters["product_code"] == "0030323"
    assert merged.filters.get("min_bill_value") == 600000
    assert merged.time_range.start == "2026-07-01"
    assert merged.metrics == ["quantity"]
    assert "tương tự" not in (merged.intent or "").lower() or "0030344" in merged.intent or "quà" in merged.intent.lower() or "Bổ sung" in merged.intent


def test_follow_up_without_prior_asks_chitchat():
    brief = AnalysisBrief(intent="làm tương tự")
    merged, override = session_merge_brief(
        brief=brief,
        dialogue_act="follow_up_same_task",
        prior_brief=None,
    )
    assert override == "chitchat"
    assert "khoảng thời gian" in empty_follow_up_message()


def test_follow_up_signal_overrides_new_request_act():
    prior = AnalysisBrief(
        intent="gift analysis",
        metrics=["quantity"],
        filters={"product_code": ["0030344"], "min_bill_value": 600000},
        time_range=TimeRange(start="2026-07-01", end="2026-07-06", grain="day"),
    )
    thin = AnalysisBrief(intent="làm tương tự mã 30323", filters={"product_code": "30323"})
    merged, override = session_merge_brief(
        brief=thin,
        dialogue_act="new_request",
        prior_brief=prior,
        current_message="làm tương tự với mã 30323 cho tôi",
    )
    assert override is None
    assert merged is not None
    assert merged.filters["product_code"] == "0030323"
    assert merged.filters["min_bill_value"] == 600000
    assert merged.time_range is not None
    assert merged.time_range.start == "2026-07-01"


def test_topic_switch_does_not_fill_prior():
    prior = AnalysisBrief(
        intent="gift",
        filters={"product_code": ["0030344"]},
        time_range=TimeRange(start="2026-07-01", end="2026-07-06"),
        metrics=["quantity"],
    )
    brief = AnalysisBrief(intent="Phân tích tồn kho tuần này", metrics=["inventory"], filters={})
    merged, _ = session_merge_brief(
        brief=brief,
        dialogue_act="topic_switch",
        prior_brief=prior,
    )
    assert merged is not None
    assert merged.filters == {}
    assert merged.metrics == ["inventory"]


def test_curator_selection_and_archive_bounds():
    cands = [
        SelectedTurn(id="a", role="user", content_trimmed="x", kind="analysis"),
        SelectedTurn(id="b", role="user", content_trimmed="y", kind="satisfaction"),
        SelectedTurn(id="c", role="assistant", content_trimmed="z", kind="assistant"),
    ]
    picked = apply_curator_selection(cands, ["a", "c"], ["b"])
    assert [p.id for p in picked] == ["a", "c"]


def test_long_transcript_noise_pack_bounded():
    wf = WorkflowState(session_id="s", actor_id="a")
    turns: list[TranscriptTurn] = []
    for i in range(40):
        if i % 5 == 0:
            turns.append(_turn(i, "user", f"cảm ơn lần {i}"))
        else:
            turns.append(_turn(i, "user", f"phân tích mã 0030344 ngày {i}"))
            turns.append(_turn(100 + i, "assistant", "ok"))
    pack, cands, need = build_context_pack_hard(
        transcript=turns,
        workflow=wf,
        current_message="làm tương tự với mã 30323",
        cfg=_cfg(window_recent_turns=16, recall_max_turns=8),
    )
    assert need is True  # follow-up without prior still may need by length>=24
    assert pack.pack_meta.pct <= 1.5  # assembled under/near budget after floor
    assert all(t.kind != "satisfaction" for t in cands)
