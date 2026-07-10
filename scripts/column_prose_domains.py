"""Domain-specific business prose — STK_DTL, RDISCINF, SKU_DEF, loyalty, kho, KM."""

from __future__ import annotations

import re

# --- STK_DTL: sổ chi tiết tồn kho theo kỳ -----------------------------------

STK_DTL_MOVEMENT_VI: dict[str, str] = {
    "SUPP": "nhập từ nhà cung cấp",
    "DEAL": "xuất bán / giao dịch bán lẻ",
    "CUST": "phát sinh liên quan khách (trả hàng / xuất KH)",
    "TRF": "điều chuyển kho nội bộ",
    "MUL": "ghép lô / nhân bản tồn",
    "BAL": "điều chỉnh cân bằng kỳ",
    "CQTY": "tích lũy theo số lượng",
    "CAMT": "tích lũy theo giá trị tiền",
}

STK_DTL_METRIC_VI: dict[str, str] = {
    "QTY": "số lượng",
    "AMT": "giá trị tồn (tiền)",
    "SUR": "thặng dư / chênh lệch tồn",
    "VAT": "thuế GTGT",
    "DIS": "chiết khấu",
    "COM": "hoa hồng / chi phí liên quan",
}

_STK_DTL_MOVEMENT_RE = re.compile(
    r"^(FR|TO)(SUPP|DEAL|CUST|TRF|MUL|BAL|CQTY|CAMT)_(QTY|AMT|SUR|VAT|DIS|COM)$"
)


def compose_stk_dtl_prose(column: str) -> str | None:
    col = column.upper()
    if col == "BEGIN_QTY":
        return (
            "Tồn kho đầu kỳ theo số lượng trên STK_DTL — "
            "snapshot trước các phát sinh nhập/xuất/bán/điều chuyển trong kỳ."
        )
    if col == "BEGIN_AMT":
        return (
            "Tồn kho đầu kỳ theo giá trị (tiền) trên STK_DTL — "
            "dùng cùng BEGIN_QTY để đối chiếu qty × giá vốn."
        )
    if col == "PRD_CODE":
        return "Mã kỳ báo cáo tồn kho — xác định chu kỳ (tháng/tuần) của bản ghi STK_DTL."

    m = _STK_DTL_MOVEMENT_RE.match(col)
    if not m:
        return None
    period, movement, metric = m.group(1), m.group(2), m.group(3)
    period_vi = "đầu kỳ" if period == "FR" else "cuối kỳ"
    move_vi = STK_DTL_MOVEMENT_VI.get(movement, movement.lower())
    metric_vi = STK_DTL_METRIC_VI.get(metric, metric.lower())
    return (
        f"Phát sinh {period_vi} — {move_vi} ({metric_vi}) trên sổ chi tiết tồn kho STK_DTL. "
        "Grain: STK_ID × SKU_ID × kỳ (PRD_CODE)."
    )


# --- RDISCINF: rule khuyến mãi ------------------------------------------------

