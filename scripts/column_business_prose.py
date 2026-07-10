"""Natural-language business prose for column semantic docs — no sample dumps."""

from __future__ import annotations

import re
from typing import Any

from column_semantic_registry import SEMANTIC_BUSINESS
from column_prose_domains import compose_domain_prose

# Table-level business context (anchors multi-table columns).
TABLE_CONTEXT: dict[str, str] = {
    "CUSTOMER": "danh mục master khách hàng",
    "CSCARD": "master thẻ khách hàng thân thiết",
    "CRD_INFO": "tổng hợp điểm và lịch sử mua theo thẻ",
    "CRDTRANS": "giao dịch tích điểm live (db2)",
    "CRDTRANS_ARC": "giao dịch điều chỉnh / đổi quà lưu archive (db1)",
    "CRDTRANS_TMP": "giao dịch tích điểm tạm",
    "STRANS": "dòng bán hàng POS",
    "STRANS_TMP": "dòng bán tạm / suspend",
    "TRANSHDR": "header bill bán lẻ",
    "TRANSHDR_ARC": "header bill đã archive",
    "PMTRANS": "dòng thanh toán / quỹ bill",
    "SKU_DEF": "master sản phẩm (SKU)",
    "BARCODE": "bảng barcode ↔ SKU",
    "SUPPLIER": "master nhà cung cấp",
    "PARTNER": "đối tác / khách B2B",
    "INV_ISS": "phiếu xuất kho",
    "INV_HDR": "header hóa đơn mua / nhập",
    "STK_DTL": "tồn kho chi tiết theo cửa hàng",
    "SUSPEND": "bill đang treo / chưa hoàn tất",
    "ST_ORDER": "đơn đặt hàng nội bộ",
    "CASH_ST": "quỹ tiền mặt theo mệnh giá",
    "PMCRDINF": "master thẻ PM / voucher",
    "CUSTHIST": "lịch sử thay đổi thông tin khách",
    "DEBT": "công nợ khách / NCC",
    "RDISCINF": "rule khuyến mãi / chiết khấu",
    "CTRANS": "chứng từ kế toán / công nợ",
    "ACCOUNT": "tài khoản kế toán công nợ",
    "ASSOLST": "master combo / bundle",
    "ASSO_INF": "chi tiết thành phần combo",
    "WebRpt_sales_sku_daily": "báo cáo doanh số SKU theo ngày",
    "WebRpt_inventory_daily": "báo cáo tồn kho theo ngày",
    "WebRpt_rfm_snapshot": "snapshot RFM khách hàng",
}

