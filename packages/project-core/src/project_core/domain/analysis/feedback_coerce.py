from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from project_core.domain.contracts.feedback import DataFeedback, ExpectedVsObserved, ProbeRequest

_PURPOSE_TABLE: dict[str, str] = {
    "sku_lookup": "SKU_DEF",
    "product_lookup": "SKU_DEF",
    "barcode_lookup": "BARCODE",
    "bill_lookup": "TRANSHDR",
    "fact_lookup": "STRANS",
}


def coerce_data_feedback(raw: dict[str, Any]) -> DataFeedback:
    """Best-effort normalize LLM IV feedback before Pydantic validation."""
    data = dict(raw)
    if "issue" not in data:
        data["issue"] = "empty_result"
    if "summary" not in data:
        data["summary"] = str(data.get("suggested_intent_fix") or "IV data feedback")

    diagnosis = data.get("diagnosis")
    if diagnosis not in {"solvable", "needs_probe", "impossible", "needs_user_clarify"}:
        data["diagnosis"] = "solvable"

    evo = data.get("expected_vs_observed")
    if isinstance(evo, dict):
        data["expected_vs_observed"] = [
            ExpectedVsObserved(
                aspect=str(evo.get("aspect") or "data"),
                expected=str(evo.get("expected") or ""),
                observed=str(evo.get("observed") or ""),
                source=str(evo.get("source") or ""),
            ).model_dump()
        ]
    elif evo is None:
        data["expected_vs_observed"] = []

    probes = data.get("probe_requests") or []
    fixed_probes: list[dict[str, Any]] = []
    for p in probes:
        if not isinstance(p, dict):
            continue
        pr = dict(p)
        if not pr.get("table"):
            purpose = str(pr.get("purpose") or "")
            pr["table"] = _PURPOSE_TABLE.get(purpose, "SKU_DEF")
        if not pr.get("purpose"):
            pr["purpose"] = "lookup"
        if not pr.get("suggested_sql"):
            pr["suggested_sql"] = f"SELECT TOP 100 * FROM {pr['table']}"
        fixed_probes.append(pr)
    data["probe_requests"] = fixed_probes

    try:
        return DataFeedback.model_validate(data)
    except ValidationError:
        return DataFeedback(
            needs_sql_retry=bool(data.get("needs_sql_retry", True)),
            issue=str(data.get("issue") or "empty_result"),
            summary=str(data.get("summary") or "IV feedback coerced"),
            diagnosis=data.get("diagnosis", "solvable"),
            suggested_intent_fix=str(data.get("suggested_intent_fix") or ""),
        )


def try_validate_data_feedback(raw: dict[str, Any]) -> tuple[DataFeedback | None, str | None]:
    """Validate or coerce; return (feedback, error_message)."""
    if not raw:
        return None, "empty payload"
    try:
        return DataFeedback.model_validate(raw), None
    except ValidationError as exc:
        try:
            return coerce_data_feedback(raw), str(exc.errors()[0].get("msg", exc))
        except Exception as inner:  # noqa: BLE001
            return None, str(inner)
