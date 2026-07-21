from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from project_core.domain.contracts.datasets import DatasetManifestEntry
from project_core.domain.contracts.external_source import ExternalSource
from project_core.config.loader import load_project_config
from project_core.tabular.io import read_tabular, sha256_file

logger = logging.getLogger(__name__)


def ingest_file(
    *,
    session_id: str,
    file_name: str,
    content: bytes,
    base_dir: str | Path | None = None,
) -> ExternalSource:
    root = Path(base_dir or os.getenv("ATTACHMENTS_DIR", "data/attachments"))
    if len(content) > 20 * 1024 * 1024:
        raise ValueError("file_too_large")
    file_id = str(uuid4())
    safe_session = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)[:100]
    safe_name = Path(file_name).name
    safe_name = re.sub(r"[^A-Za-z0-9_. -]", "_", safe_name)[:180] or "upload.bin"
    dest_dir = (root / safe_session).resolve()
    resolved_root = root.resolve()
    if resolved_root not in dest_dir.parents and dest_dir != resolved_root:
        raise ValueError("attachment_path_not_allowed")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{file_id}_{safe_name}"
    dest.write_bytes(content)

    suffix = dest.suffix.lower()
    mime = {
        ".txt": "text/plain",
        ".pdf": "application/pdf",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".csv": "text/csv",
        ".parquet": "application/vnd.apache.parquet",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "application/octet-stream")

    text_excerpt = ""
    parquet_path: str | None = None
    schema_profile: dict[str, Any] = {}
    row_count = 0
    datasets: list[DatasetManifestEntry] = []

    if suffix == ".txt":
        text_excerpt = content.decode("utf-8", errors="replace")[:8000]
    elif suffix == ".pdf":
        text_excerpt = _extract_pdf_text(dest)
    elif suffix == ".xls":
        raise ValueError("legacy_xls_not_supported")
    elif suffix in {".xlsx", ".csv", ".parquet"}:
        datasets = _tabular_assets(dest, dest_dir, file_id)
        if datasets:
            parquet_path = datasets[0].path
            row_count = sum(int(d.row_count or 0) for d in datasets)
            schema_profile = {
                "datasets": [
                    {
                        "ref": d.ref,
                        "sheet_name": d.sheet_name,
                        "columns": d.columns,
                        "row_count": d.row_count,
                    }
                    for d in datasets
                ]
            }
    elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        from PIL import Image

        with Image.open(dest) as image:
            image.verify()
        with Image.open(dest) as image:
            schema_profile = {
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "format": image.format,
            }

    return ExternalSource(
        file_id=file_id,
        path=str(dest),
        mime=mime,
        original_name=file_name,
        text_excerpt=text_excerpt,
        parquet_path=parquet_path,
        schema_profile=schema_profile,
        row_count=row_count,
        format=suffix.lstrip("."),
        byte_size=dest.stat().st_size,
        sha256=sha256_file(dest),
        datasets=datasets,
    )


def _extract_pdf_text(path: Path) -> str:
    try:
        import pypdf
    except ImportError:
        logger.warning("pypdf not installed — PDF text excerpt will be empty")
        return ""
    try:
        reader = pypdf.PdfReader(str(path))
        parts = []
        for page in reader.pages[:20]:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)[:8000]
    except Exception:
        return ""


def _tabular_assets(
    path: Path, dest_dir: Path, file_id: str
) -> list[DatasetManifestEntry]:
    suffix = path.suffix.lower()
    sheet_names: list[str | None]
    if suffix == ".xlsx":
        workbook = pd.ExcelFile(path, engine="openpyxl")
        sheet_names = list(workbook.sheet_names)
    else:
        sheet_names = [None]

    assets: list[DatasetManifestEntry] = []
    for index, sheet_name in enumerate(sheet_names):
        fmt = suffix.lstrip(".")
        df = read_tabular(
            path,
            format=fmt,
            sheet_name=sheet_name,
            max_rows=load_project_config().policy.max_rows,
        )
        # Empty workbook sheets are not analytical datasets.
        if len(df) == 0 and len(df.columns) == 0:
            continue
        out = dest_dir / f"{file_id}_{index}.parquet"
        df.to_parquet(out, index=False)
        assets.append(
            DatasetManifestEntry(
                ref=f"upload_{file_id[:8]}_{index}",
                path=str(out),
                format="parquet",
                role="external",
                source_kind="upload",
                source_id=file_id,
                sheet_name=sheet_name,
                row_count=len(df),
                columns=[str(c) for c in df.columns],
                byte_size=out.stat().st_size,
                sha256=sha256_file(out),
            )
        )
    return assets
