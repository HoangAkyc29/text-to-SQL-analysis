"""Native folder picker for export (opened when user clicks Xuất)."""
from __future__ import annotations

import os
import re
from pathlib import Path

import flet as ft

from app.config import APP_ROOT, settings

_PICKER_TAG = "data_access_file_picker"


def ensure_file_picker(page: ft.Page) -> ft.FilePicker:
    """One FilePicker per page — strong ref so ServiceRegistry does not GC it."""
    existing = getattr(page, "_da_file_picker", None)
    if isinstance(existing, ft.FilePicker):
        return existing
    picker = ft.FilePicker()
    picker.data = _PICKER_TAG
    page._da_file_picker = picker  # type: ignore[attr-defined]
    return picker


def remember_output_dir(path: Path) -> Path:
    """Remember last chosen folder (initial dir next time + optional .env)."""
    path = path.expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    settings.output_dir = path
    os.environ["DATA_ACCESS_OUTPUT_DIR"] = str(path)
    env_path = APP_ROOT / ".env"
    line = f"DATA_ACCESS_OUTPUT_DIR={path}"
    if env_path.exists():
        text = env_path.read_text(encoding="utf-8")
        if re.search(r"(?m)^DATA_ACCESS_OUTPUT_DIR=", text):
            text = re.sub(r"(?m)^DATA_ACCESS_OUTPUT_DIR=.*$", line, text)
        else:
            text = text.rstrip() + "\n" + line + "\n"
        env_path.write_text(text, encoding="utf-8")
    else:
        env_path.write_text(line + "\n", encoding="utf-8")
    return path


async def pick_export_directory(
    page: ft.Page,
    *,
    title: str = "Chọn thư mục lưu file xuất",
) -> Path | None:
    """
    Open OS folder dialog. Returns chosen path, or None if cancelled / unsupported.
    Remembers choice for the next dialog's initial directory.
    """
    if getattr(page, "web", False):
        return None
    picker = ensure_file_picker(page)
    start = settings.output_dir
    try:
        start_s = str(start) if start and Path(start).exists() else str(APP_ROOT / "output")
    except OSError:
        start_s = str(APP_ROOT / "output")
    chosen = await picker.get_directory_path(dialog_title=title, initial_directory=start_s)
    if not chosen:
        return None
    return remember_output_dir(Path(chosen))
