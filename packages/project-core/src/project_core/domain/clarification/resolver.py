from __future__ import annotations

from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationReply


def _set_nested(data: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    cur: dict[str, Any] = data
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


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
    return AnalysisBrief.model_validate(data)
