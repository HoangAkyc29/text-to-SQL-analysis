"""Form layout primitives — aligned grids, equal columns, no wrap chaos."""
from __future__ import annotations

from typing import Callable

import flet as ft
import pandas as pd

from app import theme
from app.domain.frame_sort import ResultSort
from app.ui.tooltips import as_tooltip, tip_for_field, tip_for_stk


def tip_badge(message: str | None) -> ft.Control | None:
    """Small ⓘ cue so users notice a field has an explanation."""
    tip = as_tooltip(message)
    if tip is None:
        return None
    return ft.Container(
        content=ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=15, color=theme.ACCENT),
        padding=ft.Padding.only(left=2, top=1),
        tooltip=tip,
        ink=True,
        border_radius=10,
    )


def label(text: str, *, tooltip: str | None = None) -> ft.Control:
    tip_msg = tip_for_field(text) if tooltip is None else tooltip
    tip = as_tooltip(tip_msg)
    title = ft.Text(
        text,
        size=13,
        weight=ft.FontWeight.W_700,
        color=theme.TEXT_MUTED,
        tooltip=tip,
    )
    badge = tip_badge(tip_msg)
    if badge is None:
        return title
    return ft.Row(
        [title, badge],
        spacing=4,
        tight=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def field_block(
    caption: str,
    *controls: ft.Control,
    hint: str = "",
    tooltip: str | None = None,
) -> ft.Control:
    """One caption + one row of equal-width controls, vertically centered."""
    tip = tip_for_field(caption) if tooltip is None else tooltip
    head: list[ft.Control] = [label(caption, tooltip=tip)]
    if hint:
        head.append(ft.Text(hint, size=10, color=theme.TEXT_MUTED, tooltip=as_tooltip(tip)))
    cells: list[ft.Control] = []
    for c in controls:
        if hasattr(c, "width"):
            c.width = None  # type: ignore[attr-defined]
        if hasattr(c, "expand"):
            c.expand = True  # type: ignore[attr-defined]
        cells.append(
            ft.Container(
                content=c,
                expand=True,
                alignment=ft.Alignment.CENTER_LEFT,
            )
        )
    return ft.Column(
        [
            ft.Row(head, spacing=8) if hint else head[0],
            ft.Row(
                cells,
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        spacing=6,
    )


def section(title: str, body: ft.Control, *, hint: str = "", tooltip: str | None = None) -> ft.Container:
    tip_msg = tip_for_field(title) if tooltip is None else tooltip
    tip = as_tooltip(tip_msg)
    title_row = ft.Row(
        [
            ft.Text(title, size=13, weight=ft.FontWeight.W_700, color=theme.TEXT, tooltip=tip),
            *([tip_badge(tip_msg)] if tip_msg else []),
        ],
        spacing=6,
        tight=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    head: list[ft.Control] = [title_row]
    if hint:
        head.append(ft.Text(hint, size=11, color=theme.TEXT_MUTED))
    return ft.Container(
        content=ft.Column(
            [
                ft.Column(head, spacing=2),
                ft.Container(height=10),
                body,
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        bgcolor=theme.BG_CARD,
        border=ft.Border.all(1, theme.BORDER),
        border_radius=10,
        padding=ft.Padding.symmetric(horizontal=14, vertical=12),
    )


def chip_toggle(
    text: str,
    *,
    selected: bool = True,
    on_click=None,
    tooltip: str | None = None,
) -> ft.Container:
    state = {"on": selected}
    box = ft.Container(
        content=ft.Text(
            text,
            size=12,
            weight=ft.FontWeight.W_600,
            color="#FFFFFF" if selected else theme.TEXT,
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        border_radius=6,
        ink=True,
        bgcolor=theme.ACCENT if selected else theme.BG_ELEVATED,
        border=ft.Border.all(1, theme.ACCENT if selected else theme.BORDER_STRONG),
        alignment=ft.Alignment.CENTER,
        tooltip=as_tooltip(tooltip),
    )

    def _toggle(_):
        state["on"] = not state["on"]
        box.bgcolor = theme.ACCENT if state["on"] else theme.BG_ELEVATED
        box.border = ft.Border.all(1, theme.ACCENT if state["on"] else theme.BORDER_STRONG)
        if isinstance(box.content, ft.Text):
            box.content.color = "#FFFFFF" if state["on"] else theme.TEXT
        box.update()
        if on_click:
            on_click(state["on"])

    box.on_click = _toggle
    box.data = state
    return box


def stk_chips(*, show_label: bool = False):
    from app.domain.columns import STK_PRESETS

    chips = {s: chip_toggle(s, selected=True, tooltip=tip_for_stk(s)) for s in STK_PRESETS}
    extra = ft.TextField(
        hint_text="Thêm mã siêu thị (phẩy)",
        height=40,
        text_size=13,
        content_padding=10,
        border_width=1.5,
        expand=True,
        tooltip=as_tooltip(tip_for_field("Thêm mã siêu thị (phẩy)")),
        **theme.field_style(),
    )

    def get_ids() -> list[str]:
        ids = [s for s, c in chips.items() if c.data.get("on")]
        if extra.value:
            ids.extend(x.strip() for x in extra.value.split(",") if x.strip())
        seen: set[str] = set()
        out: list[str] = []
        for i in ids:
            if i not in seen:
                seen.add(i)
                out.append(i)
        return out

    parts: list[ft.Control] = []
    if show_label:
        parts.append(label("SIÊU THỊ"))
    parts.append(
        ft.Row(
            list(chips.values()),
            spacing=8,
            wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
    parts.append(extra)
    return ft.Column(parts, spacing=8, horizontal_alignment=ft.CrossAxisAlignment.STRETCH), get_ids


def search_opts_bar():
    """Default-ON: không phân biệt hoa/thường + tìm gần đúng (LIKE %…%)."""
    from app.domain.search_opts import SearchOpts

    case_cb = ft.Checkbox(
        label="Không phân biệt hoa/thường",
        value=True,
        tooltip=as_tooltip(tip_for_field("Không phân biệt hoa/thường")),
    )
    fuzzy_cb = ft.Checkbox(
        label="Tìm gần đúng (chứa chuỗi; tiền tố = bắt đầu bằng)",
        value=True,
        tooltip=as_tooltip(tip_for_field("Tìm gần đúng (chứa chuỗi; tiền tố = bắt đầu bằng)")),
    )
    for cb in (case_cb, fuzzy_cb):
        cb.fill_color = theme.ACCENT
        cb.check_color = "#FFFFFF"
        cb.label_style = ft.TextStyle(size=13, color=theme.TEXT, weight=ft.FontWeight.W_500)
        cb.height = 32

    def get_opts() -> SearchOpts:
        return SearchOpts(
            case_insensitive=bool(case_cb.value),
            fuzzy=bool(fuzzy_cb.value),
        )

    bar = ft.Container(
        content=ft.Column(
            [
                label("CÁCH TÌM"),
                ft.Row(
                    [
                        ft.Container(content=case_cb, expand=True, alignment=ft.Alignment.CENTER_LEFT),
                        ft.Container(content=fuzzy_cb, expand=True, alignment=ft.Alignment.CENTER_LEFT),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=6,
        ),
        padding=ft.Padding.symmetric(horizontal=0, vertical=2),
    )
    return bar, get_opts


def check_grid(items: dict[str, ft.Checkbox], *, cols: int = 2) -> ft.Control:
    """Equal-width columns; short labels recommended in narrow filter panels."""
    boxes = list(items.values())
    for cb in boxes:
        cb.fill_color = theme.ACCENT
        cb.check_color = "#FFFFFF"
        cb.label_style = ft.TextStyle(size=13, color=theme.TEXT, weight=ft.FontWeight.W_500)
        cb.height = 32
        cb.scale = 1.0
        if not getattr(cb, "tooltip", None):
            tip = tip_for_field(getattr(cb, "label", None))
            if tip:
                cb.tooltip = as_tooltip(tip)

    rows: list[ft.Control] = []
    for i in range(0, len(boxes), cols):
        chunk = boxes[i : i + cols]
        cells: list[ft.Control] = [
            ft.Container(
                content=cb,
                expand=True,
                height=34,
                alignment=ft.Alignment.CENTER_LEFT,
                clip_behavior=ft.ClipBehavior.NONE,
            )
            for cb in chunk
        ]
        while len(cells) < cols:
            cells.append(ft.Container(expand=True, height=34))
        rows.append(
            ft.Row(
                cells,
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
    return ft.Column(rows, spacing=4, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)


def dropdown(
    label_text: str,
    value: str,
    options: list[tuple[str, str]],
    *,
    width: int | None = None,
    tooltip: str | None = None,
) -> ft.Dropdown:
    tip = tip_for_field(label_text) if tooltip is None else tooltip
    return ft.Dropdown(
        label=label_text,
        value=value,
        options=[ft.dropdown.Option(k, v) for k, v in options],
        width=width,
        height=44,
        text_size=13,
        content_padding=10,
        border_width=1.5,
        dense=True,
        tooltip=as_tooltip(tip),
        **theme.dropdown_style(),
    )


# Common CARD_ID first letters seen in retail data; user can still type others.
CARD_PREFIX_PRESETS: list[tuple[str, str]] = [
    ("A", "A"),
    ("E", "E"),
    ("F", "F"),
]


def card_prefix_field(
    *,
    label: str = "Tiền tố thẻ",
    value: str = "",
    width: int | None = None,
) -> ft.Dropdown:
    """Dropdown presets + editable free text (gõ tay thêm tiền tố khác)."""
    raw = (value or "").strip()
    opts = [ft.dropdown.Option(key="__none__", text="(không lọc)")]
    seen = {"__none__"}
    for key, text in CARD_PREFIX_PRESETS:
        opts.append(ft.dropdown.Option(key=key, text=text))
        seen.add(key)
    if raw and raw not in seen:
        opts.append(ft.dropdown.Option(key=raw, text=raw))

    dd = ft.Dropdown(
        label=label,
        value="__none__" if not raw else raw,
        options=opts,
        editable=True,
        enable_filter=True,
        hint_text="Chọn A/E/F hoặc gõ tay",
        width=width,
        height=44,
        text_size=13,
        content_padding=10,
        border_width=1.5,
        dense=True,
        tooltip=as_tooltip(tip_for_field(label)),
        error_style=ft.TextStyle(color=theme.DANGER, size=11),
        **theme.dropdown_style(),
    )

    def on_text_change(e: ft.ControlEvent):
        # Keep .value in sync with typed text so validate/copy read correctly.
        typed = (getattr(e.control, "text", None) or e.data or "").strip()
        if typed and typed != "__none__":
            e.control.value = typed

    dd.on_text_change = on_text_change
    return dd


def column_sort_bar(
    *,
    lead: str,
    on_change: Callable[[], None] | None = None,
) -> tuple[ft.Control, ResultSort, Callable[[pd.DataFrame | None], None]]:
    """
    Dropdown sort-by-column (any result column). Sort is client-side only.

    Returns (control, sort_state, refresh_options_from_df).
    """
    sort = ResultSort(lead=lead, ascending=True)
    dd = ft.Dropdown(
        label="Sắp xếp theo cột",
        value=lead,
        options=[ft.dropdown.Option(lead, lead)],
        height=44,
        text_size=13,
        content_padding=10,
        border_width=1.5,
        dense=True,
        tooltip=as_tooltip(tip_for_field("Sắp xếp theo cột")),
        **theme.dropdown_style(),
    )
    dir_label = ft.Text("↑ tăng dần", size=12, color=theme.TEXT_MUTED)

    def _sync_dir_label():
        dir_label.value = "↑ tăng dần" if sort.ascending else "↓ giảm dần"

    def _on_dd(_e):
        col = (dd.value or "").strip()
        if col:
            sort.set_column(col, reset_ascending=True)
            _sync_dir_label()
            if on_change:
                on_change()

    def _toggle_dir(_e):
        sort.ascending = not sort.ascending
        _sync_dir_label()
        if on_change:
            on_change()

    dd.on_change = _on_dd
    dir_btn = ft.TextButton(
        content=dir_label,
        on_click=_toggle_dir,
        tooltip=as_tooltip("Đổi chiều sắp xếp"),
        style=ft.ButtonStyle(padding=ft.Padding.symmetric(horizontal=8, vertical=4)),
    )

    def refresh(df: pd.DataFrame | None) -> None:
        if df is None or df.empty:
            dd.options = [ft.dropdown.Option(sort.lead, sort.lead)]
            dd.value = sort.lead
            sort.column = sort.lead
            _sync_dir_label()
            return
        cols = [str(c) for c in df.columns]
        sort.sync_column_if_needed(df)
        dd.options = [ft.dropdown.Option(c, c) for c in cols]
        dd.value = sort.column if sort.column in cols else (sort.lead if sort.lead in cols else cols[0])
        sort.column = dd.value
        _sync_dir_label()

    bar = ft.Row(
        [ft.Container(content=dd, expand=True), dir_btn],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    return bar, sort, refresh


def page_header(title: str, subtitle: str, *, tooltip: str | None = None) -> ft.Control:
    tip_msg = tip_for_field(title) if tooltip is None else tooltip
    tip = as_tooltip(tip_msg)
    title_row = ft.Row(
        [
            ft.Text(title, size=20, weight=ft.FontWeight.W_800, color=theme.TEXT, tooltip=tip),
            *([tip_badge(tip_msg)] if tip_msg else []),
        ],
        spacing=8,
        tight=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    return ft.Column(
        [
            title_row,
            ft.Text(subtitle, size=12, color=theme.TEXT_MUTED),
        ],
        spacing=2,
    )


def actions_bar(
    *buttons: ft.Control,
    status: ft.Control | None = None,
    cols: int = 2,
) -> ft.Control:
    """Equal-width button grid (no wrap-jumble in narrow filter column)."""
    btns = list(buttons)
    rows: list[ft.Control] = []
    for i in range(0, len(btns), cols):
        chunk = btns[i : i + cols]
        cells: list[ft.Control] = []
        for b in chunk:
            if hasattr(b, "expand"):
                b.expand = True  # type: ignore[attr-defined]
            if hasattr(b, "width"):
                b.width = None  # type: ignore[attr-defined]
            cells.append(ft.Container(content=b, expand=True))
        while len(cells) < cols:
            cells.append(ft.Container(expand=True))
        rows.append(
            ft.Row(
                cells,
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
    body = ft.Column(rows, spacing=8, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
    if status is None:
        return body
    return ft.Column([body, status], spacing=8)


def workspace_split(
    filter_panel: ft.Control,
    result_panel: ft.Control,
    *,
    filter_width: int = 400,
) -> ft.Control:
    """Filter (fixed width) + result (fills rest). Scales with window resize."""
    return ft.Row(
        [
            ft.Container(content=filter_panel, width=filter_width),
            ft.Container(content=result_panel, expand=True),
        ],
        expand=True,
        spacing=16,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )


def result_panel(title: str, body: ft.Control) -> ft.Control:
    return ft.Column(
        [
            ft.Text(title, size=13, weight=ft.FontWeight.W_700, color=theme.TEXT),
            ft.Container(content=body, expand=True),
        ],
        spacing=8,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
