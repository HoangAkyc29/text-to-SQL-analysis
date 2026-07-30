"""App shell — sidebar + content that fills the window on resize."""
from __future__ import annotations

import flet as ft

from app import theme

NAV = [
    ("home", "Tổng quan", ft.Icons.HOME_ROUNDED),
    ("product", "Tìm mặt hàng", ft.Icons.INVENTORY_2_ROUNDED),
    ("customer", "Tìm khách", ft.Icons.PERSON_ROUNDED),
    ("loyalty", "KH theo kỳ", ft.Icons.CARD_MEMBERSHIP_ROUNDED),
    ("cust_orders", "Đơn theo khách", ft.Icons.RECEIPT_LONG_ROUNDED),
    ("prod_orders", "Đơn theo SP", ft.Icons.SHOPPING_BAG_ROUNDED),
    ("group", "SP theo nhóm", ft.Icons.CATEGORY_ROUNDED),
    ("settings", "Cài đặt", ft.Icons.SETTINGS_ROUNDED),
]

OVERVIEW = [
    ("product", "Tìm mặt hàng", "Tra cứu SKU theo mã, barcode hoặc tên.", ft.Icons.INVENTORY_2_ROUNDED),
    ("customer", "Tìm khách hàng", "Tra cứu thẻ: mã thẻ, tiền tố, tên, SĐT.", ft.Icons.PERSON_ROUNDED),
    (
        "loyalty",
        "Khách hàng theo kỳ",
        "Chọn khoảng ngày · lọc điểm/giá trị · chia Excel theo mức điểm · thống kê TXT.",
        ft.Icons.CARD_MEMBERSHIP_ROUNDED,
    ),
    (
        "cust_orders",
        "Đơn hàng theo khách",
        "Nhiều thẻ → nhiều Excel · lọc SP · khoảng giá trị đơn · quà/trả tiền.",
        ft.Icons.RECEIPT_LONG_ROUNDED,
    ),
    (
        "prod_orders",
        "Đơn hàng theo sản phẩm",
        "Mỗi mã/tên SP → 1 Excel · thêm file tổng · tách theo thẻ/SKU/siêu thị.",
        ft.Icons.SHOPPING_BAG_ROUNDED,
    ),
    ("group", "Mặt hàng theo nhóm", "Tra cứu theo mã hoặc tên nhóm sản phẩm.", ft.Icons.CATEGORY_ROUNDED),
]


def _page_builder(key: str):
    if key == "product":
        from app.ui.pages.product_page import build_product_page

        return build_product_page
    if key == "customer":
        from app.ui.pages.customer_page import build_customer_page

        return build_customer_page
    if key == "loyalty":
        from app.ui.pages.loyalty_page import build_loyalty_page

        return build_loyalty_page
    if key == "cust_orders":
        from app.ui.pages.customer_orders_page import build_customer_orders_page

        return build_customer_orders_page
    if key == "prod_orders":
        from app.ui.pages.product_orders_page import build_product_orders_page

        return build_product_orders_page
    if key == "group":
        from app.ui.pages.product_page import build_group_page

        return build_group_page
    if key == "settings":
        from app.ui.pages.settings_page import build_settings_page

        return build_settings_page
    raise KeyError(key)


