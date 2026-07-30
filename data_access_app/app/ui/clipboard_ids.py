"""Copy unique ID columns from result DataFrames → clipboard (cross-feature paste)."""
from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from typing import Any

import flet as ft
import pandas as pd

from app import theme


def unique_column_values(df: pd.DataFrame | None, column: str) -> list[str]:
    """Distinct non-empty string values, first-seen order."""
    if df is None or df.empty or column not in df.columns:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for v in df[column].tolist():
        if v is None or (isinstance(v, float) and pd.isna(v)):
            continue
        s = str(v).strip()
        if not s or s.lower() == "nan":
            continue
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def format_id_list(ids: list[str]) -> str:
    """Newline-separated — paste vào TextField multiline (F4 thẻ / F5 SP)."""
    return "\n".join(ids)


def _windows_clip(text: str) -> bool:
    try:
        flags = 0
        if sys.platform == "win32":
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        proc = subprocess.run(
            ["clip"],
            input=text.encode("utf-16le"),
            check=False,
            creationflags=flags,
        )
        return proc.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def copy_text_to_clipboard(page: Any, text: str, *, on_done: Callable[[bool], None] | None = None) -> None:
    """Async Flet clipboard when available; Windows `clip` fallback."""

    def _finish(ok: bool) -> None:
        if on_done:
            on_done(ok)

    async def _via_flet() -> None:
        ok = False
        try:
            clip = getattr(page, "clipboard", None)
            if clip is not None and hasattr(clip, "set"):
                await clip.set(text)
                ok = True
        except Exception:  # noqa: BLE001
            ok = False
        if not ok:
            ok = _windows_clip(text)
        _finish(ok)

    if page is not None and hasattr(page, "run_task"):
        try:
            page.run_task(_via_flet)
            return
        except Exception:  # noqa: BLE001
            pass
    _finish(_windows_clip(text))


def copy_ids_button(
    page: ft.Page,
    *,
    get_df: Callable[[], pd.DataFrame | None],
    column: str,
    label: str,
    status: ft.Text | None = None,
    noun: str | None = None,
) -> ft.OutlinedButton:
    """Secondary button: copy unique `column` values from latest result df."""
    label_noun = noun or column

    def on_click(_):
        ids = unique_column_values(get_df(), column)
        if not ids:
            if status is not None:
                status.value = f"Không có {label_noun} để copy — chạy tìm/xem trước trước"
                status.color = theme.WARN
                page.update()
            return

        text = format_id_list(ids)

        def done(ok: bool) -> None:
            if status is not None:
                if ok:
                    status.value = f"Đã copy {len(ids)} {label_noun} → clipboard (Ctrl+V sang chức năng khác)"
                    status.color = theme.SUCCESS
                else:
                    status.value = "Copy clipboard thất bại"
                    status.color = theme.DANGER
            page.update()

        copy_text_to_clipboard(page, text, on_done=done)

    return theme.secondary_button(label, on_click=on_click, icon=ft.Icons.CONTENT_COPY)
