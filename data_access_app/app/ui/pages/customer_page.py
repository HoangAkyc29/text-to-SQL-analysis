"""F2 customer search."""
from __future__ import annotations

import flet as ft
import pandas as pd

from app import theme
from app.config import settings
from app.domain import customer as customer_svc
from app.export.excel import write_excel
from app.ui import form_kit as fk
from app.ui import validate as v
from app.ui import widgets as w
from app.ui.clipboard_ids import copy_ids_button
from app.ui.jobs import JobRunner


def build_customer_page(page: ft.Page) -> ft.Control:
    card = w.text_field("Mã thẻ")
    prefix = fk.card_prefix_field()
    name = w.text_field("Tên khách")
    phone = w.text_field("SĐT")
    birth_month = fk.dropdown(
        "Tháng sinh",
        "any",
        [("any", "Tất cả")] + [(str(i), f"Tháng {i}") for i in range(1, 13)],
    )
    age_from = w.text_field("Tuổi từ", value="", hint="vd 30")
    age_to = w.text_field("Tuổi đến", value="", hint="vd 50")
    opts_bar, get_opts = fk.search_opts_bar()
    status = w.status_bar()
    holder = ft.Column(
        [ft.Text("Chưa có dữ liệu — nhập điều kiện rồi bấm Tìm", color=theme.TEXT_MUTED, size=13)],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    preview = theme.card(content=holder, expand=True)
    runner = JobRunner(page)
    last: dict[str, pd.DataFrame] = {"df": pd.DataFrame()}

    def render_preview():
        raw = last.get("df")
        if raw is None or raw.empty:
            holder.controls.clear()
            holder.controls.append(
                ft.Text("Chưa có dữ liệu — nhập điều kiện rồi bấm Tìm", color=theme.TEXT_MUTED, size=13)
            )
            holder.update()
            return
        view = sort_state.apply(raw)
        refresh_sort(view)
        holder.controls.clear()
        holder.controls.append(
            w.df_to_datatable(
                view,
                sort_column=sort_state.column,
                sort_ascending=sort_state.ascending,
                on_header_click=on_header_sort,
            )
        )
        holder.update()

    def on_sort_change():
        if last.get("df") is not None and not last["df"].empty:
            render_preview()
            page.update()

    def on_header_sort(col: str):
        sort_state.toggle_column(col)
        refresh_sort(sort_state.apply(last["df"]))
        render_preview()
        page.update()

    sort_bar, sort_state, refresh_sort = fk.column_sort_bar(lead="CARD_ID", on_change=on_sort_change)

    def run_search(_):
        v.clear_errors(card, name, phone, age_from, age_to, prefix)
        ok_age, amin, amax = v.validate_number_range(age_from, age_to, label="Độ tuổi")
        page.update()
        if not ok_age:
            v.fail_status(status, page)
            return

        month_raw = (birth_month.value or "any").strip()
        bmonth: int | None = None
        if month_raw not in {"", "any"}:
            try:
                bmonth = int(month_raw)
            except ValueError:
                status.value = "Tháng sinh không hợp lệ"
                status.color = theme.DANGER
                page.update()
                return

        holder.controls.clear()
        holder.controls.append(w.loading_row("Đang tìm khách…"))
        status.value = "Đang tìm…"
        status.color = theme.TEXT_MUTED
        page.update()

        def job():
            return customer_svc.search_customers(
                card_id=card.value or "",
                card_prefix=v.card_prefix_value(prefix),
                name=name.value or "",
                phone=phone.value or "",
                birth_month=bmonth,
                min_age=amin,
                max_age=amax,
                search=get_opts(),
            )

        def done(state):
            if state.error:
                status.value = state.error.split("\n", 1)[0]
                status.color = theme.DANGER
            else:
                last["df"] = state.result
                render_preview()
                w.apply_search_result_status(status, state.result, noun="khách")
            page.update()

        runner.run(job, on_done=done)

    def export(_):
        path = settings.output_dir / "khach_hang_search.xlsx"
        write_excel(sort_state.apply(last["df"]), path)
        status.value = f"Đã ghi {path}"
        status.color = theme.SUCCESS
        page.update()

    return ft.Column(
        [
            theme.section_title("Tìm khách hàng", "Tra cứu thẻ khách — không xuất mật khẩu / PERSON_ID"),
            theme.card(
                content=ft.Column(
                    [
                        fk.field_block("Tra cứu", card, prefix, name, phone),
                        fk.field_block("Tháng sinh & độ tuổi", birth_month, age_from, age_to),
                        opts_bar,
                        ft.Row(
                            [
                                theme.primary_button("Tìm", on_click=run_search, icon=ft.Icons.PERSON_SEARCH),
                                theme.secondary_button("Xuất Excel", on_click=export, icon=ft.Icons.DOWNLOAD),
                                copy_ids_button(
                                    page,
                                    get_df=lambda: sort_state.apply(last["df"]),
                                    column="CARD_ID",
                                    label="Copy mã thẻ",
                                    status=status,
                                    noun="mã thẻ",
                                ),
                            ],
                            wrap=True,
                            spacing=10,
                        ),
                        status,
                    ],
                    spacing=12,
                )
            ),
            sort_bar,
            preview,
        ],
        spacing=16,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