RDISCINF_COLUMN_BUSINESS: dict[str, str] = {
    "DISC_CODE": "Mã chương trình chiết khấu / khuyến mãi — khóa tra rule trong RDISCINF.",
    "GIFT": "Cờ đánh dấu rule quà tặng — khi bật, KM trả quà thay vì (hoặc kèm) giảm giá tiền.",
    "LOTTERY": "Cờ rule xổ số / quay thưởng gắn KM.",
    "MARKUP": "Cờ rule markup giá — tăng/giảm giá theo điều kiện thay vì chiết khấu trực tiếp.",
    "SOLD_QTY": "Ngưỡng số lượng đã bán / cần mua để rule KM kích hoạt.",
    "SOLD_AMT": "Ngưỡng doanh số / tiền hàng đã bán để rule KM kích hoạt — hay dùng cho min bill.",
    "SOLD_CNT": "Ngưỡng số lần giao dịch / số bill để rule KM kích hoạt.",
    "BUY_AMT": "Điều kiện giá trị mua tối thiểu (min bill) trong rule KM.",
    "BUY_MARK": "Điều kiện điểm tích lũy tối thiểu trong rule KM.",
    "TRS_AMT": "Ngưỡng tiền giao dịch trong rule — thường so với tổng bill.",
    "MAXSUMAMT": "Trần tổng tiền chiết khấu / quà tối đa cho cả rule.",
    "MAXSUMQTY": "Trần tổng số lượng quà / hàng KM tối đa cho cả rule.",
    "MAXSUMTRS": "Trần số lần áp dụng rule trên tổng chương trình.",
    "MAXDISCAMT": "Trần tiền chiết khấu tối đa mỗi lần áp dụng.",
    "MAXDISCQTY": "Trần số lượng KM tối đa mỗi lần áp dụng.",
    "MAXDISCTRS": "Trần số lần KM tối đa mỗi khách / mỗi bill.",
    "CNTSUMAMT": "Tổng tiền KM đã cộng dồn (counter) — theo dõi ngân sách rule.",
    "CNTSUMQTY": "Tổng số lượng KM đã cộng dồn (counter).",
    "CNTSUMTRS": "Tổng số lần KM đã cộng dồn (counter).",
    "CARDEXCL": "Cờ loại trừ thẻ — rule không áp dụng cho loại thẻ trong danh sách loại trừ.",
    "CARDINCL": "Cờ chỉ áp dụng cho loại thẻ trong danh sách include.",
    "CARDRQ": "Cờ bắt buộc quét thẻ loyalty để rule KM có hiệu lực.",
    "BY_EACH": "Cờ áp dụng theo từng đơn vị / từng dòng thay vì cả bill.",
    "OBJ_CODE": "Mã đối tượng KM (SKU, ngành hàng, nhóm, …) — join với OBJ_VALUE.",
    "OBJ_VALUE": "Giá trị đối tượng KM — mã SKU, mã ngành, … tùy OBJ_CODE/DATA_TYPE.",
    "OBJ_NOT": "Cờ phủ định đối tượng — rule áp dụng khi KHÔNG thuộc OBJ_VALUE.",
    "DATA_TYPE": "Kiểu dữ liệu đối tượng KM (SKU, dept, group, …) — quyết định cách parse OBJ_VALUE.",
    "LAYER_ID": "Mức ưu tiên / lớp xếp chồng rule KM — rule priority khi nhiều KM cùng match.",
    "FR_TIME": "Giờ bắt đầu áp dụng rule trong ngày (khung giờ KM).",
    "TO_TIME": "Giờ kết thúc áp dụng rule trong ngày.",
    "DOWMAP": "Bitmap ngày trong tuần áp dụng rule (Mon–Sun).",
    "DISC_LMT": "Giới hạn mức chiết khấu tối đa (%) hoặc trần theo rule.",
    "DISC_FRB": "Cờ chiết khấu forbidden / loại trừ một số hình thức KM.",
    "CHG_TYPE": "Kiểu thay đổi giá trị khi KM kích hoạt (%, tiền, quà, điểm, …).",
}


def compose_rdiscinf_prose(column: str) -> str | None:
    return RDISCINF_COLUMN_BUSINESS.get(column.upper())


# --- SKU_DEF: master sản phẩm -------------------------------------------------

