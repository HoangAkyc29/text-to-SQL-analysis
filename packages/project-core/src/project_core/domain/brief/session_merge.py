from __future__ import annotations

import re
from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief, BriefRequirement
from project_core.domain.memory.context_pack import has_follow_up_signal
from project_core.domain.memory.working_memory import WorkingMemory

_ANAPHORA_RE = re.compile(
    r"(tương\s*tự(\s+như\s+(phân\s*tích\s+)?trước(\s+đó)?)?|như\s*trên|như\s*trước|"
    r"làm\s*lại\s*như|trước\s*đó|same\s+as\s+before)",
    re.I,
)

_FOLLOW_UP_ACTS = frozenset(
    {
        "follow_up_same_task",
        "revise_and_rerun",
        "correction_only",
    }
)


def _pad_code_to_width(code: str, width: int) -> str:
    raw = str(code).strip()
    if not raw.isdigit() or width <= 0 or len(raw) >= width:
        return raw
    return raw.zfill(width)


def _prior_code_width(prior_codes: list[str]) -> int | None:
    widths = [len(c) for c in prior_codes if str(c).isdigit()]
    if not widths:
        return None
    # Prefer common padded width (e.g. 7 for 0030344)
    from collections import Counter

    most, _ = Counter(widths).most_common(1)[0]
    return most if most >= 4 else None


def pad_product_codes_to_prior(
    codes: Any,
    prior_codes: Any,
) -> Any:
    prior_list = prior_codes if isinstance(prior_codes, list) else ([prior_codes] if prior_codes else [])
    prior_list = [str(c) for c in prior_list if c is not None]
    width = _prior_code_width(prior_list)
    if width is None:
        return codes
    if isinstance(codes, list):
        return [_pad_code_to_width(str(c), width) for c in codes]
    if codes is None:
        return codes
    return _pad_code_to_width(str(codes), width)


def rewrite_anaphora_intent(intent: str, prior: AnalysisBrief | None) -> str:
    text = (intent or "").strip()
    if not text or not _ANAPHORA_RE.search(text):
        return text
    if prior is None:
        return _ANAPHORA_RE.sub("", text).strip() or text
    base = (prior.intent or "").strip()
    # Keep any non-anaphora remnant (e.g. new SKU mention) appended
    remnant = _ANAPHORA_RE.sub(" ", text)
    remnant = re.sub(r"\s+", " ", remnant).strip(" ,.;")
    if remnant and remnant.lower() not in base.lower():
        return f"{base}. Bổ sung/thay đổi: {remnant}"
    return base or text


def _merge_requirements(
    prior: AnalysisBrief,
    current: AnalysisBrief,
) -> list[BriefRequirement]:
    by_key: dict[tuple[str, str], BriefRequirement] = {}
    for item in prior.requirements or []:
        carried = item.model_copy(
            update={
                "source": "carried",
                "evidence_quote": item.evidence_quote or "(carried from prior brief)",
            }
        )
        by_key[(item.kind, item.key)] = carried
    for item in current.requirements or []:
        if item.source == "carried":
            by_key[(item.kind, item.key)] = item
            continue
        by_key[(item.kind, item.key)] = item
    return list(by_key.values())


def _fill_from_prior(brief: AnalysisBrief, prior: AnalysisBrief) -> AnalysisBrief:
    data = brief.model_dump(mode="json")
    prior_data = prior.model_dump(mode="json")
    if not data.get("metrics"):
        data["metrics"] = list(prior_data.get("metrics") or [])
    if not data.get("dimensions"):
        data["dimensions"] = list(prior_data.get("dimensions") or [])
    if not data.get("output_format"):
        data["output_format"] = list(prior_data.get("output_format") or ["table"])
    filters = dict(data.get("filters") or {})
    prior_filters = dict(prior_data.get("filters") or {})
    for key, value in prior_filters.items():
        if key not in filters or filters[key] in (None, "", [], {}):
            filters[key] = value
    # Pad product codes using prior width when current has shorter digit codes
    if "product_code" in filters or "product_code" in prior_filters:
        filters["product_code"] = pad_product_codes_to_prior(
            filters.get("product_code", prior_filters.get("product_code")),
            prior_filters.get("product_code"),
        )
    data["filters"] = filters
    tr = data.get("time_range") or {}
    ptr = prior_data.get("time_range") or {}
    if not tr.get("start") and not tr.get("end"):
        data["time_range"] = dict(ptr)
    data["intent"] = rewrite_anaphora_intent(str(data.get("intent") or ""), prior)
    merged = AnalysisBrief.model_validate(data)
    if not merged.requirements and prior.requirements:
        merged.requirements = _merge_requirements(prior, merged)
    elif prior.requirements:
        merged.requirements = _merge_requirements(prior, merged)
    return merged


def session_merge_brief(
    *,
    brief: AnalysisBrief | None,
    dialogue_act: str | None,
    prior_brief: AnalysisBrief | None,
    working_memory: WorkingMemory | None = None,
    current_message: str = "",
) -> tuple[AnalysisBrief | None, str | None]:
    """Deterministic guardrail after Agent I ingress.

    Returns (brief, route_override) where route_override may be 'chitchat' if follow-up
    lacks prior context.
    """
    act = dialogue_act or "new_request"
    if (
        act == "new_request"
        and prior_brief is not None
        and has_follow_up_signal(current_message)
    ):
        act = "follow_up_same_task"

    if brief is None:
        return None, None

    if act == "topic_switch":
        # Do not fill from prior; still strip anaphora if any
        cleaned = brief.model_copy(
            update={"intent": rewrite_anaphora_intent(brief.intent, None)}
        )
        return cleaned, None

    if act in _FOLLOW_UP_ACTS:
        if prior_brief is None:
            # Cannot safely invent carried constraints
            return brief, "chitchat"
        merged = _fill_from_prior(brief, prior_brief)
        return merged, None

    # Heuristic: anaphora in intent + prior exists → treat as follow-up fill
    if prior_brief is not None and (
        _ANAPHORA_RE.search(brief.intent or "")
        or _ANAPHORA_RE.search(current_message or "")
    ):
        return _fill_from_prior(brief, prior_brief), None

    # Soft pad product codes even on new_request if WM/prior has width hint
    prior_codes = None
    if prior_brief and prior_brief.filters:
        prior_codes = prior_brief.filters.get("product_code")
    elif working_memory and working_memory.active_filters:
        prior_codes = working_memory.active_filters.get("product_code")
    if prior_codes and brief.filters.get("product_code"):
        filters = dict(brief.filters)
        filters["product_code"] = pad_product_codes_to_prior(
            filters.get("product_code"), prior_codes
        )
        brief = brief.model_copy(update={"filters": filters})

    if _ANAPHORA_RE.search(brief.intent or ""):
        brief = brief.model_copy(
            update={"intent": rewrite_anaphora_intent(brief.intent, prior_brief)}
        )
    return brief, None


def empty_follow_up_message() -> str:
    return (
        "Bạn muốn giữ khoảng thời gian và chỉ số phân tích nào từ lần trước? "
        "Hãy nêu rõ để tôi chạy lại cho đúng."
    )
