"""Vietnamese tooltips for form labels and preview/export columns.

Plain business language — avoid DB field names / technical jargon in user-facing copy.
"""
from __future__ import annotations

# Preview / Excel column headers (keys stay English as shown in the table)
COLUMN_TIPS: dict[str, str] = {
    # Product
    "SKU_ID": "Mã nội bộ của mặt hàng trong hệ thống (dùng để khớp với dòng bán).",
    "SKU_CODE": "Mã hàng nhìn thấy trên quầy / phiếu (thường khoảng 8 số; nhập tay dễ thiếu số 0 đầu).",
    "BARCODE": "Mã vạch trên bao bì — quét tại quầy hoặc tra cứu nhanh.",
    "FULL_NAME_U": "Tên đầy đủ của mặt hàng để đọc và tìm kiếm.",
    "GRP_ID": "Mã nhóm hàng trong cây phân loại.",
    "GRP_NAME": "Tên nhóm hàng (vd nhóm sữa, nhóm bánh…).",
    "DEPT_ID": "Mã ngành hàng lớn hơn nhóm (cấp phân loại cao hơn).",
    "UNIT_SYMB": "Đơn vị bán: gói, hộp, kg…",
    "RTPRICE": "Giá bán lẻ đề xuất trên danh mục.",
    "STATUS": "Trạng thái mặt hàng trên danh mục (còn hiệu lực / đã khóa…).",
    # Customer / card
    "CARD_ID": "Số thẻ khách hàng thân thiết. Chữ cái đầu (A, E, F…) thường gắn với hạng thẻ.",
    "NAME": "Họ tên chủ thẻ (ưu tiên bản tiếng Việt đầy đủ nếu có).",
    "NAME_U": "Họ tên chủ thẻ viết Unicode, dùng để hiển thị.",
    "PHONE": "Số điện thoại liên hệ ghi trên thẻ.",
    "MOBI": "Số di động trên hồ sơ thẻ (dùng khi lọc; không luôn xuất ra file danh sách khách).",
    "SEX": "Giới tính trên hồ sơ thẻ: Nam hoặc Nữ.",
    "BIRTHDAY": "Ngày sinh — dùng tính tuổi và lọc tháng sinh nhật.",
    "DISC_LVL": "Mức chiết khấu / hạng ưu đãi của thẻ.",
    "CUST_ID": "Mã khách nội bộ gắn với thẻ (không phải số thẻ).",
    # Transaction
    "TRANS_NUM": "Số hóa đơn / phiếu mua — mỗi đơn một số.",
    "STK_ID": "Mã siêu thị (cửa hàng) nơi phát sinh giao dịch.",
    "TRAN_DATE": "Ngày mua hàng.",
    "TRAN_TIME": "Giờ mua hàng tại quầy (giờ:phút).",
    "TRANS_CODE": "Loại phiếu (bán lẻ, thanh toán, tích điểm…). Ứng dụng không tự ép một loại cố định.",
    "IDX": "Thứ tự dòng hàng trong cùng một hóa đơn (thường không xuất ở xem trước đơn).",
    "QTY": "Số lượng mặt hàng trên dòng (thường không xuất ở xem trước đơn).",
    "AMOUNT": "Tiền hàng thuần trên dòng STRANS (không xuất Excel — dùng nội bộ lọc quà/trả tiền).",
    "SURPLUS": "Khoản phụ cộng thêm vào dòng hoặc cả đơn.",
    "VAT_AMT": "Tiền thuế GTGT trên dòng hoặc trên cả đơn.",
    "line_total": (
        "Thành tiền dòng (đủ): tiền hàng + phụ phí + thuế GTGT trên dòng STRANS. "
        "Đây là số dùng để cộng giá trị, không phải cột AMOUNT thuần."
    ),
    "bill_value": "Tổng thành tiền cả hóa đơn (cùng công thức: tiền hàng + phụ phí + thuế).",
    # Loyalty metrics
    "total_value": "Tổng tiền mua của thẻ trong kỳ đang chọn.",
    "points": "Điểm tích lũy = floor(tổng tiền mua ÷ 50.000) — luôn làm tròn xuống.",
    "bill_count": "Số hóa đơn (số lần mua) của thẻ trong kỳ.",
}

