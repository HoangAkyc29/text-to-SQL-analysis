from __future__ import annotations

import json
import re
from typing import Any, Literal
from uuid import uuid4

from project_core.config.loader import ContextPackConfig
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.workflow import WorkflowState
from project_core.domain.memory.session_bundle import TranscriptTurn
from project_core.domain.memory.working_memory import (
    STICKY_RULES_DEFAULT,
    CompactArchiveEntry,
    ContextPack,
    ContextPackMeta,
    SelectedTurn,
    WorkingMemory,
)
from project_core.domain.time import utc_now

TurnKind = Literal["analysis", "clarify", "satisfaction", "chitchat", "error", "assistant", "user"]

_FOLLOW_UP_RE = re.compile(
    r"(tương\s*tự|như\s*trên|như\s*trước|làm\s*lại|tính\s*lại|thêm\s*điều\s*kiện|"
    r"bỏ\s*mã|đổi\s*sang|giữ\s*nguyên|same\s*as|retry)",
    re.I,
)
_SATISFACTION_RE = re.compile(
    r"^(cảm\s*ơn|thanks|thank\s*you|tốt\s*lắm|ok|được\s*rồi|chuẩn|hay\s*quá)[\s!.]*$",
    re.I,
)
_CHITCHAT_RE = re.compile(r"^(xin\s*chào|hello|hi|chào)[\s!.]*$", re.I)
_RECALL_HINTS = (
    "excel",
    "bỏ",
    "tương tự",
    "mã",
    "bill",
    "sku",
    "ngày",
    "quà",
    "top",
    "600",
)


def estimate_tokens(text: str) -> int:
    return max(1, len(text or "") // 4)


def unwrap_turn_content(content: str) -> str:
    raw = (content or "").strip()
    if raw.startswith("{"):
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict) and payload.get("text"):
                return str(payload["text"])
        except json.JSONDecodeError:
            pass
    return raw


def trim_turn_content(content: str, max_chars: int = 600) -> str:
    text = unwrap_turn_content(content)
    text = re.sub(r"https?://\S+", "[artifact:url]", text)
    text = re.sub(r"/artifacts/\S+", "[artifact:path]", text)
    if len(text) <= max_chars:
        return text
    head = max(1, int(max_chars * 0.67))
    tail = max(1, max_chars - head - 5)
    return f"{text[:head]} ... {text[-tail:]}"


def classify_turn(role: str, content: str) -> TurnKind:
    text = unwrap_turn_content(content).strip()
    lowered = text.lower()
    if role == "assistant":
        if "chưa thể hoàn tất" in lowered or "không tìm thấy" in lowered:
            return "error"
        return "assistant"
    if _SATISFACTION_RE.match(text) or detect_thanks(lowered):
        return "satisfaction"
    if _CHITCHAT_RE.match(text):
        return "chitchat"
    if "clarify" in lowered or "bạn muốn" in lowered:
        return "clarify"
    return "analysis" if role == "user" else "assistant"


def detect_thanks(lowered: str) -> bool:
    return any(tok in lowered for tok in ("cảm ơn", "tốt lắm", "thanks", "chuẩn"))


def has_follow_up_signal(message: str) -> bool:
    return bool(_FOLLOW_UP_RE.search(message or ""))


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z0-9à-ỹÀ-Ỹ_]{2,}", (text or "").lower()) if t}


def _keyword_score(message: str, turn_text: str) -> float:
    msg_tokens = _tokenize(message)
    turn_tokens = _tokenize(turn_text)
    if not msg_tokens or not turn_tokens:
        return 0.0
    overlap = len(msg_tokens & turn_tokens)
    hint_bonus = sum(1 for h in _RECALL_HINTS if h in turn_text.lower() and h in message.lower())
    # digit codes (SKU-like)
    msg_nums = set(re.findall(r"\d{4,}", message))
    turn_nums = set(re.findall(r"\d{4,}", turn_text))
    num_bonus = len(msg_nums & turn_nums) * 2
    return float(overlap + hint_bonus + num_bonus)