# Column → base nghiệp vụ (tiếng Việt tự nhiên).
COLUMN_BASE_GLOSS: dict[str, str] = {
    "CUST_NAME": "Tên khách hàng",
    "CUST_ID": "Mã khách hàng nội bộ",
    "CUST_CODE": "Mã khách hiển thị / mã tra cứu",
    "SKU_ID": "Mã sản phẩm nội bộ (join master SKU)",
    "SKU_CODE": "Mã SKU hiển thị (thường 8 chữ số, có thể thiếu số 0 đầu)",
    "BARCODE": "Mã vạch quét tại quầy (EAN/GTIN)",
    "TRANS_NUM": "Số chứng từ / số bill — khóa join header ↔ dòng ↔ thanh toán",
    "TRANS_CODE": "Loại chứng từ (phân biệt bán lẻ, thanh toán, tích điểm, …)",
    "TRANS_TYPE": "Kiểu giao dịch chi tiết hơn TRANS_CODE",
    "TRAN_DATE": "Ngày giao dịch",
    "TRAN_TIME": "Giờ giao dich (HH:MM trên POS)",
    "STK_ID": "Mã cửa hàng / siêu thị phát sinh giao dịch",
    "CARD_ID": "Mã thẻ khách hàng thân thiết",
    "CARD_ID2": "Slot thẻ phụ / mã liên kết thứ hai trên master thẻ",
    "AMOUNT": "Số tiền / giá trị giao dịch (grain phụ thuộc bảng)",
    "QTY": "Số lượng",
    "PRICE": "Đơn giá",
    "DISCOUNT": "Giảm giá / chiết khấu trên dòng",
    "MARK": "Điểm tích lũy loyalty",
    "PMT_CODE": "Hình thức thanh toán (tiền mặt, thẻ, chuyển khoản, …)",
    "REMARK": "Ghi chú do nhân viên nhập",
    "DEPT_ID": "Mã ngành hàng / phòng ban merchandise",
    "SUPP_ID": "Mã nhà cung cấp",
    "TAX_ID": "Mã số thuế",
    "TAX_NAME": "Tên đơn vị trên hóa đơn GTGT",
    "TAX_ADDR": "Địa chỉ trên hóa đơn GTGT",
    "ADDRESS": "Địa chỉ liên hệ",
    "PHONE": "Số điện thoại",
    "EMAIL": "Email liên hệ",
    "INV_NO": "Số hóa đơn",
    "PLU_CODE": "Mã PLU trên quầy",
    "BU_ID": "Mã đơn vị kinh doanh / chi nhánh logic",
    "GRP_ID": "Mã nhóm phân loại",
    "ACCOUNT_ID": "Mã tài khoản công nợ",
    "DISC_LVL": "Mức chiết khấu được hưởng",
    "OPEN_DATE": "Ngày mở / ngày tạo bản ghi",
    "MODI_DATE": "Ngày cập nhật gần nhất",
    "DUE_DATE": "Ngày đến hạn",
    "EF_DATE": "Ngày hiệu lực",
    "BIRTHDAY": "Ngày sinh khách hàng",
    "VAT_AMT": "Số tiền thuế GTGT (VAT)",
    "TAX_AMT": "Số tiền thuế",
    "TAX_RATE": "Thuế suất GTGT / thuế suất áp dụng",
    "DISCOUNT": "Giảm giá / chiết khấu trên dòng",
    "DISC_AMT": "Số tiền chiết khấu",
    "DISC_RATE": "Tỷ lệ chiết khấu (%)",
    "COMM_AMT": "Số tiền hoa hồng",
    "COMM_RATE": "Tỷ lệ hoa hồng (%)",
    "CDISC_AMT": "Số tiền chiết khấu coupon",
    "CDISC_RATE": "Tỷ lệ chiết khấu coupon (%)",
    "MDISC_AMT": "Số tiền chiết khấu khuyến mãi",
    "MDISC_RATE": "Tỷ lệ chiết khấu khuyến mãi (%)",
    "PAID_AMT": "Số tiền đã thanh toán",
    "SALE_AMT": "Doanh số / giá trị bán",
    "PRICE": "Đơn giá bán",
    "RTPRICE": "Giá bán lẻ đề xuất",
    "SPPRICE": "Giá khuyến mãi / giá đặc biệt",
    "ITEM_TYPE": "Loại mặt hàng",
    "MERC_TYPE": "Loại merchandise",
    "BEGIN_QTY": "Tồn đầu kỳ — số lượng",
    "BEGIN_AMT": "Tồn đầu kỳ — giá trị",
    "SUPP_NAME": "Tên nhà cung cấp",
    "SUPP_CODE": "Mã nhà cung cấp hiển thị",
    "MOQ": "Số lượng đặt hàng tối thiểu (MOQ)",
    "MOA": "Giá trị đơn đặt tối thiểu (MOA)",
    "STK_QTY": "Số lượng tồn kho",
    "ISS_QTY": "Số lượng xuất kho",
    "ORD_QTY": "Số lượng đặt hàng",
    "COSTPRICE": "Giá vốn / giá nhập",
    "ASSO_ID": "Mã combo / bundle",
    "ASSO_TYPE": "Loại combo",
    "ASSO_QTY": "Số lượng trong combo",
    "GIFT_SQTY": "Số lượng quà tặng",
    "GCOMM_QTY": "Số lượng quà / hàng KM trong combo",
    "DEBT_NO": "Số chứng từ công nợ",
    "DEBT_DATE": "Ngày phát sinh công nợ",
    "DEBT_AMT": "Số tiền công nợ",
    "FINE_AMT": "Số tiền phạt chậm trả",
    "ACTION": "Mã thao tác nghiệp vụ trên chứng từ",
    "COMP_ID": "Mã công ty / pháp nhân",
    "NODE_ID": "Mã node / chi nhánh hệ thống",
    "CITY": "Thành phố / tỉnh liên hệ",
    "SEX": "Giới tính khách hàng",
    "SHIFT": "Ca làm việc POS",
    "POS_ID": "Mã quầy / POS terminal",
    "WS_ID": "Mã máy trạm (workstation)",
    "USER_ID": "Mã user thao tác",
    "IMPORT": "Cờ hàng nhập khẩu",
    "FOREX_RATE": "Tỷ giá ngoại tệ",
    "FOREX_AMT": "Số tiền quy đổi ngoại tệ",
    "CYS": "Loại tiền tệ (VND, …)",
    "VAT_INCL": "Cờ giá đã bao gồm VAT",
    "SURPLUS": "Số lượng / giá trị thặng dư",
    "CNT_QTY": "Số lượng đếm / count quantity",
    "KIT_ID": "Mã bộ kit / combo kit",
    "KIT_QTY": "Số lượng trong kit",
    "PACK_QTY": "Số lượng trong pack / thùng",
    "INV_TYPE": "Loại hóa đơn / chứng từ kho",
    "INV_CODE": "Mã serial / mã hóa đơn",
    "INV_DATE": "Ngày hóa đơn",
    "INV_REF": "Tham chiếu hóa đơn liên quan",
    "INV_VATAMT": "Tiền thuế GTGT trên hóa đơn",
    "ZONE_CODE": "Mã vùng / zone cửa hàng",
    "PERSON_ID": "Mã nhân viên / người liên hệ",
    "CON_PERSON": "Người liên hệ",
    "COPIES": "Số liên in / số bản sao chứng từ",
    "CS_LEVEL": "Cấp độ chăm sóc khách hàng (customer service level)",
    "MARK_VAL": "Giá trị quy đổi điểm",
    "MARK_MUL": "Hệ số nhân điểm tích lũy",
    "RFN_AMT": "Số tiền hoàn trả",
    "RFN_RATE": "Tỷ lệ hoàn trả (%)",
    "RFN_MARK": "Điểm hoàn / điểm trả lại",
    "RBT_AMT": "Số tiền rebate",
    "CR_LIMIT": "Hạn mức công nợ",
    "CR_AMT": "Số tiền công nợ phải thu",
    "TDADD_AMT": "Số tiền phụ thu thêm (trade add-on)",
    "TDADD_RATE": "Tỷ lệ phụ thu thêm (%)",
    "MDADD_AMT": "Số tiền phụ thu markdown add-on",
    "MDADD_RATE": "Tỷ lệ phụ thu markdown (%)",
    "GDISC_AMT": "Số tiền chiết khấu quà tặng",
    "TDISC_AMT": "Số tiền chiết khấu thương mại (trade discount)",
    "TDISC_RATE": "Tỷ lệ chiết khấu thương mại (%)",
    "MARGIN": "Biên lợi nhuận (%)",
    "BASE_UNIT": "Đơn vị cơ sở quy đổi",
    "UNITCONV": "Hệ số quy đổi đơn vị",
    "UNIT_SYMB": "Ký hiệu đơn vị tính",
}

