from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from project_core.paths import ROOT


@dataclass
class ColumnMeta:
    name: str
    data_type: str = "varchar"
    nullable: bool = True
    description: str = ""


@dataclass
class TableMeta:
    name: str
    schema: str = "dbo"
    data_source: str = ""
    schema_file: str = ""
    description: str = ""
    columns: list[ColumnMeta] = field(default_factory=list)


class SchemaCatalog:
    def __init__(
        self,
        tables: dict[str, TableMeta] | None = None,
        *,
        shard_physical: dict[str, list[str]] | None = None,
    ) -> None:
        self._tables = tables or {}
        # If set, freeze allowlist (tests). Otherwise expand from shards.yaml + rolling cutoff.
        self._shard_physical_override = shard_physical

    def _shard_physical(self) -> dict[str, list[str]]:
        if self._shard_physical_override is not None:
            return self._shard_physical_override
        from project_core.domain.sql.shard_resolver import physical_shard_map

        return physical_shard_map()

    @classmethod
    def from_dictionary_dir(cls, directory: Path | None = None) -> SchemaCatalog:
        base = directory or (ROOT / "data_dictionary")
        tables: dict[str, TableMeta] = {}
        if not base.exists():
            return cls(tables)

        skip_names = {"domain_definitions.md", "brief_templates.md", "sensitive_columns.md", "readme.md"}
        patterns = [
            base.glob("tables/db1/*.md"),
            base.glob("tables/db2/*.md"),
            base.glob("tables/*.md"),
            base.glob("*.md"),
        ]
        seen: set[str] = set()
        for pattern in patterns:
            for path in sorted(pattern):
                if path.name.lower() in skip_names:
                    continue
                text = path.read_text(encoding="utf-8")
                frontmatter = cls._parse_frontmatter(text)
                table_name = path.stem
                data_source = str(frontmatter.get("data_source") or path.parent.name)
                if data_source in {"tables", "data_dictionary"}:
                    data_source = ""
                key = f"{data_source}:{table_name}".lower() if data_source else table_name.lower()
                if key in seen:
                    continue
                seen.add(key)
                description = str(frontmatter.get("description") or "")
                columns = cls._parse_columns(text)
                rel = path.relative_to(base).as_posix()
                tables[key] = TableMeta(
                    name=table_name,
                    data_source=data_source,
                    schema_file=rel,
                    description=description,
                    columns=columns,
                )

        shard_physical = cls._load_shard_physical(base / "db1" / "shards.yaml")
        # None override → runtime expand via shard_resolver (rolling cutoff).
        # Pass empty dict only when yaml missing so callers still get consistent type.
        return cls(tables, shard_physical=shard_physical)

    @staticmethod
    def _load_shard_physical(path: Path) -> dict[str, list[str]] | None:
        if not path.exists():
            return {}
        # Prefer dynamic expansion; returning None tells __init__ to use physical_shard_map().
        return None

    @staticmethod
    def _parse_frontmatter(text: str) -> dict[str, object]:
        if not text.startswith("---"):
            return {}
        end = text.find("---", 3)
        if end < 0:
            return {}
        block = text[3:end].strip()
        if not block:
            return {}
        try:
            loaded = yaml.safe_load(block)
            return loaded if isinstance(loaded, dict) else {}
        except yaml.YAMLError:
            return {}

    @staticmethod
    def _parse_columns(text: str) -> list[ColumnMeta]:
        columns: list[ColumnMeta] = []
        for line in text.splitlines():
            if line.startswith("|") and "|" in line[1:] and not line.startswith("|--"):
                parts = [p.strip() for p in line.strip("|").split("|")]
                if len(parts) >= 2 and parts[0].lower() not in {"column", "cột"}:
                    desc = parts[2] if len(parts) >= 3 else ""
                    columns.append(ColumnMeta(name=parts[0], data_type=parts[1], description=desc))
        return columns

    def tables(self) -> list[str]:
        return list(self._tables.keys())

    def table(self, name: str) -> TableMeta | None:
        return self._tables.get(name.lower())

    def logical_table_names(self) -> list[str]:
        return sorted({meta.name for meta in self._tables.values()}, key=str.lower)

    def sql_table_names(self) -> set[str]:
        """All table identifiers that may appear in SQL (logical + db1 physical shards)."""
        names: set[str] = set()
        for meta in self._tables.values():
            names.add(meta.name.lower())
        for logical, physicals in self._shard_physical().items():
            names.add(logical.lower())
            names.update(p.lower() for p in physicals)
        return names

    def is_dictionary_table(self, sql_table: str) -> bool:
        return sql_table.lower() in self.sql_table_names()

    def resolve_allowed_sql_tables(self, role_tables: list[str] | None) -> set[str]:
        """Expand role logical names to SQL identifiers, restricted to data_dictionary."""
        dictionary = self.sql_table_names()
        if role_tables is None:
            return set(dictionary)
        if len(role_tables) == 0:
            return set()

        allowed: set[str] = set()
        role_set = {t.lower() for t in role_tables}
        for meta in self._tables.values():
            if meta.name.lower() in role_set:
                allowed.add(meta.name.lower())
        for logical, physicals in self._shard_physical().items():
            if logical.lower() in role_set:
                allowed.add(logical.lower())
                allowed.update(p.lower() for p in physicals)
        return allowed & dictionary

    def agent_schema_bundle(
        self,
        role_tables: list[str],
        *,
        max_columns_per_table: int = 48,
        domain_max_chars: int = 6000,
        table_filter: list[str] | None = None,
        column_priority: list[str] | None = None,
    ) -> dict[str, object]:
        allowed = {t.lower() for t in role_tables}
        if table_filter:
            filter_set = {t.lower() for t in table_filter}
            allowed = allowed & filter_set
        tables_out: list[dict[str, object]] = []
        priority = [c.upper() for c in (column_priority or [])]
        for meta in sorted(self._tables.values(), key=lambda m: (m.data_source, m.name)):
            if meta.name.lower() not in allowed:
                continue
            cols = meta.columns
            if priority:
                pri = [c for c in cols if c.name.upper() in priority]
                rest = [c for c in cols if c.name.upper() not in priority]
                cols = pri + rest
            tables_out.append(
                {
                    "name": meta.name,
                    "data_source": meta.data_source,
                    "description": meta.description,
                    "schema_file": meta.schema_file,
                    "columns": [
                        {"name": c.name, "type": c.data_type, "description": c.description or ""}
                        for c in cols[:max_columns_per_table]
                    ],
                }
            )

        from project_core.domain.sql.shard_resolver import archive_newest_ym, table_naming_context

        shards_out: dict[str, object] = {}
        for logical, physicals in self._shard_physical().items():
            if logical.lower() in allowed:
                monthly = any(
                    len(p.rsplit("_", 1)[-1]) == 6 and p.rsplit("_", 1)[-1].isdigit() for p in physicals
                )
                shards_out[logical] = {
                    "physical_pattern": f"{logical}_{{YYYYMM}}" if monthly else logical,
                    "physical_tables": physicals,
                    "shard_key_column": "TRAN_DATE",
                    "archive_newest_ym": archive_newest_ym() if monthly else None,
                }

        domain_path = ROOT / "data_dictionary" / "domain_definitions.md"
        domain_excerpt = ""
        if domain_path.exists():
            domain_excerpt = domain_path.read_text(encoding="utf-8")[:domain_max_chars]

        return {
            "tables": tables_out,
            "db1_shards": shards_out,
            "domain_definitions_excerpt": domain_excerpt,
            "data_sources": {"db1": "history archive", "db2": "live + master + recent"},
            "table_naming": table_naming_context(),
        }

    def snapshot(self) -> dict[str, list[dict[str, str]]]:
        """Schema keyed by catalog id (db1:strans, db2:strans, …)."""
        return {
            name: [{"name": c.name, "type": c.data_type} for c in meta.columns]
            for name, meta in self._tables.items()
        }

    def snapshot_for_agents(self, role_tables: list[str] | None = None) -> dict[str, object]:
        bundle = self.agent_schema_bundle(role_tables or self.logical_table_names())
        return {
            "tables": bundle["tables"],
            "db1_shards": bundle["db1_shards"],
        }

    def tables_meta(self) -> dict[str, dict[str, str]]:
        return {
            name: {
                "description": meta.description or f"table {meta.name} ({meta.data_source})",
                "schema": meta.schema,
                "data_source": meta.data_source,
                "schema_file": meta.schema_file,
            }
            for name, meta in self._tables.items()
        }

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.snapshot(), sort_keys=True)