# Form / section captions and control labels
FIELD_TIPS: dict[str, str] = {
    # Shared
    "CÁCH TÌM": "Cách khớp chữ khi tìm mã hoặc tên (chính xác hay gần đúng).",
    "Không phân biệt hoa/thường": "Bỏ qua chữ hoa/thường và khoảng trắng thừa khi so sánh.",
    "Tìm gần đúng (chứa chuỗi; tiền tố = bắt đầu bằng)": (
        "Cho phép tìm khi chỉ gõ một phần mã/tên. Với tiền tố thẻ: khớp phần đầu số thẻ, không tìm chữ nằm giữa."
    ),
    "SIÊU THỊ": "Chọn cửa hàng cần xem. Có thể chọn sẵn vài mã phổ biến hoặc tự thêm.",
    "Thêm mã siêu thị (phẩy)": "Gõ thêm mã cửa hàng khác, cách nhau bằng dấu phẩy.",
    "Tiền tố thẻ": "Lọc thẻ theo chữ/số mở đầu (vd A, E, F). Chỉ khớp phần đầu, không phải chữ bất kỳ trong số thẻ.",
    "Từ ngày": "Ngày bắt đầu khoảng thời gian mua hàng.",
    "Đến ngày": "Ngày kết thúc khoảng thời gian mua hàng.",
    "Khoảng ngày": "Chỉ lấy giao dịch trong khoảng ngày này.",
    "Tuổi từ": "Tuổi tối thiểu của chủ thẻ (tính từ ngày sinh đến hôm nay).",
    "Tuổi đến": "Tuổi tối đa của chủ thẻ.",
    "Độ tuổi": "Lọc khách theo khoảng tuổi.",
    "Giới tính": "Chỉ lấy Nam, Nữ, hoặc tất cả.",
    "Giá trị từ": "Giá trị hóa đơn tối thiểu (tiền hàng + phụ phí + thuế).",
    "Giá trị đến": "Giá trị hóa đơn tối đa. Để trống = không giới hạn trên.",
    "Khoảng giá trị đơn": "Chỉ giữ hóa đơn có tổng tiền nằm trong khoảng này.",
    "Khoảng giá trị": "Ngưỡng dưới–trên theo điểm hoặc theo tổng tiền mua (tùy tiêu chí đã chọn).",
    "Loại dòng SP": "Chỉ dòng trả tiền, chỉ quà tặng (tiền = 0), hoặc cả hai — áp khi đã lọc theo sản phẩm.",
    "Sắp xếp theo cột": "Đổi thứ tự dòng trên màn hình kết quả. Không chạy lại tìm kiếm; file Excel cũng theo cách sắp này.",
    # Product search
    "Mã sản phẩm / barcode": "Nhập mã hàng, mã nội bộ, hoặc mã vạch để tìm mặt hàng.",
    "Tên sản phẩm": "Tìm theo tên mặt hàng.",
    "Mã nhóm": "Lọc mặt hàng thuộc một mã nhóm.",
    "Tên nhóm": "Lọc mặt hàng theo tên nhóm hàng.",
    # Customer search
    "Tra cứu": "Có thể kết hợp mã thẻ, tiền tố, tên và SĐT — tất cả điều kiện cùng lúc.",
    "Mã thẻ": "Số thẻ khách. Bật tìm gần đúng = chứa đoạn số; tắt = khớp đúng cả số thẻ.",
    "Mã thẻ (mỗi dòng một mã, hoặc cách bằng phẩy)": (
        "Danh sách số thẻ cần lấy đúng từng mã — mỗi dòng một thẻ hoặc cách bằng dấu phẩy."
    ),
    "Tên khách": "Tìm theo họ tên chủ thẻ.",
    "SĐT": "Tìm theo số điện thoại / di động trên hồ sơ thẻ.",
    "Tháng sinh & độ tuổi": "Lọc theo tháng sinh nhật và/hoặc khoảng tuổi.",
    "Tháng sinh": "Chỉ khách sinh trong tháng đã chọn, hoặc Tất cả.",
    # Loyalty period
    "Bộ lọc": "Điều kiện kỳ mua, điểm/tiền, và siêu thị trước khi gom theo từng thẻ.",
    "Tiêu chí": "Lọc theo điểm tích lũy hoặc theo tổng tiền mua.",
    "Tiêu chí lọc": "Lọc theo điểm tích lũy hoặc theo tổng tiền mua.",
    "Từ": "Ngưỡng dưới của điểm hoặc tổng tiền (theo tiêu chí đã chọn).",
    "Đến": "Ngưỡng trên. Để trống = không giới hạn.",
    "Mức điểm chia file": "Các mốc điểm để tách nhiều file Excel, ví dụ 0-200,200-500,>500.",
    "Chia Excel theo mức điểm": "Xuất nhiều file theo từng khoảng điểm đã khai báo.",
    "NỘI DUNG FILE THỐNG KÊ": "Chọn phần nào sẽ ghi vào báo cáo dạng văn bản.",
    "Số lượng khách": "Ghi tổng số khách trong nhóm kết quả.",
    "Phân bố điểm": "Thống kê số khách theo từng khoảng điểm.",
    "Theo siêu thị": "Số đơn, tổng tiền và trung bình theo từng cửa hàng.",
    "Theo giờ mua": "Phân bố đơn theo khung giờ trong ngày.",
    "Theo độ tuổi": "Phân khúc khách theo nhóm tuổi.",
    "Theo tháng": "Phân bố mua hàng theo tháng trong kỳ.",
    # Orders by customer
    "Danh sách thẻ": "Các số thẻ cần tra cứu đúng từng mã (không tìm mơ hồ).",
    "Sản phẩm trong đơn": "Chỉ giữ hóa đơn có ít nhất một dòng chứa mặt hàng này.",
    "Sản phẩm phải có trong đơn": "Chỉ giữ hóa đơn có ít nhất một dòng chứa mặt hàng này.",
    "ĐIỀU KIỆN KHÁCH": "Lọc thêm theo tuổi hoặc giới tính của chủ thẻ.",
    "Chế độ xem trước": "Xem tóm tắt từng hóa đơn, hoặc xem đủ mọi mặt hàng trong hóa đơn.",
    "Dòng đơn khớp": "Các dòng hàng đã thỏa bộ lọc (không gồm thứ tự dòng / số lượng).",
    "Chi tiết full bill (mọi SP trong đơn)": "Mọi mặt hàng trong các hóa đơn đã giữ lại — kể cả hàng không nằm trong bộ lọc.",
    # Orders by product
    "Sản phẩm cần tìm": "Mỗi dòng một mã hoặc tên hàng. Để trống = lấy tất cả đơn trong khoảng ngày (vẫn áp dụng siêu thị / thẻ / giá trị / quà).",
    "Mã hoặc tên sản phẩm (mỗi dòng một mục)": "Mỗi dòng một mặt hàng cần tìm.",
    "ĐIỀU KIỆN KHÁCH HÀNG": (
        "Lọc theo tháng sinh, tuổi, giới tính hoặc tiền tố thẻ. "
        "Nếu bật tháng sinh/tuổi/giới tính, chỉ lấy hóa đơn gắn thẻ khách."
    ),
    "Chỉ đơn có thẻ": "Bỏ qua giao dịch khách vãng lai (không quẹt thẻ).",
    "Kèm danh sách thẻ đã mua": "Khi xuất file, thêm danh sách thẻ đã mua mặt hàng đang tìm.",
    "TÙY CHỌN XUẤT": "Tuỳ chọn khi ghi file Excel / báo cáo.",
    "Tách file Excel": "Tách nhiều file theo thẻ, theo mã hàng, hoặc theo siêu thị (trên chi tiết đủ dòng hóa đơn).",
    "Tách file": "Tách nhiều file theo thẻ, theo mã hàng, hoặc theo siêu thị.",
    "Tách file (chọn một) — luôn theo full STRANS": (
        "File tách dựa trên chi tiết đủ dòng trong hóa đơn. "
        "File chính vẫn gồm cả tóm tắt đơn và chi tiết dòng."
    ),
    "Đơn hàng (TRANSHDR)": "Mỗi dòng là một hóa đơn có chứa sản phẩm đang tìm (tóm tắt đơn).",
    "Chi tiết đơn (full STRANS)": "Liệt kê mọi mặt hàng trong các hóa đơn đó, không chỉ sản phẩm đang tìm.",
    "Giới tính & tiền tố": "Lọc theo giới tính chủ thẻ và/hoặc chữ mở đầu số thẻ.",
    # Settings / nav
    "ANALYTICS_DB_DSN (db1 — Server=DESKTOP-AUQEDC5)": (
        "Chuỗi kết nối tới kho dữ liệu lịch sử (các tháng cũ)."
    ),
    "ANALYTICS_DB_DSN_2 (db2)": (
        "Chuỗi kết nối tới kho dữ liệu hiện hành (danh mục hàng, thẻ, giao dịch gần đây)."
    ),
    "Thư mục xuất": "Khi bấm Xuất, cửa sổ chọn thư mục sẽ mở — chọn nơi lưu bộ file lần đó.",
    "Tìm mặt hàng": "Tra cứu mặt hàng theo mã, mã vạch hoặc tên.",
    "Tìm khách": "Tra cứu thẻ khách theo mã thẻ, tên hoặc SĐT.",
    "KH theo kỳ": "Danh sách khách trong một kỳ mua, lọc điểm/tiền, xuất Excel và thống kê.",
    "Đơn theo khách": "Lấy hóa đơn theo danh sách thẻ; có thể lọc thêm hàng, giá trị đơn, quà/trả tiền.",
    "Đơn theo SP": "Tìm hóa đơn có chứa sản phẩm chỉ định (hoặc tất cả đơn nếu để trống danh sách SP); xuất tóm tắt đơn và chi tiết dòng.",
    "SP theo nhóm": "Tra cứu mặt hàng theo mã hoặc tên nhóm.",
    "Cài đặt": "Kết nối dữ liệu và thư mục lưu kết quả.",
    "Tổng quan": "Chọn chức năng cần làm.",
    # Page titles (full headers)
    "Khách hàng theo kỳ": (
        "Tìm khách mua trong khoảng ngày: lọc điểm/giá trị, tháng sinh, tuổi, giới tính, tiền tố thẻ, "
        "siêu thị; chia Excel theo mức điểm; xuất thống kê TXT."
    ),
    "Đơn hàng theo khách": (
        "Nhập danh sách thẻ → lấy hóa đơn của từng thẻ; có thể lọc sản phẩm trong đơn, "
        "giá trị đơn, tuổi/giới tính; xem dòng khớp hoặc full bill."
    ),
    "Đơn hàng theo sản phẩm": (
        "Nhập mã/tên sản phẩm → tìm hóa đơn có chứa hàng đó; "
        "xuất tóm tắt đơn (TRANSHDR) và chi tiết mọi dòng trong đơn (STRANS)."
    ),
    "Tìm khách hàng": "Tra cứu thẻ khách theo mã thẻ, tiền tố, tên, SĐT, tháng sinh hoặc độ tuổi.",
    "Mặt hàng theo nhóm": "Tra cứu mặt hàng theo mã hoặc tên nhóm hàng trên danh mục.",
    "Cài đặt kết nối": "Cấu hình chuỗi kết nối ODBC (db1 lịch sử / db2 hiện hành) và thư mục lưu file.",
    "Kết quả": "Bảng xem trước kết quả tìm; sắp xếp tại đây không chạy lại truy vấn.",
}


def tip_for_stk(stk_id: str | None) -> str:
    code = (stk_id or "").strip() or "?"
    return f"Siêu thị {code}. Bật để đưa cửa hàng này vào bộ lọc; tắt để bỏ ra."


def tip_for_column(column: str | None) -> str | None:
    if not column:
        return None
    return COLUMN_TIPS.get(str(column).strip())


def tip_for_field(label: str | None) -> str | None:
    if not label:
        return None
    key = str(label).strip()
    if key in FIELD_TIPS:
        return FIELD_TIPS[key]
    base = key.split("(")[0].strip()
    return FIELD_TIPS.get(base)


def as_tooltip(message: str | None) -> str | None:
    """Normalize tip copy for Control.tooltip (plain str — Theme styles the bubble)."""
    if not message:
        return None
    text = str(message).strip()
    return text or None


def column_header_tooltip(column: str, *, sortable: bool = False) -> str | None:
    tip = tip_for_column(column) or ""
    if sortable:
        sort_hint = "Bấm để sắp xếp cột này (tăng / giảm)."
        tip = f"{tip}\n\n{sort_hint}".strip() if tip else sort_hint
    return as_tooltip(tip or None)
