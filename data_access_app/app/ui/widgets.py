"""Form field helpers — stronger borders, consistent height."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Callable

import flet as ft
import pandas as pd

from app import theme
from app.domain.columns import STK_PRESETS
from app.ui import form_kit
from app.ui.tooltips import as_tooltip, column_header_tooltip, tip_for_field

PREVIEW_MAX_ROWS = 40
PREVIEW_MAX_COLS = 10


def df_to_datatable(
    df: pd.DataFrame,
    max_rows: int = PREVIEW_MAX_ROWS,
    *,
    sort_column: str | None = None,
    sort_ascending: bool = True,
    on_header_click: Callable[[str], None] | None = None,
) -> ft.Control:
    if df is None or df.empty:
        return ft.Container(
            content=ft.Text("Chưa có dữ liệu preview", color=theme.TEXT_MUTED, size=13),
            padding=20,
            alignment=ft.Alignment.CENTER,
        )

    view = df.iloc[:max_rows, :PREVIEW_MAX_COLS]
    cols = [str(c) for c in view.columns]

    def _header_cell(c: str) -> ft.Control:
        mark = ""
        if sort_column and c == sort_column:
            mark = " ↑" if sort_ascending else " ↓"
        tip = column_header_tooltip(c, sortable=bool(on_header_click))
        label = ft.Text(
            f"{c}{mark}",
            size=11,
            weight=ft.FontWeight.W_700,
            color=theme.ACCENT if mark else theme.ACCENT_DIM,
            no_wrap=True,
        )
        cell_body: ft.Control = label
        if tip is not None:
            cell_body = ft.Row(
                [
                    label,
                    ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=11, color=theme.ACCENT),
                ],
                spacing=2,
                tight=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        box = ft.Container(
            cell_body,
            width=118,
            padding=ft.Padding.symmetric(horizontal=6, vertical=8),
            ink=bool(on_header_click),
            tooltip=tip,
            bgcolor=theme.ACCENT_SOFT if tip is not None else None,
            border_radius=4,
        )
        if on_header_click:

            def _click(_e, col=c):
                on_header_click(col)

            box.on_click = _click
        return box

    header = ft.Row([_header_cell(c) for c in cols], spacing=0)
    rows: list[ft.Control] = [
        ft.Container(
            header,
            bgcolor=theme.BG_ELEVATED,
            border=ft.Border.only(bottom=ft.BorderSide(1, theme.BORDER_STRONG)),
        )
    ]
    for i, row in enumerate(view.itertuples(index=False, name=None)):
        bg = theme.BG_PANEL if i % 2 == 0 else "#F8FAFC"
        cells = []
        for val in row:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                text = ""
            else:
                text = str(val)
            if len(text) > 34:
                text = text[:31] + "…"
            cells.append(
                ft.Container(
                    ft.Text(text, size=11, color=theme.TEXT, no_wrap=True),
                    width=118,
                    padding=ft.Padding.symmetric(horizontal=6, vertical=6),
                )
            )
        rows.append(ft.Container(ft.Row(cells, spacing=0), bgcolor=bg))

    note = None
    if len(df) > max_rows or df.shape[1] > PREVIEW_MAX_COLS:
        note = ft.Text(
            f"Preview {min(len(df), max_rows)}/{len(df)} dòng · "
            f"{min(df.shape[1], PREVIEW_MAX_COLS)}/{df.shape[1]} cột",
            size=11,
            color=theme.TEXT_MUTED,
        )
    body: list[ft.Control] = []
    if note:
        body.append(note)
    body.append(
        ft.Container(
            content=ft.Column(rows, spacing=0, scroll=ft.ScrollMode.AUTO),
            border=ft.Border.all(1, theme.BORDER_STRONG),
            border_radius=8,
            height=min(340, 52 + 26 * len(rows)),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )
    )
    return ft.Column(body, spacing=6)


def text_field(
    label: str,
    *,
    multiline: bool = False,
    width: int | None = None,
    value: str = "",
    hint: str = "",
    tooltip: str | None = None,
) -> ft.TextField:
    tip = tip_for_field(label) if tooltip is None else tooltip
    return ft.TextField(
        label=label,
        value=value,
        hint_text=hint or None,
        width=width,
        height=None if multiline else 44,
        multiline=multiline,
        min_lines=3 if multiline else 1,
        max_lines=5 if multiline else 1,
        text_size=13,
        content_padding=10,
        border_width=1.5,
        dense=True,
        tooltip=as_tooltip(tip),
        error_style=ft.TextStyle(color=theme.DANGER, size=11),
        **theme.field_style(),
    )


def unwrap_date_field(ctrl: ft.Control) -> ft.TextField:
    """date_field() may return a Column wrapping the TextField (legacy) or TextField."""
    if isinstance(ctrl, ft.TextField):
        return ctrl
    data = getattr(ctrl, "data", None) or {}
    inner = data.get("field")
    if isinstance(inner, ft.TextField):
        return inner
    raise TypeError(f"Expected date TextField, got {type(ctrl)!r}")


def date_field_value(ctrl: ft.Control) -> str:
    return unwrap_date_field(ctrl).value or ""


_DATE_CAL_TAG = "date_cal_overlay"
_CELL = 34
_GAP = 4
_CAL_PAD = 12
_CAL_WIDTH = 7 * _CELL + 6 * _GAP + 2 * _CAL_PAD  # ~286


def _dismiss_date_calendars(page: ft.Page | None) -> None:
    if page is None:
        return
    kept: list[ft.Control] = []
    for c in list(page.overlay):
        if getattr(c, "data", None) == _DATE_CAL_TAG:
            continue
        kept.append(c)
    page.overlay.clear()
    page.overlay.extend(kept)


def date_field(
    label: str,
    value: date | None = None,
    *,
    width: int | None = None,
    tooltip: str | None = None,
) -> ft.TextField:
    """Date text field; calendar icon opens a floating popover (overlay, dismiss on outside click)."""
    v = value or date.today()
    tip = tip_for_field(label) if tooltip is None else tooltip
    field = ft.TextField(
        label=label,
        value=v.isoformat(),
        hint_text="YYYY-MM-DD",
        width=width,
        height=44,
        text_size=13,
        content_padding=10,
        border_width=1.5,
        dense=True,
        tooltip=as_tooltip(tip),
        error_style=ft.TextStyle(color=theme.DANGER, size=11),
        **theme.field_style(),
    )

    state = {"month": date(v.year, v.month, 1), "page": None}
    month_label = ft.Text(
        "",
        size=13,
        weight=ft.FontWeight.W_600,
        color=theme.TEXT,
        no_wrap=True,
        text_align=ft.TextAlign.CENTER,
    )
    grid_host = ft.Column(spacing=_GAP, tight=True)

    def _current() -> date:
        raw = (field.value or "").strip()
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            return date.today()

    def _close():
        _dismiss_date_calendars(state["page"] or field.page)
        if field.page:
            field.page.update()

    def _apply(d: date):
        field.value = d.isoformat()
        field.error_text = None
        field.border_color = theme.BORDER_STRONG
        field.focused_border_color = theme.ACCENT
        _close()

    def _shift_month(delta: int):
        m = state["month"]
        y, mo = m.year, m.month + delta
        while mo < 1:
            mo += 12
            y -= 1
        while mo > 12:
            mo -= 12
            y += 1
        state["month"] = date(y, mo, 1)
        _rebuild()
        if field.page:
            field.page.update()

    def _rebuild():
        selected = _current()
        cursor = state["month"]
        month_label.value = f"{cursor.month:02d}/{cursor.year}"
        headers = ft.Row(
            [
                ft.Container(
                    content=ft.Text(h, size=11, color=theme.TEXT_MUTED, text_align=ft.TextAlign.CENTER, no_wrap=True),
                    width=_CELL,
                    alignment=ft.Alignment.CENTER,
                )
                for h in ("T2", "T3", "T4", "T5", "T6", "T7", "CN")
            ],
            spacing=_GAP,
        )
        first_wd = cursor.weekday()  # Mon=0
        if cursor.month == 12:
            next_month = date(cursor.year + 1, 1, 1)
        else:
            next_month = date(cursor.year, cursor.month + 1, 1)
        days_in_month = (next_month - timedelta(days=1)).day
        cells: list[ft.Control] = [ft.Container(width=_CELL, height=_CELL) for _ in range(first_wd)]
        today = date.today()
        for day in range(1, days_in_month + 1):
            d = date(cursor.year, cursor.month, day)
            is_sel = d == selected
            is_today = d == today
            bg = theme.ACCENT if is_sel else (theme.ACCENT_SOFT if is_today else None)
            fg = "#FFFFFF" if is_sel else theme.TEXT

            def _on_click(_e, picked=d):
                _apply(picked)

            cells.append(
                ft.Container(
                    content=ft.Text(str(day), size=12, color=fg, text_align=ft.TextAlign.CENTER),
                    width=_CELL,
                    height=_CELL,
                    alignment=ft.Alignment.CENTER,
                    bgcolor=bg,
                    border_radius=8,
                    on_click=_on_click,
                    ink=True,
                )
            )
        rows: list[ft.Control] = [headers]
        for i in range(0, len(cells), 7):
            chunk = cells[i : i + 7]
            while len(chunk) < 7:
                chunk.append(ft.Container(width=_CELL, height=_CELL))
            rows.append(ft.Row(chunk, spacing=_GAP))
        grid_host.controls = rows

    def _panel() -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_LEFT_ROUNDED,
                                icon_size=18,
                                on_click=lambda e: _shift_month(-1),
                                style=ft.ButtonStyle(padding=4),
                                tooltip=as_tooltip("Tháng trước"),
                            ),
                            ft.Container(
                                content=month_label,
                                expand=True,
                                alignment=ft.Alignment.CENTER,
                                height=32,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_RIGHT_ROUNDED,
                                icon_size=18,
                                on_click=lambda e: _shift_month(1),
                                style=ft.ButtonStyle(padding=4),
                                tooltip=as_tooltip("Tháng sau"),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE_ROUNDED,
                                icon_size=16,
                                on_click=lambda e: _close(),
                                style=ft.ButtonStyle(padding=4),
                                tooltip=as_tooltip("Đóng"),
                            ),
                        ],
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    grid_host,
                ],
                spacing=6,
                tight=True,
            ),
            bgcolor="#FFFFFF",
            border=ft.Border.all(1, theme.BORDER_STRONG),
            border_radius=10,
            padding=_CAL_PAD,
            width=_CAL_WIDTH,
            shadow=ft.BoxShadow(
                blur_radius=14,
                spread_radius=0,
                color="#15203328",
                offset=ft.Offset(0, 4),
            ),
            # swallow clicks so barrier behind doesn't receive them
            on_click=lambda e: None,
        )

    def _open(e: ft.ControlEvent):
        page = e.page
        if page is None:
            return
        state["page"] = page
        _dismiss_date_calendars(page)

        cur = _current()
        state["month"] = date(cur.year, cur.month, 1)
        _rebuild()
        panel = _panel()

        # Prefer tap coordinates; fall back under typical filter column
        left, top = 24.0, 120.0
        gpos = getattr(e, "global_position", None)
        if gpos is not None:
            left = float(getattr(gpos, "x", left) or left) - 20
            top = float(getattr(gpos, "y", top) or top) + 12
        # Keep on-screen if page size known
        pw = float(page.width or 0)
        ph = float(page.height or 0)
        if pw > 0:
            left = max(8.0, min(left, pw - _CAL_WIDTH - 8))
        if ph > 0:
            top = max(8.0, min(top, ph - 320))

        barrier = ft.Container(
            expand=True,
            bgcolor="#00000000",
            on_click=lambda _e: _close(),
        )
        layer = ft.Stack(
            [
                barrier,
                ft.Container(content=panel, left=left, top=top),
            ],
            expand=True,
        )
        layer.data = _DATE_CAL_TAG
        page.overlay.append(layer)
        page.update()

    # GestureDetector gives TapEvent.global_position for placement
    field.suffix = ft.GestureDetector(
        content=ft.Container(
            content=ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=18, color=theme.TEXT_MUTED),
            padding=6,
            border_radius=6,
            ink=True,
        ),
        on_tap=_open,
    )
    field.data = {"field": field}
    return field


def parse_date(field: ft.Control) -> date:
    return datetime.strptime(unwrap_date_field(field).value.strip(), "%Y-%m-%d").date()



def default_range() -> tuple[date, date]:
    end = date.today()
    start = end - timedelta(days=30)
    return start, end


def stk_selector() -> tuple[ft.Control, Callable[[], list[str]]]:
    # Prefer chip UI from form_kit
    return form_kit.stk_chips()


def status_bar() -> ft.Text:
    return ft.Text("", color=theme.TEXT_MUTED, size=12)


def apply_search_result_status(
    status: ft.Text,
    df: pd.DataFrame,
    *,
    noun: str = "dòng",
) -> None:
    """Set status text/color; warn when master search hit TOP cap."""
    n = len(df) if df is not None else 0
    attrs = getattr(df, "attrs", {}) or {}
    if attrs.get("truncated"):
        lim = attrs.get("limit")
        status.value = f"OK — {n} {noun} (đã cắt TOP {lim}, còn nhiều hơn — thu hẹp điều kiện)"
        status.color = theme.WARN
    else:
        status.value = f"OK — {n} {noun}"
        status.color = theme.SUCCESS


def loading_row(message: str = "Đang tải…") -> ft.Control:
    return ft.Row(
        [
            ft.ProgressRing(width=18, height=18, stroke_width=2, color=theme.ACCENT),
            ft.Text(message, color=theme.TEXT_MUTED, size=13),
        ],
        spacing=10,
    )


# keep STK_PRESETS import used for typing/tools
_ = STK_PRESETS
