"""F1 product search + F6 group search pages."""
from __future__ import annotations

import flet as ft
import pandas as pd

from app import theme
from app.domain import product as product_svc
from app.export.excel import write_excel
from app.ui import form_kit as fk
from app.ui import widgets as w
from app.ui.clipboard_ids import copy_ids_button
from app.ui.jobs import JobRunner
from app.ui.output_path import pick_export_directory


def _build_search_page(
    page: ft.Page,
    *,
    title: str,
    subtitle: str,
    fields: list[ft.Control],
    run_job,
    export_name: str,
    copy_column: str = "SKU_CODE",
    copy_label: str = "Copy mã SP",
    sort_lead: str = "SKU_CODE",
) -> ft.Control:
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

    sort_bar, sort_state, refresh_sort = fk.column_sort_bar(lead=sort_lead, on_change=on_sort_change)

    def run_search(_):
        holder.controls.clear()
        holder.controls.append(w.loading_row("Đang truy vấn…"))
        holder.update()
        status.value = "Đang tìm…"
        status.color = theme.TEXT_MUTED
        page.update()

        def job():
            return run_job(get_opts())

        def done(state):
            if state.error:
                status.value = state.error.split("\n", 1)[0]
                status.color = theme.DANGER
                last["df"] = pd.DataFrame()
                render_preview()
            else:
                last["df"] = state.result
                render_preview()
                w.apply_search_result_status(status, state.result, noun="dòng")
            page.update()

        runner.run(job, on_done=done)

    def export(_):
        async def _go():
            base = await pick_export_directory(page)
            if base is None:
                status.value = "Đã hủy — chưa chọn thư mục xuất"
                status.color = theme.TEXT_MUTED
                page.update()
                return
            path = base / export_name
            write_excel(sort_state.apply(last["df"]), path)
            status.value = f"Đã ghi {path}"
            status.color = theme.SUCCESS
            page.update()

        page.run_task(_go)

    return ft.Column(
        [
            theme.section_title(title, subtitle),
            theme.card(
                content=ft.Column(
                    [
                        ft.Row(fields, wrap=True, spacing=12),
                        opts_bar,
                        ft.Row(
                            [
                                theme.primary_button("Tìm", on_click=run_search, icon=ft.Icons.SEARCH),
                                theme.secondary_button("Xuất Excel", on_click=export, icon=ft.Icons.DOWNLOAD),
                                copy_ids_button(
                                    page,
                                    get_df=lambda: sort_state.apply(last["df"]),
                                    column=copy_column,
                                    label=copy_label,
                                    status=status,
                                    noun="mã",
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


def build_product_page(page: ft.Page) -> ft.Control:
    code = w.text_field("Mã sản phẩm / barcode")
    name = w.text_field("Tên sản phẩm")

    def job(search):
        return product_svc.search_products(code=code.value or "", name=name.value or "", search=search)

    return _build_search_page(
        page,
        title="Tìm mặt hàng",
        subtitle="Tra cứu danh mục sản phẩm (db2)",
        fields=[code, name],
        run_job=job,
        export_name="mat_hang_search.xlsx",
        sort_lead="SKU_CODE",
    )


def build_group_page(page: ft.Page) -> ft.Control:
    gcode = w.text_field("Mã nhóm")
    gname = w.text_field("Tên nhóm")

    def job(search):
        return product_svc.search_by_group(
            group_code=gcode.value or "",
            group_name=gname.value or "",
            search=search,
        )

    return _build_search_page(
        page,
        title="Mặt hàng theo nhóm",
        subtitle="Tra cứu theo mã hoặc tên nhóm",
        fields=[gcode, gname],
        run_job=job,
        export_name="mat_hang_theo_nhom.xlsx",
        sort_lead="SKU_CODE",
    )