def build_home(on_open) -> ft.Control:
    rows: list[ft.Control] = []
    for i, (key, title, blurb, icon) in enumerate(OVERVIEW):
        border = ft.Border.only(bottom=ft.BorderSide(1, theme.BORDER)) if i < len(OVERVIEW) - 1 else None
        rows.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, color=theme.ACCENT, size=20),
                            width=40,
                            height=40,
                            bgcolor=theme.ACCENT_SOFT,
                            border_radius=8,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column(
                            [
                                ft.Text(title, size=14, weight=ft.FontWeight.W_700, color=theme.TEXT),
                                ft.Text(blurb, size=12, color=theme.TEXT_MUTED),
                            ],
                            spacing=2,
                            expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Mở", size=13, color=theme.ACCENT_DIM, weight=ft.FontWeight.W_700
                            ),
                            alignment=ft.Alignment.CENTER,
                            height=40,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                bgcolor=theme.BG_CARD,
                border=border,
                ink=True,
                on_click=lambda e, k=key: on_open(k),
            )
        )

    list_box = ft.Container(
        content=ft.Column(rows, spacing=0),
        bgcolor=theme.BG_CARD,
        border=ft.Border.all(1, theme.BORDER),
        border_radius=10,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )
    tip = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.INFO_OUTLINE, color=theme.ACCENT, size=18),
                ft.Text(
                    "Cài đặt → Test db1/db2. Báo cáo theo kỳ tự gộp dữ liệu lịch sử + hiện tại.",
                    size=12,
                    color=theme.TEXT_MUTED,
                    expand=True,
                ),
            ],
            spacing=10,
        ),
        padding=12,
        bgcolor=theme.ACCENT_SOFT,
        border_radius=8,
    )

    return ft.Column(
        [
            theme.section_title("Tổng quan", "Chọn chức năng — hoặc dùng menu trái"),
            list_box,
            tip,
        ],
        spacing=14,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )


def build_shell(page: ft.Page) -> ft.Control:
    # Column (not Container) so page bodies with expand=True actually fill on resize
    content_slot = ft.Column(expand=True, spacing=0)
    state = {"key": "", "busy": False}
    rail_ref: dict[str, ft.NavigationRail] = {}

    def _set_body(ctrl: ft.Control) -> None:
        content_slot.controls.clear()
        content_slot.controls.append(
            ft.Container(
                content=ctrl,
                expand=True,
                padding=20,
                bgcolor=theme.BG_DEEP,
                alignment=ft.Alignment.TOP_LEFT,
            )
        )

    def navigate(key: str, *, sync_rail: bool = True) -> None:
        if state["busy"]:
            return
        if key == state["key"] and content_slot.controls:
            return
        state["busy"] = True
        try:
            body = build_home(navigate) if key == "home" else _page_builder(key)(page)
            _set_body(body)
            state["key"] = key
            if sync_rail and "rail" in rail_ref:
                idx = next(i for i, item in enumerate(NAV) if item[0] == key)
                if rail_ref["rail"].selected_index != idx:
                    rail_ref["rail"].selected_index = idx
            page.update()
        finally:
            state["busy"] = False

    def on_rail_change(e: ft.ControlEvent) -> None:
        idx = int(e.control.selected_index)
        navigate(NAV[idx][0], sync_rail=False)

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=96,
        min_extended_width=220,
        extended=True,
        bgcolor=theme.BG_PANEL,
        indicator_color=theme.ACCENT_SOFT,
        selected_label_text_style=ft.TextStyle(color=theme.ACCENT_DIM, weight=ft.FontWeight.W_700, size=14),
        unselected_label_text_style=ft.TextStyle(color=theme.TEXT, size=14),
        destinations=[
            ft.NavigationRailDestination(icon=icon, selected_icon=icon, label=label)
            for _, label, icon in NAV
        ],
        on_change=on_rail_change,
    )
    rail_ref["rail"] = rail
    _set_body(build_home(navigate))
    state["key"] = "home"

    top = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.Text("DATA ACCESS", size=17, weight=ft.FontWeight.W_800, color=theme.ACCENT_DIM),
                        ft.Container(
                            content=ft.Text(
                                "readonly SQL", size=11, color=theme.ACCENT_DIM, weight=ft.FontWeight.W_600
                            ),
                            bgcolor=theme.ACCENT_SOFT,
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            border_radius=6,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Text("Supermarket · db1 / db2", size=12, color=theme.TEXT_MUTED),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=22, vertical=12),
        bgcolor=theme.BG_PANEL,
        border=ft.Border.only(bottom=ft.BorderSide(1, theme.BORDER)),
    )

    return ft.Column(
        [
            top,
            ft.Row(
                [
                    ft.Container(
                        content=rail,
                        bgcolor=theme.BG_PANEL,
                        border=ft.Border.only(right=ft.BorderSide(1, theme.BORDER)),
                    ),
                    content_slot,
                ],
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        ],
        expand=True,
        spacing=0,
    )
