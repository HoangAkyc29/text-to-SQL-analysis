"""Flet entrypoint for Data Access App."""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `python -m app.main` from data_access_app/
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import flet as ft

from app import theme
from app.config import settings
from app.ui.shell import build_shell


def main(page: ft.Page) -> None:
    theme.page_defaults(page)
    settings.reload()
    page.add(build_shell(page))
    print("DATA_ACCESS_READY", flush=True)


if __name__ == "__main__":
    # WEB_BROWSER avoids first-time flet-desktop client download (often blocked by SSL).
    # For native window: set DATA_ACCESS_FLET_VIEW=desktop
    import os

    view_name = os.getenv("DATA_ACCESS_FLET_VIEW", "web").strip().lower()
    view = ft.AppView.FLET_APP if view_name == "desktop" else ft.AppView.WEB_BROWSER
    # Desktop must NOT share the web port — leftover browser tabs on 13050
    # reconnect forever and the native window stays on a loading spinner.
    default_port = "13055" if view_name == "desktop" else "13050"
    port = int(os.getenv("DATA_ACCESS_PORT", default_port) or default_port)
    print(f"DATA_ACCESS_VIEW={view_name} PORT={port}", flush=True)
    ft.run(main, view=view, port=port)