def maybe_truncate_transcript(
    turns: list[TranscriptTurn],
    workflow: WorkflowState,
    cfg: ContextPackConfig,
) -> list[TranscriptTurn]:
    """Soft L0 cap: archive head into L3 then truncate."""
    max_turns = cfg.transcript_max_turns
    if len(turns) <= max_turns:
        return turns
    drop_n = len(turns) - max_turns
    dropped = turns[:drop_n]
    summary = f"archived {drop_n} turns before {utc_now().isoformat()}"
    entry = CompactArchiveEntry(
        at=utc_now().isoformat(),
        reason="l0_truncate",
        summary=summary[:1600],
        source_turn_ids=[t.id for t in dropped[:50]],
        observations=[],
    )
    archive = list(workflow.compact_archive or [])
    archive.append(entry)
    workflow.compact_archive = archive[-cfg.compact_archive_max :]
    return turns[drop_n:]


def build_candidates(
    turns: list[TranscriptTurn],
    current_message: str,
    cfg: ContextPackConfig,
    *,
    exclude_current_id: str | None = None,
) -> list[SelectedTurn]:
    ordered = list(turns)
    if exclude_current_id:
        ordered = [t for t in ordered if t.id != exclude_current_id]
    recent = ordered[-cfg.window_recent_turns :]
    older = ordered[: max(0, len(ordered) - cfg.window_recent_turns)]
    scored: list[tuple[float, TranscriptTurn]] = []
    for turn in older:
        if turn.role != "user":
            continue
        text = unwrap_turn_content(turn.content)
        score = _keyword_score(current_message, text)
        if score > 0:
            scored.append((score, turn))
    scored.sort(key=lambda item: item[0], reverse=True)
    recall = [t for _, t in scored[: cfg.recall_max_turns]]
    by_id: dict[str, TranscriptTurn] = {t.id: t for t in recent}
    for t in recall:
        by_id[t.id] = t
    merged = sorted(by_id.values(), key=lambda t: t.at)
    selected: list[SelectedTurn] = []
    for turn in merged:
        kind = classify_turn(turn.role, turn.content)
        if kind in {"satisfaction", "chitchat"}:
            continue
        why = "recency" if turn in recent else "keyword_recall"
        selected.append(
            SelectedTurn(
                id=turn.id,
                role=turn.role,
                content_trimmed=trim_turn_content(turn.content, cfg.turn_trim_chars),
                why_selected=why,
                kind=kind,
            )
        )
    return selected


def estimate_pack_tokens(
    *,
    working_memory: WorkingMemory,
    last_resolved_brief: AnalysisBrief | None,
    selected_turns: list[SelectedTurn],
    current_message: str,
    compact_notes: list[CompactArchiveEntry] | None = None,
) -> int:
    parts = [
        json.dumps(working_memory.model_dump(mode="json"), ensure_ascii=False),
        json.dumps(
            last_resolved_brief.model_dump(mode="json") if last_resolved_brief else {},
            ensure_ascii=False,
        ),
        json.dumps([t.model_dump(mode="json") for t in selected_turns], ensure_ascii=False),
        current_message or "",
        json.dumps(
            [n.model_dump(mode="json") for n in (compact_notes or [])],
            ensure_ascii=False,
        ),
    ]
    return sum(estimate_tokens(p) for p in parts)


def noise_ratio_est(turns: list[SelectedTurn]) -> float:
    if not turns:
        return 0.0
    noisy = sum(1 for t in turns if t.kind in {"satisfaction", "chitchat", "error"})
    return noisy / max(1, len(turns))


