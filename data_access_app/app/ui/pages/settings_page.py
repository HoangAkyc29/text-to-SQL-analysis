"""Settings page — DSN test + session cutoff clock (TRANSHDR as-of)."""
from __future__ import annotations

import re

import flet as ft

from app import theme
from app.config import APP_ROOT, settings
from app.db.connection import DbError, test_connection
from app.db.cutoff import archive_newest_ym, rolling_cutoff
from app.db import session_clock as clock
from app.ui import widgets as w


def build_settings_page(page: ft.Page) -> ft.Control:
    dsn1 = w.text_field("ANALYTICS_DB_DSN (db1 — Server=DESKTOP-AUQEDC5)", width=720, value=settings.dsn_db1)
    dsn1.password = True
    dsn1.can_reveal_password = True
    dsn2 = w.text_field("ANALYTICS_DB_DSN_2 (db2)", width=720, value=settings.dsn_db2)
    dsn2.password = True
    dsn2.can_reveal_password = True
    status = w.status_bar()
    clock_info = ft.Text("", color=theme.ACCENT, size=13)

    def _refresh_clock_label():
        st = clock.status()
        cutoff = rolling_cutoff()
        arch = archive_newest_ym()
        src = "TRANSHDR (db2)" if st.source == "transhdr" else "đồng hồ máy"
        clock_info.value = (
            f"Mốc as-of: {st.as_of.date().isoformat()} · nguồn: {src}\n"
            f"Cutoff: {cutoff.isoformat()} · archive_newest_ym={arch}\n"
            f"{st.detail}"
        )

    _refresh_clock_label()

    def save_and_reload(_):
        env_path = APP_ROOT / ".env"
        desired = {
            "ANALYTICS_DB_DSN": dsn1.value or "",
            "ANALYTICS_DB_DSN_2": dsn2.value or "",
        }
        existing = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
        lines = existing.splitlines()
        seen: set[str] = set()
        new_lines: list[str] = []
        for line in lines:
            m = re.match(r"^([A-Za-z0-9_]+)=", line)
            if m and m.group(1) in desired:
                key = m.group(1)
                new_lines.append(f"{key}={desired[key]}")
                seen.add(key)
            else:
                new_lines.append(line)
        for key, val in desired.items():
            if key not in seen:
                new_lines.append(f"{key}={val}")
        env_path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
        settings.reload(env_path)
        status.value = f"Đã lưu {env_path}"
        status.color = theme.SUCCESS
        page.update()

    def test_db(target: str):
        def _go(_):
            try:
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

    def refresh_as_of(_):
        settings.dsn_db1 = dsn1.value or ""
        settings.dsn_db2 = dsn2.value or ""
        st = clock.refresh_from_transhdr()
        _refresh_clock_label()
        status.value = "Đã lấy lại mốc từ TRANSHDR" if st.source == "transhdr" else st.detail
        status.color = theme.SUCCESS if st.source == "transhdr" else theme.WARN
        page.update()

    def reset_wall(_):
        clock.reset_to_wall_clock()
        _refresh_clock_label()
        status.value = "Đã reset mốc về đồng hồ máy"
        status.color = theme.WARN
        page.update()

    return ft.Column(
        [
            theme.section_title(
                "Cài đặt kết nối",
                "Cutoff theo MAX(TRANSHDR.TRAN_DATE) db2 lúc mở app — xuất file sẽ hỏi thư mục mỗi lần",
            ),
            theme.card(
                content=ft.Column(
                    [
                        clock_info,
                        ft.Row(
                            [
                                theme.secondary_button(
                                    "Làm mới từ TRANSHDR",
                                    on_click=refresh_as_of,
                                    icon=ft.Icons.REFRESH_ROUNDED,
                                ),
                                theme.secondary_button(
                                    "Reset đồng hồ máy",
                                    on_click=reset_wall,
                                    icon=ft.Icons.SCHEDULE_ROUNDED,
                                ),
                            ],
                            spacing=12,
                            wrap=True,
                        ),
                        dsn1,
                        dsn2,
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
