"""Business semantic key registry — meaningful chunk names, not raw column lowercase."""

from __future__ import annotations

# table.COLUMN → semantic_key (stable RAG chunk id)
TABLE_COLUMN_SEMANTIC: dict[str, str] = {
    "CSCARD.CARD_ID": "loyalty_card_master_id",
    "CSCARD.CARD_ID2": "cscard_alternate_card_slot",
    "CSCARD.CUST_ID": "loyalty_card_customer_id",
    "CRD_INFO.CARD_ID": "loyalty_card_master_id",
    "CRD_INFO.BUY_TRS": "loyalty_purchase_tx_count",
    "CRD_INFO.MARK": "loyalty_points_balance",
    "STRANS.CARD_ID": "sale_line_loyalty_card_ref",
    "STRANS.SKU_ID": "sale_line_sku_id",
    "STRANS.TRANS_NUM": "sale_document_number",
    "STRANS.TRANS_CODE": "sale_line_document_type",
    "STRANS.AMOUNT": "amount_line_item",
    "STRANS.QTY": "sale_line_quantity",
    "TRANSHDR.CARD_ID": "sale_header_loyalty_card_ref",
    "TRANSHDR.TRANS_NUM": "sale_document_number",
    "TRANSHDR.TRANS_CODE": "sale_header_document_type",
    "TRANSHDR.AMOUNT": "amount_bill_header",
    "PMTRANS.CARD_ID": "payment_loyalty_card_ref",
    "PMTRANS.TRANS_CODE": "payment_document_type",
    "PMTRANS.PMT_CODE": "payment_method_code",
    "PMTRANS.AMOUNT": "amount_payment",
    "PMTRANS.TRANS_NUM": "sale_document_number",
    "CRDTRANS.CARD_ID": "loyalty_tx_card_id",
    "CRDTRANS.TRANS_CODE": "loyalty_accrual_document_type",
    "CRDTRANS.MARK": "loyalty_points_earned",
    "CRDTRANS.AMOUNT": "loyalty_tx_amount",
    "CRDTRANS.REMARK": "loyalty_tx_operator_note",
    "CRDTRANS_ARC.CARD_ID": "loyalty_tx_card_id",
    "CRDTRANS_ARC.TRANS_CODE": "loyalty_adjustment_document_type",
    "CRDTRANS_ARC.MARK": "loyalty_points_redeemed",
    "CRDTRANS_ARC.AMOUNT": "loyalty_tx_amount",
    "CRDTRANS_ARC.REMARK": "loyalty_tx_operator_note",
    "CRDTRANS_TMP.CARD_ID": "loyalty_tx_card_id",
    "CRDTRANS_TMP.AMOUNT": "loyalty_tx_amount",
    "CRD_INFO.BUY_AMT": "loyalty_lifetime_purchase_amount",
    "CRD_INFO.BUY_MARK": "loyalty_lifetime_points_earned",
    "STRANS.SKU_ID": "sale_line_sku_id",
    "STRANS.QTY": "sale_line_quantity",
    "STRANS.PRICE": "sale_line_unit_price",
    "STRANS.STK_ID": "sale_store_id",
    "TRANSHDR.STK_ID": "sale_header_store_id",
    "TRANSHDR.CUST_ID": "sale_customer_id",
    "PMTRANS.STK_ID": "payment_store_id",
    "PMTRANS.PMT_CODE": "payment_method_code",
    "SKU_DEF.SKU_ID": "product_internal_id",
    "SKU_DEF.SKU_CODE": "product_display_sku_code",
    "SKU_DEF.BARCODE": "product_barcode",
    "BARCODE.BARCODE": "product_barcode",
    "BARCODE.SKU_ID": "product_internal_id",
    "WebRpt_rfm_snapshot.card_id": "rfm_snapshot_card_id",
    "WebRpt_sales_sku_daily.sku_id": "daily_report_sku_id",
    "WebRpt_sales_sku_daily.stk_id": "daily_report_store_id",
}

