"""Deterministic topology checks vs shard_plan — sanitize false III/II claims.

Keeps Agent II from over-correcting to invented db1 shards when the brief
range is covered by db2 (date >= cutoff).
"""

from __future__ import annotations

import re
from typing import Any

from project_core.domain.sql.shard_resolver import ShardPlan

_SHARD_TABLE = re.compile(
    r"\b((?:STRANS|PMTRANS|CRDTRANS))_(\d{6})\b",
    re.IGNORECASE,
)

# Concern / issue tokens that claim wrong db routing (often inverted vs cutoff).
_FALSE_TOPOLOGY_TOKENS = (
    "wrong_db_for_date_range",
    "db1_shard_missing",
    "outside db2",
    "outside of db2",
    "historical dates before cutoff",
    "before cutoff",
    "dates outside db2",
    "db2 only contains",
    "use db1",
    "needs db1 shard",
    "missing db1",
)

_SOFT_DATA_FEEDBACK_ISSUES = frozenset(
    {
        "grain",
        "coverage",
        "partial_coverage",
        "formatting",
        "presentation",
        "missing_artifacts",
        "insufficient_deliverable",
    }
)


def invented_shard_yms(sql: str) -> list[tuple[str, str]]:
    """Return (logical, yyyymm) for monthly shard names appearing in SQL."""
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for m in _SHARD_TABLE.finditer(sql or ""):
        logical = m.group(1).upper()
        ym = m.group(2)
        key = f"{logical}_{ym}"
        if key in seen:
            continue
        seen.add(key)
        out.append((logical, ym))
    return out


def topology_sql_violations(
    sql: str,
    *,
    shard_plan: ShardPlan | dict[str, Any] | None,
    target_db: str | None = None,
) -> list[str]:
    """Machine violations for SQL that invents shards past archive_newest_ym."""
    plan = _as_plan(shard_plan)
    violations: list[str] = []
    newest = (plan.archive_newest_ym or "").strip()
    tdb = (target_db or "").lower().strip()

    for logical, ym in invented_shard_yms(sql):
        if tdb == "db2":
            violations.append(f"db2_monthly_shard_forbidden:{logical}_{ym}")
        if newest and ym > newest:
            violations.append(f"invented_shard_past_archive:{logical}_{ym}>max:{newest}")
        if plan.needs_db2 and not plan.needs_db1 and tdb == "db1":
            violations.append(f"db1_shard_when_only_db2_needed:{logical}_{ym}")
    return violations


def topology_feedback_hints(violations: list[str]) -> list[str]:
    hints: list[str] = []
    for v in violations:
        if v.startswith("invented_shard_past_archive:"):
            hints.append(
                "Không invent STRANS_YYYYMM / PMTRANS_YYYYMM vượt archive_newest_ym — "
                "dùng đúng shard_plan.shards hoặc bare name trên db2 khi needs_db2."
            )
        elif v.startswith("db2_monthly_shard_forbidden:"):
            hints.append("db2 chỉ dùng bare logical fact/header names — không gắn _YYYYMM.")
        elif v.startswith("db1_shard_when_only_db2_needed:"):
            hints.append(
                "shard_plan chỉ cần db2 (date >= cutoff): giữ bare fact tables trên db2, "
                "đừng chuyển sang db1 shard."
            )
    # dedupe preserve order
    out: list[str] = []
    for h in hints:
        if h not in out:
            out.append(h)
    return out


def is_false_topology_claim(
    text: str,
    *,
    shard_plan: ShardPlan | dict[str, Any] | None,
    allowed_tables: list[str] | None = None,
) -> bool:
    """True when a concern/issue wrongly claims db2 range needs db1 / missing allowlist."""
    plan = _as_plan(shard_plan)
    raw = text or ""
    lowered = raw.lower()
    if not lowered:
        return False

    # Concern text says "not in allowed_tables" while that table is in the allowlist payload.
    if allowed_tables and ("not in allowed" in lowered or "table_not_allowed" in lowered):
        bare = {a.split(":")[-1].upper() for a in allowed_tables if str(a).strip()}
        for name in bare:
            if re.search(rf"\b{re.escape(name)}\b", raw, flags=re.IGNORECASE):
                return True

    # Only treat routing claims as false when plan says db2-only for this brief.
    if not (plan.needs_db2 and not plan.needs_db1):
        return False
    return any(tok in lowered for tok in _FALSE_TOPOLOGY_TOKENS)


def sanitize_risk_rejection(
    record: dict[str, Any],
    *,
    shard_plan: ShardPlan | dict[str, Any] | None,
    allowed_tables: list[str] | None = None,
) -> dict[str, Any]:
    """Drop false topology concerns; reinforce shard_plan in suggestion when needed."""
    plan = _as_plan(shard_plan)
    out = dict(record)
    concerns = [str(c) for c in (out.get("concerns") or []) if str(c).strip()]
    kept: list[str] = []
    dropped = 0
    for c in concerns:
        if is_false_topology_claim(c, shard_plan=plan, allowed_tables=allowed_tables):
            dropped += 1
            continue
        kept.append(c)
    out["concerns"] = kept

    issue = str(out.get("issue") or "")
    if is_false_topology_claim(issue, shard_plan=plan, allowed_tables=allowed_tables):
        out["issue"] = kept[0] if kept else "semantic_risk"
        dropped += 1

    suggestion = str(out.get("suggestion") or "")
    if suggestion and is_false_topology_claim(suggestion, shard_plan=plan, allowed_tables=allowed_tables):
        out.pop("suggestion", None)
        dropped += 1

    if dropped and plan.needs_db2 and not plan.needs_db1:
        reinforce = (
            f"Giữ topology theo shard_plan: needs_db2=true, needs_db1=false, "
            f"cutoff={plan.cutoff}. Dùng bare fact/header names trên db2 — "
            f"không chuyển db1 hay invent _YYYYMM."
        )
        prev = str(out.get("suggestion") or "").strip()
        out["suggestion"] = f"{prev} {reinforce}".strip() if prev else reinforce
        out["topology_claims_dropped"] = dropped
    return out


def is_vacuous_topology_reject(
    record: dict[str, Any],
    *,
    shard_plan: ShardPlan | dict[str, Any] | None,
) -> bool:
    """True when reject had only false topology claims (now empty of real concerns)."""
    plan = _as_plan(shard_plan)
    if not (plan.needs_db2 and not plan.needs_db1):
        return False
    concerns = record.get("concerns") or []
    if concerns:
        return False
    # Vacuous if we dropped topology and nothing semantic remains.
    return int(record.get("topology_claims_dropped") or 0) > 0


def is_soft_data_feedback_issue(issue: str | None) -> bool:
    return (issue or "").strip().lower() in _SOFT_DATA_FEEDBACK_ISSUES


def _as_plan(shard_plan: ShardPlan | dict[str, Any] | None) -> ShardPlan:
    if shard_plan is None:
        return ShardPlan()
    if isinstance(shard_plan, ShardPlan):
        return shard_plan
    try:
        return ShardPlan.model_validate(shard_plan)
    except Exception:
        return ShardPlan(
            needs_db1=bool(shard_plan.get("needs_db1")),
            needs_db2=bool(shard_plan.get("needs_db2")),
            shards=list(shard_plan.get("shards") or []),
            archive_newest_ym=shard_plan.get("archive_newest_ym"),
            cutoff=shard_plan.get("cutoff"),
        )

