from __future__ import annotations

import re
from dataclasses import dataclass, field

import sqlglot
from sqlglot import exp

from project_core.config.loader import load_project_config
from project_core.domain.schema.catalog import SchemaCatalog


@dataclass
class PolicyVerdict:
    allowed: bool
    sanitized_sql: str | None = None
    violations: list[str] = field(default_factory=list)


class PolicyEngine:
    def __init__(
        self,
        catalog: SchemaCatalog,
        *,
        allowed_tables: list[str] | None = None,
        denied_columns: list[str] | None = None,
        store_ids: list[int] | None = None,
        store_filter_required: bool = False,
    ) -> None:
        self.catalog = catalog
        cfg = load_project_config().policy
        self.max_rows = cfg.max_rows
        self.max_join_depth = cfg.max_join_depth
        self.default_schema = cfg.default_schema
        self._dictionary_tables = catalog.sql_table_names()
        self.allowed_tables = catalog.resolve_allowed_sql_tables(allowed_tables)
        self.denied_columns = {c.lower() for c in (denied_columns or [])}
        self.store_ids = store_ids
        self.store_filter_required = store_filter_required

    def validate(self, sql: str) -> PolicyVerdict:
        violations: list[str] = []
        sql = sql.strip().rstrip(";").strip()
        if self._has_logical_db_prefix(sql):
            return PolicyVerdict(False, violations=["logical_db_prefix_forbidden"])
        try:
            statements = sqlglot.parse(sql, read="tsql")
        except Exception as exc:  # noqa: BLE001
            return PolicyVerdict(False, violations=[f"parse_error: {exc}"])

        if len(statements) != 1:
            violations.append("single_statement_required")
            return PolicyVerdict(False, violations=violations)

        statement = statements[0]
        root = statement.this if isinstance(statement, exp.With) else statement
        if not isinstance(root, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
            violations.append("select_only")
            return PolicyVerdict(False, violations=violations)

        if self._has_forbidden_patterns(sql):
            violations.append("forbidden_pattern")
            return PolicyVerdict(False, violations=violations)

        cte_names = self._cte_names(statement)
        tables = {t.name.lower() for t in statement.find_all(exp.Table) if t.name}
        for table in tables:
            if table in cte_names:
                continue
            if table not in self._dictionary_tables:
                violations.append(f"table_not_in_dictionary:{table}")
            elif table not in self.allowed_tables:
                violations.append(f"table_not_allowed:{table}")

        for column in statement.find_all(exp.Column):
            col_name = (column.name or "").lower()
            table_name = (column.table or "").lower()
            qualified = f"{table_name}.{col_name}" if table_name else col_name
            if qualified in self.denied_columns or col_name in self.denied_columns:
                violations.append(f"column_denied:{qualified}")

        joins = list(statement.find_all(exp.Join))
        if len(joins) > self.max_join_depth:
            violations.append("join_depth_exceeded")

        if violations:
            return PolicyVerdict(False, violations=violations)

        sanitized = self._sanitize_readonly(statement)
        if self.store_filter_required and self.store_ids and isinstance(statement, exp.Select):
            statement = sqlglot.parse_one(sanitized, read="tsql")
            if isinstance(statement, exp.Select):
                sanitized = self._inject_store_filter(statement).sql(dialect="tsql")

        return PolicyVerdict(True, sanitized_sql=sanitized)

    def _sanitize_readonly(self, statement: exp.Expression) -> str:
        if isinstance(statement, exp.Select):
            return self._inject_top(statement).sql(dialect="tsql")
        if isinstance(statement, (exp.Union, exp.Intersect, exp.Except)):
            out = statement.sql(dialect="tsql")
            if not re.search(r"\bTOP\b", out, flags=re.IGNORECASE):
                out = re.sub(
                    r"(?i)^SELECT",
                    f"SELECT TOP {self.max_rows}",
                    out.strip(),
                    count=1,
                )
            return out
        if isinstance(statement, exp.With):
            inner = self._sanitize_readonly(statement.this)
            with_sql = statement.sql(dialect="tsql")
            # Replace only when inner was rewritten (Select path); Union path already handled.
            if inner != statement.this.sql(dialect="tsql"):
                return with_sql
            return inner if statement.this else with_sql
        return statement.sql(dialect="tsql")

    def _cte_names(self, statement: exp.Select) -> set[str]:
        names: set[str] = set()
        for cte in statement.find_all(exp.CTE):
            alias = cte.args.get("alias")
            if alias and getattr(alias, "name", None):
                names.add(str(alias.name).lower())
            elif alias and getattr(alias, "this", None) and getattr(alias.this, "name", None):
                names.add(str(alias.this.name).lower())
        return names

    def _has_logical_db_prefix(self, sql: str) -> bool:
        return bool(re.search(r"\b(?:db1|db2)\s*\.\s*(?:\[?dbo\]?\s*\.)?", sql, flags=re.IGNORECASE))

    def _has_forbidden_patterns(self, sql: str) -> bool:
        sql = sql.strip().rstrip(";").strip()
        if ";" in sql:
            return True
        lowered = sql.lower()
        if re.search(r"\bxp_\w+", lowered):
            return True
        try:
            tree = sqlglot.parse_one(sql, read="tsql")
            forbidden = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter, exp.Command)
            if any(tree.find(t) for t in forbidden):
                return True
        except Exception:
            pass
        return any(token in lowered for token in (" insert ", " update ", " delete ", " drop ", " exec "))

    def _inject_top(self, statement: exp.Select) -> exp.Select:
        if statement.args.get("limit"):
            return statement
        statement.set("limit", exp.Limit(expression=exp.Literal.number(self.max_rows)))
        return statement

    def _inject_store_filter(self, statement: exp.Select) -> exp.Select:
        store_col = exp.column("STK_ID")
        condition = exp.In(
            this=store_col,
            expressions=[exp.Literal.string(str(i)) for i in (self.store_ids or [])],
        )
        where = statement.args.get("where")
        if where:
            statement.set("where", exp.And(this=where, expression=condition))
        else:
            statement.set("where", exp.Where(this=condition))
        return statement

    def sql_fingerprint(self, sql: str) -> str:
        normalized = re.sub(r"\s+", " ", sql.strip().lower())
        return normalized[:128]
