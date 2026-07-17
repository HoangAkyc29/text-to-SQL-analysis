"""Build IV-facing semantics for tables/columns present in SQL result outputs.

Pipeline pre-resolves dictionary meanings for only:
- tables referenced in executed SQL (logical, shard-normalized)
- columns that appear on the parquet result (output names)

No full schema_context / RAG — unresolved projections stay explicit.
"""

from __future__ import annotations

import re
from typing import Any, Literal

import sqlglot
from sqlglot import exp

from project_core.domain.schema.catalog import SchemaCatalog, TableMeta
from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog, ColumnSemanticMeta

_MAX_FACTS = 4
_MAX_DESC = 240
_SHARD_SUFFIX = re.compile(r"^(.+)_(\d{6})$", re.IGNORECASE)

MatchKind = Literal[
    "sqlglot_projection",
    "name_exact",
    "aggregated",
    "unresolved",
]
Confidence = Literal["high", "medium", "low"]


def normalize_logical_table(sql_table: str) -> str:
    """Strip db1 monthly shard suffix when present (STRANS_202401 -> STRANS)."""
    name = (sql_table or "").strip()
    if not name:
        return ""
    m = _SHARD_SUFFIX.match(name)
    if m:
        return m.group(1)
    return name


def extract_sql_tables(sql: str) -> list[str]:
    """Logical table names from SQL (CTEs excluded, shards normalized)."""
    try:
        tree = sqlglot.parse_one(sql, read="tsql")
    except Exception:
        return []
    cte_names = _cte_names(tree)
    out: list[str] = []
    seen: set[str] = set()
    for table in tree.find_all(exp.Table):
        raw = (table.name or "").strip()
        if not raw:
            continue
        if raw.lower() in cte_names:
            continue
        logical = normalize_logical_table(raw)
        key = logical.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(logical)
    return out


def extract_alias_map(sql: str) -> dict[str, str]:
    """Map table alias / bare name (lower) -> logical table name."""
    try:
        tree = sqlglot.parse_one(sql, read="tsql")
    except Exception:
        return {}
    cte_names = _cte_names(tree)
    mapping: dict[str, str] = {}
    for table in tree.find_all(exp.Table):
        raw = (table.name or "").strip()
        if not raw or raw.lower() in cte_names:
            continue
        logical = normalize_logical_table(raw)
        mapping[raw.lower()] = logical
        mapping[logical.lower()] = logical
        alias = table.alias_or_name
        if alias:
            mapping[str(alias).lower()] = logical
        # sqlglot may expose alias via args
        alias_node = table.args.get("alias")
        if alias_node is not None:
            aname = getattr(alias_node, "name", None) or getattr(getattr(alias_node, "this", None), "name", None)
            if aname:
                mapping[str(aname).lower()] = logical
    return mapping


def extract_projections(sql: str) -> list[dict[str, Any]]:
    """SELECT-list projections for the outermost (or left-most UNION) select."""
    try:
        tree = sqlglot.parse_one(sql, read="tsql")
    except Exception:
        return []
    select = _outer_select(tree)
    if select is None:
        return []
    projections: list[dict[str, Any]] = []
    for proj in select.expressions:
        if isinstance(proj, exp.Star) or (isinstance(proj, exp.Alias) and isinstance(proj.this, exp.Star)):
            projections.append(
                {
                    "output_name": "*",
                    "expression_sql": proj.sql(dialect="tsql"),
                    "source_columns": [],
                    "is_star": True,
                    "is_aggregate": False,
                }
            )
            continue
        if isinstance(proj, exp.Alias):
            output_name = proj.alias or proj.alias_or_name
            expr = proj.this
        else:
            output_name = proj.alias_or_name or getattr(proj, "name", None) or proj.sql(dialect="tsql")
            expr = proj
        source_columns: list[dict[str, str | None]] = []
        for col in expr.find_all(exp.Column):
            source_columns.append(
                {
                    "table_alias": (col.table or None),
                    "column": col.name,
                }
            )
        is_aggregate = _is_aggregate(expr)
        projections.append(
            {
                "output_name": str(output_name),
                "expression_sql": expr.sql(dialect="tsql") if expr is not None else None,
                "source_columns": source_columns,
                "is_star": False,
                "is_aggregate": is_aggregate,
            }
        )
    return projections


