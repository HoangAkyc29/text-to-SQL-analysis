from __future__ import annotations

from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief, BriefRequirement
from project_core.domain.contracts.clarification import ClarificationReply


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
        if answer.selected_option_id == "other":
            value = {"other_text": answer.other_text}
        else:
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
        evidence = answer.other_text or (selected.label if selected else "")
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
    data["requirements"] = [item.model_dump(mode="json") for item in requirements]
    return AnalysisBrief.model_validate(data)
