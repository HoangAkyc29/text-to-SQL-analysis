from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from project_core.paths import ROOT


@dataclass
class ColumnMeta:
    name: str
    data_type: str = "varchar"
    nullable: bool = True


@dataclass
class TableMeta:
    name: str
    schema: str = "dbo"
    columns: list[ColumnMeta] = field(default_factory=list)


class SchemaCatalog:
    def __init__(self, tables: dict[str, TableMeta] | None = None) -> None:
        self._tables = tables or {}

    @classmethod
    def from_dictionary_dir(cls, directory: Path | None = None) -> SchemaCatalog:
        base = directory or (ROOT / "data_dictionary")
        tables: dict[str, TableMeta] = {}
        if not base.exists():
            return cls(tables)
        patterns = [base.glob("*.md"), base.glob("tables/*.md")]
        seen: set[str] = set()
        for pattern in patterns:
            for path in pattern:
                if path.name in {"domain_definitions.md", "brief_templates.md", "sensitive_columns.md"}:
                    continue
                table_name = path.stem
                key = table_name.lower()
                if key in seen:
                    continue
                seen.add(key)
                columns = cls._parse_columns(path.read_text(encoding="utf-8"))
                tables[key] = TableMeta(name=table_name, columns=columns)
        return cls(tables)

    @staticmethod
    def _parse_columns(text: str) -> list[ColumnMeta]:
        columns: list[ColumnMeta] = []
        for line in text.splitlines():
            if line.startswith("|") and "|" in line[1:] and not line.startswith("|--"):
                parts = [p.strip() for p in line.strip("|").split("|")]
                if len(parts) >= 2 and parts[0].lower() not in {"column", "cột"}:
                    columns.append(ColumnMeta(name=parts[0], data_type=parts[1]))
        return columns

    def tables(self) -> list[str]:
        return list(self._tables.keys())

    def table(self, name: str) -> TableMeta | None:
        return self._tables.get(name.lower())

    def snapshot(self) -> dict[str, list[dict[str, str]]]:
        return {
            name: [{"name": c.name, "type": c.data_type} for c in meta.columns]
            for name, meta in self._tables.items()
        }

    def tables_meta(self) -> dict[str, dict[str, str]]:
        return {
            name: {
                "description": f"table {meta.name} with {len(meta.columns)} columns",
                "schema": meta.schema,
            }
            for name, meta in self._tables.items()
        }

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.snapshot(), sort_keys=True)
