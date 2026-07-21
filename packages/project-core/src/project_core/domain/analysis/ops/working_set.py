"""In-memory / spilled parquet working set for Agent IV ops."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import mimetypes
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from project_core.domain.contracts.datasets import ArtifactRecord, LineageNode
from project_core.tabular.io import read_tabular, sha256_file


@dataclass
class DatasetHandle:
    ref: str
    path: str | None = None
    role: str | None = None
    purpose: str | None = None
    format: str | None = None
    sheet_name: str | None = None
    df: pd.DataFrame | None = field(default=None, repr=False)
    meta: dict[str, Any] = field(default_factory=dict)

    def frame(self) -> pd.DataFrame:
        if self.df is not None:
            return self.df
        if not self.path:
            raise FileNotFoundError(f"dataset {self.ref} has no path or frame")
        p = Path(self.path)
        if not p.exists():
            raise FileNotFoundError(f"dataset {self.ref} missing path={self.path}")
        self.df = read_tabular(
            p,
            format=self.format,
            sheet_name=self.sheet_name,
        )
        return self.df

    def profile(self, *, sample_n: int = 5) -> dict[str, Any]:
        try:
            df = self.frame()
        except Exception as exc:  # noqa: BLE001
            return {"ref": self.ref, "role": self.role, "error": str(exc)}
        cols = [str(c) for c in df.columns]
        dtypes = {str(c): str(df[c].dtype) for c in df.columns}
        null_frac = {
            str(c): float(df[c].isna().mean()) if len(df) else 0.0 for c in df.columns
        }
        sample = df.head(sample_n).astype(object).where(pd.notnull(df.head(sample_n)), None)
        return {
            "ref": self.ref,
            "role": self.role,
            "purpose": self.purpose,
            "path": self.path,
            "format": self.format or Path(self.path or "").suffix.lstrip(".").lower(),
            "sheet_name": self.sheet_name,
            "row_count": int(len(df)),
            "columns": cols,
            "dtypes": dtypes,
            "null_frac": null_frac,
            "sample": sample.to_dict(orient="records"),
            **({k: v for k, v in self.meta.items() if k not in {"df"}}),
        }


class DatasetWorkingSet:
    """Named datasets for one IV analysis session."""

    def __init__(self, *, work_dir: str | Path | None = None) -> None:
        self._datasets: dict[str, DatasetHandle] = {}
        self.work_dir = Path(work_dir) if work_dir else None
        if self.work_dir is not None:
            self.work_dir.mkdir(parents=True, exist_ok=True)
        self.artifact_paths: list[str] = []
        self.chart_artifacts: list[str] = []
        self.excel_artifacts: list[str] = []
        self.primary_artifacts: list[str] = []
        self.artifacts: dict[str, ArtifactRecord] = {}
        self.sources: dict[str, DatasetHandle] = {}
        self.lineage: dict[str, LineageNode] = {}
        self.revision: int = 0
        self.output_root: Path | None = None
        self.allowed_roots: list[Path] = []
        if self.work_dir is not None:
            self.allowed_roots.append(self.work_dir.resolve().parent)

    @classmethod
    def from_manifest(
        cls,
        manifest: dict[str, Any],
        query_meta: list[dict[str, Any]] | None = None,
        *,
        work_dir: str | Path | None = None,
    ) -> DatasetWorkingSet:
        ws = cls(work_dir=work_dir)
        meta = list(query_meta or [])
        for idx, q in enumerate(manifest.get("queries") or []):
            path = q.get("path")
            if not path:
                continue
            m = meta[idx] if idx < len(meta) else {}
            ref = str(q.get("ref") or f"q{idx}")
            ws.put(
                DatasetHandle(
                    ref=ref,
                    path=str(path),
                    role=m.get("role") or q.get("role"),
                    purpose=m.get("purpose") or q.get("purpose"),
                    format=q.get("format"),
                    sheet_name=q.get("sheet_name"),
                    meta={"query_index": idx, "row_count": q.get("row_count")},
                )
            )
            ws.sources[ref] = ws._datasets[ref]
            ws.lineage[ref] = LineageNode(
                node_id=ref,
                kind="source",
                ref=ref,
                row_count=q.get("row_count"),
                columns=list(q.get("columns") or []),
            )
            # Also alias by index for LLM convenience
            if ref != f"q{idx}":
                ws._datasets[f"q{idx}"] = ws._datasets[ref]
        return ws

    def put(self, handle: DatasetHandle) -> None:
        self._datasets[handle.ref] = handle

    def set_output_root(self, root: str | Path) -> None:
        resolved = Path(root).resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        self.output_root = resolved
        if resolved not in self.allowed_roots:
            self.allowed_roots.append(resolved)

    def register_allowed_source(self, ref: str, handle: DatasetHandle) -> None:
        path = Path(handle.path or "").resolve()
        if path.parent not in self.allowed_roots:
            self.allowed_roots.append(path.parent)
        self.sources[ref] = handle
        self.put(handle)

    def get(self, ref: str) -> DatasetHandle:
        if ref not in self._datasets:
            raise KeyError(f"unknown_dataset:{ref}")
        return self._datasets[ref]

    def has(self, ref: str) -> bool:
        return ref in self._datasets

    def refs(self) -> list[str]:
        # Deduplicate aliases that point to same object
        seen: set[int] = set()
        out: list[str] = []
        for ref, h in self._datasets.items():
            oid = id(h)
            if oid in seen and not ref.startswith("q"):
                continue
            if oid in seen:
                continue
            seen.add(oid)
            out.append(ref)
        return out

    def list_profiles(self) -> list[dict[str, Any]]:
        seen: set[int] = set()
        out: list[dict[str, Any]] = []
        for ref, h in self._datasets.items():
            if id(h) in seen:
                continue
            seen.add(id(h))
            out.append(h.profile())
        return out

    def save_frame(
        self,
        ref: str,
        df: pd.DataFrame,
        *,
        role: str | None = None,
        purpose: str | None = None,
        source: str | None = None,
        parents: list[str] | None = None,
        op_id: str | None = None,
        op_args: dict[str, Any] | None = None,
    ) -> DatasetHandle:
        path: str | None = None
        if self.work_dir is not None:
            safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in ref)[:80]
            path = str(self.work_dir / f"{safe}.parquet")
            df.to_parquet(path, index=False)
        handle = DatasetHandle(
            ref=ref,
            path=path,
            role=role,
            purpose=purpose,
            df=df,
            meta={"source": source} if source else {},
        )
        self.put(handle)
        self.revision += 1
        args_hash = None
        if op_args:
            args_hash = hashlib.sha256(
                json.dumps(op_args, sort_keys=True, default=str).encode("utf-8")
            ).hexdigest()
        self.lineage[ref] = LineageNode(
            node_id=ref,
            kind="dataset",
            ref=ref,
            parents=list(parents or ([source] if source else [])),
            op_id=op_id or source,
            args_hash=args_hash,
            row_count=len(df),
            columns=[str(c) for c in df.columns],
        )
        return handle

    def register_artifact(
        self,
        path: str,
        *,
        kind: str = "file",
        primary: bool = False,
        source_refs: list[str] | None = None,
        sheet_map: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
        validated: bool = False,
    ) -> ArtifactRecord:
        resolved = Path(path).resolve()
        if self.output_root is not None:
            try:
                resolved.relative_to(self.output_root)
            except ValueError as exc:
                raise ValueError("artifact_path_not_allowed") from exc
        if not resolved.exists() or not resolved.is_file() or resolved.is_symlink():
            raise ValueError("artifact_missing_or_unsafe")
        from project_core.config.loader import load_project_config

        max_bytes = int(load_project_config().artifacts.max_bytes_per_trace)
        current_bytes = sum(a.size_bytes for a in self.artifacts.values())
        if current_bytes + resolved.stat().st_size > max_bytes:
            resolved.unlink(missing_ok=True)
            raise ValueError("artifact_quota_exceeded")
        p = str(resolved)
        if p not in self.artifact_paths:
            self.artifact_paths.append(p)
        if kind == "chart" and p not in self.chart_artifacts:
            self.chart_artifacts.append(p)
        if kind == "excel" and p not in self.excel_artifacts:
            self.excel_artifacts.append(p)
        if primary and p not in self.primary_artifacts:
            self.primary_artifacts.append(p)
        media_type = mimetypes.guess_type(resolved.name)[0] or "application/octet-stream"
        normalized_kind = {
            "file": "file",
            "excel": "excel",
            "chart": "chart",
            "image": "image",
            "csv": "csv",
        }.get(kind, "file")
        record = ArtifactRecord(
            artifact_id=str(uuid4()),
            path=p,
            filename=resolved.name,
            kind=normalized_kind,  # type: ignore[arg-type]
            media_type=media_type,
            source_refs=list(source_refs or []),
            sheet_map=dict(sheet_map or {}),
            size_bytes=resolved.stat().st_size,
            sha256=sha256_file(resolved),
            primary=primary,
            validation_status="valid" if validated else "pending",
            metadata=dict(metadata or {}),
        )
        self.artifacts[record.artifact_id] = record
        self.lineage[record.artifact_id] = LineageNode(
            node_id=record.artifact_id,
            kind="artifact",
            ref=record.filename,
            parents=list(source_refs or []),
            sha256=record.sha256,
            row_count=(metadata or {}).get("row_count"),
            columns=list((metadata or {}).get("columns") or []),
        )
        return record

    def artifact_for_path(self, path: str) -> ArtifactRecord | None:
        resolved = str(Path(path).resolve())
        return next((a for a in self.artifacts.values() if a.path == resolved), None)

    def get_artifact(self, artifact_id: str) -> ArtifactRecord:
        if artifact_id not in self.artifacts:
            raise KeyError(f"unknown_artifact:{artifact_id}")
        return self.artifacts[artifact_id]
