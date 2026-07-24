"""DataFetchToolkit — Flexible Parameter Patterns under PolicyEngine."""

from __future__ import annotations

import logging
from typing import Any, Protocol

import pandas as pd

from project_core.config.loader import load_project_config
from project_core.domain.analysis.ops.working_set import DatasetWorkingSet
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.data_fetch import builders
from project_core.domain.data_fetch import flexible_builders as flex
from project_core.domain.data_fetch.arg_coerce import coerce_time_range, sanitize_filter_clauses
from project_core.domain.data_fetch.catalog import (
    ALLOWED_PREVIEW_TABLES,
    DEPRECATED_FETCH_TOOL_IDS,
    FACT_TABLES,
    FETCH_TOOL_IDS,
    catalog_for_prompt,
)
from project_core.domain.sql.policy_engine import PolicyEngine
from project_core.domain.sql.shard_resolver import suggest_query_plan

logger = logging.getLogger(__name__)

_ARG_ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    "resolve_products": {"codes": ("product_codes", "sku_codes", "products", "codes")},
    "preview_table": {"table": ("table_name",)},
    "query_rows": {
        "table": ("table_name",),
        "min_amount": ("min_bill_value", "min_bill", "amount_min"),
        "sku_ids": ("sku_id", "skus", "resolved_sku_ids"),
        "trans_nums": ("trans_num", "bill_ids", "bills"),
    },
    "aggregate_rows": {
        "table": ("table_name",),
        "sku_ids": ("sku_id", "skus", "resolved_sku_ids"),
        "min_amount": ("min_bill_value", "min_bill", "amount_min"),
    },
    "lookup_distinct": {"column": ("col", "field"), "table": ("table_name",)},
}

_DATASET_ID_ARGS: dict[str, dict[str, tuple[str, ...]]] = {
    "query_rows": {
        "sku_ids": ("SKU_ID", "sku_id"),
        "trans_nums": ("TRANS_NUM", "trans_num"),
    },
    "aggregate_rows": {"sku_ids": ("SKU_ID", "sku_id")},
}
_DATASET_ID_LIMITS: dict[str, int] = {"sku_ids": 500, "trans_nums": 2000}


