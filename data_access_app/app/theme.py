"""Light visual theme — clear hierarchy, teal accent (not dark-first)."""
from __future__ import annotations

import flet as ft

# Light palette
BG_DEEP = "#F3F5F8"
BG_PANEL = "#FFFFFF"
BG_CARD = "#FFFFFF"
BG_ELEVATED = "#F7F9FC"
BG_HOVER = "#EEF6F4"
BORDER = "#D8DEE8"
BORDER_STRONG = "#B8C2D0"
TEXT = "#152033"
TEXT_MUTED = "#5B6B82"
ACCENT = "#0D9488"
ACCENT_DIM = "#0F766E"
ACCENT_SOFT = "#CCFBF1"
WARN = "#B45309"
DANGER = "#DC2626"
SUCCESS = "#059669"

FONT_FAMILY = "Segoe UI"


def page_defaults(page: ft.Page) -> None:
    page.title = "Data Access — Supermarket"
    page.bgcolor = BG_DEEP
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window.min_width = 1100
    page.window.min_height = 720
    page.theme = ft.Theme(
        color_scheme_seed=ACCENT,
        font_family=FONT_FAMILY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )


def card(*, content: ft.Control, expand: bool = False, padding: int = 20) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=BG_CARD,
        border=ft.Border.all(1, BORDER),
        border_radius=12,
        padding=padding,
        expand=expand,
        width=None,
        alignment=ft.Alignment.TOP_LEFT if not expand else None,
        shadow=ft.BoxShadow(
            blur_radius=10,
            spread_radius=0,
            color="#15203314",
            offset=ft.Offset(0, 2),
        ),
    )


def section_title(text: str, subtitle: str = "") -> ft.Control:
    controls: list[ft.Control] = [
        ft.Text(text, size=24, weight=ft.FontWeight.W_700, color=TEXT),
    ]
    if subtitle:
        controls.append(ft.Text(subtitle, size=13, color=TEXT_MUTED))
    return ft.Column(controls, spacing=4)


def primary_button(label: str, on_click=None, icon=None) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        label,
        icon=icon,
        on_click=on_click,
        bgcolor=ACCENT,
        color="#FFFFFF",
        height=42,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            elevation=0,
        ),
    )


def secondary_button(label: str, on_click=None, icon=None) -> ft.OutlinedButton:
    return ft.OutlinedButton(
        label,
        icon=icon,
        on_click=on_click,
        height=42,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            side=ft.BorderSide(1, BORDER_STRONG),
            color=TEXT,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        ),
    )


def field_style() -> dict:
    """TextField-safe style (includes cursor_color)."""
    return {
        "bgcolor": "#FFFFFF",
        "border_color": BORDER_STRONG,
        "focused_border_color": ACCENT,
        "color": TEXT,
        "cursor_color": ACCENT,
        "label_style": ft.TextStyle(color=TEXT_MUTED, size=12),
        "border_radius": 8,
    }


def dropdown_style() -> dict:
    """Dropdown-safe style (no cursor_color — Flet rejects it)."""
    return {
        "bgcolor": "#FFFFFF",
        "border_color": BORDER_STRONG,
        "focused_border_color": ACCENT,
        "color": TEXT,
        "label_style": ft.TextStyle(color=TEXT_MUTED, size=12),
        "border_radius": 8,
    }