# (TABLE, COLUMN) → bổ sung ngữ cảnh khi cùng tên cột khác vai trò.
TABLE_COLUMN_NUANCE: dict[tuple[str, str], str] = {
    ("CUSTOMER", "CUST_NAME"): "tên chính thức trên danh mục master khách hàng đã đăng ký",
    ("INV_ISS", "CUST_NAME"): "tên khách in trên phiếu xuất — có thể lấy từ master hoặc nhập khi xuất",
    ("TRANSHDR", "AMOUNT"): "tổng tiền cả bill — dùng lọc bill tối thiểu (min bill)",
    ("STRANS", "AMOUNT"): "thành tiền từng dòng hàng — có thể bằng 0 với quà tặng",
    ("PMTRANS", "AMOUNT"): "số tiền thanh toán / chi quỹ trên bill",
    ("SKU_DEF", "DEPT_ID"): "ngành hàng của SKU trong cây phân loại hàng hóa",
    ("SUPPLIER", "DEPT_ID"): "ngành hàng mặc định gắn với nhà cung cấp",
    ("STRANS", "CARD_ID"): "thẻ quét trên dòng bán — thường trống nếu khách không đưa thẻ",
    ("TRANSHDR", "CARD_ID"): "thẻ gắn trên header bill khi thanh toán có loyalty",
    ("CSCARD", "CARD_ID"): "mã thẻ chính trên master loyalty",
    ("CRDTRANS", "TRANS_CODE"): "811 = tích điểm từ mua hàng",
    ("CRDTRANS_ARC", "TRANS_CODE"): "812 = điều chỉnh / đổi quà / trừ điểm",
    ("STRANS", "TRANS_CODE"): "113 = dòng bán lẻ POS",
    ("TRANSHDR", "TRANS_CODE"): "113 = header bill bán lẻ",
    ("PMTRANS", "TRANS_CODE"): "221 thanh toán bill, 222/008 chi quỹ hoặc điều chỉnh",
    ("STRANS", "VAT_AMT"): "thuế GTGT trên từng dòng bán POS",
    ("STRANS_TMP", "VAT_AMT"): "thuế GTGT trên dòng bán tạm / bill treo",
    ("SUSPEND", "VAT_AMT"): "thuế GTGT trên dòng bill đang treo",
    ("TRANSHDR", "VAT_AMT"): "tổng thuế GTGT của cả bill header",
    ("TRANSHDR_ARC", "VAT_AMT"): "tổng thuế GTGT bill đã archive",
    ("CRDTRANS", "VAT_AMT"): "thuế trên doanh thu gốc tích điểm (811)",
    ("CRDTRANS_ARC", "VAT_AMT"): "thuế trên giao dịch điều chỉnh / đổi quà (812)",
    ("CRDTRANS_TMP", "VAT_AMT"): "thuế trên giao dịch tích điểm tạm",
    ("INV_HDR", "VAT_AMT"): "thuế GTGT trên header hóa đơn mua / nhập kho",
    ("INV_ISS", "VAT_AMT"): "thuế GTGT trên phiếu xuất kho",
    ("ST_ORDER", "VAT_AMT"): "thuế GTGT trên đơn đặt hàng nội bộ",
    ("CUSTHIST", "VAT_AMT"): "thuế ghi trong snapshot lịch sử khách (ít dùng cho phân tích)",
    ("STRANS", "DISCOUNT"): "giảm giá / chiết khấu trên dòng bán",
    ("TRANSHDR", "DISCOUNT"): "tổng giảm giá trên header bill",
    ("STRANS", "PRICE"): "đơn giá bán trên dòng POS",
    ("STRANS", "COMM_AMT"): "hoa hồng trên dòng bán",
    ("CRDTRANS", "COMM_AMT"): "hoa hồng gắn giao dịch tích điểm",
}

