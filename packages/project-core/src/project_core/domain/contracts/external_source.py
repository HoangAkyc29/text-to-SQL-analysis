from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExternalSource(BaseModel):
    file_id: str
    path: str
    mime: str = ""
    original_name: str = ""
    text_excerpt: str = ""
    parquet_path: str | None = None
    schema_profile: dict[str, Any] = Field(default_factory=dict)
    row_count: int = 0
