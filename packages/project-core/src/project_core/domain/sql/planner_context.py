from __future__ import annotations

import re
from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief

_SHARD_NAME = re.compile(r"^(?:strans|pmtrans|crdtrans)_\d{6}$", re.IGNORECASE)


def re_match_shard(name: str) -> bool:
    return bool(_SHARD_NAME.match((name or "").strip()))


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
            if re_match_shard(bad):
                hints.append(
                    "Nếu đó là STRANS_YYYYMM / PMTRANS_YYYYMM: chỉ dùng khi shard_plan.needs_db1 "
                    "và YYYYMM ≤ archive_newest_ym (ưu tiên đúng list shard_plan.shards). "
                    "Khi needs_db2 và không needs_db1: bare STRANS trên db2 — không invent tháng hiện tại."
                )
        elif v.startswith("invented_shard_past_archive:") or v.startswith("db2_monthly_shard_forbidden:"):
            hints.append(
                "Không invent shard tháng vượt archive_newest_ym; db2 = bare names; "
                "đọc shard_plan.shards / table_naming."
            )
        elif v.startswith("db1_shard_when_only_db2_needed:"):
            hints.append(
                "shard_plan chỉ cần db2 (date ≥ cutoff): giữ bare fact tables trên db2."
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