# Nhóm bảng theo miền nghiệp vụ — dùng khi cột xuất hiện trên nhiều bảng.
TABLE_DOMAIN: dict[str, frozenset[str]] = {
    "POS bán lẻ": frozenset({"STRANS", "STRANS_TMP", "TRANSHDR", "TRANSHDR_ARC", "SUSPEND", "PMTRANS"}),
    "Loyalty / thẻ": frozenset({"CRDTRANS", "CRDTRANS_ARC", "CRDTRANS_TMP", "CRD_INFO", "CSCARD"}),
    "Kho / mua hàng": frozenset({"INV_HDR", "INV_ISS", "ST_ORDER", "STK_DTL"}),
    "Master / danh mục": frozenset({"CUSTOMER", "SKU_DEF", "SUPPLIER", "PARTNER", "BARCODE"}),
}

# Prose đầy đủ cho cột vật lý xuất hiện trên nhiều bảng (key = tên cột UPPER).
MULTI_TABLE_COLUMN_BUSINESS: dict[str, str] = {
    "VAT_AMT": (
        "Số tiền thuế GTGT (VAT) ghi trên chứng từ — grain phụ thuộc bảng. "
        "Trên STRANS/STRANS_TMP/SUSPEND là thuế từng dòng bán; "
        "TRANSHDR/TRANSHDR_ARC là tổng thuế cả bill; "
        "CRDTRANS/CRDTRANS_ARC/CRDTRANS_TMP là thuế trên doanh thu loyalty; "
        "INV_HDR/INV_ISS là thuế trên chứng từ kho; ST_ORDER là thuế trên đơn nội bộ. "
        "Không cộng VAT dòng STRANS để suy ra min bill — dùng TRANSHDR.AMOUNT / TRANSHDR.VAT_AMT."
    ),
    "DISCOUNT": (
        "Giảm giá / chiết khấu trên chứng từ bán. "
        "STRANS: chiết khấu từng dòng; TRANSHDR: tổng giảm trên bill. "
        "Có thể bằng 0 với hàng không KM."
    ),
    "COMM_AMT": (
        "Tiền hoa hồng ghi trên dòng bán hoặc giao dịch loyalty — "
        "thường populate khi có chương trình hoa hồng / coupon liên kết."
    ),
    "CDISC_AMT": (
        "Số tiền chiết khấu từ coupon (CDISC) trên dòng bán hoặc đơn hàng — "
        "khác DISCOUNT thông thường và MDISC khuyến mãi."
    ),
    "CDISC_RATE": "Tỷ lệ chiết khấu coupon (%) áp dụng trên dòng / đơn.",
    "MDISC_AMT": "Số tiền chiết khấu khuyến mãi (MDISC) — thường trên STRANS / đơn KM.",
    "MDISC_RATE": "Tỷ lệ chiết khấu khuyến mãi (%) trên dòng / đơn.",
    "TAX_RATE": (
        "Thuế suất GTGT (%) áp dụng cho dòng hoặc chứng từ — "
        "dùng cùng VAT_AMT để kiểm tra tính thuế."
    ),
    "PRICE": (
        "Đơn giá bán trên dòng POS (STRANS). "
        "Khác RTPRICE trên master SKU — PRICE là giá thực tế tại thời điểm bán."
    ),
    "REMARK": (
        "Ghi chú do nhân viên nhập trên chứng từ — "
        "CRDTRANS/CRDTRANS_ARC thường giải thích điều chỉnh điểm / đổi quà."
    ),
    "TRANS_CODE": (
        "Phân loại loại chứng từ trong hệ POS/ERP. "
        "113 = bán lẻ; 221 = thanh toán bill; 811/812 = tích điểm / điều chỉnh loyalty — grain phụ thuộc bảng."
    ),
    "ADDRESS": (
        "Địa chỉ liên hệ khách / đối tác — trên CUSTOMER/CSCARD là master; "
        "trên chứng từ kho có thể là địa chỉ giao nhận in trên phiếu."
    ),
    "BIRTHDAY": "Ngày sinh khách hàng trên master CUSTOMER / CSCARD — dùng phân khúc CRM.",
    "PHONE": "Số điện thoại liên hệ khách trên master hoặc snapshot tổng hợp.",
    "EMAIL": "Email liên hệ khách trên master CUSTOMER / CSCARD.",
    "BARCODE": "Mã vạch quét POS — join BARCODE ↔ SKU_DEF để tra SKU.",
    "BU_ID": (
        "Mã đơn vị kinh doanh / chi nhánh logic trong tập đoàn — "
        "phân tách dữ liệu theo BU trên quỹ, kho, POS."
    ),
    "SUPP_ID": "Mã nhà cung cấp — join SUPPLIER master trên chứng từ mua / kho.",
    "INV_NO": "Số hóa đơn GTGT / số chứng từ kho in trên INV_HDR, INV_ISS.",
    "PLU_CODE": "Mã PLU (Price Look-Up) trên quầy — map sang SKU nội bộ.",
    "STATUS": "Trạng thái bản ghi / chứng từ (active, closed, cancelled, …) — ý nghĩa cụ thể theo bảng.",
    "QTY": (
        "Số lượng — grain phụ thuộc bảng: STRANS = qty bán; STK_DTL = tồn/movement; "
        "ST_ORDER = qty đặt/giao; INV = qty nhập/xuất."
    ),
    "AMOUNT": (
        "Số tiền / giá trị — grain phụ thuộc bảng. "
        "TRANSHDR = tổng bill; STRANS = thành tiền dòng; PMTRANS = thanh toán; CRDTRANS = doanh thu tích điểm."
    ),
    "DISC_AMT": (
        "Số tiền chiết khấu trên dòng/chứng từ — khác CDISC (coupon) và MDISC (khuyến mãi)."
    ),
    "DISC_RATE": "Tỷ lệ chiết khấu (%) trên dòng hoặc bill.",
    "CCOMM_AMT": "Tiền hoa hồng coupon trên dòng bán / đơn hàng.",
    "CCOMM_RATE": "Tỷ lệ hoa hồng coupon (%) trên dòng / đơn.",
    "MCOMM_AMT": "Tiền hoa hồng khuyến mãi trên dòng / đơn.",
    "TCOMM_AMT": "Tiền hoa hồng thương mại trên dòng / đơn.",
    "TCOMM_RATE": "Tỷ lệ hoa hồng thương mại (%) trên dòng / đơn.",
    "STK_QTY": "Số lượng tồn kho hiện tại — snapshot hoặc movement tùy bảng.",
    "TRAN_TIME": "Giờ giao dịch (HH:MM) trên POS — join cùng TRAN_DATE.",
    "TRAN_DATE": "Ngày giao dịch — cutoff db2 live vs db1 archive tùy bảng.",
    "TRANS_TYPE": "Phân loại chi tiết loại giao dịch — bổ sung cho TRANS_CODE.",
    "PMT_MODE": "Chế độ thanh toán (trả ngay / trả góp / công nợ, …).",
    "EF_DATE": "Ngày hiệu lực bản ghi / chứng từ.",
    "FR_DATE": "Ngày bắt đầu hiệu lực (from date) — rule KM, giá, …",
    "TO_DATE": "Ngày kết thúc hiệu lực (to date).",
    "OPEN_DATE": "Ngày mở / tạo bản ghi master hoặc chứng từ.",
    "MODI_DATE": "Ngày cập nhật / sửa gần nhất.",
    "DUE_DATE": "Ngày đến hạn thanh toán / giao hàng.",
    "REPORT_DATE": "Ngày snapshot báo cáo WebRpt.",
    "REFRESHED_AT": "Thời điểm refresh snapshot báo cáo.",
}