# When same COLUMN name spans tables with different roles → group table → semantic_key
COLUMN_DOMAIN_SPLIT: dict[str, dict[str, str]] = {
    "CARD_ID": {
        "CSCARD": "loyalty_card_master_id",
        "CRD_INFO": "loyalty_card_master_id",
        "PMCRDINF": "pm_voucher_card_id",
        "PMCRDSTK": "pm_voucher_card_id",
        "PMCRDRCV": "pm_voucher_card_id",
        "CUSTOMER": "customer_primary_card_ref",
        "CUSTSUMM": "customer_summary_card_ref",
        "CRDTRANS": "loyalty_tx_card_id",
        "CRDTRANS_ARC": "loyalty_tx_card_id",
        "CRDTRANS_TMP": "loyalty_tx_card_id",
        "STRANS": "sale_line_loyalty_card_ref",
        "STRANS_TMP": "sale_line_loyalty_card_ref",
        "SUSPEND": "sale_line_loyalty_card_ref",
        "TRANSHDR": "sale_header_loyalty_card_ref",
        "TRANSHDR_ARC": "sale_header_loyalty_card_ref",
        "PMTRANS": "payment_loyalty_card_ref",
        "ST_ORDER": "order_card_ref",
        "SUPPLIER": "supplier_card_ref",
        "WebRpt_rfm_snapshot": "rfm_snapshot_card_id",
        "CustSumm": "customer_summary_card_ref",
    },
    "TRANS_NUM": {
        "*": "sale_document_number",
    },
    "TRANS_CODE": {
        "STRANS": "sale_line_document_type",
        "STRANS_TMP": "sale_line_document_type",
        "SUSPEND": "sale_line_document_type",
        "TRANSHDR": "sale_header_document_type",
        "TRANSHDR_ARC": "sale_header_document_type",
        "PMTRANS": "payment_document_type",
        "CRDTRANS": "loyalty_accrual_document_type",
        "CRDTRANS_ARC": "loyalty_adjustment_document_type",
        "CRDTRANS_TMP": "loyalty_accrual_document_type",
    },
    "MARK": {
        "CRDTRANS": "loyalty_points_earned",
        "CRDTRANS_ARC": "loyalty_points_redeemed",
        "CRDTRANS_TMP": "loyalty_points_earned",
        "CRD_INFO": "loyalty_points_balance",
    },
    "REMARK": {
        "CRDTRANS": "loyalty_tx_operator_note",
        "CRDTRANS_ARC": "loyalty_tx_operator_note",
    },
    "STK_ID": {
        "STRANS": "sale_store_id",
        "TRANSHDR": "sale_header_store_id",
        "TRANSHDR_ARC": "sale_header_store_id",
        "PMTRANS": "payment_store_id",
        "CRDTRANS": "loyalty_tx_store_id",
        "CRDTRANS_ARC": "loyalty_tx_store_id",
        "*": "store_id_ref",
    },
    "SKU_ID": {
        "STRANS": "sale_line_sku_id",
        "SKU_DEF": "product_internal_id",
        "BARCODE": "product_internal_id",
        "WebRpt_sales_sku_daily": "daily_report_sku_id",
        "*": "sku_id_ref",
    },
    "CUST_ID": {
        "CSCARD": "loyalty_card_customer_id",
        "CUSTOMER": "customer_master_id",
        "TRANSHDR": "sale_customer_id",
        "CUSTHIST": "customer_history_id",
        "*": "customer_id_ref",
    },
}