def resolve_table_ref(
    logical_name: str,
    *,
    catalog: SchemaCatalog,
    target_db: str | None = None,
) -> tuple[str | None, TableMeta | None]:
    """Pick dictionary table_ref (db2:strans) and TableMeta for a logical name."""
    logical = normalize_logical_table(logical_name)
    if not logical:
        return None, None
    candidates: list[str] = []
    db = (target_db or "").lower().strip()
    if db in {"db1", "db2"}:
        candidates.append(f"{db}:{logical}")
    candidates.extend([f"db2:{logical}", f"db1:{logical}", logical])
    seen: set[str] = set()
    for key in candidates:
        k = key.lower()
        if k in seen:
            continue
        seen.add(k)
        meta = catalog.table(k)
        if meta is not None:
            ref = f"{meta.data_source}:{meta.name}".lower() if meta.data_source else meta.name.lower()
            return ref, meta
    # Fallback: scan by bare name via public keys
    for key in catalog.tables():
        meta = catalog.table(key)
        if meta is not None and meta.name.lower() == logical.lower():
            ref = f"{meta.data_source}:{meta.name}".lower() if meta.data_source else meta.name.lower()
            return ref, meta
    return None, None


def build_output_semantics(
    *,
    approved_sql: list[str],
    query_files: list[Any],
    catalog: SchemaCatalog,
    column_catalog: ColumnSemanticCatalog,
    target_dbs: list[str] | None = None,
    default_target_db: str = "db2",
    max_facts: int = _MAX_FACTS,
    max_description_chars: int = _MAX_DESC,
) -> dict[str, list[dict[str, Any]]]:
    """Resolve slim output_*_semantics for Agent IV.

    ``query_files`` items must expose ``query_index``, ``columns`` (result names).
    ``approved_sql[i]`` pairs with ``query_files[i]``.
    """
    tables_out: list[dict[str, Any]] = []
    columns_out: list[dict[str, Any]] = []
    target_dbs = list(target_dbs or [])

    for i, qf in enumerate(query_files):
        sql = approved_sql[i] if i < len(approved_sql) else ""
        qidx = int(getattr(qf, "query_index", None) if not isinstance(qf, dict) else qf.get("query_index", i))
        result_cols = list(
            getattr(qf, "columns", None) if not isinstance(qf, dict) else (qf.get("columns") or [])
        )
        result_cols = [str(c) for c in result_cols]
        result_upper = {c.upper(): c for c in result_cols}

        tdb = default_target_db
        if qidx < len(target_dbs) and target_dbs[qidx]:
            tdb = str(target_dbs[qidx])
        elif i < len(target_dbs) and target_dbs[i]:
            tdb = str(target_dbs[i])

        logical_tables = extract_sql_tables(sql) if sql else []
        alias_map = extract_alias_map(sql) if sql else {}
        table_refs_used: list[str] = []

        for logical in logical_tables:
            ref, meta = resolve_table_ref(logical, catalog=catalog, target_db=tdb)
            if ref:
                table_refs_used.append(ref)
            desc = (meta.description if meta else "") or ""
            if len(desc) > max_description_chars:
                desc = desc[: max_description_chars - 1] + "…"
            tables_out.append(
                {
                    "query_index": qidx,
                    "logical_name": logical.upper() if logical else logical,
                    "table_ref": ref,
                    "description": desc,
                    "confidence": "high" if meta is not None else "low",
                }
            )

        projections = extract_projections(sql) if sql else []
        # Expand SELECT * into result columns (no per-column expression from SQL).
        expanded: list[dict[str, Any]] = []
        for proj in projections:
            if proj.get("is_star"):
                for col in result_cols:
                    expanded.append(
                        {
                            "output_name": col,
                            "expression_sql": None,
                            "source_columns": [{"table_alias": None, "column": col}],
                            "is_star": True,
                            "is_aggregate": False,
                        }
                    )
            else:
                expanded.append(proj)

        # Index projections by output name (case-insensitive) for parquet allowlist.
        by_output: dict[str, dict[str, Any]] = {}
        for proj in expanded:
            name = str(proj.get("output_name") or "")
            if not name or name == "*":
                continue
            by_output[name.upper()] = proj

        # Every parquet column gets an entry (allowlist).
        for out_name in result_cols:
            proj = by_output.get(out_name.upper())
            entry = _resolve_column_entry(
                query_index=qidx,
                output_name=out_name,
                projection=proj,
                alias_map=alias_map,
                table_refs_used=table_refs_used,
                logical_tables=logical_tables,
                catalog=catalog,
                column_catalog=column_catalog,
                target_db=tdb,
                max_facts=max_facts,
            )
            columns_out.append(entry)

        # If SQL named a projection that somehow isn't in parquet keys (rare), skip —
        # allowlist is parquet only. If parquet has cols with no projection match,
        # _resolve_column_entry already handled via name_exact / unresolved.

        _ = result_upper  # reserved for future alias alignment

    return {
        "output_table_semantics": tables_out,
        "output_column_semantics": columns_out,
    }


