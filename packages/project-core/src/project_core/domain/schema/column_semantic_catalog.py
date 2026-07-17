from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from project_core.paths import ROOT


@dataclass
class ColumnSemanticMeta:
    semantic_key: str
    display_names: list[str] = field(default_factory=list)
    kind: str = "text"
    tables: list[dict[str, str]] = field(default_factory=list)
    join_with: list[str] = field(default_factory=list)
    related_semantic_keys: list[str] = field(default_factory=list)
    facts: list[str] = field(default_factory=list)
    schema_file: str = ""
    body: str = ""


class ColumnSemanticCatalog:
    def __init__(self, columns: dict[str, ColumnSemanticMeta] | None = None) -> None:
        self._columns = columns or {}

    @classmethod
    def from_columns_dir(cls, directory: Path | None = None) -> ColumnSemanticCatalog:
        base = directory or (ROOT / "data_dictionary" / "columns")
        columns: dict[str, ColumnSemanticMeta] = {}
        if not base.exists():
            return cls(columns)
        for path in sorted(base.glob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            text = path.read_text(encoding="utf-8")
            fm = cls._parse_frontmatter(text)
            key = str(fm.get("semantic_key") or path.stem).lower()
            body = text.split("---", 2)[-1].strip() if text.startswith("---") else text
            dd_root = base.parent if base.name.lower() == "columns" else base
            try:
                rel = path.relative_to(dd_root).as_posix()
            except ValueError:
                rel = path.name
            columns[key] = ColumnSemanticMeta(
                semantic_key=key,
                display_names=[str(x) for x in (fm.get("display_names") or [])],
                kind=str(fm.get("kind") or "text"),
                tables=list(fm.get("tables") or []),
                join_with=[str(x) for x in (fm.get("join_with") or [])],
                related_semantic_keys=[str(x) for x in (fm.get("related_semantic_keys") or [])],
                facts=[str(x) for x in (fm.get("facts") or [])],
                schema_file=rel,
                body=body,
            )
        return cls(columns)

    @staticmethod
    def _parse_frontmatter(text: str) -> dict[str, Any]:
        if not text.startswith("---"):
            return {}
        end = text.find("---", 3)
        if end < 0:
            return {}
        block = text[3:end].strip()
        if not block:
            return {}
        loaded = yaml.safe_load(block)
        return loaded if isinstance(loaded, dict) else {}

    def semantic_keys(self) -> list[str]:
        return sorted(self._columns.keys())

    def get(self, semantic_key: str) -> ColumnSemanticMeta | None:
        return self._columns.get(semantic_key.lower())

    def tables_for_semantic(self, semantic_key: str) -> list[str]:
        meta = self.get(semantic_key)
        if not meta:
            return []
        return [str(t.get("ref", "")) for t in meta.tables if t.get("ref")]

    def semantic_by_table(self, table_ref: str) -> list[ColumnSemanticMeta]:
        ref = table_ref.lower()
        return [m for m in self._columns.values() if any(str(t.get("ref", "")).lower() == ref for t in m.tables)]

    def resolve_physical(self, semantic_key: str, table_ref: str) -> dict[str, str] | None:
        meta = self.get(semantic_key)
        if not meta:
            return None
        for t in meta.tables:
            if str(t.get("ref", "")).lower() == table_ref.lower():
                return t
        return None

    def semantic_for_column(self, table_ref: str, column: str) -> ColumnSemanticMeta | None:
        ref = table_ref.lower()
        col = column.upper()
        for meta in self._columns.values():
            for t in meta.tables:
                if str(t.get("ref", "")).lower() == ref and str(t.get("column", "")).upper() == col:
                    return meta
        return None

    def embed_text(self, semantic_key: str) -> str:
        meta = self.get(semantic_key)
        if not meta:
            return ""
        names = ", ".join(meta.display_names) or semantic_key
        physical = []
        for t in meta.tables:
            col = t.get("column")
            if col and str(col) not in physical:
                physical.append(str(col))
        table_refs = self._sorted_table_refs([str(t.get("ref")) for t in meta.tables if t.get("ref")])
        facts = "; ".join(meta.facts[:6])
        title = ""
        business = ""
        if meta.body:
            for line in meta.body.splitlines():
                s = line.strip()
                if s.startswith("# ") and not title:
                    title = s[2:].strip()
                    break
            if "## Ý nghĩa nghiệp vụ" in meta.body:
                section = meta.body.split("## Ý nghĩa nghiệp vụ", 1)[-1]
                business = section.split("\n##", 1)[0].strip().replace("\n", " ")[:600]
        sk_tokens = semantic_key.replace("__", " ").replace("_", " ")
        keyword_parts = list(dict.fromkeys([*meta.display_names, *physical, sk_tokens]))
        parts = [
            f"column {semantic_key} ({names}): kind={meta.kind}.",
            f"Tables: {', '.join(table_refs)}.",
        ]
        if physical:
            parts.append(f"Physical: {', '.join(physical)}.")
        if title:
            parts.append(f"Title: {title}.")
        if business:
            parts.append(f"Business: {business}")
        if facts:
            parts.append(f"Facts: {facts}")
        if meta.join_with:
            parts.append("Joins: " + ", ".join(meta.join_with[:8]))
        if meta.related_semantic_keys:
            parts.append("Related: " + ", ".join(meta.related_semantic_keys[:8]))
        if keyword_parts:
            parts.append("Keywords: " + ", ".join(str(k) for k in keyword_parts[:24]))
        return " ".join(parts)

    @staticmethod
    def _sorted_table_refs(refs: list[str]) -> list[str]:
        def key(ref: str) -> tuple[int, int, int, str]:
            r = ref.lower()
            stem = r.split(":")[-1]
            db2 = 0 if r.startswith("db2:") else 1
            noise = 1 if ("_tmp" in stem or stem == "suspend" or "webrpt" in stem) else 0
            arc = 1 if "_arc" in stem else 0
            return (db2, noise, arc, r)

        # preserve first-seen casing from input while sorting unique lower keys
        seen: dict[str, str] = {}
        for ref in refs:
            low = ref.lower()
            if low not in seen:
                seen[low] = ref
        return [seen[k] for k in sorted(seen.keys(), key=key)]

    def table_refs(self) -> set[str]:
        refs: set[str] = set()
        for meta in self._columns.values():
            for t in meta.tables:
                if t.get("ref"):
                    refs.add(str(t["ref"]).lower())
        return refs