# Human-readable titles for semantic keys
SEMANTIC_TITLES: dict[str, str] = {
    "loyalty_card_master_id": "Mã thẻ loyalty (master CSCARD/CRD_INFO)",
    "cscard_alternate_card_slot": "CSCARD — slot thẻ phụ / liên kết thứ hai (CARD_ID2)",
    "sale_line_loyalty_card_ref": "Thẻ loyalty ghi trên dòng bán (STRANS) — thường rỗng nếu KH không quét thẻ",
    "sale_header_loyalty_card_ref": "Thẻ loyalty trên header bill (TRANSHDR / archive)",
    "payment_loyalty_card_ref": "Thẻ loyalty trên dòng thanh toán (PMTRANS)",
    "loyalty_tx_card_id": "Thẻ trong giao dịch tích điểm (CRDTRANS)",
    "loyalty_purchase_tx_count": "Số lần phát sinh mua tích điểm (CRD_INFO.BUY_TRS)",
    "amount_bill_header": "Tổng tiền bill header — lọc min bill",
    "amount_line_item": "Thành tiền / giá trị dòng hàng STRANS",
    "amount_payment": "Số tiền thanh toán PMTRANS",
    "sale_document_number": "Số chứng từ / bill — join header ↔ dòng ↔ thanh toán",
    "product_internal_id": "Mã sản phẩm nội bộ SKU_ID",
    "product_display_sku_code": "Mã SKU hiển thị (user thường nhập thiếu số 0)",
    "sale_line_document_type": "Loại chứng từ dòng — 113=bán lẻ",
    "payment_document_type": "Loại chứng từ thanh toán — 221/222/008",
    "payment_method_code": "Hình thức TT: CASH, CARD, BANK",
    "loyalty_points_earned": "Điểm tích lũy phát sinh (CRDTRANS 811)",
    "loyalty_points_redeemed": "Điểm bị trừ / đổi quà (CRDTRANS_ARC 812)",
    "loyalty_points_balance": "Số dư điểm trên master thẻ (CRD_INFO.MARK)",
    "loyalty_tx_amount": "Doanh thu gốc gắn giao dịch tích điểm (CRDTRANS)",
    "loyalty_tx_operator_note": "Ghi chú thủ công trên giao dịch thẻ (REMARK)",
    "loyalty_accrual_document_type": "Loại GD tích điểm live — 811 (CRDTRANS db2)",
    "loyalty_adjustment_document_type": "Loại GD điều chỉnh/đổi quà — 812 (CRDTRANS_ARC db1)",
    "loyalty_lifetime_purchase_amount": "Tổng doanh thu mua tích điểm lifetime (CRD_INFO.BUY_AMT)",
    "loyalty_lifetime_points_earned": "Tổng điểm tích lifetime (CRD_INFO.BUY_MARK)",
    "sale_line_sku_id": "Mã SKU trên dòng bán — join SKU_DEF",
    "sale_line_quantity": "Số lượng bán trên dòng STRANS",
    "sale_line_unit_price": "Đơn giá dòng STRANS",
    "sale_store_id": "Cửa hàng phát sinh dòng bán (STRANS.STK_ID)",
    "sale_header_store_id": "Cửa hàng trên header bill",
    "sale_customer_id": "Mã khách trên header bill",
    "product_barcode": "Barcode quét POS — join BARCODE ↔ SKU_DEF",
    "cust_name": "Tên khách hàng",
    "dept_id": "Mã ngành hàng (merchandise department)",
    "vat_amt": "Tiền thuế GTGT (VAT_AMT)",
    "discount": "Giảm giá / chiết khấu (DISCOUNT)",
    "comm_amt": "Tiền hoa hồng (COMM_AMT)",
    "tax_rate": "Thuế suất (TAX_RATE)",
    "price": "Đơn giá bán (PRICE)",
}