def _resolve_column_entry(
    *,
    query_index: int,
    output_name: str,
    projection: dict[str, Any] | None,
    alias_map: dict[str, str],
    table_refs_used: list[str],
    logical_tables: list[str],
    catalog: SchemaCatalog,
    column_catalog: ColumnSemanticCatalog,
    target_db: str,
    max_facts: int,
) -> dict[str, Any]:
    expression = None
    source_physical: list[str] = []
    source_tables: list[str] = []
    is_aggregate = False
    match: MatchKind = "unresolved"
    confidence: Confidence = "low"
    semantic: ColumnSemanticMeta | None = None

    if projection:
        expression = projection.get("expression_sql")
        is_aggregate = bool(projection.get("is_aggregate"))
        for sc in projection.get("source_columns") or []:
            col = str(sc.get("column") or "")
            if not col:
                continue
            if col.upper() not in {c.upper() for c in source_physical}:
                source_physical.append(col)
            alias = sc.get("table_alias")
            logical = None
            if alias:
                logical = alias_map.get(str(alias).lower())
            if logical:
                ref, _ = resolve_table_ref(logical, catalog=catalog, target_db=target_db)
                if ref and ref not in source_tables:
                    source_tables.append(ref)

        # High confidence: single source column with bound table
        if len(source_physical) == 1 and len(source_tables) == 1:
            semantic = column_catalog.semantic_for_column(source_tables[0], source_physical[0])
            if semantic:
                match = "aggregated" if is_aggregate else "sqlglot_projection"
                confidence = "medium" if is_aggregate else "high"
        elif len(source_physical) == 1 and not source_tables:
            # Bare column — unique among used tables?
            semantic, ref = _unique_column_among_tables(
                source_physical[0], logical_tables, catalog, column_catalog, target_db
            )
            if semantic and ref:
                source_tables = [ref]
                match = "aggregated" if is_aggregate else "sqlglot_projection"
                confidence = "medium"
            elif is_aggregate:
                match = "aggregated"
                confidence = "low"

    # Fallback: exact name match on output_name against used tables' physical columns
    if semantic is None:
        semantic, ref = _unique_column_among_tables(
            output_name, logical_tables, catalog, column_catalog, target_db
        )
        if semantic and ref:
            if ref not in source_tables:
                source_tables.append(ref)
            if output_name.upper() not in {c.upper() for c in source_physical}:
                source_physical.append(output_name)
            match = "name_exact"
            confidence = "medium"

    if semantic is None:
        match = "aggregated" if is_aggregate else "unresolved"
        confidence = "low"

    facts = list(semantic.facts[:max_facts]) if semantic else []
    return {
        "query_index": query_index,
        "output_name": output_name,
        "semantic_key": semantic.semantic_key if semantic else None,
        "kind": semantic.kind if semantic else None,
        "facts": facts,
        "source": {
            "tables": source_tables,
            "physical_columns": source_physical,
            "expression": expression,
            "match": match,
        },
        "confidence": confidence,
    }


def _unique_column_among_tables(
    column: str,
    logical_tables: list[str],
    catalog: SchemaCatalog,
    column_catalog: ColumnSemanticCatalog,
    target_db: str,
) -> tuple[ColumnSemanticMeta | None, str | None]:
    hits: list[tuple[str, ColumnSemanticMeta]] = []
    for logical in logical_tables:
        ref, _ = resolve_table_ref(logical, catalog=catalog, target_db=target_db)
        if not ref:
            continue
        meta = column_catalog.semantic_for_column(ref, column)
        if meta is not None:
            hits.append((ref, meta))
    if len(hits) == 1:
        return hits[0][1], hits[0][0]
    return None, None


def _cte_names(tree: exp.Expression) -> set[str]:
    names: set[str] = set()
    for cte in tree.find_all(exp.CTE):
        alias = cte.args.get("alias")
        if alias and getattr(alias, "name", None):
            names.add(str(alias.name).lower())
        elif alias and getattr(alias, "this", None) and getattr(alias.this, "name", None):
            names.add(str(alias.this.name).lower())
    return names


def _outer_select(tree: exp.Expression) -> exp.Select | None:
    node: exp.Expression | None = tree
    if isinstance(node, exp.With):
        node = node.this
    while isinstance(node, (exp.Union, exp.Intersect, exp.Except)):
        node = node.this
    if isinstance(node, exp.Select):
        return node
    return None


def _is_aggregate(expr: exp.Expression) -> bool:
    agg_types = (exp.Sum, exp.Count, exp.Avg, exp.Max, exp.Min)
    if isinstance(expr, agg_types):
        return True
    return any(isinstance(n, agg_types) for n in expr.find_all(*agg_types))