def _normalize_fetch_args(tool_id: str, args: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    out = dict(args)
    repairs: list[str] = []
    for canonical, aliases in _ARG_ALIASES.get(tool_id, {}).items():
        if out.get(canonical) is not None:
            continue
        for alias in aliases:
            if alias == canonical:
                continue
            if out.get(alias) is None:
                continue
            out[canonical] = out[alias]
            repairs.append(f"{alias}->{canonical}")
            break
    return out, repairs


def _unique_str_ids(values: list[Any], *, max_ids: int) -> list[str]:
    out: list[str] = []
    for raw in values:
        text = str(raw).strip()
        if not text or text in out:
            continue
        out.append(text)
        if len(out) >= max_ids:
            break
    return out


def _ids_from_dataset_frame(
    df: pd.DataFrame,
    preferred_cols: tuple[str, ...],
    *,
    max_ids: int,
    column_override: str | None = None,
) -> list[str]:
    upper_map = {str(c).upper(): c for c in df.columns}
    chosen: str | None = None
    if column_override:
        key = str(column_override).upper()
        if key not in upper_map:
            raise ValueError(f"dataset_missing_column:{column_override}")
        chosen = str(upper_map[key])
    else:
        for pref in preferred_cols:
            if pref.upper() in upper_map:
                chosen = str(upper_map[pref.upper()])
                break
    if chosen is None:
        raise ValueError(
            f"dataset_missing_id_column:need_one_of={list(preferred_cols)};have={list(df.columns)}"
        )
    ids = _unique_str_ids(df[chosen].dropna().tolist(), max_ids=max_ids)
    if not ids:
        raise ValueError(f"dataset_id_column_empty:{chosen}")
    return ids


def _resolve_dataset_id_arg(
    working_set: DatasetWorkingSet,
    value: Any,
    preferred_cols: tuple[str, ...],
    *,
    arg_name: str,
    max_ids: int,
) -> tuple[Any, str | None]:
    if value is None:
        return None, None
    if isinstance(value, dict):
        ref = (
            value.get("dataset")
            or value.get("ref")
            or value.get("from")
            or value.get("source")
            or value.get("save_as")
        )
        if ref is None:
            raise ValueError(f"invalid_{arg_name}_ref_object")
        ref_s = str(ref).strip()
        if not working_set.has(ref_s):
            raise ValueError(f"unknown_dataset_ref:{ref_s}")
        ids = _ids_from_dataset_frame(
            working_set.get(ref_s).frame(),
            preferred_cols,
            max_ids=max_ids,
            column_override=str(value["column"]) if value.get("column") else None,
        )
        return ids, f"{arg_name}:dataset_ref:{ref_s}->{len(ids)}_ids"
    if isinstance(value, str):
        ref_s = value.strip()
        if working_set.has(ref_s):
            ids = _ids_from_dataset_frame(
                working_set.get(ref_s).frame(), preferred_cols, max_ids=max_ids
            )
            return ids, f"{arg_name}:dataset_ref:{ref_s}->{len(ids)}_ids"
        # Accept "dataset.COLUMN" when dataset is in the working set.
        if "." in ref_s:
            left, right = ref_s.split(".", 1)
            left, right = left.strip(), right.strip()
            if left and right and working_set.has(left):
                ids = _ids_from_dataset_frame(
                    working_set.get(left).frame(),
                    preferred_cols,
                    max_ids=max_ids,
                    column_override=right,
                )
                return ids, f"{arg_name}:dataset_ref:{left}.{right}->{len(ids)}_ids"
        return value, None
    if isinstance(value, list) and len(value) == 1 and isinstance(value[0], str):
        ref_s = value[0].strip()
        if working_set.has(ref_s):
            ids = _ids_from_dataset_frame(
                working_set.get(ref_s).frame(), preferred_cols, max_ids=max_ids
            )
            return ids, f"{arg_name}:dataset_ref:{ref_s}->{len(ids)}_ids"
        if "." in ref_s:
            left, right = ref_s.split(".", 1)
            left, right = left.strip(), right.strip()
            if left and right and working_set.has(left):
                ids = _ids_from_dataset_frame(
                    working_set.get(left).frame(),
                    preferred_cols,
                    max_ids=max_ids,
                    column_override=right,
                )
                return ids, f"{arg_name}:dataset_ref:{left}.{right}->{len(ids)}_ids"
    return value, None


def _preferred_cols_for_filter(column: str) -> tuple[str, ...]:
    upper = column.upper()
    if upper in {"SKU_ID", "SKU_CODE"}:
        return ("SKU_ID", "sku_id", "SKU_CODE")
    if upper in {"TRANS_NUM", "BILL_NO"}:
        return ("TRANS_NUM", "trans_num")
    return (column, column.upper(), column.lower())


class _SqlGateway(Protocol):
    def execute_readonly(
        self, sql: str, acl: SqlAclContext, *, target_db: str = "db2"
    ) -> dict[str, Any]: ...


class DataFetchToolkit:
    """Bound fetch executor for one analysis (ACL + working set + budgets)."""

    def __init__(
        self,
        *,
        sql_gateway: _SqlGateway,
        policy: PolicyEngine,
        acl: SqlAclContext,
        working_set: DatasetWorkingSet,
        max_rows: int | None = None,
        max_fetch_calls: int = 24,
        max_total_rows: int = 200_000,
    ) -> None:
        self.sql_gateway = sql_gateway
        self.policy = policy
        self.acl = acl
        self.working_set = working_set
        cfg = load_project_config().policy
        self.max_rows = int(max_rows or cfg.max_rows)
        self.max_fetch_calls = max_fetch_calls
        self.max_total_rows = max_total_rows
        self.fetch_calls = 0
        self.fetch_attempts = 0
        self.fetch_errors: list[str] = []
        self.total_rows = 0
        self._resolved_products = False
        self._probed_facts: set[str] = set()

    def catalog(self) -> list[dict[str, str]]:
        return catalog_for_prompt()

    def _expand_filters(
        self, filters: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        out: list[dict[str, Any]] = []
        notes: list[str] = []
        for clause in filters:
            c = dict(clause)
            value = c.get("value")
            col = str(c.get("column") or "")
            op = str(c.get("op") or "eq").lower()
            if op in {"in", "not_in"} and value is not None:
                if isinstance(value, str) and (" " in value.strip() or " from " in value.lower()):
                    # Prose placeholder slipped through — drop clause rather than treat as SKU.
                    notes.append(f"dropped_prose_filter:{col}")
                    continue
                try:
                    resolved, note = _resolve_dataset_id_arg(
                        self.working_set,
                        value,
                        _preferred_cols_for_filter(col),
                        arg_name=col or "filter",
                        max_ids=2000,
                    )
                except ValueError:
                    resolved, note = value, None
                c["value"] = resolved
                if note:
                    notes.append(note)
            out.append(c)
        return out, notes

    def execute(
        self,
        tool_id: str,
        args: dict[str, Any] | None = None,
        *,
        save_as: str | None = None,
        brief: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tid = str(tool_id or "").strip()
        if tid in DEPRECATED_FETCH_TOOL_IDS:
            self.fetch_attempts += 1
            hint = {
                "fetch_sale_lines": "query_rows",
                "fetch_bill_headers": "query_rows",
                "fetch_lines_for_bills": "query_rows",
                "aggregate_metric": "aggregate_rows",
                "lookup_codes": "lookup_distinct",
            }.get(tid, "query_rows")
            err = f"deprecated_fetch_tool:{tid}:use_{hint}"
            self.fetch_errors.append(err)
            return {"ok": False, "error": err, "hint": f"Use {hint} with filters[] instead."}
        if tid not in FETCH_TOOL_IDS:
            self.fetch_attempts += 1
            self.fetch_errors.append(f"unknown_fetch_tool:{tid}")
            return {"ok": False, "error": f"unknown_fetch_tool:{tid}"}
        if self.fetch_calls >= self.max_fetch_calls:
            self.fetch_attempts += 1
            self.fetch_errors.append("fetch_budget_exceeded")
            return {"ok": False, "error": "fetch_budget_exceeded"}

        raw_args = dict(args or {})
        args, arg_repairs = _normalize_fetch_args(tid, raw_args)
        self.fetch_attempts += 1
        warnings: list[str] = list(arg_repairs)

        # Defense: never let prose time_range / filters reach builders.
        brief_tr = (brief or {}).get("time_range") if isinstance(brief, dict) else None
        coerced_tr = coerce_time_range(args.get("time_range"), fallback=brief_tr if isinstance(brief_tr, dict) else None)
        if args.get("time_range") is not None and not isinstance(args.get("time_range"), dict):
            warnings.append("coerced_time_range_from_brief")
        args["time_range"] = coerced_tr
        if "filters" in args:
            cleaned = sanitize_filter_clauses(args.get("filters"))
            if cleaned != (args.get("filters") or []) and isinstance(args.get("filters"), list):
                warnings.append(f"sanitized_filters:{len(args.get('filters') or [])}->{len(cleaned)}")
            args["filters"] = cleaned

        for arg_name, preferred_cols in _DATASET_ID_ARGS.get(tid, {}).items():
            if args.get(arg_name) is None:
                continue
            try:
                resolved, note = _resolve_dataset_id_arg(
                    self.working_set,
                    args.get(arg_name),
                    preferred_cols,
                    arg_name=arg_name,
                    max_ids=_DATASET_ID_LIMITS.get(arg_name, 500),
                )
            except ValueError as exc:
                err = str(exc)
                self.fetch_errors.append(f"{tid}:{err}")
                return {"ok": False, "error": err, "arg_keys": sorted(raw_args.keys()), "tool_id": tid}
            args[arg_name] = resolved
            if note:
                warnings.append(note)

        if tid in {"query_rows", "aggregate_rows", "preview_table", "lookup_distinct"}:
            table_u = str(args.get("table") or "").strip().upper()
            # TRANSHDR has no SKU_ID — never push product sugar onto headers.
            if table_u in {"TRANSHDR", "TRANSHDR_ARC"} and args.get("sku_ids") is not None:
                warnings.append("dropped_sku_ids_on_header_table")
                args.pop("sku_ids", None)
            if table_u in {"TRANSHDR", "TRANSHDR_ARC"}:
                before = list(args.get("filters") or [])
                kept: list[dict[str, Any]] = []
                for c in before:
                    if not isinstance(c, dict):
                        continue
                    col_u = str(c.get("column") or "").strip().upper()
                    if col_u in {"SKU_ID", "SKU_CODE"}:
                        continue
                    # Normalize invented bill-amount columns to AMOUNT when value is numeric.
                    if col_u in {"BILL_AMT", "BILL_AMOUNT", "BILL_VALUE", "TOTAL_AMT", "TOTAL_AMOUNT"}:
                        val = c.get("value")
                        if isinstance(val, (int, float)) or (
                            isinstance(val, str) and val.replace(".", "", 1).isdigit()
                        ):
                            kept.append({**c, "column": "AMOUNT"})
                            warnings.append(f"rewrote_amount_column:{col_u}->AMOUNT")
                        else:
                            warnings.append(f"dropped_prose_amount_filter:{col_u}")
                        continue
                    kept.append(c)
                if len(kept) != len(before):
                    warnings.append("sanitized_header_filters")
                args["filters"] = kept

            sugar_filters, sugar_notes = flex.normalize_sugar_to_filters(args)
            base_filters = [dict(c) for c in (args.get("filters") or []) if isinstance(c, dict)]
            merged = base_filters + sugar_filters
            expanded, expand_notes = self._expand_filters(merged)
            args["filters"] = expanded
            warnings.extend(sugar_notes)
            warnings.extend(expand_notes)

        if tid == "query_rows" and args.get("sku_ids") and not self._resolved_products:
            if not args.get("allow_unresolved"):
                # Soft: allow if filters already have SKU_ID; sugar path should resolve first.
                warnings.append("prefer_resolve_products_before_sku_filter")

        if tid == "aggregate_rows" and "sale_lines" not in self._probed_facts:
            warnings.append("prefer_probe_before_aggregate")

        try:
            plans = self._build_plans(tid, args, brief=brief or {})
        except ValueError as exc:
            err = str(exc)
            self.fetch_errors.append(f"{tid}:{err}")
            return {
                "ok": False,
                "error": err,
                "arg_keys": sorted(raw_args.keys()),
                "arg_repairs": arg_repairs,
                "tool_id": tid,
            }

        frames: list[pd.DataFrame] = []
        target_dbs: list[str] = []
        meta: dict[str, Any] = {"parts": []}
        self.fetch_calls += 1
        for sql, target_db, part_meta in plans:
            verdict = self.policy.validate(sql)
            if not verdict.allowed:
                err = "policy_blocked"
                self.fetch_errors.append(f"{tid}:{err}")
                return {
                    "ok": False,
                    "error": err,
                    "violations": list(verdict.violations),
                    "tool_id": tid,
                    "arg_keys": sorted(args.keys()),
                }
            sanitized = verdict.sanitized_sql or sql
            result = self.sql_gateway.execute_readonly(sanitized, self.acl, target_db=target_db)
            if result.get("error"):
                return {
                    "ok": False,
                    "error": str(result.get("error")),
                    "message": result.get("message"),
                    "violations": result.get("violations"),
                    "target_db": target_db,
                    "tool_id": tid,
                    "sql_preview": sanitized[:500],
                    "warnings": warnings,
                }
            rows = list(result.get("rows") or [])
            columns = list(result.get("columns") or [])
            df = pd.DataFrame(rows, columns=columns) if columns else pd.DataFrame(rows)
            frames.append(df)
            target_dbs.append(target_db)
            meta["parts"].append({**part_meta, "target_db": target_db, "row_count": len(df)})

        if not frames:
            df = pd.DataFrame()
        elif len(frames) == 1:
            df = frames[0]
        else:
            df = pd.concat(frames, ignore_index=True)

        row_count = int(len(df))
        self.total_rows += row_count
        if self.total_rows > self.max_total_rows:
            return {"ok": False, "error": "total_row_budget_exceeded", "row_count": row_count}

        ref = (save_as or f"fetch_{self.fetch_calls}").strip() or f"fetch_{self.fetch_calls}"
        handle = self.working_set.save_frame(
            ref,
            df,
            role="fetch",
            purpose=tid,
            source="data_fetch",
            op_id=tid,
            op_args={k: v for k, v in args.items() if k != "raw_sql"},
        )
        if tid == "resolve_products":
            self._resolved_products = True
        if tid in {"query_rows", "preview_table", "lookup_distinct", "aggregate_rows"}:
            self._probed_facts.add("sale_lines")

        sample = df.head(5).astype(object).where(pd.notnull(df.head(5)), None)
        primary_db = target_dbs[0] if target_dbs else "db2"
        return {
            "ok": True,
            "tool_id": tid,
            "save_as": handle.ref,
            "row_count": row_count,
            "columns": list(df.columns),
            "sample": sample.to_dict(orient="records"),
            "target_db": primary_db,
            "target_dbs": target_dbs,
            "lineage": {
                "tool_id": tid,
                "params": {k: v for k, v in args.items() if k != "raw_sql"},
                "target_db": primary_db,
                "target_dbs": target_dbs,
                **meta,
            },
            "warnings": warnings,
        }

    def _route_targets(
        self, brief: dict[str, Any], time_range: dict[str, Any], target_db: str | None
    ) -> list[str]:
        if target_db in {"db1", "db2"}:
            return [str(target_db)]
        plan = suggest_query_plan(
            {"time_range": time_range or (brief.get("time_range") or {}), "filters": brief.get("filters") or {}}
        )
        targets: list[str] = []
        if plan.needs_db1:
            targets.append("db1")
        if plan.needs_db2:
            targets.append("db2")
        if not targets:
            targets = ["db2"]
        return targets

    def _physical_for(self, logical: str, target_db: str, brief: dict[str, Any]) -> str:
        logical_u = logical.upper()
        if target_db == "db2":
            return logical_u
        plan = suggest_query_plan(brief)
        if logical_u == "STRANS" and plan.shards:
            if len(plan.shards) == 1:
                return plan.shards[0]
            # Multi-shard: return first; caller may UNION — for now use newest + warn via shards list
            return plan.shards[-1]
        if logical_u == "TRANSHDR":
            return "TRANSHDR_ARC"
        if logical_u == "PMTRANS" and plan.shards:
            # shards_for_range is STRANS-named; keep logical for unknown shard helpers
            return logical_u
        return logical_u

    def _build_plans(
        self, tool_id: str, args: dict[str, Any], *, brief: dict[str, Any]
    ) -> list[tuple[str, str, dict[str, Any]]]:
        hard_max = self.max_rows
        time_range = coerce_time_range(
            args.get("time_range"),
            fallback=brief.get("time_range") if isinstance(brief.get("time_range"), dict) else None,
        )
        store_ids = args.get("store_ids")
        if store_ids is None and self.acl.store_filter_required:
            store_ids = list(self.acl.store_ids or [])
            if store_ids and tool_id in {"query_rows", "aggregate_rows"}:
                filters = list(args.get("filters") or [])
                filters.append({"column": "STK_ID", "op": "in", "value": store_ids})
                args = {**args, "filters": filters}

        if tool_id == "resolve_products":
            sql = builders.build_resolve_products(
                codes=args.get("codes"),
                limit=args.get("limit", 50),
                hard_max=hard_max,
            )
            return [(sql, "db2", {"table": "SKU_DEF"})]

        table = str(args.get("table") or "").strip().upper()
        if tool_id == "preview_table":
            if not table:
                raise ValueError("table_required")
            allowed = set(self.acl.allowed_tables or []) or set(ALLOWED_PREVIEW_TABLES)
            # Prefer ACL; fall back to preview allowlist intersection for tests.
            if table not in allowed and table not in ALLOWED_PREVIEW_TABLES:
                raise ValueError(f"table_not_allowed_for_preview:{table}")
            require_time = table in FACT_TABLES
            targets = self._route_targets(brief, time_range, args.get("target_db")) if require_time else ["db2"]
            plans: list[tuple[str, str, dict[str, Any]]] = []
            for target_db in targets:
                physical = self._physical_for(table, target_db, {**brief, "time_range": time_range}) if require_time else table
                sql = flex.build_query_rows(
                    table=table,
                    columns=args.get("columns"),
                    time_range=time_range if require_time else args.get("time_range"),
                    filters=args.get("filters") or [],
                    order_by=args.get("order_by"),
                    limit=args.get("limit", 20),
                    hard_max=min(50, hard_max),
                    require_time=require_time,
                    physical_table=physical,
                )
                # Also apply equals/contains sugar already merged into filters via normalize_sugar
                plans.append((sql, target_db, {"table": physical, "logical": table}))
            return plans

        if tool_id == "lookup_distinct":
            if not table:
                table = "STRANS"
            require_time = table in FACT_TABLES
            targets = self._route_targets(brief, time_range, args.get("target_db")) if require_time else ["db2"]
            plans = []
            for target_db in targets:
                physical = (
                    self._physical_for(table, target_db, {**brief, "time_range": time_range})
                    if require_time
                    else table
                )
                sql = flex.build_lookup_distinct(
                    table=table,
                    column=str(args.get("column") or "TRANS_CODE"),
                    time_range=time_range if require_time else args.get("time_range"),
                    contains=args.get("contains"),
                    filters=args.get("filters") or [],
                    limit=args.get("limit", 30),
                    hard_max=min(100, hard_max),
                    require_time=require_time,
                    physical_table=physical,
                )
                plans.append((sql, target_db, {"table": physical, "logical": table}))
            return plans

        if tool_id == "query_rows":
            if not table:
                raise ValueError("table_required")
            require_time = table in FACT_TABLES
            if require_time and not (time_range.get("start") and time_range.get("end")):
                raise ValueError("pushdown_required:time_range")
            # Reject inventing TRANS_CODE unless brief asks for document type.
            for clause in args.get("filters") or []:
                if str(clause.get("column") or "").upper() == "TRANS_CODE":
                    filters_brief = brief.get("filters") or {}
                    if not any(
                        k in filters_brief
                        for k in ("trans_code", "TRANS_CODE", "document_type", "document_types")
                    ):
                        raise ValueError("trans_code_filter_not_in_brief")
            targets = self._route_targets(brief, time_range, args.get("target_db"))
            plans = []
            for target_db in targets:
                physical = (
                    self._physical_for(table, target_db, {**brief, "time_range": time_range})
                    if require_time or table in FACT_TABLES
                    else table
                )
                sql = flex.build_query_rows(
                    table=table,
                    columns=args.get("columns"),
                    time_range=time_range if require_time else args.get("time_range"),
                    filters=args.get("filters") or [],
                    order_by=args.get("order_by"),
                    limit=args.get("limit", 5000),
                    hard_max=hard_max,
                    require_time=require_time,
                    physical_table=physical,
                )
                plans.append((sql, target_db, {"table": physical, "logical": table}))
            return plans

        if tool_id == "aggregate_rows":
            if not table:
                table = "STRANS"
            require_time = table in FACT_TABLES
            if require_time and not (time_range.get("start") and time_range.get("end")):
                raise ValueError("pushdown_required:time_range")
            targets = self._route_targets(brief, time_range, args.get("target_db"))
            plans = []
            for target_db in targets:
                physical = self._physical_for(table, target_db, {**brief, "time_range": time_range})
                sql = flex.build_aggregate_rows(
                    table=table,
                    time_range=time_range if require_time else args.get("time_range"),
                    filters=args.get("filters") or [],
                    group_by=args.get("group_by"),
                    aggs=args.get("aggs"),
                    limit=args.get("limit", 5000),
                    hard_max=hard_max,
                    require_time=require_time,
                    physical_table=physical,
                )
                plans.append((sql, target_db, {"table": physical, "logical": table}))
            return plans

        raise ValueError(f"unknown_fetch_tool:{tool_id}")