SKU_DEF_COLUMN_BUSINESS: dict[str, str] = {
    "FULL_NAME": "Tên đầy đủ sản phẩm trên master SKU — hiển thị POS / báo cáo.",
    "SHORT_NAME": "Tên rút gọn sản phẩm — in tem / màn hình quầy.",
    "FULL_NAME_U": "Tên đầy đủ không dấu / unicode alternate — search & tích hợp.",
    "GRP_NAME": "Tên nhóm hàng (merchandise group) trên master SKU.",
    "GOODS_ID": "Mã hàng hóa / mã phân loại goods nội bộ (ngoài SKU_ID).",
    "BASEPRICE": "Giá cơ sở / giá vốn tham chiếu trên master — khác giá bán RTPRICE.",
    "RTPRICE": "Giá bán lẻ đề xuất (retail price) trên master SKU.",
    "WSPRICE": "Giá bán sỉ (wholesale) trên master SKU.",
    "COSTPRICE": "Giá vốn / giá nhập tham chiếu trên master SKU.",
    "MDPRICE": "Giá markdown / giá giảm kệ trên master.",
    "PREFPR": "Giá ưu tiên / preferred price — override tạm trên master.",
    "LASTIMPPR": "Giá nhập gần nhất — cập nhật từ phiếu nhập kho.",
    "DISC_RTPR": "Tỷ lệ chiết khấu so với giá bán lẻ đề xuất.",
    "DISC_SPPR": "Tỷ lệ chiết khấu so với giá khuyến mãi / special price.",
    "TAX_RATE": "Thuế suất GTGT mặc định gắn SKU — dùng tính VAT trên dòng bán.",
    "TAX_DRATE": "Thuế suất giảm / đặc biệt (nếu có) trên master SKU.",
    "TAX_CODE": "Mã nhóm thuế áp dụng cho SKU.",
    "MIN_MG": "Biên lợi nhuận tối thiểu (%) cho SKU.",
    "MAX_MG": "Biên lợi nhuận tối đa (%) cho SKU.",
    "RC_QTY": "Số lượng reorder point — ngưỡng đặt hàng lại.",
    "RC_TYPE": "Kiểu reorder (auto/manual, …) trên master SKU.",
    "UNIT_DESC": "Mô tả đơn vị tính (chai, hộp, kg, …).",
    "VAR_ID": "Mã biến thể sản phẩm (size/màu) trong cùng SKU matrix.",
    "VAR_TYPE": "Loại biến thể (size, color, …).",
    "MRK_ID": "Mã thương hiệu / brand trên master SKU.",
    "LBL_TYPE": "Loại nhãn in (tem, shelf talker, …).",
    "ABC": "Phân loại ABC tồn kho / doanh thu trên master SKU.",
    "DOMESTIC": "Cờ hàng nội địa vs nhập khẩu.",
    "EXPIRY": "Cờ quản lý hạn sử dụng — SKU có date expiry.",
    "IsConsign": "Cờ hàng ký gửi (consignment) — không thuộc sở hữu tồn thông thường.",
    "IsInstall": "Cờ hàng cần lắp đặt (điện máy, …).",
    "IsOwnBrd": "Cờ nhãn hàng riêng (private label / own brand).",
    "IsPack": "Cờ hàng bán theo combo / pack.",
    "IsReserv": "Cờ cho phép đặt trước / giữ hàng.",
    "IsSerial": "Cờ quản lý serial number từng unit.",
    "IsTicket": "Cờ hàng vé / dịch vụ (không tồn kho vật lý).",
    "IsWebshow": "Cờ hiển thị bán online / web catalog.",
    "POS_SHW": "Cờ hiển thị trên POS quầy.",
    "RES_SHW": "Cờ hiển thị trên màn reservation / đặt hàng.",
    "BON_MARK": "Điểm thưởng mặc định gắn SKU khi tích loyalty.",
    "DISP_GRP": "Nhóm trưng bày (display group) trên kệ.",
    "PICEUNIT": "Đơn vị bán lẻ mặc định (piece unit code).",
}


def compose_sku_def_prose(column: str) -> str | None:
    col = column.upper()
    if col in SKU_DEF_COLUMN_BUSINESS:
        return SKU_DEF_COLUMN_BUSINESS[col]
    if col.startswith("IS") and len(col) > 2:
        flag = col[2:].replace("_", " ").lower()
        return f"Cờ thuộc tính sản phẩm ({flag}) trên master SKU — yes/no."
    return None


# --- CRD_INFO: aggregate loyalty ----------------------------------------------

CRD_INFO_COLUMN_BUSINESS: dict[str, str] = {
    "BEG_BAMT": "Doanh thu mua tích điểm đầu kỳ (beginning buy amount) trên CRD_INFO.",
    "BEG_BMARK": "Điểm tích đầu kỳ (beginning buy mark) trên CRD_INFO.",
    "BEG_BTRS": "Số giao dịch mua tích điểm đầu kỳ (beginning buy transactions).",
    "BEG_OAMT": "Doanh thu mua khác đầu kỳ (other amount) — ngoài bucket chính.",
    "BEG_OMARK": "Điểm other đầu kỳ trên CRD_INFO.",
    "BEG_OTRS": "Số giao dịch other đầu kỳ trên CRD_INFO.",
    "BEG_RAMT": "Doanh thu redeem / đổi quà đầu kỳ trên CRD_INFO.",
    "OTH_AMT": "Doanh thu / giá trị phát sinh other (ngoài tích chuẩn) trong kỳ.",
    "OTH_MARK": "Điểm phát sinh other trong kỳ trên CRD_INFO.",
    "OTH_TRS": "Số giao dịch other trong kỳ trên CRD_INFO.",
}


def compose_crd_info_prose(column: str) -> str | None:
    return CRD_INFO_COLUMN_BUSINESS.get(column.upper())


# --- CSCARD: master thẻ -------------------------------------------------------