# Tiêu đề hiển thị khi không có SEMANTIC_TITLES (key = tên cột UPPER hoặc semantic_key).
COLUMN_TITLE_VI: dict[str, str] = {
    "VAT_AMT": "Tiền thuế GTGT (VAT_AMT)",
    "TAX_AMT": "Tiền thuế (TAX_AMT)",
    "TAX_RATE": "Thuế suất (TAX_RATE)",
    "DISCOUNT": "Giảm giá / chiết khấu (DISCOUNT)",
    "DISC_AMT": "Tiền chiết khấu (DISC_AMT)",
    "COMM_AMT": "Tiền hoa hồng (COMM_AMT)",
    "CDISC_AMT": "Chiết khấu coupon (CDISC_AMT)",
    "MDISC_AMT": "Chiết khấu khuyến mãi (MDISC_AMT)",
    "PAID_AMT": "Số tiền đã thanh toán (PAID_AMT)",
    "SALE_AMT": "Doanh số bán (SALE_AMT)",
    "PRICE": "Đơn giá bán (PRICE)",
    "RTPRICE": "Giá bán lẻ đề xuất (RTPRICE)",
    "TRANS_CODE": "Loại chứng từ (TRANS_CODE)",
    "REMARK": "Ghi chú (REMARK)",
    "vat_amt": "Tiền thuế GTGT (VAT_AMT)",
    "discount": "Giảm giá / chiết khấu (DISCOUNT)",
    "comm_amt": "Tiền hoa hồng (COMM_AMT)",
    "price": "Đơn giá bán (PRICE)",
    "tax_rate": "Thuế suất (TAX_RATE)",
}

