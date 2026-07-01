#!/usr/bin/env python3
"""Generate data_dictionary/tables/db1|db2/*.md from JSON schema exports + exploration report."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB1_JSON = ROOT / "docs" / "JSON_F52E2B61-18A1-11d1-B105-00805F49916B3.json"
DB2_JSON = ROOT / "docs" / "JSON_F52E2B61-18A1-11d1-B105-00805F49916B5.json"
TABLES_DIR = ROOT / "data_dictionary" / "tables"
DB1_TABLES_DIR = TABLES_DIR / "db1"
DB2_TABLES_DIR = TABLES_DIR / "db2"

# Rolling window between db1 (history) and db2 (live + recent)
TEMPORAL_CUTOFF_RULE = (
    "cutoff = ngày 1 của tháng trước (so với ngày chạy query). "
    "Ví dụ hôm nay 22/06/2026 → cutoff = 2026-05-01."
)
TEMPORAL_DB2_RULE = "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
TEMPORAL_DB1_RULE = "TRAN_DATE < cutoff (lịch sử từ tháng trước đó nữa trở về quá khứ)."

# --- Table-level semantics (from DB_EXPLORATION_REPORT.md) ---
TABLE_META: dict[str, dict] = {
    "STRANS": {
        "title": "STRANS",
        "description": "Chi tiết từng dòng trên chứng từ bán: SKU, số lượng, giá, chiết khấu, VAT, quà tặng.",
        "shard_key_column": "TRAN_DATE",
        "join_keys": "TRANS_NUM + TRANS_CODE + TRAN_DATE → TRANSHDR / PMTRANS",
    },
    "PMTRANS": {
        "title": "PMTRANS",
        "description": "Thanh toán bill và quỹ: TRANS_CODE=221 (bill), 008 (thu/chi quỹ), 222 (loại khác — xem domain_definitions).",
        "shard_key_column": "TRAN_DATE",
        "join_keys": "TRANS_NUM + TRANS_CODE → TRANSHDR, STRANS",
    },
    "TRANSHDR_ARC": {
        "title": "TRANSHDR_ARC",
        "description": "Archive header chứng từ giao dịch (nhiều TRANS_CODE: 113 bán lẻ, 221 thanh toán, …). Lọc TRANS_CODE=113 khi cần tổng bill bán.",
        "data_source": "db1",
        "physical_pattern": "TRANSHDR_ARC",
        "shard_key_column": "TRAN_DATE",
        "temporal_scope": "history",
        "temporal_rule": TEMPORAL_DB1_RULE,
        "join_keys": "TRANS_NUM + TRANS_CODE → STRANS, PMTRANS",
        "notes": f"Chỉ giao dịch trước cutoff. {TEMPORAL_CUTOFF_RULE}",
    },
    "TRANSHDR": {
        "title": "TRANSHDR",
        "description": "Header chứng từ giao dịch gần đây (db2) — cùng schema TRANSHDR_ARC. Bill bán lẻ thường TRANS_CODE=113.",
        "data_source": "db2",
        "physical_pattern": "TRANSHDR",
        "shard_key_column": "TRAN_DATE",
        "temporal_scope": "recent",
        "temporal_rule": TEMPORAL_DB2_RULE,
        "join_keys": "TRANS_NUM + TRANS_CODE → STRANS, PMTRANS",
        "notes": f"Giao dịch ~2 tháng gần nhất. {TEMPORAL_CUTOFF_RULE}",
    },
    "CRDTRANS_ARC": {
        "title": "CRDTRANS_ARC",
        "description": "Giao dịch thẻ loyalty / điểm — archive lịch sử trên db1.",
        "data_source": "db1",
        "physical_pattern": "CRDTRANS_ARC",
        "shard_key_column": "TRAN_DATE",
        "temporal_scope": "history",
        "temporal_rule": TEMPORAL_DB1_RULE,
        "join_keys": "CARD_ID → CSCARD (db2); TRANS_NUM liên quan bill",
        "notes": f"Chỉ giao dịch trước cutoff. {TEMPORAL_CUTOFF_RULE}",
    },
    "CRDTRANS": {
        "title": "CRDTRANS",
        "description": "Giao dịch thẻ loyalty gần đây trên db2 — schema giống CRDTRANS_ARC.",
        "data_source": "db2",
        "physical_pattern": "CRDTRANS",
        "shard_key_column": "TRAN_DATE",
        "temporal_scope": "recent",
        "temporal_rule": TEMPORAL_DB2_RULE,
        "join_keys": "CARD_ID → CSCARD",
        "notes": f"Giao dịch ~2 tháng gần nhất. {TEMPORAL_CUTOFF_RULE}",
    },
    "CRDTRANS_TMP": {
        "title": "CRDTRANS_TMP",
        "description": "Staging giao dịch thẻ trước khi post — không dùng báo cáo chính thức.",
        "data_source": "db2",
        "physical_pattern": "CRDTRANS_TMP",
    },
    "STRANS_TMP": {
        "title": "STRANS_TMP",
        "description": "Staging chi tiết dòng bán trước khi post.",
        "data_source": "db2",
        "physical_pattern": "STRANS_TMP",
    },
    "SUSPEND": {
        "title": "SUSPEND",
        "description": "Bill treo tại quầy (chưa hoàn tất) — schema gần STRANS.",
        "data_source": "db2",
        "physical_pattern": "SUSPEND",
    },
    "CASH_ST": {
        "title": "CASH_ST",
        "description": "Kiểm đếm quỹ tiền mặt theo ca — đếm số tờ theo mệnh giá (TRANS_CODE=010).",
        "data_source": "db2",
    },
    "CTRANS": {
        "title": "CTRANS",
        "description": "Dòng công nợ / thanh toán công nợ gắn chứng từ (DEBT_NO, ACCOUNT_ID); có thể TRANS_CODE=113.",
        "data_source": "db2",
    },
    "CUSTOMER": {
        "title": "CUSTOMER",
        "description": "Master khách hàng B2B/B2C — chỉ trên db2 (live).",
        "data_source": "db2",
        "temporal_scope": "master",
    },
    "CSCARD": {
        "title": "CSCARD",
        "description": "Master thẻ loyalty.",
        "data_source": "db2",
    },
    "CRD_INFO": {
        "title": "CRD_INFO",
        "description": "Số dư tích lũy điểm theo kỳ và chương trình.",
        "data_source": "db2",
    },
    "CUSTHIST": {
        "title": "CUSTHIST",
        "description": "Lịch sử mua theo SKU/khách.",
        "data_source": "db2",
    },
    "CustSumm": {
        "title": "CustSumm",
        "description": "Tóm tắt KH + thẻ (denormalized).",
        "data_source": "db2",
    },
    "SKU_DEF": {
        "title": "SKU_DEF",
        "description": "Master sản phẩm (SKU), nhóm hàng, đơn vị — chỉ trên db2.",
        "data_source": "db2",
        "temporal_scope": "master",
    },
    "PLU": {
        "title": "PLU",
        "description": "Giá bán theo PLU/quầy và hiệu lực.",
        "data_source": "db2",
    },
    "BARCODE": {
        "title": "BARCODE",
        "description": "Barcode phụ và quy đổi đơn vị cho SKU.",
        "data_source": "db2",
    },
    "ASSOLST": {
        "title": "ASSOLST",
        "description": "Header combo/bundle khuyến mãi.",
        "data_source": "db2",
    },
    "ASSO_INF": {
        "title": "ASSO_INF",
        "description": "Thành phần trong combo/bundle.",
        "data_source": "db2",
    },
    "sku_activity": {
        "title": "sku_activity",
        "description": "Ngày bán/nhập đầu–cuối theo cửa hàng × SKU.",
        "data_source": "db2",
    },
    "SUPPLIER": {
        "title": "SUPPLIER",
        "description": "Master nhà cung cấp.",
        "data_source": "db2",
    },
    "PARTNER": {
        "title": "PARTNER",
        "description": "Master đối tác (đại lý, guarantor, …).",
        "data_source": "db2",
    },
    "HISRTPR": {
        "title": "HISRTPR",
        "description": "Lịch sử giá bán lẻ theo ngày × SKU × cửa hàng.",
        "data_source": "db2",
    },
    "HISSPPR": {
        "title": "HISSPPR",
        "description": "Lịch sử giá mua NCC.",
        "data_source": "db2",
    },
    "RDISCINF": {
        "title": "RDISCINF",
        "description": "Rule khuyến mãi: điều kiện, đối tượng, thời gian.",
        "data_source": "db2",
    },
    "STK_DTL": {
        "title": "STK_DTL",
        "description": "Sổ chi tiết tồn kho theo kỳ (nhập/xuất/bán/điều chuyển).",
        "data_source": "db2",
    },
    "ST_ORDER": {
        "title": "ST_ORDER",
        "description": "Đơn đặt hàng / chuyển kho.",
        "data_source": "db2",
    },
    "INV_HDR": {
        "title": "INV_HDR",
        "description": "Header hóa đơn GTGT điện tử.",
        "data_source": "db2",
    },
    "INV_ISS": {
        "title": "INV_ISS",
        "description": "Chi tiết phát hành HĐ GTGT, gắn TRANS_NUM bán lẻ.",
        "data_source": "db2",
    },
    "PMCRDINF": {
        "title": "PMCRDINF",
        "description": "Thông tin thẻ PM (gift/voucher).",
        "data_source": "db2",
    },
    "PMCRDISS": {
        "title": "PMCRDISS",
        "description": "Phiếu xuất thẻ PM cho khách (TRANS_CODE thường 821).",
        "data_source": "db2",
    },
    "PMCRDRCV": {
        "title": "PMCRDRCV",
        "description": "Thu hồi / nhận lại thẻ PM.",
        "data_source": "db2",
    },
    "PMCRDSTK": {
        "title": "PMCRDSTK",
        "description": "Tồn thẻ PM tại cửa hàng (seri).",
        "data_source": "db2",
    },
    "ACCOUNT": {
        "title": "ACCOUNT",
        "description": "Tài khoản công nợ KH/NCC/NV.",
        "data_source": "db2",
    },
    "DEBT": {
        "title": "DEBT",
        "description": "Chứng từ công nợ.",
        "data_source": "db2",
    },
    "WebRpt_sales_sku_daily": {
        "title": "WebRpt_sales_sku_daily",
        "description": "Báo cáo doanh thu SKU × cửa hàng × ngày (ưu tiên cho aggregate).",
        "data_source": "db2",
    },
    "WebRpt_inventory_daily": {
        "title": "WebRpt_inventory_daily",
        "description": "Báo cáo tồn kho ngày: on-hand, DOI, trạng thái.",
        "data_source": "db2",
    },
    "WebRpt_rfm_snapshot": {
        "title": "WebRpt_rfm_snapshot",
        "description": "Snapshot RFM loyalty theo thẻ/khách.",
        "data_source": "db2",
    },
}

# Table-specific column overrides
TABLE_COLUMN_EXACT: dict[str, str] = {
    "CSCARD.IDX": "ID nội bộ bản ghi thẻ",
    "CRD_INFO.IDX": "ID nội bộ bản ghi tích lũy",
    "RDISCINF.IDX": "ID rule khuyến mãi",
    "CSCARD.NAME": "Tên chủ thẻ",
    "CSCARD.DISC_LVL": "Mức chiết khấu / hạng thẻ",
    "CSCARD.DISC_CODE": "Mã chương trình chiết khấu thẻ",
    "CSCARD.BONUS_PC": "Phần trăm thưởng",
    "CSCARD.ISS_DATE": "Ngày phát hành thẻ",
    "CSCARD.DUE_DATE": "Ngày hết hạn thẻ",
    "CSCARD.BIRTHDAY": "Ngày sinh",
    "CSCARD.RS_CODE": "Mã lý do / trạng thái thẻ",
    "WebRpt_sales_sku_daily.bill_count": "Số bill trong ngày",
    "WebRpt_sales_sku_daily.mdisc_total": "Tổng chiết khấu manual",
    "WebRpt_sales_sku_daily.tdisc_total": "Tổng chiết khấu transaction",
    "WebRpt_sales_sku_daily.cdisc_total": "Tổng chiết khấu coupon",
    "WebRpt_sales_sku_daily.gdisc_total": "Tổng chiết khấu gift",
    "WebRpt_sales_sku_daily.discount_total": "Tổng chiết khấu",
    "WebRpt_sales_sku_daily.tdadd_total": "Tổng phụ thu transaction",
    "WebRpt_sales_sku_daily.mdadd_total": "Tổng phụ thu manual",
    "WebRpt_sales_sku_daily.gift_qty": "Số lượng quà tặng",
    "WebRpt_sales_sku_daily.free_qty": "Số lượng hàng tặng",
    "WebRpt_sales_sku_daily.free_cogs": "Giá vốn hàng tặng",
    "WebRpt_inventory_daily.DMS": "Chỉ số DMS (days of supply)",
    "STK_DTL.PRD_CODE": "Mã kỳ tồn kho",
    "TRANSHDR.IDX": "Chỉ số dòng header (thường 0)",
    "TRANSHDR_ARC.IDX": "Chỉ số dòng header (thường 0)",
    "CASH_ST.VALUE": "Mệnh giá tờ tiền (200, 500, 1000, … VND)",
    "CASH_ST.QTY": "Số tờ theo mệnh giá trong ca",
    "CTRANS.BILL": "Tham chiếu bill / chứng từ gốc",
    "CTRANS.DEBT_NO": "Số chứng từ công nợ",
    "CTRANS.ACCOUNT_ID": "Mã tài khoản công nợ",
}

COLUMN_EXACT: dict[str, str] = {
    "TRANS_NUM": "Số chứng từ / bill; join header ↔ dòng ↔ thanh toán",
    "TRANS_CODE": "Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …)",
    "TRAN_DATE": "Ngày giao dịch",
    "TRAN_DATE_DB1": "Ngày giao dịch; chọn shard db1 theo YYYYMM",
    "TRAN_DATE_DB2": "Ngày giao dịch (bảng live db2, không shard)",
    "TRAN_TIME": "Giờ giao dịch (HH:MM)",
    "DUE_DATE": "Hạn thanh toán / hạn giao",
    "EF_DATE": "Ngày hiệu lực",
    "BU_ID": "Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200)",
    "REF_NO": "Số tham chiếu chứng từ liên quan",
    "REF_DATE": "Ngày tham chiếu",
    "REF": "Mã/tham chiếu nội bộ",
    "STK_ID": "Mã cửa hàng / kho (10001, 10004, 10005, …)",
    "STK_TYPE": "Loại kho",
    "OSTK_ID": "Kho đích / kho đối ứng",
    "OSTK_TYPE": "Loại kho đối ứng",
    "SKU_ID": "Mã sản phẩm nội bộ",
    "SKU_CODE": "Mã SKU hiển thị",
    "CARD_ID": "Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng",
    "CUST_ID": "Mã khách hàng",
    "CUST_NAME": "Tên khách hàng",
    "CUST_CODE": "Mã khách (hiển thị)",
    "SUPP_ID": "Mã nhà cung cấp",
    "SUPP_NAME": "Tên nhà cung cấp",
    "SUPP_CODE": "Mã NCC hiển thị",
    "IDX": "Số thứ tự dòng trong chứng từ",
    "BEGIN_QTY": "Tồn đầu kỳ — số lượng",
    "BEGIN_AMT": "Tồn đầu kỳ — giá trị",
    "BEG_QTY": "Số dư đầu kỳ — số lượng",
    "BEG_AMT": "Số dư đầu kỳ — giá trị",
    "QTY": "Số lượng",
    "SAL_QTY": "Số lượng bán",
    "STK_QTY": "Số lượng tồn / xuất kho",
    "AMOUNT": "Thành tiền / số tiền (ngữ cảnh theo bảng)",
    "PRICE": "Đơn giá",
    "RTPRICE": "Giá bán lẻ",
    "LASTRTPR": "Giá bán lẻ gần nhất",
    "SPPRICE": "Giá mua NCC",
    "LASTSPPR": "Giá mua NCC gần nhất",
    "PMT_CODE": "Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space)",
    "PMT_MODE": "Chế độ thanh toán",
    "PMT_TYPE": "Loại thanh toán",
    "PMT_TIME": "Thời điểm thanh toán",
    "CYS": "Loại tiền (VND)",
    "FOREX_RATE": "Tỷ giá ngoại tệ",
    "FOREX_AMT": "Số tiền quy đổi ngoại tệ",
    "FOREX_CYS": "Loại tiền ngoại tệ",
    "ROUNDIFF": "Chênh lệch làm tròn thanh toán",
    "MARK": "Điểm tích lũy; ~AMOUNT/50000 trên CRDTRANS 811",
    "MARK_VAL": "Giá trị quy đổi điểm",
    "MARK_MUL": "Hệ số nhân điểm",
    "ACML_CODE": "Mã chương trình tích lũy",
    "DISCOUNT": "Giảm giá (số tiền hoặc % tùy ngữ cảnh)",
    "DISC_RATE": "Tỷ lệ chiết khấu",
    "VAT_AMT": "Tiền thuế VAT",
    "VAT_INCL": "Giá đã gồm VAT",
    "TAX_CODE": "Mã thuế",
    "TAX_RATE": "Thuế suất",
    "TAX_ID": "Mã số thuế",
    "TAX_NAME": "Tên đơn vị trên HĐ",
    "TAX_ADDR": "Địa chỉ trên HĐ",
    "TRANS_TYPE": "Phân loại giao dịch thẻ",
    "TYPE": "Loại bản ghi (ngữ cảnh theo bảng)",
    "RS_CODE": "Mã lý do (hủy, trả, …)",
    "POST": "Trạng thái post chứng từ",
    "STATUS": "Trạng thái active/duyệt",
    "ACTION": "Mã thao tác",
    "UPDATED": "Đã cập nhật (bit)",
    "WS_ID": "Mã máy trạm",
    "POS_ID": "Mã quầy POS",
    "SHIFT": "Ca làm việc",
    "USER_ID": "Mã user thao tác",
    "STAFF_ID": "Mã nhân viên",
    "REMARK": "Ghi chú nghiệp vụ",
    "NOTES": "Ghi chú bổ sung",
    "INV_TYPE": "Loại hóa đơn",
    "INV_CODE": "Mã serial HĐ",
    "INV_NO": "Số hóa đơn",
    "INV_Date": "Ngày hóa đơn",
    "INV_DATE": "Ngày hóa đơn",
    "INV_VATAMT": "VAT trên hóa đơn",
    "INV_REF": "Tham chiếu hóa đơn",
    "INV_POS": "Vị trí / quầy HĐ",
    "EINV": "Hóa đơn điện tử",
    "EINV_STATUS": "Trạng thái HĐ điện tử",
    "ASSO_ID": "Mã combo/bundle",
    "ASSO_QTY": "Số lượng trong combo",
    "ASSO_TYPE": "Loại combo",
    "KIT_ID": "Mã kit",
    "KIT_QTY": "Số lượng kit",
    "PACK_ID": "Mã gói đóng",
    "PACK_QTY": "Số lượng gói",
    "UNIT_SYMB": "Ký hiệu đơn vị (GOI, HOP, KG, …)",
    "BASE_UNIT": "Đơn vị cơ sở",
    "UNITCONV": "Hệ số quy đổi đơn vị",
    "BARCODE": "Mã vạch",
    "IMPORT": "Cờ nhập / import",
    "COMM_AMT": "Tiền hoa hồng",
    "COMM_RATE": "Tỷ lệ hoa hồng",
    "SURPLUS": "Phụ phí / surplus",
    "ACCOUNT_ID": "Mã tài khoản công nợ",
    "DEBT_NO": "Số chứng từ công nợ",
    "DEBT_DATE": "Ngày phát sinh công nợ",
    "DEBT_AMT": "Số tiền công nợ",
    "PAID_AMT": "Số tiền đã thanh toán",
    "CR_LIMIT": "Hạn mức tín dụng",
    "CR_AMT": "Dư nợ hiện tại",
    "report_date": "Ngày báo cáo",
    "snapshot_date": "Ngày snapshot",
    "stk_id": "Mã cửa hàng",
    "sku_id": "Mã SKU",
    "skucode": "Mã SKU hiển thị",
    "skuname": "Tên sản phẩm",
    "stkname": "Tên cửa hàng",
    "grp_id": "Mã nhóm hàng",
    "grpname": "Tên nhóm hàng",
    "qty": "Số lượng bán trong ngày",
    "revenue": "Doanh thu",
    "cogs": "Giá vốn",
    "gross_profit": "Lãi gộp",
    "qty_onhand": "Tồn kho hiện tại",
    "value_onhand": "Giá trị tồn",
    "doi_days": "Days of inventory",
    "days_no_sale": "Số ngày không bán",
    "stock_status": "Trạng thái tồn (WARN - Discontinued, INFO - Never Sold, …)",
    "card_id": "Mã thẻ",
    "cust_id": "Mã khách",
    "rfm_segment": "Phân khúc RFM: At Risk, Loyal, Others",
    "rfm_score": "Điểm RFM",
    "recency_days": "Số ngày từ lần mua gần nhất",
    "frequency": "Tần suất mua",
    "monetary": "Tổng chi tiêu",
    "card_type": "Loại thẻ",
    "refreshed_at": "Thời điểm làm mới báo cáo",
    "VALUE": "Giá trị / mệnh giá (ngữ cảnh theo bảng — CASH_ST: mệnh giá tờ tiền)",
    "VALUE_AMT": "Mệnh giá / giá trị thẻ PM",
    "FR_SERI": "Seri thẻ PM từ",
    "TO_SERI": "Seri thẻ PM đến",
    "FR_CARDID": "Thẻ PM nguồn",
    "TO_CARDID": "Thẻ PM đích",
    "PREFIX": "Prefix seri thẻ PM (@P)",
    "Name": "Tên khách (CustSumm)",
    "Amount": "Tổng mua (CustSumm)",
    "Phone": "Điện thoại",
    "Mobil": "Di động",
    "NAME": "Tên",
    "OPEN_DATE": "Ngày mở / tạo",
    "MODI_DATE": "Ngày sửa gần nhất",
    "CLOSE_DATE": "Ngày đóng",
    "LAST_DATE": "Ngày giao dịch / cập nhật gần nhất",
    "PERSON_ID": "CMND/CCCD",
    "EMAIL": "Email",
    "PHONE": "Điện thoại",
    "MOBI": "Di động",
    "ADDRESS": "Địa chỉ",
    "SEX": "Giới tính",
    "DISC_LVL": "Mức chiết khấu",
    "DISC_CODE": "Mã chiết khấu",
    "PASSCODE": "Mã PIN thẻ",
    "PLC_ID": "Mã địa phương",
    "NODE_ID": "Mã node / chi nhánh hệ thống",
    "COMP_ID": "Mã công ty",
    "GRP_ID": "Mã nhóm",
    "PLU_CODE": "Mã PLU",
    "MERC_TYPE": "Loại hàng hóa",
    "ITEM_TYPE": "Loại dòng hàng",
    "ORD_QTY": "Số lượng đặt",
    "DLV_QTY": "Số lượng đã giao",
    "ORD_PRICE": "Giá đặt hàng",
    "DELIVER_DT": "Ngày giao hàng",
    "FINISH_DT": "Ngày hoàn tất",
    "ACTIVATE": "Đã kích hoạt",
    "SALEABLE": "Được phép bán",
    "SALE_AMT": "Số tiền bán",
    "BAL_AMT": "Số dư",
    "ISS_QTY": "SL xuất",
    "RCV_QTY": "SL nhận",
    "STP_QTY": "SL dừng/hủy",
    "first_sale_date": "Ngày bán đầu tiên",
    "last_sale_date": "Ngày bán gần nhất",
    "first_receipt_date": "Ngày nhập đầu tiên",
    "last_receipt_date": "Ngày nhập gần nhất",
    "updated_at": "Thời điểm cập nhật",
    "DESCRIPT": "Mô tả",
    "ISDEFAULT": "Mặc định",
    "DMS": "Days of supply",
    "bill_count": "Số bill trong ngày",
    "mdisc_total": "Tổng chiết khấu manual",
    "tdisc_total": "Tổng chiết khấu transaction",
    "cdisc_total": "Tổng chiết khấu coupon",
    "gdisc_total": "Tổng chiết khấu gift",
    "discount_total": "Tổng chiết khấu",
    "tdadd_total": "Tổng phụ thu transaction",
    "mdadd_total": "Tổng phụ thu manual",
    "gift_qty": "Số lượng quà tặng",
    "free_qty": "Số lượng hàng tặng",
    "free_cogs": "Giá vốn hàng tặng",
}

# Prefix/suffix patterns (applied if no exact match)
COLUMN_PATTERNS: list[tuple[str, str]] = [
    (r"^CDISC_", "Chiết khấu coupon: "),
    (r"^TDISC_", "Chiết khấu transaction: "),
    (r"^MDISC_", "Chiết khấu manual: "),
    (r"^GDISC_", "Chiết khấu gift/khuyến mãi: "),
    (r"^GIFT_", "Quà tặng: "),
    (r"^CCOMM_", "Hoa hồng coupon: "),
    (r"^TCOMM_", "Hoa hồng transaction: "),
    (r"^MCOMM_", "Hoa hồng manual: "),
    (r"^GCOMM_", "Hoa hồng gift: "),
    (r"^TDADD_", "Phụ thu transaction: "),
    (r"^MDADD_", "Phụ thu manual: "),
    (r"^FR(SUPP|DEAL|CUST|TRF|MUL|BAL|CQTY|CAMT)_", "Đầu kỳ — movement: "),
    (r"^TO(SUPP|DEAL|CUST|TRF|MUL|BAL|CQTY|CAMT)_", "Cuối kỳ — movement: "),
    (r"^BEG_", "Số dư đầu kỳ: "),
    (r"^BUY_", "Phát sinh mua/tích: "),
    (r"^OTH_", "Phát sinh khác: "),
    (r"^RFN_", "Hoàn / refund điểm: "),
    (r"^RBT_", "Rebate: "),
    (r"^INV_", "Hóa đơn: "),
    (r"^EXP_", "Xuất / export: "),
    (r"^IMP_", "Nhập / import: "),
    (r"_DATE$", "Ngày"),
    (r"_AMT$", "Số tiền"),
    (r"_QTY$", "Số lượng"),
    (r"_RATE$", "Tỷ lệ"),
    (r"_CODE$", "Mã"),
]


def db1_table_meta(table: str, base: dict) -> dict:
    """Per-table metadata for db1 (history archive)."""
    shared = {**base, "data_source": "db1", "temporal_scope": "history", "temporal_rule": TEMPORAL_DB1_RULE}
    if table == "STRANS":
        return {
            **shared,
            "physical_pattern": "STRANS_{YYYYMM}",
            "notes": (
                f"Lịch sử trước cutoff; chọn shard YYYYMM theo TRAN_DATE. "
                f"{TEMPORAL_CUTOFF_RULE} AMOUNT=0 thường là dòng quà/KM."
            ),
        }
    if table == "PMTRANS":
        return {
            **shared,
            "physical_pattern": "PMTRANS_{YYYYMM}",
            "notes": (
                f"Lịch sử trước cutoff; chọn shard YYYYMM theo TRAN_DATE. {TEMPORAL_CUTOFF_RULE} "
                "008 thường có AMOUNT âm (chi quỹ)."
            ),
        }
    if table == "TRANSHDR_ARC":
        return {
            **shared,
            "notes": (
                f"Nhiều TRANS_CODE trong cùng bảng — lọc 113 cho bill bán. "
                f"Chỉ giao dịch trước cutoff. {TEMPORAL_CUTOFF_RULE}"
            ),
        }
    return {**shared, "notes": shared.get("notes", f"Chỉ giao dịch trước cutoff. {TEMPORAL_CUTOFF_RULE}")}


def db2_table_meta(table: str, base: dict) -> dict:
    """Per-table metadata for db2 (live + master + recent transactions)."""
    if table.startswith("WebRpt_"):
        return {
            **base,
            "data_source": "db2",
            "temporal_scope": "report",
            "temporal_rule": "Báo cáo tổng hợp trên db2 — lọc theo report_date / snapshot_date.",
        }
    if table in ("SUSPEND", "STRANS_TMP", "CRDTRANS_TMP"):
        return {
            **base,
            "data_source": "db2",
            "temporal_scope": "staging",
            "temporal_rule": "Dữ liệu tạm POS — không dùng báo cáo chính thức.",
        }
    scope = base.get("temporal_scope", "recent")
    if scope == "master":
        return {
            **base,
            "data_source": "db2",
            "temporal_scope": "master",
            "temporal_rule": "Không phụ thuộc cutoff — danh mục / báo cáo tổng hợp luôn trên db2.",
        }
    shared = {**base, "data_source": "db2", "temporal_scope": scope, "temporal_rule": TEMPORAL_DB2_RULE}
    if table == "STRANS":
        return {
            **shared,
            "physical_pattern": "STRANS",
            "notes": (
                f"Giao dịch ~2 tháng gần nhất (không shard). {TEMPORAL_CUTOFF_RULE} "
                "AMOUNT=0 thường là dòng quà/KM."
            ),
        }
    if table == "PMTRANS":
        return {
            **shared,
            "physical_pattern": "PMTRANS",
            "notes": f"Thanh toán ~2 tháng gần nhất. {TEMPORAL_CUTOFF_RULE}",
        }
    if table in ("TRANSHDR", "CRDTRANS"):
        return {**shared, "notes": base.get("notes", f"Giao dịch ~2 tháng gần nhất. {TEMPORAL_CUTOFF_RULE}")}
    return shared


DB1_TABLES = ("STRANS", "PMTRANS", "CRDTRANS_ARC", "TRANSHDR_ARC")

DB2_ONLY_TABLES = tuple(
    k
    for k in TABLE_META
    if k not in DB1_TABLES and TABLE_META[k].get("data_source", "db2") == "db2"
)

# Transaction tables on both DBs (db2 copy uses live schema)
DB2_TRANSACTION_TABLES = ("STRANS", "PMTRANS")


def describe_column(col: str, table: str = "", data_source: str = "") -> str:
    tkey = f"{table}.{col}"
    if tkey in TABLE_COLUMN_EXACT:
        return TABLE_COLUMN_EXACT[tkey]
    if col == "TRAN_DATE":
        if data_source == "db1":
            return COLUMN_EXACT["TRAN_DATE_DB1"]
        if data_source == "db2":
            return COLUMN_EXACT["TRAN_DATE_DB2"]
    if col in COLUMN_EXACT:
        return COLUMN_EXACT[col]
    for pattern, hint in COLUMN_PATTERNS:
        if re.search(pattern, col):
            return f"{hint}{col}"
    return f"Cột {col}"


def load_json_tables(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    out: dict[str, dict] = {}
    for t in data:
        name = t["table_name"]
        out[name] = {
            "record_count": t.get("record_count"),
            "columns": [(c["column_name"], c["data_type"]) for c in t["columns"]],
        }
    return out


def pick_schema(table: str, db1: dict, db2: dict, *, data_source: str) -> list[tuple[str, str]]:
    if data_source == "db2" and table in db2:
        return db2[table]["columns"]
    if table in db1:
        return db1[table]["columns"]
    if table in db2:
        return db2[table]["columns"]
    # logical db1 shard — use STRANS from db1 first shard
    for key, meta in db1.items():
        if key.startswith(table + "_") or key == table:
            return meta["columns"]
    raise KeyError(table)


def yaml_scalar(value: str) -> str:
    """Emit a YAML scalar safe for frontmatter (colons, unicode)."""
    if re.search(r"[:#\n\"'&*!|>]", value) or value.startswith(("{", "[", "-")):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def render_table_md(table: str, columns: list[tuple[str, str]], meta: dict) -> str:
    lines = ["---"]
    lines.append(f"logical_table: {meta.get('title', table)}")
    lines.append(f"data_source: {meta.get('data_source', 'db2')}")
    if meta.get("physical_pattern"):
        lines.append(f"physical_pattern: {yaml_scalar(meta['physical_pattern'])}")
    if meta.get("shard_key_column"):
        lines.append(f"shard_key_column: {meta['shard_key_column']}")
    if meta.get("temporal_scope"):
        lines.append(f"temporal_scope: {meta['temporal_scope']}")
    if meta.get("temporal_rule"):
        lines.append(f"temporal_rule: {yaml_scalar(meta['temporal_rule'])}")
    lines.append(f"description: {yaml_scalar(meta['description'])}")
    lines.append(f"column_count: {len(columns)}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {meta.get('title', table)}")
    lines.append("")
    lines.append(meta["description"])
    if meta.get("join_keys"):
        lines.append("")
        lines.append(f"**Liên kết:** {meta['join_keys']}")
    if meta.get("notes"):
        lines.append("")
        lines.append(f"**Lưu ý:** {meta['notes']}")
    lines.append("")
    lines.append("| column | type | description |")
    lines.append("|--------|------|-------------|")
    for col, dtype in columns:
        desc = describe_column(col, table, meta.get("data_source", "")).replace("|", "\\|")
        lines.append(f"| {col} | {dtype} | {desc} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    db1 = load_json_tables(DB1_JSON)
    db2 = load_json_tables(DB2_JSON)

    DB1_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    DB2_TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # Remove flat legacy files under tables/
    for stale in ("sales", "customers", "transactions"):
        p = TABLES_DIR / f"{stale}.md"
        if p.exists():
            p.unlink()
    for p in TABLES_DIR.glob("*.md"):
        p.unlink()

    written_db1: list[str] = []
    for table in DB1_TABLES:
        base = TABLE_META[table]
        meta = db1_table_meta(table, base)
        columns = pick_schema(table, db1, db2, data_source="db1")
        content = render_table_md(table, columns, meta)
        (DB1_TABLES_DIR / f"{table}.md").write_text(content, encoding="utf-8")
        written_db1.append(table)

    written_db2: list[str] = []
    for table in DB2_ONLY_TABLES:
        base = TABLE_META[table]
        meta = db2_table_meta(table, base)
        columns = pick_schema(table, db1, db2, data_source="db2")
        content = render_table_md(table, columns, meta)
        (DB2_TABLES_DIR / f"{table}.md").write_text(content, encoding="utf-8")
        written_db2.append(table)

    for table in DB2_TRANSACTION_TABLES:
        base = TABLE_META[table]
        meta = db2_table_meta(table, base)
        columns = pick_schema(table, db1, db2, data_source="db2")
        content = render_table_md(table, columns, meta)
        (DB2_TABLES_DIR / f"{table}.md").write_text(content, encoding="utf-8")
        written_db2.append(table)

    print(f"Wrote {len(written_db1)} files to {DB1_TABLES_DIR}")
    print(f"Wrote {len(written_db2)} files to {DB2_TABLES_DIR}")


if __name__ == "__main__":
    main()