CSCARD_COLUMN_BUSINESS: dict[str, str] = {
    "ISLOCKED": "Cờ khóa thẻ — thẻ bị khóa không tích/đổi điểm.",
    "ISWEBUSE": "Cờ cho phép dùng thẻ trên web / app.",
    "CHANGEPWD": "Cờ bắt buộc đổi mật khẩu thẻ / PIN lần đăng nhập tới.",
    "FRESH_DATE": "Ngày làm mới / cập nhật trạng thái thẻ gần nhất.",
    "BONUS_PC": "Tỷ lệ thưởng điểm bonus (%) so với tích chuẩn.",
    "RADIUS": "Bán kính / phạm vi cửa hàng áp dụng thẻ (geo radius).",
    "POST": "Trạng thái post / duyệt thẻ trên master CSCARD.",
}


def compose_cscard_prose(column: str) -> str | None:
    return CSCARD_COLUMN_BUSINESS.get(column.upper())


# --- ST_ORDER -----------------------------------------------------------------

ST_ORDER_COLUMN_BUSINESS: dict[str, str] = {
    "ORD_QTY": "Số lượng đặt hàng trên đơn ST_ORDER.",
    "ORDP_QTY": "Số lượng đặt theo pack / đơn vị đặt hàng.",
    "DLV_QTY": "Số lượng đã giao / đã nhận so với đơn.",
    "SAL_QTY": "Số lượng đã bán / xuất từ đơn nội bộ.",
    "ST_QTY": "Số lượng tồn / còn lại trên đơn ST_ORDER.",
    "ORD_PRICE": "Đơn giá đặt hàng trên đơn nội bộ — khác RTPRICE master.",
    "GCOMM_AMT": "Tiền hoa hồng / chi phí giao hàng trên đơn ST_ORDER.",
    "DELIVER_DT": "Ngày giao hàng dự kiến / thực tế trên đơn ST_ORDER.",
    "STOPED_DT": "Ngày dừng / hủy đơn ST_ORDER.",
}


def compose_st_order_prose(column: str) -> str | None:
    return ST_ORDER_COLUMN_BUSINESS.get(column.upper())


# --- CTRANS / DEBT / ACCOUNT --------------------------------------------------

TABLE_SINGLE_COLUMN_BUSINESS: dict[tuple[str, str], str] = {
    ("CTRANS", "TAX_AMT"): (
        "Số tiền thuế trên dòng chứng từ kế toán CTRANS — "
        "grain dòng chứng từ, join TRANS_NUM với header."
    ),
    ("CTRANS", "DEP_CODE"): "Mã phòng ban / cost center trên dòng CTRANS.",
    ("CTRANS", "BILL"): "Cờ tham chiếu bill POS gốc — link CTRANS ↔ bán lẻ.",
    ("DEBT", "DEBT_AMT"): "Số tiền công nợ còn lại trên chứng từ DEBT.",
    ("DEBT", "FINE_AMT"): "Tiền phạt chậm trả / phí phạt trên công nợ DEBT.",
    ("ACCOUNT", "ACCO_TYPE"): "Loại tài khoản công nợ (phải thu / phải trả / …).",
    ("ACCOUNT", "BANK_ACC"): "Cờ tài khoản ngân hàng — phân biệt TK công nợ vs bank.",
    ("ACCOUNT", "B_CREDIT"): "Số dư có đầu kỳ (beginning credit) trên tài khoản.",
    ("ACCOUNT", "Y_CREDIT"): "Phát sinh có trong kỳ (year/period credit).",
    ("ACCOUNT", "Y_DEBIT"): "Phát sinh nợ trong kỳ (year/period debit).",
    ("ACCOUNT", "BEG_CREDIT"): "Dư có đầu kỳ trên tài khoản kế toán.",
    ("INV_HDR", "EINV"): "Cờ hóa đơn điện tử (e-invoice) trên header nhập.",
    ("INV_HDR", "STR_NUM"): "Số chứng từ bán lẻ tham chiếu khi nhập hàng trả / đối soát.",
    ("INV_HDR", "STR_DATE"): "Ngày chứng từ bán lẻ tham chiếu trên header nhập.",
    ("INV_HDR", "CUSTAC"): "Tài khoản công nợ khách gắn hóa đơn mua / nhập.",
}


def compose_table_column_prose(table: str, column: str) -> str | None:
    return TABLE_SINGLE_COLUMN_BUSINESS.get((table.upper(), column.upper()))


# --- ASSO / combo -------------------------------------------------------------

ASSO_COLUMN_BUSINESS: dict[str, str] = {
    "ASSO_ID": "Mã combo / bundle — liên kết ASSOLST (header) ↔ ASSO_INF (chi tiết thành phần).",
    "ASSO_TYPE": "Loại combo (fixed bundle, pick-N, …) trên ASSOLST/ASSO_INF.",
    "ASSO_QTY": "Số lượng thành phần trong combo trên dòng bán STRANS.",
}