# Business prose — natural language (exploration-informed, no sample dumps in text)
SEMANTIC_BUSINESS: dict[str, str] = {
    "loyalty_card_master_id": (
        "Định danh thẻ khách hàng thân thiết trên master CSCARD/CRD_INFO. "
        "Thẻ thường có prefix A (phổ thông) hoặc E/F/H (VIP). "
        "Dùng join CRDTRANS và tra cứu điểm; khác CARD_ID trên STRANS (chỉ khi quét thẻ lúc bán, thường để trống)."
    ),
    "cscard_alternate_card_slot": (
        "Slot thẻ phụ (CARD_ID2) trên master CSCARD — mã liên kết thứ hai nếu có. "
        "Ít được populate; không nhầm với CARD_ID chính."
    ),
    "sale_line_loyalty_card_ref": (
        "Thẻ loyalty gắn trên dòng STRANS khi POS ghi nhận quét thẻ lúc bán. "
        "Thường để trống với bill không loyalty."
    ),
    "amount_bill_header": (
        "Tổng tiền cả bill trên TRANSHDR (TRANS_CODE=113). "
        "Dùng cho điều kiện bill tối thiểu (min bill). Khác grain với AMOUNT từng dòng STRANS."
    ),
    "amount_line_item": (
        "Thành tiền / giá trị trên dòng STRANS. "
        "Có thể bằng 0 với quà tặng hoặc khuyến mãi. Không thay TRANSHDR.AMOUNT khi lọc min bill."
    ),
    "amount_payment": (
        "Số tiền trên PMTRANS — thanh toán hoặc chi quỹ bill. "
        "Có thể âm khi hoàn / điều chỉnh quỹ."
    ),
    "loyalty_purchase_tx_count": (
        "Số lần phát sinh mua được tính vào tích điểm (CRD_INFO.BUY_TRS). "
        "Là số lượng giao dịch, không phải số tiền."
    ),
    "sale_document_number": (
        "Số chứng từ / bill (TRANS_NUM) — khóa join TRANSHDR ↔ STRANS ↔ PMTRANS."
    ),
    "product_internal_id": (
        "Mã sản phẩm nội bộ (SKU_ID). Join STRANS ↔ SKU_DEF/BARCODE. "
        "Khác mã SKU_CODE 8 số mà user thường nhập."
    ),
    "loyalty_tx_card_id": (
        "Thẻ trong giao dịch tích điểm CRDTRANS — luôn populate (khác STRANS.CARD_ID). "
        "Prefix E thường gắn VIP."
    ),
    "loyalty_tx_amount": (
        "Doanh thu gốc dùng tính điểm trên CRDTRANS (811) / CRDTRANS_ARC (812). "
        "Archive có thể âm khi đổi quà. Quy tắc tham khảo: ~50.000 VND / 1 điểm."
    ),
    "loyalty_points_earned": (
        "Điểm cộng trên CRDTRANS (TRANS_CODE=811) khi tích từ mua hàng."
    ),
    "loyalty_points_redeemed": (
        "Điểm trừ trên CRDTRANS_ARC (TRANS_CODE=812) khi đổi quà hoặc điều chỉnh thủ công."
    ),
    "loyalty_tx_operator_note": (
        "Ghi chú do nhân viên nhập khi điều chỉnh thẻ — giải thích trừ/cộng điểm, đổi quà, sửa tích nhầm."
    ),
    "loyalty_accrual_document_type": (
        "Loại giao dịch tích điểm live (TRANS_CODE=811 trên CRDTRANS db2)."
    ),
    "loyalty_adjustment_document_type": (
        "Loại giao dịch điều chỉnh / đổi quà (TRANS_CODE=812 trên CRDTRANS_ARC db1)."
    ),
    "loyalty_points_balance": (
        "Số dư điểm tích lũy aggregate trên CRD_INFO — khác điểm phát sinh từng dòng CRDTRANS."
    ),
    "loyalty_lifetime_purchase_amount": (
        "Tổng doanh thu mua đã tích điểm lifetime (CRD_INFO.BUY_AMT)."
    ),
    "loyalty_lifetime_points_earned": (
        "Tổng điểm đã tích lifetime (CRD_INFO.BUY_MARK)."
    ),
    "sale_line_sku_id": (
        "Mã SKU trên dòng STRANS — join SKU_DEF/BARCODE để lọc quà tặng, hàng KM. "
        "User hay tra theo SKU_CODE 8 số."
    ),
    "sale_line_quantity": (
        "Số lượng bán trên dòng STRANS. Dòng quà tặng có thể QTY=1, AMOUNT=0."
    ),
    "sale_header_document_type": (
        "Loại chứng từ header bill (TRANSHDR) — 113 = bán lẻ POS."
    ),
    "payment_method_code": (
        "Hình thức thanh toán trên PMTRANS: tiền mặt (CASH), thẻ (CARD), chuyển khoản (BANK), …"
    ),
    "product_barcode": (
        "Mã vạch EAN/GTIN trên BARCODE — quét POS, map sang SKU_ID qua master."
    ),
    "sale_customer_id": (
        "Mã khách trên header bill (TRANSHDR). Thường trống nếu KH không đăng ký; "
        "khác CUST_ID trên master loyalty CSCARD."
    ),
    "cust_name": (
        "Tên khách hàng đã đăng ký hoặc ghi nhận trên chứng từ. "
        "Trên CUSTOMER là tên master; trên INV_ISS là tên in phiếu xuất."
    ),
    "dept_id": (
        "Mã ngành hàng / phòng ban merchandise — phân loại SKU và nhà cung cấp theo cây ngành hàng nội bộ."
    ),
    "vat_amt": (
        "Số tiền thuế GTGT (VAT) ghi trên chứng từ — grain phụ thuộc bảng. "
        "Trên STRANS/STRANS_TMP/SUSPEND là thuế từng dòng bán; "
        "TRANSHDR/TRANSHDR_ARC là tổng thuế cả bill; "
        "CRDTRANS/CRDTRANS_ARC/CRDTRANS_TMP là thuế trên doanh thu loyalty; "
        "INV_HDR/INV_ISS là thuế trên chứng từ kho; ST_ORDER là thuế trên đơn nội bộ. "
        "Không cộng VAT dòng STRANS để suy ra min bill — dùng TRANSHDR.AMOUNT / TRANSHDR.VAT_AMT."
    ),
    "debt_no": (
        "Số chứng từ công nợ — khóa join DEBT ↔ CTRANS ↔ thanh toán. "
        "Dùng tra công nợ phải thu/phải trả khách hoặc NCC."
    ),
    "debt_date": "Ngày phát sinh công nợ trên chứng từ DEBT / CTRANS.",
    "buy_amt": (
        "Ngưỡng giá trị mua / min bill trong rule khuyến mãi RDISCINF — "
        "khác BUY_AMT trên CRD_INFO (lifetime loyalty)."
    ),
    "cdisc_rate": "Tỷ lệ chiết khấu coupon (%) trên dòng bán STRANS / đơn KM.",
    "rdiscinf__gift": (
        "Cờ đánh dấu rule quà tặng — khi bật, KM trả quà thay vì (hoặc kèm) giảm giá tiền."
    ),
}


def infer_semantic_key(table_name: str, column: str) -> str | None:
    """Return explicit semantic key if registered."""
    tkey = f"{table_name}.{column}"
    if tkey in TABLE_COLUMN_SEMANTIC:
        return TABLE_COLUMN_SEMANTIC[tkey]
    col_upper = column.upper()
    if col_upper in COLUMN_DOMAIN_SPLIT:
        split = COLUMN_DOMAIN_SPLIT[col_upper]
        # exact table match (case-insensitive)
        for k, v in split.items():
            if k != "*" and k.upper() == table_name.upper():
                return v
        if table_name in split:
            return split[table_name]
        if "*" in split:
            return split["*"]
    return None


def infer_role_slug(column: str) -> str:
    """Fallback role slug for single-table columns."""
    col = column.upper()
    if col.endswith("2") and not col.endswith("_ID2"):
        return column.lower() + "_alt"
    if col.endswith("_ID2") or col == "CARD_ID2":
        return "alternate_" + column.lower().replace("_id2", "_id")
    if col.endswith("_ID"):
        return column.lower().replace("_id", "") + "_id"
    return column.lower()
