from __future__ import annotations

import re
from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief, BriefRequirement
from project_core.domain.contracts.clarification import ClarificationReply

# Prefer explicit STK_ID=…; else 4–6 digit tokens (typical STK_ID width).
_STK_ID_EXPLICIT = re.compile(r"STK[_\s-]?ID\s*[=:]?\s*['\"]?(\d{4,6})", re.IGNORECASE)
_STK_ID_LOOSE = re.compile(r"\b(\d{4,6})\b")
_KNOWN_OPTION_SENTINELS = frozenset({"other", "unknown", "cancel", "rephrase", "confirm"})


def _set_nested(data: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    cur: dict[str, Any] = data
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


def _get_nested(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def extract_store_ids(text: str) -> list[str]:
    """Pull STK / store id tokens from free-text clarification answers."""
    prose = str(text or "").strip()
    if not prose:
        return []
    # Merge explicit STK_ID=… with nearby numeric tokens so
    # "STK_ID 10001, 10004, 10005" yields all three ids.
    found = _STK_ID_EXPLICIT.findall(prose) + _STK_ID_LOOSE.findall(prose)
    return list(dict.fromkeys(found))


def _free_text_prose(answer) -> str:
    """Normalize free-text: UI may send prose as selected_option_id instead of other."""
    selected = str(getattr(answer, "selected_option_id", "") or "").strip()
    other = str(getattr(answer, "other_text", None) or "").strip()
    if other:
        return other
    if selected and selected not in _KNOWN_OPTION_SENTINELS:
        return selected
    return ""


def _is_free_text_answer(answer, option_map: dict, question_id: str) -> bool:
    selected = str(getattr(answer, "selected_option_id", "") or "").strip()
    if selected == "other":
        return True
    if selected in _KNOWN_OPTION_SENTINELS:
        return False
    return (question_id, selected) not in option_map


def _value_for_field(field: str, prose: str) -> Any:
    if field.endswith("store_ids") or field == "filters.store_ids":
        ids = extract_store_ids(prose)
        return ids if ids else ([prose] if prose else [])
    if field.endswith("clarify_note"):
        return prose
    return prose


def apply_clarification_reply(brief: AnalysisBrief, reply: ClarificationReply, request) -> AnalysisBrief:
    data = brief.model_dump()
    option_map = {
        (q.id, opt.id): opt.brief_value
        for q in request.questions
        for opt in q.options
    }
    for answer in reply.answers:
        field = next((q.maps_to_brief_field for q in request.questions if q.id == answer.question_id), None)
        if not field:
            continue
        if _is_free_text_answer(answer, option_map, answer.question_id):
            prose = _free_text_prose(answer)
            value = _value_for_field(field, prose)
            _set_nested(data, field, value)
            # Store clarifies often map to clarify_note historically — still lift STK ids.
            if prose and not field.endswith("store_ids"):
                store_ids = extract_store_ids(prose)
                if store_ids:
                    _set_nested(data, "filters.store_ids", store_ids)
            continue
        value = option_map.get((answer.question_id, answer.selected_option_id)) or {}
        leaf = field.split(".")[-1]
        if isinstance(value, dict) and leaf in value:
            _set_nested(data, field, value[leaf])
        elif isinstance(value, dict) and "." not in field:
            for k, v in value.items():
                _set_nested(data, f"{field}.{k}" if field else k, v)
        else:
            _set_nested(data, field, value)
    for answer in reply.answers:
        if answer.selected_option_id == "unknown":
            data["exploration_mode"] = True
            data["user_knowledge_level"] = "unknown"
    requirements = [
        BriefRequirement.model_validate(item)
        for item in (data.get("requirements") or [])
    ]
    kind_by_root = {
        "metrics": "metric",
        "dimensions": "dimension",
        "filters": "filter",
        "time_range": "time",
        "output_format": "output",
    }
    for answer in reply.answers:
        question = next(
            (item for item in request.questions if item.id == answer.question_id),
            None,
        )
        if question is None or not question.maps_to_brief_field:
            continue
        field = question.maps_to_brief_field
        root = field.split(".")[0]
        kind = kind_by_root.get(root)
        if kind is None:
            continue
        key = "time_range" if kind == "time" else field.split(".")[-1]
        selected = next(
            (item for item in question.options if item.id == answer.selected_option_id),
            None,
        )
        evidence = _free_text_prose(answer) or (selected.label if selected else "")
        value = _get_nested(data, field)
        requirement = BriefRequirement(
            requirement_id=f"clarification:{field}",
            kind=kind,
            key=key,
            source="explicit",
            required=True,
            evidence_quote=evidence,
            value=value,
        )
        requirements = [
            item
            for item in requirements
            if not (item.kind == requirement.kind and item.key == requirement.key)
        ]
        requirements.append(requirement)
        # If we also set store_ids as a side-effect, record that requirement.
        if extract_store_ids(evidence) and not field.endswith("store_ids"):
            store_req = BriefRequirement(
                requirement_id="clarification:filters.store_ids",
                kind="filter",
                key="store_ids",
                source="explicit",
                required=True,
                evidence_quote=evidence,
                value=_get_nested(data, "filters.store_ids"),
            )
            requirements = [
                item
                for item in requirements
                if not (item.kind == store_req.kind and item.key == store_req.key)
            ]
            requirements.append(store_req)
    data["requirements"] = [item.model_dump(mode="json") for item in requirements]
    return AnalysisBrief.model_validate(data)
