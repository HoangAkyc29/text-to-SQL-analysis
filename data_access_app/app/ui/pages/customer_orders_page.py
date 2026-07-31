"""F4 customer orders — tidy labeled filter panel."""
from __future__ import annotations

from datetime import date, datetime

import flet as ft
import pandas as pd

from app import theme
from app.domain import customer_orders as orders_svc
from app.domain.bill_expand import bill_keys_from_lines, fetch_bill_lines
from app.domain.columns import F4_ORDER_LINE_COLUMNS
from app.export.excel import project_columns
from app.ui import form_kit as fk
from app.ui import validate as v
from app.ui import widgets as w
from app.ui.clipboard_ids import copy_ids_button
from app.ui.jobs import JobRunner
from app.ui.output_path import pick_export_directory
from app.ui.tooltips import as_tooltip, tip_for_field


def build_customer_orders_page(page: ft.Page) -> ft.Control:
    start_d, end_d = w.default_range()
    d_from = w.date_field("Từ ngày", start_d)
    d_to = w.date_field("Đến ngày", end_d)
    cards = w.text_field("Mã thẻ (mỗi dòng một mã, hoặc cách bằng phẩy)", multiline=True)
    product = w.text_field("Sản phẩm phải có trong đơn", hint="Mã hoặc tên (một mục)")
    min_b = w.text_field("Giá trị từ", value="")
    max_b = w.text_field("Giá trị đến", value="", hint="để trống = không giới hạn")
    age_from = w.text_field("Tuổi từ", value="", hint="vd 30")
    age_to = w.text_field("Tuổi đến", value="", hint="vd 50")
    sex = fk.dropdown(
        "Giới tính",
        "any",
        [("any", "Tất cả"), ("M", "Nam"), ("F", "Nữ")],
    )
    gift = fk.dropdown(
        "Loại dòng SP",
        "any",
        [("any", "Tất cả"), ("paid", "Trả tiền"), ("gift", "Quà tặng")],
    )
    preview_mode = fk.dropdown(
        "Chế độ xem trước",
        "matched",
        [
            ("matched", "Dòng đơn khớp"),
            ("bill", "Chi tiết full bill (mọi SP trong đơn)"),
        ],
    )
    stk_block, get_stk = fk.stk_chips()
    search_bar, get_search = fk.search_opts_bar()
    status = w.status_bar()
    holder = ft.Column(
        [ft.Text("Chạy Preview để xem kết quả", color=theme.TEXT_MUTED, size=13)],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    preview = theme.card(content=holder, expand=True, padding=14)
    runner = JobRunner(page)
    last: dict = {
        "df": pd.DataFrame(columns=F4_ORDER_LINE_COLUMNS),
        "full": pd.DataFrame(columns=F4_ORDER_LINE_COLUMNS),
        "date_start": None,
        "date_end": None,
        "seed_skus": [],
    }

    def matched_df() -> pd.DataFrame:
        df = last.get("df")
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame(columns=F4_ORDER_LINE_COLUMNS)

    def full_df() -> pd.DataFrame:
        df = last.get("full")
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame(columns=F4_ORDER_LINE_COLUMNS)

    def result_df() -> pd.DataFrame:
        raw = full_df() if (preview_mode.value or "matched") == "bill" else matched_df()
        return sort_state.apply(raw)

    def on_sort_change():
        if not matched_df().empty or not full_df().empty:
            render_preview()
            page.update()

    def on_header_sort(col: str):
        sort_state.toggle_column(col)
        refresh_sort(result_df())
        render_preview()
        page.update()

    sort_bar, sort_state, refresh_sort = fk.column_sort_bar(lead="TRANS_NUM", on_change=on_sort_change)

    def render_preview():
        holder.controls.clear()
        mode = preview_mode.value or "matched"
        if mode == "bill":
            raw = full_df()
            if matched_df().empty:
                holder.controls.append(ft.Text("Không có đơn", color=theme.TEXT_MUTED))
            elif raw.empty:
                holder.controls.append(
                    ft.Text(
                        "Chưa có full bill — đang / hãy đợi bung chi tiết…",
                        color=theme.TEXT_MUTED,
                        size=12,
                    )
                )
            else:
                df = sort_state.apply(raw)
                refresh_sort(df)
                n_bills = (
                    df[["STK_ID", "TRANS_NUM"]].drop_duplicates().shape[0]
                    if {"STK_ID", "TRANS_NUM"}.issubset(df.columns)
                    else 0
                )
                holder.controls.append(
                    ft.Text(
                        f"Chi tiết full bill — {len(df)} dòng · {n_bills} đơn",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=theme.TEXT_MUTED,
                    )
                )
                holder.controls.append(
                    w.df_to_datatable(
                        project_columns(df, F4_ORDER_LINE_COLUMNS),
                        sort_column=sort_state.column,
                        sort_ascending=sort_state.ascending,
                        on_header_click=on_header_sort,
                    )
                )
        else:
            raw = matched_df()
            if raw.empty:
                holder.controls.append(ft.Text("Không có đơn", color=theme.TEXT_MUTED))
            else:
                df = sort_state.apply(raw)
                refresh_sort(df)
                holder.controls.append(
                    ft.Text(
                        f"Dòng đơn khớp — {len(df)} dòng",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=theme.TEXT_MUTED,
                    )
                )
                holder.controls.append(
                    w.df_to_datatable(
                        project_columns(df, F4_ORDER_LINE_COLUMNS),
                        sort_column=sort_state.column,
                        sort_ascending=sort_state.ascending,
                        on_header_click=on_header_sort,
                    )
                )
        holder.update()

    def set_loading(msg: str = "Đang truy vấn…"):
        holder.controls.clear()
        holder.controls.append(w.loading_row(msg))
        holder.update()

    def ensure_full_bills(*, force: bool = False):
        if not force and not full_df().empty:
            render_preview()
            return
        matched = matched_df()
        if matched.empty:
            last["full"] = pd.DataFrame(columns=F4_ORDER_LINE_COLUMNS)
            render_preview()
            return
        if last["date_start"] is None or last["date_end"] is None:
            status.value = "Thiếu khoảng ngày — chạy Xem trước lại"
            status.color = theme.WARN
            page.update()
            return

        set_loading("Đang bung full bill để xem chi tiết…")
        status.value = "Đang bung chi tiết đơn…"
        status.color = theme.TEXT_MUTED
        page.update()

        def job():
            keys = bill_keys_from_lines(matched)
            full = fetch_bill_lines(
                last["date_start"],
                last["date_end"],
                keys,
                progress=runner.set_message,
            )
            return project_columns(full, F4_ORDER_LINE_COLUMNS)

        def done(state):
            if state.error:
                status.value = state.error.split("\n", 1)[0]
                status.color = theme.DANGER
            else:
                last["full"] = state.result if isinstance(state.result, pd.DataFrame) else pd.DataFrame()
                render_preview()
                status.value = f"Chi tiết full bill — {len(full_df())} dòng"
                status.color = theme.SUCCESS
            page.update()

        runner.run(job, on_done=done)

    def on_preview_mode_change(_):
        mode = preview_mode.value or "matched"
        if mode == "bill":
            if matched_df().empty:
                status.value = "Chưa có kết quả — bấm Xem trước trước"
                status.color = theme.WARN
                page.update()
                return
            if full_df().empty:
                ensure_full_bills()
                return
        render_preview()
        page.update()

    preview_mode.on_change = on_preview_mode_change

    def validate_form() -> (
        tuple[date, date, list[str], str, float | None, float | None, float | None, float | None] | None
    ):
        v.clear_errors(d_from, d_to, cards, product, min_b, max_b, age_from, age_to)
        dates = v.validate_date_range(d_from, d_to)
        card_ids = v.validate_card_list(cards, required=True)
        prod = v.validate_product_query_single(product, required=False)
        ok_rng, lo, hi = v.validate_number_range(min_b, max_b, label="Giá trị đơn")
        ok_age, amin, amax = v.validate_number_range(age_from, age_to, label="Độ tuổi")
        page.update()
        if dates is None or card_ids is None or prod is None or not ok_rng or not ok_age:
            v.fail_status(status, page)
            return None
        return dates[0], dates[1], card_ids, prod, lo, hi, amin, amax

    def run(fetch_only: bool):
        checked = validate_form()
        if checked is None:
            return
        date_start, date_end, card_ids, prod, lo, hi, amin, amax = checked

        def start_job(*, base=None):
            set_loading()
            status.value = "Đang chạy…" if fetch_only else f"Đang xuất → {base}"
            status.color = theme.TEXT_MUTED
            page.update()

            def job():
                df, seed_skus = orders_svc.fetch_customer_orders(
                    date_start,
                    date_end,
                    card_ids,
                    store_ids=get_stk(),
                    product_query=prod,
                    min_bill=lo,
                    max_bill=hi,
                    gift_mode=gift.value,  # type: ignore[arg-type]
                    min_age=amin,
                    max_age=amax,
                    sex=sex.value or "any",  # type: ignore[arg-type]
                    search=get_search(),
                    progress=runner.set_message,
                )
                last["df"] = df
                last["seed_skus"] = seed_skus
                last["date_start"] = date_start
                last["date_end"] = date_end
                last["full"] = pd.DataFrame(columns=F4_ORDER_LINE_COLUMNS)
                if fetch_only:
                    return df
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                out = base / f"F4_don_theo_khach_{stamp}"
                return orders_svc.export_customer_orders(
                    df,
                    out,
                    date_start=date_start,
                    date_end=date_end,
                    exclude_skus=seed_skus,
                    meta={"from": w.date_field_value(d_from), "to": w.date_field_value(d_to)},
                    sort_column=sort_state.column,
                    sort_ascending=sort_state.ascending,
                    progress=runner.set_message,
                )

            def done(state):
                if state.error:
                    status.value = state.error.split("\n", 1)[0]
                    status.color = theme.DANGER
                else:
                    if fetch_only:
                        if (preview_mode.value or "matched") == "bill":
                            ensure_full_bills(force=True)
                        else:
                            render_preview()
                            status.value = f"Preview OK — {len(matched_df())} dòng"
                            status.color = theme.SUCCESS
                    else:
                        render_preview()
                        status.value = f"Đã xuất {len(state.result or [])} file → {base}"
                        status.color = theme.SUCCESS
                page.update()

            runner.run(job, on_done=done)

        if fetch_only:
            start_job()
            return

        async def _pick_then_export():
            base = await pick_export_directory(page)
            if base is None:
                status.value = "Đã hủy — chưa chọn thư mục xuất"
                status.color = theme.TEXT_MUTED
                page.update()
                return
            start_job(base=base)

        page.run_task(_pick_then_export)

    filters = fk.section(
        "Bộ lọc",
        ft.Column(
            [
                fk.field_block("Khoảng ngày", d_from, d_to),
                fk.field_block("Danh sách thẻ", cards),
                fk.field_block("Sản phẩm trong đơn", product),
                search_bar,
                fk.field_block("Khoảng giá trị đơn", min_b, max_b),
                fk.label("ĐIỀU KIỆN KHÁCH"),
                fk.field_block("Độ tuổi", age_from, age_to),
                fk.field_block("Giới tính", sex),
                fk.field_block("Loại dòng SP", gift),
                ft.Container(height=4),
                fk.label("SIÊU THỊ"),
                stk_block,
            ],
            spacing=12,
        ),
        hint="Thẻ + (SP) + tuổi/giới tính · mỗi thẻ một file Excel",
    )
    actions = ft.Container(
        content=fk.actions_bar(
            theme.primary_button("Xem trước", on_click=lambda e: run(True), icon=ft.Icons.PLAY_ARROW_ROUNDED),
            theme.secondary_button(
                "Xuất Excel + TXT", on_click=lambda e: run(False), icon=ft.Icons.DOWNLOAD_ROUNDED
            ),
            copy_ids_button(
                page,
                get_df=result_df,
                column="CARD_ID",
                label="Copy mã thẻ",
                status=status,
                noun="mã thẻ",
            ),
            copy_ids_button(
                page,
                get_df=result_df,
                column="SKU_CODE",
                label="Copy mã SP",
                status=status,
                noun="mã SP",
            ),
            status=status,
        ),
        padding=ft.Padding.only(top=4),
    )
    left = ft.Column(
        [filters, actions],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
    right = ft.Column(
        [
            ft.Text("Kết quả", size=13, weight=ft.FontWeight.W_700, color=theme.TEXT, tooltip=as_tooltip(tip_for_field("Kết quả"))),
            ft.Row(
                [
                    ft.Container(content=preview_mode, expand=True),
                    ft.Container(content=sort_bar, expand=True),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(content=preview, expand=True),
        ],
        spacing=8,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
    return ft.Column(
        [
            fk.page_header(
                "Đơn hàng theo khách",
                "Chọn khoảng ngày · lọc sản phẩm và giá trị đơn · xem dòng khớp hoặc full bill · xuất theo thẻ",
            ),
            fk.workspace_split(left, right, filter_width=400),
        ],
        spacing=12,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
