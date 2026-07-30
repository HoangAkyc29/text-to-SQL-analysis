"""Instantiate every page builder — catch Flet kwarg / construct errors before browser."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import flet as ft  # noqa: E402

from app.ui.pages.customer_orders_page import build_customer_orders_page  # noqa: E402
from app.ui.pages.customer_page import build_customer_page  # noqa: E402
from app.ui.pages.loyalty_page import build_loyalty_page  # noqa: E402
from app.ui.pages.product_orders_page import build_product_orders_page  # noqa: E402
from app.ui.pages.product_page import build_group_page, build_product_page  # noqa: E402
from app.ui.pages.settings_page import build_settings_page  # noqa: E402
from app.ui.shell import build_shell  # noqa: E402


def fake_page() -> MagicMock:
    page = MagicMock(spec=ft.Page)
    page.session = SimpleNamespace()
    page.update = MagicMock()
    page.snack_bar = None
    page.overlay = []
    page.controls = []
    return page


def main() -> None:
    page = fake_page()
    builders = [
        ("loyalty", build_loyalty_page),
        ("cust_orders", build_customer_orders_page),
        ("prod_orders", build_product_orders_page),
        ("product", build_product_page),
        ("customer", build_customer_page),
        ("group", build_group_page),
        ("settings", build_settings_page),
        ("shell", build_shell),
    ]
    for name, fn in builders:
        ctrl = fn(page)
        assert ctrl is not None, name
        print(f"OK  {name}: {type(ctrl).__name__}")
    print("ALL PAGE BUILDS OK")


if __name__ == "__main__":
    main()
