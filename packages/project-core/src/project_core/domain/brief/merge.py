from __future__ import annotations

from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.feedback import DataFeedback


def apply_data_feedback(brief: AnalysisBrief, feedback: DataFeedback | dict[str, Any]) -> AnalysisBrief:
    """Merge IV data_feedback into brief for the next II attempt."""
    if isinstance(feedback, dict):
        feedback = DataFeedback.model_validate(feedback)
    data = brief.model_dump()
    if feedback.suggested_intent_fix and not data.get("intent"):
        data["intent"] = feedback.suggested_intent_fix
    elif feedback.suggested_intent_fix:
        data["intent"] = f"{data['intent']} | {feedback.suggested_intent_fix}"

    if feedback.issue in {"identifier_mismatch", "empty_result", "grain"}:
        data.setdefault("probe_hints", [])
        for hint in feedback.evidence_refs:
            if hint not in data["probe_hints"]:
                data["probe_hints"].append(hint)

    if feedback.diagnosis == "needs_probe":
        data["exploration_mode"] = True

    for probe in feedback.probe_requests:
        hint = f"probe:{probe.table}:{probe.purpose}"
        data.setdefault("probe_hints", [])
        if hint not in data["probe_hints"]:
            data["probe_hints"].append(hint)

    filters = dict(data.get("filters") or {})
    for obs in feedback.expected_vs_observed:
        if obs.aspect == "product_code" and "observed" in obs.observed.lower():
            filters["_iv_product_hint"] = obs.observed
    data["filters"] = filters
    return AnalysisBrief.model_validate(data)