def should_invoke_curator(
    *,
    pct: float,
    current_message: str,
    transcript_len: int,
    has_resolved_brief: bool,
    cfg: ContextPackConfig,
) -> bool:
    if pct >= cfg.soft_pct:
        return True
    if transcript_len >= 24:
        return True
    if has_follow_up_signal(current_message) and has_resolved_brief:
        return True
    return False


def apply_hard_floor(
    selected: list[SelectedTurn],
    *,
    keep: int = 4,
) -> list[SelectedTurn]:
    if len(selected) <= keep:
        return selected
    # Prefer analysis/user turns then most recent
    ranked = sorted(
        selected,
        key=lambda t: (
            0 if t.kind == "analysis" else 1 if t.role == "user" else 2,
            t.id,
        ),
    )
    # Keep last `keep` by original order among top-ranked kinds
    preferred_ids = {t.id for t in ranked[:keep]}
    # Actually keep the most recent keep turns that are preferred, else tail
    recent = selected[-keep:]
    out = [t for t in selected if t.id in preferred_ids]
    if len(out) < keep:
        for t in reversed(selected):
            if t.id not in {x.id for x in out}:
                out.insert(0, t)
            if len(out) >= keep:
                break
    # Preserve chronological order
    order = {t.id: i for i, t in enumerate(selected)}
    out.sort(key=lambda t: order.get(t.id, 0))
    return out[-keep:] if len(out) > keep else out or recent


def merge_ccs_patch(
    current: WorkingMemory,
    patch: dict[str, Any] | None,
) -> WorkingMemory:
    if not patch:
        return current.capped()
    data = current.model_dump(mode="json")
    for key, value in patch.items():
        if key not in data or value is None:
            continue
        if isinstance(data[key], list) and isinstance(value, list):
            merged = list(data[key])
            for item in value:
                if item not in merged:
                    merged.append(item)
            data[key] = merged
        elif isinstance(data[key], dict) and isinstance(value, dict):
            data[key] = {**data[key], **value}
        else:
            data[key] = value
    return WorkingMemory.model_validate(data).capped()


def refresh_working_memory_from_brief(
    brief: AnalysisBrief,
    existing: WorkingMemory | None = None,
) -> WorkingMemory:
    base = existing or WorkingMemory()
    facts = list(base.key_facts)
    intent = (brief.intent or "").strip()
    if intent and intent not in facts:
        facts.insert(0, intent[:200])
    return WorkingMemory(
        current_goal=intent or base.current_goal,
        active_constraints=list(base.active_constraints)[:10],
        key_facts=facts[:20],
        decision_log=list(base.decision_log)[-15:],
        open_questions=list(base.open_questions)[:5],
        active_filters=dict(brief.filters or {}),
        active_time_range=brief.time_range.model_copy(deep=True),
        output_format=list(brief.output_format or []),
    ).capped()


def append_compact_archive(
    workflow: WorkflowState,
    entry: CompactArchiveEntry,
    *,
    max_entries: int,
) -> str:
    archive = list(workflow.compact_archive or [])
    archive.append(entry)
    workflow.compact_archive = archive[-max_entries:]
    return entry.at