def compose_asso_prose(column: str) -> str | None:
    return ASSO_COLUMN_BUSINESS.get(column.upper())


ASSOLST_COLUMN_BUSINESS: dict[str, str] = {
    "DESCRIPT": "Mô tả combo / bundle — tên chương trình gộp hàng hiển thị trên ASSOLST master.",
    "FIX_RATIO": "Cờ tỷ lệ cố định giữa các thành phần combo — không cho phép thay đổi tỷ lệ mix.",
    "IsProcess": "Cờ combo đang trong quy trình xử lý / duyệt — chưa active bán POS.",
    "Planned": "Cờ combo đã lên kế hoạch nhưng chưa hiệu lực — chờ ngày FR_DATE.",
    "REVERSE": "Cờ combo reverse — đảo chiều quy tắc gộp (bundle ngược / unbundle).",
}


def compose_assolst_prose(column: str) -> str | None:
    col = column.upper()
    if col == "ISPROCESS":
        return ASSOLST_COLUMN_BUSINESS["IsProcess"]
    return ASSOLST_COLUMN_BUSINESS.get(col) or ASSOLST_COLUMN_BUSINESS.get(column)


SUPPLIER_COLUMN_BUSINESS: dict[str, str] = {
    "SUPP_NAME": "Tên nhà cung cấp chính thức trên master SUPPLIER — dùng tra cứu và in chứng từ mua.",
    "SUPP_NAME_U": "Tên NCC không dấu / unicode alternate — phục vụ search và tích hợp.",
    "SUPP_CODE": "Mã hiển thị / mã tra cứu nhà cung cấp — khác SUPP_ID nội bộ.",
    "MOQ": "Minimum Order Quantity — số lượng đặt hàng tối thiểu với NCC.",
    "MOA": "Minimum Order Amount — giá trị đơn đặt tối thiểu với NCC.",
    "ORD_PERIOD": "Chu kỳ đặt hàng mặc định (ngày/tuần) gắn NCC — lập lịch replenishment.",
    "FIXSALEPR": "Cờ giá bán cố định do NCC quy định — POS không tự điều chỉnh RTPRICE.",
    "PMT_SEQ": "Thứ tự / điều khoản thanh toán mặc định với NCC (công nợ, COD, …).",
    "ACC_CYS": "Loại tiền tệ tài khoản / giao dịch mặc định với NCC.",
}


def compose_supplier_prose(column: str) -> str | None:
    return SUPPLIER_COLUMN_BUSINESS.get(column.upper())


PMCRDINF_COLUMN_BUSINESS: dict[str, str] = {
    "BAL_AMT": "Số dư còn lại trên thẻ PM / voucher — dùng trước khi thanh toán bill.",
    "COND_AMT": "Ngưỡng giá trị bill tối thiểu để voucher PM có hiệu lực (điều kiện sử dụng).",
    "ISS_NUM": "Số phiếu phát hành thẻ PM / voucher — trace lifecycle phát hành.",
    "RCV_NUM": "Số phiếu nhận / kích hoạt voucher PM.",
    "STK_NUM": "Số phiếu nhập kho voucher PM (batch stock PM card).",
    "RCV_DATE": "Ngày nhận / kích hoạt voucher PM.",
    "STK_DATE": "Ngày nhập kho batch voucher PM.",
}


def compose_pmcrdinf_prose(column: str) -> str | None:
    return PMCRDINF_COLUMN_BUSINESS.get(column.upper())


ASSO_INF_COLUMN_BUSINESS: dict[str, str] = {
    "RATIO": "Tỷ lệ thành phần trong combo — số lượng / % so với bundle header ASSOLST.",
    "BASE_UNIT": "Đơn vị cơ sở quy đổi giữa các SKU trong combo ASSO_INF.",
}


def compose_asso_inf_prose(column: str) -> str | None:
    return ASSO_INF_COLUMN_BUSINESS.get(column.upper())


# --- WebRpt báo cáo -----------------------------------------------------------

