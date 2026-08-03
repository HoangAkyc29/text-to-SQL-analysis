"""Slim export column allowlists — from data_dictionary / plan lock."""
from __future__ import annotations

PRODUCT_COLUMNS = [
    "SKU_ID",
    "SKU_CODE",
    "BARCODE",
    "FULL_NAME_U",
    "GRP_ID",
    "GRP_NAME",
    "DEPT_ID",
    "UNIT_SYMB",
    "RTPRICE",
    "STATUS",
]

# F2 / sheet danh sách khách — không NAME_U, MOBI, DISC_LVL, ISS_DATE, DUE_DATE
CUSTOMER_COLUMNS = [
    "CARD_ID",
    "NAME",
    "PHONE",
    "SEX",
    "BIRTHDAY",
    "CUST_ID",
]

# lookup_cards cho F3/F4/F5 gắn hồ sơ (vẫn cần NAME_U / MOBI / DISC_LVL)
CARD_LOOKUP_COLUMNS = [
    "CARD_ID",
    "NAME_U",
    "NAME",
    "PHONE",
    "MOBI",
    "SEX",
    "BIRTHDAY",
    "DISC_LVL",
    "CUST_ID",
]

# F3 metrics appended after aggregation
LOYALTY_METRIC_COLUMNS = [
    "CARD_ID",
    "NAME_U",
    "PHONE",
    "MOBI",
    "SEX",
    "BIRTHDAY",
    "DISC_LVL",
    "STK_ID",
    "total_value",
    "points",
    "bill_count",
]

ORDER_COLUMNS = [
    "TRANS_NUM",
    "STK_ID",
    "TRAN_DATE",
    "TRAN_TIME",
    "CARD_ID",
    "NAME_U",
    "TRANS_CODE",
    "bill_value",
]

ORDER_LINE_COLUMNS = [
    "TRANS_NUM",
    "STK_ID",
    "TRAN_DATE",
    "TRAN_TIME",
    "CARD_ID",
    "NAME_U",
    "IDX",
    "SKU_ID",
    "SKU_CODE",
    "FULL_NAME_U",
    "QTY",
    "UNIT_SYMB",
    # line_total = AMOUNT+SURPLUS+VAT on the STRANS row (not raw AMOUNT)
    "line_total",
    "bill_value",
    "TRANS_CODE",
]

# F4/F5 export/preview — không IDX, QTY (AMOUNT cũng không xuất)
F4_ORDER_LINE_COLUMNS = [c for c in ORDER_LINE_COLUMNS if c not in {"IDX", "QTY"}]
F5_ORDER_LINE_COLUMNS = [c for c in ORDER_LINE_COLUMNS if c not in {"IDX", "QTY"}]

TEXT_DECODE_COLUMNS = {
    "NAME",
    "FULL_NAME",
    "GRP_NAME",
    "REMARK",
    "ADDRESS",
}

POINTS_DIVISOR = 50_000.0


def points_from_value(total_value: float | int | None) -> float:
    """Loyalty points = floor(total_value / 50_000). Always round down after divide."""
    import math

    try:
        v = float(total_value or 0)
    except (TypeError, ValueError):
        return 0.0
    if v != v:  # NaN
        return 0.0
    return float(math.floor(v / POINTS_DIVISOR))

STK_PRESETS = ["10001", "10004", "10005"]

BILL_VALUE_SQL = (
    "(ISNULL(AMOUNT,0)+ISNULL(SURPLUS,0)+ISNULL(VAT_AMT,0))"
)

LINE_VALUE_SQL = BILL_VALUE_SQL
