from __future__ import annotations

from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief


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
                "trong schema_context; không đặt alias CTE trùng tên bảng ảo."
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
                "dùng tên bảng trần theo data_dictionary."
            )
        elif "join_depth" in v:
            hints.append("Giảm số JOIN hoặc tách query.")
    return hints


def product_resolution_hints(brief: AnalysisBrief) -> list[dict[str, Any]] | None:
    """Flag user-entered product identifiers for Agent II — never inject SQL.

    Agent must invent probes/filters from brief + dictionary + samples + text-filter rule.
    """
    filters = brief.filters or {}
    raw = filters.get("product_code") or filters.get("sku")
    if not raw:
        return None
    codes = raw if isinstance(raw, list) else [raw]
    out = [{"user_input": str(code)} for code in codes if code]
    return out or None


def db_error_feedback_hints(message: str) -> list[str]:
    """Meta T-SQL recovery hints from SQL Server/ODBC errors — never domain recipes."""
    hints: list[str] = []
    m = (message or "").lower()
    if "invalid column name" in m:
        hints.append(
            "Invalid column: cột phải tồn tại trên bảng (schema_context / table_samples) "
            "và nếu dùng ngoài CTE thì phải có trong SELECT list của CTE đó "
            "(vd. ORDER BY ft.X / STRING_AGG … ORDER BY ft.X ⇒ CTE phải SELECT X)."
        )
    if "invalid object name" in m or "invalid object" in m:
        hints.append(
            "Invalid object: dùng bare name trong dictionary; db2 không _YYYYMM; "
            "db1 shard chỉ khi shard_plan.needs_db1 / shard_plan.shards."
        )
    if "syntax" in m or "incorrect syntax" in m:
        hints.append("Lỗi cú pháp T-SQL — đơn giản hóa: tách nhiều SELECT thay vì CTE lồng phức tạp.")
    if "string_agg" in m:
        hints.append(
            "STRING_AGG: cột trong WITHIN GROUP (ORDER BY …) phải có trên nguồn/CTE đang aggregate."
        )
    if not hints:
        hints.append(
            "Sửa SQL theo message engine; chỉ dùng cột/bảng trong schema_context và table_samples; "
            "ưu tiên nhiều query đơn giản hơn một CTE phức tạp."
        )
    hints.append("Không lặp lại identical rejected_sql; đọc message + rejected_sql trong inbox.db_error_feedback.")
    return hints
