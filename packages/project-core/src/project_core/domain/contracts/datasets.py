from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


DatasetFormat = Literal["parquet", "csv", "xlsx"]
SourceKind = Literal["sql", "upload", "artifact", "derived"]


class DatasetManifestEntry(BaseModel):
    ref: str
    path: str
    format: DatasetFormat = "parquet"
    role: str = "main"
    purpose: str | None = None
    source_kind: SourceKind = "sql"
    source_id: str | None = None
    sheet_name: str | None = None
    row_count: int | None = None
    columns: list[str] = Field(default_factory=list)
    byte_size: int | None = None
    sha256: str | None = None


class LineageNode(BaseModel):
    node_id: str
    kind: Literal["source", "dataset", "artifact"]
    ref: str
    parents: list[str] = Field(default_factory=list)
    op_id: str | None = None
    args_hash: str | None = None
    sha256: str | None = None
    row_count: int | None = None
    columns: list[str] = Field(default_factory=list)


class ArtifactRecord(BaseModel):
    artifact_id: str
    path: str
    filename: str
    kind: Literal["file", "csv", "excel", "chart", "image"] = "file"
    media_type: str = "application/octet-stream"
    source_refs: list[str] = Field(default_factory=list)
    sheet_map: dict[str, str] = Field(default_factory=dict)
    size_bytes: int = 0
    sha256: str = ""
    primary: bool = False
    validation_status: Literal["pending", "valid", "invalid"] = "pending"
    validation_issues: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DatasetManifest(BaseModel):
    trace_id: str = ""
    datasets: list[DatasetManifestEntry] = Field(default_factory=list)
    artifact_inputs: list[ArtifactRecord] = Field(default_factory=list)

