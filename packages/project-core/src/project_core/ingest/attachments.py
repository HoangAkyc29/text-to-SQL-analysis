from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from project_core.domain.contracts.external_source import ExternalSource


def ingest_file(
    *,
    session_id: str,
    file_name: str,
    content: bytes,
    base_dir: str | Path | None = None,
) -> ExternalSource:
    root = Path(base_dir or os.getenv("ATTACHMENTS_DIR", "data/attachments"))
    file_id = str(uuid4())
    dest_dir = root / session_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{file_id}_{file_name}"
    dest.write_bytes(content)

    suffix = dest.suffix.lower()
    mime = {
        ".txt": "text/plain",
        ".pdf": "application/pdf",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".csv": "text/csv",
    }.get(suffix, "application/octet-stream")

    text_excerpt = ""
    parquet_path: str | None = None
    schema_profile: dict[str, Any] = {}
    row_count = 0

    if suffix == ".txt":
        text_excerpt = content.decode("utf-8", errors="replace")[:8000]
    elif suffix == ".pdf":
        text_excerpt = _extract_pdf_text(dest)
    elif suffix in {".xlsx", ".xls", ".csv"}:
        parquet_path, schema_profile, row_count = _tabular_to_parquet(dest, dest_dir, file_id)

    return ExternalSource(
        file_id=file_id,
        path=str(dest),
        mime=mime,
        original_name=file_name,
        text_excerpt=text_excerpt,
        parquet_path=parquet_path,
        schema_profile=schema_profile,
        row_count=row_count,
    )


def _extract_pdf_text(path: Path) -> str:
    try:
        import pypdf

        reader = pypdf.PdfReader(str(path))
        parts = []
        for page in reader.pages[:20]:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)[:8000]
    except Exception:
        return ""


def _tabular_to_parquet(path: Path, dest_dir: Path, file_id: str) -> tuple[str, dict[str, Any], int]:
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path, nrows=50000)
    else:
        df = pd.read_excel(path, nrows=50000)
    out = dest_dir / f"{file_id}.parquet"
    df.to_parquet(out, index=False)
    profile = {
        "columns": [{"name": str(c), "dtype": str(df[c].dtype)} for c in df.columns],
        "sample_rows": json.loads(df.head(5).to_json(orient="records", force_ascii=False)),
    }
    return str(out), profile, len(df)
