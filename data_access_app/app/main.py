"""Flet entrypoint for Data Access App."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow `python -m app.main` from data_access_app/
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _run() -> None:
    # 1) Single-instance BEFORE importing Flet — second launch must not open a window.
    from app.single_instance import acquire_or_exit

    view_name = os.getenv("DATA_ACCESS_FLET_VIEW", "web").strip().lower()
    default_port = "13059" if view_name == "desktop" else "13050"
    port = int(os.getenv("DATA_ACCESS_PORT", default_port) or default_port)

    acquire_or_exit(port=port)

    # 2) Only the winning process loads Flet / builds UI.
    import flet as ft

    from app import theme
    from app.config import settings
    from app.db.session_clock import bootstrap_session_clock
    from app.ui.shell import build_shell

    def main(page: ft.Page) -> None:
        try:
            theme.page_defaults(page)
            settings.reload()
            st = bootstrap_session_clock()
            page.add(build_shell(page))
            if st.source == "wall":
                # Soft banner via console; Settings page shows details.
                print(f"DATA_ACCESS_CLOCK_WARN: {st.detail}", flush=True)
            print("DATA_ACCESS_READY", flush=True)
        except Exception as exc:  # noqa: BLE001
            # Keep Flet session alive with a visible error instead of crashing the process.
            import traceback

            print(f"DATA_ACCESS_BOOT_ERROR: {exc}\n{traceback.format_exc()}", flush=True)
            page.bgcolor = "#F3F5F8"
            page.add(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Không khởi động được Data Access", size=22, weight=ft.FontWeight.BOLD),
                            ft.Text(str(exc), size=14, color="#DC2626"),
                            ft.Text(
                                "Kiểm tra DSN / SQL Server (có thể đang restore). "
                                "Sửa .env rồi mở lại app.",
                                size=13,
                            ),
                        ],
                        spacing=12,
                    ),
                    padding=32,
                )
            )

    view = ft.AppView.FLET_APP if view_name == "desktop" else ft.AppView.WEB_BROWSER
    print(f"DATA_ACCESS_VIEW={view_name} PORT={port}", flush=True)
    ft.run(main, view=view, port=port)


if __name__ == "__main__":
    # WEB_BROWSER avoids first-time flet-desktop client download (often blocked by SSL).
    # For native window: set DATA_ACCESS_FLET_VIEW=desktop
    _run()