AMT_STEM_VI: dict[str, str] = {
    "VAT": "thuế GTGT",
    "TAX": "thuế",
    "DISC": "chiết khấu",
    "CDISC": "chiết khấu coupon",
    "MDISC": "chiết khấu khuyến mãi",
    "TDISC": "chiết khấu thương mại",
    "GDISC": "chiết khấu quà tặng",
    "COMM": "hoa hồng",
    "CCOMM": "hoa hồng coupon",
    "MCOMM": "hoa hồng khuyến mãi",
    "TCOMM": "hoa hồng thương mại",
    "FINE": "phạt",
    "DEBT": "công nợ",
    "PAID": "đã thanh toán",
    "SALE": "doanh số bán",
    "CR": "công nợ phải thu",
    "RFN": "hoàn tiền",
    "RBT": "rebate / hoàn trả",
    "FOREX": "ngoại tệ",
    "VALUE": "giá trị",
}

USELESS_TABLE_DESC = re.compile(r"^Cột\s+\w+\s*$", re.IGNORECASE)
GENERIC_TABLE_DESC = re.compile(
    r"^(Tiền thuế VAT|Mã vạch|Địa chỉ|Ghi chú|Tên khách hàng|Giảm giá|Đơn giá|Số lượng)$",
    re.IGNORECASE,
)

ENTITY_VI: dict[str, str] = {
    "CUST": "khách hàng",
    "SKU": "sản phẩm",
    "SUPP": "nhà cung cấp",
    "STK": "cửa hàng",
    "CARD": "thẻ",
    "INV": "hóa đơn / chứng từ kho",
    "TAX": "thuế",
    "DEPT": "ngành hàng",
    "PMT": "thanh toán",
    "TRANS": "giao dịch",
    "PLU": "PLU",
    "PARTNER": "đối tác",
    "ACCOUNT": "tài khoản",
    "DEBT": "công nợ",
    "ORDER": "đơn hàng",
}


def _clean_table_description(desc: str) -> str | None:
    text = (desc or "").strip()
    if not text or USELESS_TABLE_DESC.match(text):
        return None
    return text


def _table_label(table_name: str) -> str:
    return TABLE_CONTEXT.get(table_name.upper(), f"bảng {table_name}")


def _format_domain_summary(table_names: list[str]) -> str:
    """Summarize which business domains use this column."""
    upper = {t.upper() for t in table_names}
    parts: list[str] = []
    for domain, members in TABLE_DOMAIN.items():
        hit = sorted(upper & members)
        if hit:
            if len(hit) <= 2:
                parts.append(f"{domain} ({', '.join(hit)})")
            else:
                parts.append(f"{domain} ({', '.join(hit[:2])}, …)")
    if parts:
        return "; ".join(parts)
    labels = [_table_label(t) for t in sorted(table_names)[:3]]
    if len(table_names) > 3:
        return ", ".join(labels) + ", …"
    return ", ".join(labels)


