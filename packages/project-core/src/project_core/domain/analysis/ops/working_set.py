"""In-memory / spilled parquet working set for Agent IV ops."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class DatasetHandle:
    ref: str
    path: str | None = None
    role: str | None = None
    purpose: str | None = None
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
        if p.suffix.lower() == ".parquet":
            self.df = pd.read_parquet(p)
        else:
            self.df = pd.read_csv(p)
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
                    meta={"query_index": idx, "row_count": q.get("row_count")},
                )
            )
            # Also alias by index for LLM convenience
            if ref != f"q{idx}":
                ws._datasets[f"q{idx}"] = ws._datasets[ref]
        return ws

    def put(self, handle: DatasetHandle) -> None:
        self._datasets[handle.ref] = handle

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
        return handle

    def register_artifact(self, path: str, *, kind: str = "file", primary: bool = False) -> None:
        p = str(path)
        if p not in self.artifact_paths:
            self.artifact_paths.append(p)
        if kind == "chart" and p not in self.chart_artifacts:
            self.chart_artifacts.append(p)
        if kind == "excel" and p not in self.excel_artifacts:
            self.excel_artifacts.append(p)
        if primary and p not in self.primary_artifacts:
            self.primary_artifacts.append(p)
