"""F3 loyalty customers — tidy labeled filter panel."""
from __future__ import annotations

from datetime import date, datetime

import flet as ft
import pandas as pd

from app import theme
from app.domain import loyalty_customers as loyalty_svc
from app.export.splitters import parse_point_buckets
from app.ui import form_kit as fk
from app.ui import validate as v
from app.ui import widgets as w
from app.ui.clipboard_ids import copy_ids_button
from app.ui.jobs import JobRunner
from app.ui.output_path import pick_export_directory


def build_loyalty_page(page: ft.Page) -> ft.Control:
    start_d, end_d = w.default_range()
    d_from = w.date_field("Từ ngày", start_d)
    d_to = w.date_field("Đến ngày", end_d)
    prefix = fk.card_prefix_field()
    birth_month = fk.dropdown(
        "Tháng sinh",
        "any",
        [("any", "Tất cả")] + [(str(i), f"Tháng {i}") for i in range(1, 13)],
    )
    age_from = w.text_field("Tuổi từ", value="", hint="vd 30")
    age_to = w.text_field("Tuổi đến", value="", hint="vd 50")
    sex = fk.dropdown(
        "Giới tính",
        "any",
        [("any", "Tất cả"), ("M", "Nam"), ("F", "Nữ")],
    )
    filter_mode = fk.dropdown(
        "Tiêu chí",
        "points",
        [("points", "Điểm (giá trị ÷ 50000)"), ("value", "Tổng giá trị")],
    )
    min_m = w.text_field("Từ", value="")
    max_m = w.text_field("Đến", value="")
    buckets = w.text_field(
        "Mức điểm chia file",
        value="0-200,200-500,>500",
        hint="vd: 0-200,200-500,>500",
    )
    stk_block, get_stk = fk.stk_chips()
    search_bar, get_search = fk.search_opts_bar()
    txt_opts = {
        "count": ft.Checkbox(label="Số lượng khách", value=True),
        "by_points": ft.Checkbox(label="Phân bố điểm", value=True),
        "by_store": ft.Checkbox(label="Theo siêu thị", value=True),
        "by_hour": ft.Checkbox(label="Theo giờ mua", value=True),
        "by_age": ft.Checkbox(label="Theo độ tuổi", value=True),
        "by_cycle": ft.Checkbox(label="Theo tháng", value=True),
    }
    status = w.status_bar()
    holder = ft.Column(
        [ft.Text("Chạy Preview để xem kết quả", color=theme.TEXT_MUTED, size=13)],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    preview = theme.card(content=holder, expand=True, padding=14)
    runner = JobRunner(page)
    last: dict[str, pd.DataFrame] = {"df": pd.DataFrame()}

    def render_preview():
        raw = last.get("df")
        if raw is None or raw.empty:
            holder.controls.clear()
            holder.controls.append(ft.Text("Không có dữ liệu", color=theme.TEXT_MUTED))
            holder.update()
            return
        view = sort_state.apply(raw)
        refresh_sort(view)
        holder.controls.clear()
        holder.controls.append(
            ft.Text(f"{len(view)} khách", size=12, weight=ft.FontWeight.W_600, color=theme.TEXT_MUTED)
        )
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

    def set_loading():
        holder.controls.clear()
        holder.controls.append(w.loading_row("Đang truy vấn db1/db2…"))
        holder.update()

    def validate_form(
        *, for_export: bool
    ) -> (
        tuple[date, date, str, float | None, float | None, float | None, float | None, int | None]
        | None
    ):
        v.clear_errors(d_from, d_to, prefix, min_m, max_m, buckets, age_from, age_to)
        dates = v.validate_date_range(d_from, d_to)
        pref = v.validate_card_prefix(prefix)
        ok_rng, lo, hi = v.validate_number_range(min_m, max_m, label="Khoảng điểm/giá trị")
        ok_age, amin, amax = v.validate_number_range(age_from, age_to, label="Độ tuổi")
        buckets_ok = v.validate_point_buckets(buckets) if for_export else True
        month_raw = (birth_month.value or "any").strip()
        bmonth: int | None = None
        if month_raw != "any":
            try:
                bmonth = int(month_raw)
                if bmonth < 1 or bmonth > 12:
                    raise ValueError
            except ValueError:
                status.value = "Tháng sinh không hợp lệ"
                status.color = theme.DANGER
                page.update()
                return None
        page.update()
        if dates is None or pref is None or not ok_rng or not ok_age or not buckets_ok:
            v.fail_status(status, page)
            return None
        return dates[0], dates[1], pref, lo, hi, amin, amax, bmonth

    def preview_click(_):
        checked = validate_form(for_export=False)
        if checked is None:
            return
        date_start, date_end, pref, lo, hi, amin, amax, bmonth = checked

        set_loading()
        status.value = "Đang chạy…"
        status.color = theme.TEXT_MUTED
        page.update()

        def job():
            return loyalty_svc.fetch_loyalty_customers(
                date_start,
                date_end,
                card_prefix=pref,
                store_ids=get_stk(),
                filter_mode=filter_mode.value,  # type: ignore[arg-type]
                min_metric=lo,
                max_metric=hi,
                min_age=amin,
                max_age=amax,
                sex=sex.value or "any",  # type: ignore[arg-type]
                birth_month=bmonth,
                search=get_search(),
                progress=runner.set_message,
            )

        def done(state):
            if state.error:
                status.value = state.error.split("\n", 1)[0]
                status.color = theme.DANGER
            else:
                last["df"] = state.result
                render_preview()
                status.value = f"Preview OK — {len(state.result)} khách"
                status.color = theme.SUCCESS
            page.update()

        runner.run(job, on_done=done)

    def export_click(_):
        checked = validate_form(for_export=True)
        if checked is None:
            return
        date_start, date_end, pref, lo, hi, amin, amax, bmonth = checked

        async def _after_pick():
            base = await pick_export_directory(page)
            if base is None:
                status.value = "Đã hủy — chưa chọn thư mục xuất"
                status.color = theme.TEXT_MUTED
                page.update()
                return

            set_loading()
            status.value = f"Đang xuất → {base}"
            status.color = theme.TEXT_MUTED
            page.update()

            def job():
                df = last["df"]
                if df is None or df.empty:
                    df = loyalty_svc.fetch_loyalty_customers(
                        date_start,
                        date_end,
                        card_prefix=pref,
                        store_ids=get_stk(),
                        filter_mode=filter_mode.value,  # type: ignore[arg-type]
                        min_metric=lo,
                        max_metric=hi,
                        min_age=amin,
                        max_age=amax,
                        sex=sex.value or "any",  # type: ignore[arg-type]
                        birth_month=bmonth,
                        search=get_search(),
                        progress=runner.set_message,
                    )
                    last["df"] = df
                df = sort_state.apply(df)
                bkt = parse_point_buckets(buckets.value or "")
                opts = [k for k, cb in txt_opts.items() if cb.value]
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                out = base / f"F3_KH_mua_hang_{stamp}"
                return loyalty_svc.export_loyalty(
                    df,
                    out,
                    date_start=date_start,
                    date_end=date_end,
                    store_ids=get_stk(),
                    buckets=bkt or None,
                    txt_options=opts,
                    meta={
                        "from": w.date_field_value(d_from),
                        "to": w.date_field_value(d_to),
                        "prefix": pref,
                        "age": f"{amin or ''}–{amax or ''}",
                        "sex": sex.value or "any",
                        "birth_month": str(bmonth or "any"),
                        "stores": ",".join(get_stk()),
                    },
                    progress=runner.set_message,
                )

            def done(state):
                if state.error:
                    status.value = state.error.split("\n", 1)[0]
                    status.color = theme.DANGER
                else:
                    paths = state.result or []
                    status.value = f"Đã xuất {len(paths)} file → {base}"
                    status.color = theme.SUCCESS
                    if last["df"] is not None and not last["df"].empty:
                        render_preview()
                page.update()

            runner.run(job, on_done=done)

        page.run_task(_after_pick)

    filters = fk.section(
        "Bộ lọc",
        ft.Column(
            [
                fk.field_block("Khoảng ngày", d_from, d_to),
                search_bar,
                fk.field_block("Tiêu chí lọc", filter_mode),
                fk.field_block("Khoảng giá trị", min_m, max_m),
                ft.Container(height=4),
                fk.label("ĐIỀU KIỆN KHÁCH HÀNG"),
                ft.Text(
                    "Lọc thêm theo tháng sinh, tuổi, giới tính, tiền tố thẻ",
                    size=11,
                    color=theme.TEXT_MUTED,
                ),
                fk.field_block("Tháng sinh & độ tuổi", birth_month, age_from, age_to),
                fk.field_block("Giới tính & tiền tố", sex, prefix),
                ft.Container(height=4),
                fk.label("SIÊU THỊ"),
                stk_block,
                ft.Container(height=4),
                fk.field_block("Chia Excel theo mức điểm", buckets),
                ft.Container(height=4),
                fk.label("NỘI DUNG FILE THỐNG KÊ"),
                ft.Text(
                    "Siêu thị = SO đơn / TỔNG / TB từ giao dịch thật · giờ & tháng theo đơn",
                    size=11,
                    color=theme.TEXT_MUTED,
                ),
                fk.check_grid(txt_opts, cols=2),
            ],
            spacing=12,
        ),
        hint="Điểm = tổng giá trị mua / 50000 · tuổi/GT lọc trên hồ sơ thẻ",
    )
    actions = ft.Container(
        content=fk.actions_bar(
            theme.primary_button("Xem trước", on_click=preview_click, icon=ft.Icons.PLAY_ARROW_ROUNDED),
            theme.secondary_button("Xuất Excel + TXT", on_click=export_click, icon=ft.Icons.DOWNLOAD_ROUNDED),
            copy_ids_button(
                page,
                get_df=lambda: sort_state.apply(last["df"]),
                column="CARD_ID",
                label="Copy mã thẻ",
                status=status,
                noun="mã thẻ",
            ),
            status=status,
            cols=1,
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
            ft.Text("Kết quả", size=13, weight=ft.FontWeight.W_700, color=theme.TEXT),
            sort_bar,
            ft.Container(content=preview, expand=True),
        ],
        spacing=8,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    return ft.Column(
        [
            fk.page_header(
                "Khách hàng theo kỳ",
                "Khoảng ngày · điểm/giá trị · tuổi/giới tính/tiền tố thẻ · siêu thị · xuất Excel + TXT",
            ),
            fk.workspace_split(left, right, filter_width=400),
        ],
        spacing=12,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