def infer_column_title(semantic_key: str, display_names: list[str]) -> str:
    """Human title for column MD — prefer registry, then column gloss."""
    from column_semantic_registry import SEMANTIC_TITLES

    if semantic_key in SEMANTIC_TITLES:
        return SEMANTIC_TITLES[semantic_key]
    if semantic_key in COLUMN_TITLE_VI:
        return COLUMN_TITLE_VI[semantic_key]
    col = (display_names[0] if display_names else semantic_key).upper()
    if "__" in semantic_key:
        table_part, col_part = semantic_key.split("__", 1)
        col_upper = col
        if col_upper in COLUMN_BASE_GLOSS:
            gloss = COLUMN_BASE_GLOSS[col_upper]
            if f"({col_upper})" in gloss:
                return f"{gloss} ({table_part.upper()})"
            return f"{gloss} ({table_part.upper()})"
        gloss = _base_gloss(col_upper, "")
        if not gloss.startswith("Thuộc tính") and not gloss.startswith("Chỉ số"):
            return f"{gloss} ({table_part.upper()})"
        return f"{col_part.replace('_', ' ').title()} ({table_part.upper()})"
    if col in COLUMN_TITLE_VI:
        return COLUMN_TITLE_VI[col]
    if col in COLUMN_BASE_GLOSS:
        gloss = COLUMN_BASE_GLOSS[col]
        if f"({col})" in gloss:
            return gloss
        return f"{gloss} ({col})"
    return semantic_key.replace("__", " · ").replace("_", " ")


def _base_gloss(column: str, kind: str) -> str:
    col = column.upper()
    if col in COLUMN_BASE_GLOSS:
        return COLUMN_BASE_GLOSS[col]

    if col.endswith("_NAME"):
        prefix = col[:-5]
        entity = ENTITY_VI.get(prefix, prefix.replace("_", " ").lower())
        return f"Tên {entity}"

    if col.endswith("_ID") or col.endswith("_NUM") or col.endswith("_NO"):
        label = col.replace("_", " ").lower()
        return f"Mã định danh ({label})"

    if col.endswith("_RATE"):
        stem = col[:-5]
        if stem in AMT_STEM_VI:
            return f"Tỷ lệ {AMT_STEM_VI[stem]} (%)"
        return f"Tỷ lệ / phần trăm ({col.replace('_', ' ').lower()})"

    if col.endswith("_PRICE") or col == "PRICE":
        return "Đơn giá"

    if col.endswith("_DATE") or col.endswith("_DT"):
        stem = (col[:-5] if col.endswith("_DATE") else col[:-3]).replace("_", " ").lower()
        return f"Ngày {stem}"

    if col.endswith("_TIME"):
        return f"Giờ {col[:-5].replace('_', ' ').lower()}"

    if col.endswith("_CODE"):
        return f"Mã phân loại {col[:-5].replace('_', ' ').lower()}"

    if col.endswith("_AMT") or col.endswith("_AMOUNT"):
        stem = col[:-4] if col.endswith("_AMT") else col[:-7]
        if stem in AMT_STEM_VI:
            return f"Số tiền {AMT_STEM_VI[stem]}"
        return "Số tiền / giá trị"

    if col.endswith("_QTY") or col == "QTY":
        stem = col[:-4] if col.endswith("_QTY") else ""
        if stem in ("STK", "ISS", "ORD", "DLV", "SAL", "PACK", "KIT", "GIFT", "CNT"):
            return COLUMN_BASE_GLOSS.get(col, f"Số lượng {stem.lower()}" if stem else "Số lượng")
        return "Số lượng"

    if col.startswith("IS") and len(col) > 2:
        label = col[2:].replace("_", " ").lower()
        return f"Cờ thuộc tính ({label})"

    if kind == "flag":
        label = col.replace("_", " ").lower()
        return f"Cờ / trạng thái ({label})"

    if kind == "measure":
        return f"Chỉ số đo lường ({col.replace('_', ' ').lower()})"

    if kind == "date":
        return f"Mốc thời gian ({col.replace('_', ' ').lower()})"

    if kind == "identifier":
        return f"Định danh ({col.replace('_', ' ').lower()})"

    if kind == "code":
        return f"Mã nghiệp vụ ({col.replace('_', ' ').lower()})"

    return f"Thuộc tính {col.replace('_', ' ').lower()}"


def compose_table_role(table_name: str, column: str, *, table_description: str = "", kind: str = "") -> str:
    """One-line role for the table matrix — no sample stats."""
    key = (table_name.upper(), column.upper())
    if key in TABLE_COLUMN_NUANCE:
        return TABLE_COLUMN_NUANCE[key]

    cleaned = _clean_table_description(table_description)
    if cleaned and not GENERIC_TABLE_DESC.match(cleaned.strip()):
        return cleaned

    base = _base_gloss(column, kind)
    ctx = _table_label(table_name)
    return f"{base.capitalize()} trên {ctx}"


def _merge_table_descriptions(occurrences: list[Any]) -> list[str]:
    """Unique useful Vietnamese descriptions from table MD."""
    seen: set[str] = set()
    out: list[str] = []
    for occ in occurrences:
        cleaned = _clean_table_description(getattr(occ, "description", "") or "")
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            out.append(cleaned)
    return out