WEBRPT_COLUMN_BUSINESS: dict[str, str] = {
    "SKU_ID": "Mã SKU trên báo cáo doanh số/tồn theo ngày — join SKU_DEF.",
    "STK_ID": "Mã cửa hàng trên báo cáo — grain store × SKU × ngày.",
    "REPORT_DATE": "Ngày snapshot báo cáo WebRpt — dùng filter khoảng thời gian phân tích.",
    "REFRESHED_AT": "Thời điểm job refresh snapshot — kiểm tra độ mới dữ liệu báo cáo.",
    "CARD_ID": "Mã thẻ trên snapshot RFM — join CSCARD/CRD_INFO.",
    "SALE_AMT": "Doanh số bán aggregate trên báo cáo ngày — không thay STRANS chi tiết.",
    "STK_QTY": "Tồn kho snapshot trên báo cáo inventory daily.",
}


def compose_webrpt_prose(table: str, column: str) -> str | None:
    if not table.upper().startswith("WEBRPT"):
        return None
    col = column.upper()
    if col in WEBRPT_COLUMN_BUSINESS:
        return f"{WEBRPT_COLUMN_BUSINESS[col]} (bảng {table})."
    return (
        f"Chỉ số aggregate trên báo cáo {table} — "
        "dùng cho phân tích nhanh, không thay chi tiết POS live."
    )


# --- SUPPLIER / CUSTOMER / PARTNER master ------------------------------------

MASTER_COLUMN_BUSINESS: dict[str, str] = {
    "BLOCK_CODE": "Mã block / phân khối phân loại khách hoặc NCC trên master.",
    "INDUSTRY": "Ngành nghề / lĩnh vực kinh doanh của khách B2B.",
    "CON_PERSON": "Tên người liên hệ chính của NCC / đối tác.",
    "COMPANY": "Cờ pháp nhân / công ty (corporate) vs cá nhân trên master.",
    "DEBT_MODE": "Chế độ công nợ mặc định gắn khách / đối tác (trả ngay / công nợ).",
    "CS_LEVEL": "Cấp độ phân hạng chăm sóc khách hàng (CS tier).",
}


def compose_master_prose(table: str, column: str) -> str | None:
    col = column.upper()
    if col in MASTER_COLUMN_BUSINESS and table.upper() in ("CUSTOMER", "SUPPLIER", "PARTNER", "CUSTSUMM"):
        return f"{MASTER_COLUMN_BUSINESS[col]} Trên master {table}."
    return None


# --- Entry point ---------------------------------------------------------------

def compose_domain_prose(
    *,
    semantic_key: str,
    column: str,
    table_names: list[str],
) -> str | None:
    """Return business prose if this chunk belongs to a known domain."""
    col = column.upper()
    sk = semantic_key.lower()

    if sk.startswith("stk_dtl__") or table_names == ["STK_DTL"]:
        return compose_stk_dtl_prose(col)
    if sk.startswith("rdiscinf__") or table_names == ["RDISCINF"]:
        return compose_rdiscinf_prose(col)
    if sk.startswith("sku_def__") or (table_names == ["SKU_DEF"] and sk != "product_internal_id"):
        return compose_sku_def_prose(col)
    if sk.startswith("crd_info__") or table_names == ["CRD_INFO"]:
        return compose_crd_info_prose(col)
    if sk.startswith("cscard__") or (table_names == ["CSCARD"] and col not in ("CARD_ID", "CARD_ID2")):
        return compose_cscard_prose(col)
    if sk.startswith("st_order__") or (table_names == ["ST_ORDER"] and col not in ("VAT_AMT",)):
        return compose_st_order_prose(col)
    if sk.startswith("supplier__") or table_names == ["SUPPLIER"]:
        return compose_supplier_prose(col)
    if sk.startswith("pmcrdinf__") or table_names == ["PMCRDINF"]:
        return compose_pmcrdinf_prose(col)
    if sk.startswith("assolst__") or table_names == ["ASSOLST"]:
        return compose_assolst_prose(col)
    if sk.startswith("asso_inf__") or table_names == ["ASSO_INF"]:
        return compose_asso_inf_prose(col)

    if len(table_names) == 1:
        t = table_names[0]
        hit = compose_table_column_prose(t, col)
        if hit:
            return hit
        webrpt = compose_webrpt_prose(t, col)
        if webrpt:
            return webrpt
        master = compose_master_prose(t, col)
        if master:
            return master

    if col in ASSO_COLUMN_BUSINESS and any(t in ("ASSOLST", "ASSO_INF", "STRANS") for t in table_names):
        return compose_asso_prose(col)

    for t in table_names:
        if t.upper().startswith("WEBRPT"):
            webrpt = compose_webrpt_prose(t, col)
            if webrpt:
                return webrpt

    return None
