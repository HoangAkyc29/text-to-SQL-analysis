"""Settings page — DSN test + output folder."""
from __future__ import annotations

import flet as ft

from app import theme
from app.config import settings
from app.db.connection import DbError, test_connection
from app.db.cutoff import archive_newest_ym, rolling_cutoff
from app.ui import widgets as w


def build_settings_page(page: ft.Page) -> ft.Control:
    dsn1 = w.text_field("ANALYTICS_DB_DSN (db1 — Server=DESKTOP-AUQEDC5)", width=720, value=settings.dsn_db1)
    dsn1.password = True
    dsn1.can_reveal_password = True
    dsn2 = w.text_field("ANALYTICS_DB_DSN_2 (db2)", width=720, value=settings.dsn_db2)
    dsn2.password = True
    dsn2.can_reveal_password = True
    out_dir = w.text_field("Thư mục output", width=720, value=str(settings.output_dir))
    status = w.status_bar()
    cutoff = rolling_cutoff()
    info = ft.Text(
        f"Cutoff hiện tại: {cutoff.isoformat()} · archive_newest_ym={archive_newest_ym()}",
        color=theme.ACCENT,
        size=13,
    )

    def save_and_reload(_):
        import os
        from pathlib import Path

        env_path = Path(__file__).resolve().parents[2] / ".env"
        lines = [
            f"ANALYTICS_DB_DSN={dsn1.value or ''}",
            f"ANALYTICS_DB_DSN_2={dsn2.value or ''}",
            f"DATA_ACCESS_OUTPUT_DIR={out_dir.value or ''}",
        ]
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        settings.reload(env_path)
        status.value = f"Đã lưu {env_path}"
        status.color = theme.SUCCESS
        page.update()

    def test_db(target: str):
        def _go(_):
            try:
                # temporarily apply UI values
                settings.dsn_db1 = dsn1.value or ""
                settings.dsn_db2 = dsn2.value or ""
                msg = test_connection(target)
                status.value = msg
                status.color = theme.SUCCESS
            except DbError as exc:
                status.value = str(exc)
                status.color = theme.DANGER
            page.update()

        return _go

    return ft.Column(
        [
            theme.section_title("Cài đặt kết nối", "ODBC string giống agent — mạng discovery để sau"),
            theme.card(
                content=ft.Column(
                    [
                        info,
                        dsn1,
                        dsn2,
                        out_dir,
                        ft.Row(
                            [
                                theme.primary_button("Lưu .env", on_click=save_and_reload, icon=ft.Icons.SAVE),
                                theme.secondary_button("Test db1", on_click=test_db("db1"), icon=ft.Icons.STORAGE),
                                theme.secondary_button("Test db2", on_click=test_db("db2"), icon=ft.Icons.STORAGE),
                            ],
                            spacing=12,
                        ),
                        status,
                    ],
                    spacing=14,
                )
            ),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