def compose_business_prose(
    *,
    semantic_key: str,
    display_names: list[str],
    kind: str,
    tables: list[dict[str, str]],
    occurrences: list[Any] | None = None,
    facts: list[str] | None = None,
    profiles: dict[str, dict[str, Any]] | None = None,
) -> str:
    """
    Natural-language business meaning for the semantic chunk.
    Uses registry → table MD → glossary → pattern. Never dumps raw sample top values.
    """
    if semantic_key in SEMANTIC_BUSINESS:
        return SEMANTIC_BUSINESS[semantic_key]

    column = (display_names[0] if display_names else "").upper()
    occs = occurrences or []
    table_names = sorted({t["ref"].split(":")[-1].upper() for t in tables})

    domain = compose_domain_prose(semantic_key=semantic_key, column=column, table_names=table_names)
    if domain:
        return domain

    # Curated prose for physical columns spanning multiple tables
    if column in MULTI_TABLE_COLUMN_BUSINESS and len(table_names) > 1:
        return MULTI_TABLE_COLUMN_BUSINESS[column]
    if column in MULTI_TABLE_COLUMN_BUSINESS and len(table_names) == 1:
        base = MULTI_TABLE_COLUMN_BUSINESS[column]
        return f"{base} Chỉ xuất hiện trên {_table_label(table_names[0])}."

    # Single-table nuance from TABLE_COLUMN_NUANCE across attached tables
    nuances: list[str] = []
    for tname in table_names:
        key = (tname, column)
        if key in TABLE_COLUMN_NUANCE:
            nuances.append(f"Trên {_table_label(tname)}: {TABLE_COLUMN_NUANCE[key]}")

    if nuances:
        if len(nuances) == 1:
            base = _base_gloss(column, kind)
            return f"{base}. {nuances[0].split(': ', 1)[-1].capitalize()}."

    # Useful descriptions from table markdown (skip generic one-liners)
    md_descs = [
        d
        for d in (_merge_table_descriptions(occs) if occs else [])
        if not GENERIC_TABLE_DESC.match(d.strip())
    ]
    if md_descs and len(table_names) == 1:
        base = md_descs[0]
        ctx = _table_label(table_names[0])
        if len(base) >= 40 and base.lower() not in column.lower().replace("_", " "):
            return f"{base} (ngữ cảnh: {ctx})."
        return f"{_base_gloss(column, kind).capitalize()} — {ctx}."

    # Facts from inventory (non-generic)
    for fact in facts or []:
        if fact and not fact.startswith("Cột ") and not USELESS_TABLE_DESC.match(fact):
            if GENERIC_TABLE_DESC.match(fact.strip()):
                break  # fall through to composed prose
            if len(table_names) == 1:
                return f"{fact} — {_table_label(table_names[0]).capitalize()}."
            domains = _format_domain_summary(table_names)
            return f"{fact}. Dùng trong {domains}."

    base = _base_gloss(column, kind)

    # Special composed cases
    if column == "CUST_NAME":
        if "CUSTOMER" in table_names and len(table_names) == 1:
            return "Tên khách hàng đã đăng ký trong hệ thống — tên chính thức trên danh mục master."
        if "CUSTOMER" in table_names:
            others = [t for t in table_names if t != "CUSTOMER"]
            extra = ", ".join(_table_label(t) for t in others[:2])
            return (
                "Tên khách hàng đã đăng ký trong hệ thống. "
                f"Trên master CUSTOMER là tên chính thức; trên {extra} là tên ghi trên chứng từ liên quan."
            )
        hosts = ", ".join(_table_label(t) for t in table_names[:3])
        return f"Tên khách hàng ghi nhận trên {hosts}."

    if column == "DEPT_ID":
        hosts = ", ".join(_table_label(t) for t in table_names[:3])
        return (
            "Mã ngành hàng / phòng ban merchandise — phân loại sản phẩm và đối tác theo cây ngành hàng nội bộ. "
            f"Dùng trên {hosts}."
        )

    if column == "TRANS_CODE":
        return MULTI_TABLE_COLUMN_BUSINESS["TRANS_CODE"]

    profiles = profiles or {}
    if column == "CARD_ID" and profiles:
        has_loyalty_master = any(t in table_names for t in ("CSCARD", "CRD_INFO"))
        if has_loyalty_master:
            return (
                f"{base} trên master loyalty. "
                "Thẻ thường có prefix A (phổ thông) hoặc E/F/H (VIP). "
                "Khác thẻ ghi trên dòng STRANS khi quét lúc bán."
            )

    if len(table_names) == 1:
        return f"{base.capitalize()} — {_table_label(table_names[0])}."

    domains = _format_domain_summary(table_names)
    return f"{base.capitalize()} — dùng trong {domains}."
