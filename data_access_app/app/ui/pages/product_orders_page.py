"""F5 product orders — tidy labeled filter panel."""
from __future__ import annotations

from datetime import date, datetime

import flet as ft
import pandas as pd

from app import theme
from app.domain import product_orders as po_svc
from app.domain.bill_expand import bill_keys_from_lines, fetch_bill_lines
from app.domain.columns import F5_ORDER_LINE_COLUMNS, ORDER_COLUMNS
from app.export.excel import project_columns
from app.ui import form_kit as fk
from app.ui import validate as v
from app.ui import widgets as w
from app.ui.clipboard_ids import copy_ids_button
from app.ui.jobs import JobRunner
from app.ui.output_path import pick_export_directory
from app.ui.tooltips import as_tooltip, tip_for_field


def build_product_orders_page(page: ft.Page) -> ft.Control:
    start_d, end_d = w.default_range()
    d_from = w.date_field("Từ ngày", start_d)
    d_to = w.date_field("Đến ngày", end_d)
    tokens = w.text_field("Mã hoặc tên sản phẩm (mỗi dòng một mục)", multiline=True)
    min_b = w.text_field("Giá trị từ", value="")
    max_b = w.text_field("Giá trị đến", value="", hint="để trống = không giới hạn")
    age_from = w.text_field("Tuổi từ", value="", hint="vd 30")
    age_to = w.text_field("Tuổi đến", value="", hint="vd 50")
    card_prefix = fk.card_prefix_field()
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
    opts = {
        "require_card": ft.Checkbox(label="Chỉ đơn có thẻ", value=True),
        "include_cards": ft.Checkbox(label="Kèm danh sách thẻ đã mua", value=True),
    }
    split_by = fk.dropdown(
        "Tách file Excel",
        "none",
        [
            ("none", "Không tách"),
            ("CARD_ID", "Theo thẻ (CARD_ID)"),
            ("SKU_CODE", "Theo mã SP"),
            ("STK_ID", "Theo siêu thị"),
        ],
    )
    preview_mode = fk.dropdown(
        "Chế độ xem trước",
        "orders",
        [
            ("orders", "Đơn hàng (TRANSHDR)"),
            ("bill", "Chi tiết đơn (full STRANS)"),
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
        "per_token": {},
        "per_token_full": {},
        "unresolved": [],
        "date_start": None,
        "date_end": None,
    }

    def orders_df() -> pd.DataFrame:
        frames = [df for df in last["per_token"].values() if df is not None and not df.empty]
        if not frames:
            return pd.DataFrame(columns=ORDER_COLUMNS)
        return pd.concat(frames, ignore_index=True)

    def full_df() -> pd.DataFrame:
        frames = [df for df in last["per_token_full"].values() if df is not None and not df.empty]
        if not frames:
            return pd.DataFrame(columns=F5_ORDER_LINE_COLUMNS)
        return pd.concat(frames, ignore_index=True)

    def result_df() -> pd.DataFrame:
        raw = full_df() if (preview_mode.value or "orders") == "bill" else orders_df()
        return sort_state.apply(raw)

    def on_sort_change():
        if not orders_df().empty or not full_df().empty:
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
        unresolved = last.get("unresolved") or []
        if unresolved:
            holder.controls.append(
                ft.Text("Không tìm thấy: " + ", ".join(unresolved), color=theme.WARN, size=12)
            )
        mode = preview_mode.value or "orders"
        if mode == "bill":
            raw = full_df()
            if raw.empty and orders_df().empty:
                holder.controls.append(ft.Text("Không có đơn", color=theme.TEXT_MUTED))
            elif raw.empty:
                holder.controls.append(
                    ft.Text(
                        "Chưa có full STRANS — đang / hãy đợi bung chi tiết…",
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
                        f"Chi tiết đơn (STRANS) — {len(df)} dòng · {n_bills} giao dịch",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=theme.TEXT_MUTED,
                    )
                )
                holder.controls.append(
                    w.df_to_datatable(
                        project_columns(df, F5_ORDER_LINE_COLUMNS),
                        sort_column=sort_state.column,
                        sort_ascending=sort_state.ascending,
                        on_header_click=on_header_sort,
                    )
                )
        else:
            raw = orders_df()
            if raw.empty:
                holder.controls.append(ft.Text("Không có đơn", color=theme.TEXT_MUTED))
            else:
                df = sort_state.apply(raw)
                refresh_sort(df)
                n_tok = sum(1 for x in last["per_token"].values() if x is not None and not x.empty)
                holder.controls.append(
                    ft.Text(
                        f"Đơn hàng (TRANSHDR) — {len(df)} giao dịch · {n_tok} sản phẩm",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=theme.TEXT_MUTED,
                    )
                )
                holder.controls.append(
                    w.df_to_datatable(
                        project_columns(df, ORDER_COLUMNS),
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
        """Lazy expand full STRANS for preview mode 2."""
        if not force and last["per_token_full"]:
            render_preview()
            return
        orders = orders_df()
        if orders.empty:
            last["per_token_full"] = {}
            render_preview()
            return
        if last["date_start"] is None or last["date_end"] is None:
            status.value = "Thiếu khoảng ngày — chạy Xem trước lại"
            status.color = theme.WARN
            page.update()
            return

        set_loading("Đang bung full STRANS để xem chi tiết đơn…")
        status.value = "Đang bung chi tiết đơn…"
        status.color = theme.TEXT_MUTED
        page.update()

        def job():
            keys = bill_keys_from_lines(orders)
            full = fetch_bill_lines(
                last["date_start"],
                last["date_end"],
                keys,
                progress=runner.set_message,
            )
            per_full: dict[str, pd.DataFrame] = {}
            for token, odf in last["per_token"].items():
                if odf is None or odf.empty:
                    per_full[token] = pd.DataFrame(columns=F5_ORDER_LINE_COLUMNS)
                    continue
                tk = bill_keys_from_lines(odf)
                part = (
                    full.merge(tk, on=["STK_ID", "TRANS_NUM"], how="inner")
                    if not full.empty and not tk.empty
                    else pd.DataFrame(columns=F5_ORDER_LINE_COLUMNS)
                )
                per_full[token] = project_columns(part, F5_ORDER_LINE_COLUMNS)
            return per_full

        def done(state):
            if state.error:
                status.value = state.error.split("\n", 1)[0]
                status.color = theme.DANGER
            else:
                last["per_token_full"] = state.result or {}
                render_preview()
                n = len(full_df())
                status.value = f"Chi tiết đơn (STRANS) — {n} dòng"
                status.color = theme.SUCCESS
            page.update()

        runner.run(job, on_done=done)

    def on_preview_mode_change(_):
        mode = preview_mode.value or "orders"
        if mode == "bill":
            if orders_df().empty:
                status.value = "Chưa có kết quả — bấm Xem trước trước"
                status.color = theme.WARN
                page.update()
                return
            if not last["per_token_full"]:
                ensure_full_bills()
                return
        render_preview()
        page.update()

    preview_mode.on_change = on_preview_mode_change

    def validate_form() -> (
        tuple[date, date, list[str], float | None, float | None, float | None, float | None, str] | None
    ):
        v.clear_errors(d_from, d_to, tokens, min_b, max_b, age_from, age_to, card_prefix)
        dates = v.validate_date_range(d_from, d_to)
        token_list = v.validate_product_token_list(tokens, required=True)
        ok_rng, lo, hi = v.validate_number_range(min_b, max_b, label="Giá trị đơn")
        ok_age, amin, amax = v.validate_number_range(age_from, age_to, label="Độ tuổi")
        pref = v.validate_card_prefix(card_prefix)
        page.update()
        if dates is None or token_list is None or not ok_rng or not ok_age or pref is None:
            v.fail_status(status, page)
            return None
        return dates[0], dates[1], token_list, lo, hi, amin, amax, pref

    def run(export: bool):
        checked = validate_form()
        if checked is None:
            return
        date_start, date_end, token_list, lo, hi, amin, amax, pref = checked

        def start_job(*, base=None):
            set_loading()
            status.value = "Đang chạy…" if not export else f"Đang xuất → {base}"
            status.color = theme.TEXT_MUTED
            page.update()

            def job():
                per, unresolved, seeds = po_svc.fetch_product_orders(
                    date_start,
                    date_end,
                    token_list,
                    store_ids=get_stk(),
                    require_card=bool(opts["require_card"].value),
                    min_bill=lo,
                    max_bill=hi,
                    gift_mode=gift.value,  # type: ignore[arg-type]
                    min_age=amin,
                    max_age=amax,
                    sex=sex.value or "any",  # type: ignore[arg-type]
                    card_prefix=pref,
                    search=get_search(),
                    progress=runner.set_message,
                )
                last["per_token"] = per
                last["unresolved"] = unresolved
                last["seed_skus"] = seeds
                last["date_start"] = date_start
                last["date_end"] = date_end
                last["per_token_full"] = {}
                if not export:
                    return per
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                out = base / f"F5_don_chua_SP_{stamp}"
                split_col = (split_by.value or "none").strip()
                return po_svc.export_product_orders(
                    per,
                    out,
                    date_start=date_start,
                    date_end=date_end,
                    seed_skus_by_token=seeds,
                    include_aggregate=len(per) > 1,
                    include_card_list=bool(opts["include_cards"].value),
                    split_by=None if split_col == "none" else split_col,
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
                    if export:
                        status.value = f"Đã xuất {len(state.result or [])} file → {base}"
                        status.color = theme.SUCCESS
                        render_preview()
                    else:
                        if (preview_mode.value or "orders") == "bill":
                            ensure_full_bills(force=True)
                        else:
                            render_preview()
                            n = len(orders_df())
                            status.value = f"Preview OK — {n} giao dịch (TRANSHDR)"
                            status.color = theme.SUCCESS
                page.update()

            runner.run(job, on_done=done)

        if not export:
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
                fk.field_block("Sản phẩm cần tìm", tokens),
                search_bar,
                fk.field_block("Khoảng giá trị đơn", min_b, max_b),
                fk.field_block("Loại dòng SP", gift),
                ft.Container(height=4),
                fk.label("ĐIỀU KIỆN KHÁCH HÀNG"),
                ft.Text(
                    "Lọc thêm theo tuổi (CSCARD.BIRTHDAY), giới tính, tiền tố thẻ — bật tuổi/GT sẽ chỉ lấy đơn có thẻ",
                    size=11,
                    color=theme.TEXT_MUTED,
                ),
                fk.field_block("Độ tuổi", age_from, age_to),
                fk.field_block("Giới tính & tiền tố", sex, card_prefix),
                ft.Container(height=4),
                fk.label("SIÊU THỊ"),
                stk_block,
                ft.Container(height=4),
                fk.label("TÙY CHỌN XUẤT"),
                fk.check_grid(opts, cols=2),
                fk.field_block("Tách file (chọn một) — luôn theo full STRANS", split_by),
            ],
            spacing=12,
        ),
        hint="Excel: orders (TRANSHDR) + bill_lines (STRANS) · tách file = mode STRANS",
    )
    actions = ft.Container(
        content=fk.actions_bar(
            theme.primary_button("Xem trước", on_click=lambda e: run(False), icon=ft.Icons.PLAY_ARROW_ROUNDED),
            theme.secondary_button(
                "Xuất Excel + TXT", on_click=lambda e: run(True), icon=ft.Icons.DOWNLOAD_ROUNDED
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
                "Đơn hàng theo sản phẩm",
                "TRANSHDR = từng giao dịch có SP · STRANS = mọi mặt hàng trong đơn · Excel đủ 2 sheet",
            ),
            fk.workspace_split(left, right, filter_width=400),
        ],
        spacing=12,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