def assemble_context_pack(
    *,
    current_message: str,
    workflow: WorkflowState,
    selected_turns: list[SelectedTurn],
    cfg: ContextPackConfig,
    strategy: str = "hard_only",
    curator_invoked: bool = False,
    curator_failed: bool = False,
    archive_id: str | None = None,
    pct_before: float | None = None,
    external_sources: list[dict[str, Any]] | None = None,
    dropped_turns: int = 0,
) -> ContextPack:
    wm = workflow.working_memory or WorkingMemory()
    prior = workflow.last_resolved_brief
    notes = list(workflow.compact_archive or [])[-2:]
    token_est = estimate_pack_tokens(
        working_memory=wm,
        last_resolved_brief=prior,
        selected_turns=selected_turns,
        current_message=current_message,
        compact_notes=notes,
    )
    budget = cfg.pack_token_budget
    pct = token_est / max(1, budget)
    if pct > cfg.hard_pct:
        selected_turns = apply_hard_floor(selected_turns, keep=4)
        token_est = estimate_pack_tokens(
            working_memory=wm,
            last_resolved_brief=prior,
            selected_turns=selected_turns,
            current_message=current_message,
            compact_notes=notes,
        )
        pct = token_est / max(1, budget)
        strategy = f"{strategy}+hard_floor"
    return ContextPack(
        working_memory=wm,
        last_resolved_brief=prior,
        selected_turns=selected_turns,
        compact_notes=notes,
        current_message=current_message,
        sticky_rules=list(STICKY_RULES_DEFAULT),
        external_sources=list(external_sources or []),
        pack_meta=ContextPackMeta(
            token_est=token_est,
            budget=budget,
            pct=round(pct, 4),
            dropped_turns=dropped_turns,
            noise_ratio_est=round(noise_ratio_est(selected_turns), 4),
            strategy=strategy,
            curator_invoked=curator_invoked,
            curator_failed=curator_failed,
            archive_id=archive_id,
            pct_before=pct_before,
            pct_after=round(pct, 4),
            as_of_date=utc_now().date().isoformat(),
        ),
    )


def build_context_pack_hard(
    *,
    transcript: list[TranscriptTurn],
    workflow: WorkflowState,
    current_message: str,
    cfg: ContextPackConfig,
    current_turn_id: str | None = None,
    external_sources: list[dict[str, Any]] | None = None,
) -> tuple[ContextPack, list[SelectedTurn], bool]:
    """Hard path: L1 candidates + assemble. Returns (pack, candidates, need_curator).

    May truncate `transcript` in-place when over transcript_max_turns.
    """
    trimmed_l0 = maybe_truncate_transcript(list(transcript), workflow, cfg)
    if len(trimmed_l0) != len(transcript):
        transcript[:] = trimmed_l0
    candidates = build_candidates(
        trimmed_l0,
        current_message,
        cfg,
        exclude_current_id=current_turn_id,
    )
    # Emergency shrink candidates before curator if huge
    token_est = estimate_pack_tokens(
        working_memory=workflow.working_memory or WorkingMemory(),
        last_resolved_brief=workflow.last_resolved_brief,
        selected_turns=candidates,
        current_message=current_message,
    )
    pct = token_est / max(1, cfg.pack_token_budget)
    if pct >= cfg.emergency_pct:
        candidates = apply_hard_floor(candidates, keep=4)
        token_est = estimate_pack_tokens(
            working_memory=workflow.working_memory or WorkingMemory(),
            last_resolved_brief=workflow.last_resolved_brief,
            selected_turns=candidates,
            current_message=current_message,
        )
        pct = token_est / max(1, cfg.pack_token_budget)

    need = should_invoke_curator(
        pct=pct,
        current_message=current_message,
        transcript_len=len(trimmed_l0),
        has_resolved_brief=workflow.last_resolved_brief is not None,
        cfg=cfg,
    )
    dropped = max(0, len(trimmed_l0) - len(candidates) - (1 if current_turn_id else 0))
    pack = assemble_context_pack(
        current_message=current_message,
        workflow=workflow,
        selected_turns=candidates,
        cfg=cfg,
        strategy="hard_only",
        pct_before=round(pct, 4),
        external_sources=external_sources,
        dropped_turns=dropped,
    )
    return pack, candidates, need


def apply_curator_selection(
    candidates: list[SelectedTurn],
    selected_ids: list[str] | None,
    drop_ids: list[str] | None = None,
) -> list[SelectedTurn]:
    drop = set(drop_ids or [])
    if not selected_ids:
        return [c for c in candidates if c.id not in drop]
    wanted = set(selected_ids)
    picked = [c for c in candidates if c.id in wanted and c.id not in drop]
    return picked or [c for c in candidates if c.id not in drop]


def new_archive_id() -> str:
    return str(uuid4())
