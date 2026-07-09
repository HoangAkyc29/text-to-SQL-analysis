from __future__ import annotations

from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.product.resolver import resolve_product_code


def policy_feedback_hints(violations: list[str]) -> list[str]:
    """Human-readable hints for Agent II retry — not SQL, only guidance."""
    hints: list[str] = []
    for v in violations:
        if v == "forbidden_pattern":
            hints.append("Bỏ dấu ';' cuối câu; chỉ một SELECT; không DML/DDL.")
        elif v.startswith("table_not_in_dictionary:"):
            bad = v.split(":", 1)[-1]
            hints.append(
                f"Bảng '{bad}' không có trong data_dictionary — dùng CTE WITH hoặc bảng thật "
                "(STRANS, TRANSHDR, SKU_DEF, …); không đặt alias CTE trùng tên bảng ảo."
            )
        elif v.startswith("table_not_allowed:"):
            hints.append("Bảng ngoài allowlist role — chọn bảng khác trong schema_context.")
        elif v == "select_only":
            hints.append(
                "Chỉ được một câu SELECT hoặc WITH … SELECT. Không dùng EXEC, không nhiều statement, "
                "không INSERT/UPDATE."
            )
        elif v == "parse_error":
            hints.append("SQL không parse được — kiểm tra cú pháp T-SQL.")
        elif v == "logical_db_prefix_forbidden":
            hints.append(
                "db1/db2 là logical pool (target_dbs) — không viết db2.dbo.TABLE trong SQL; "
                "dùng tên bảng trần STRANS, TRANSHDR, …"
            )
        elif "join_depth" in v:
            hints.append("Giảm số JOIN hoặc tách query.")
    return hints


def product_resolution_hints(brief: AnalysisBrief) -> list[dict[str, Any]] | None:
    """Expose resolver candidates to Agent II — agent must choose predicate, not pre-built plan."""
    filters = brief.filters or {}
    raw = filters.get("product_code") or filters.get("sku")
    if not raw:
        return None
    codes = raw if isinstance(raw, list) else [raw]
    out: list[dict[str, Any]] = []
    for code in codes:
        if not code:
            continue
        resolved = resolve_product_code(str(code))
        out.append(
            {
                "user_input": str(code),
                "strategies": [
                    {
                        "strategy": c.strategy,
                        "sql_predicate": c.sql_predicate,
                        "confidence": c.confidence,
                        "explanation_vi": c.explanation_vi,
                    }
                    for c in resolved.candidates
                ],
                "suggested_probe_tables": ["SKU_DEF", "BARCODE"],
                "note_vi": (
                    "Mã user có thể là SKU_CODE (LPAD 8) hoặc barcode — probe master trước, "
                    "filter STRANS bằng SKU_ID đã resolve, không filter SKU_CODE trực tiếp trên fact."
                ),
            }
        )
    return out or None
