---
logical_table: PMTRANS
data_source: db2
physical_pattern: PMTRANS
shard_key_column: TRAN_DATE
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: "Thanh toán bill và quỹ: TRANS_CODE=221 (bill), 008 (thu/chi quỹ), 222 (loại khác — xem domain_definitions)."
column_count: 27
---

# PMTRANS

Thanh toán bill và quỹ: TRANS_CODE=221 (bill), 008 (thu/chi quỹ), 222 (loại khác — xem domain_definitions).

**Liên kết:** TRANS_NUM + TRANS_CODE → TRANSHDR, STRANS

**Lưu ý:** Thanh toán ~2 tháng gần nhất. cutoff = ngày 1 của tháng trước (so với ngày chạy query). Ví dụ hôm nay 22/06/2026 → cutoff = 2026-05-01.

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| TRAN_DATE | datetime | Ngày giao dịch (bảng live db2, không shard) |
| TRAN_TIME | char | Giờ giao dịch (HH:MM) |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| CARD_ID | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| IDX | int | Số thứ tự dòng trong chứng từ |
| PMT_CODE | char | Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space) |
| CYS | char | Loại tiền (VND) |
| FOREX_RATE | numeric | Tỷ giá ngoại tệ |
| FOREX_AMT | numeric | Số tiền quy đổi ngoại tệ |
| AMOUNT | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| ROUNDIFF | numeric | Chênh lệch làm tròn thanh toán |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| CUST_ID | char | Mã khách hàng |
| WS_ID | int | Mã máy trạm |
| POS_ID | int | Mã quầy POS |
| SHIFT | numeric | Ca làm việc |
| USER_ID | int | Mã user thao tác |
| UPDATED | bit | Đã cập nhật (bit) |
| REF | char | Mã/tham chiếu nội bộ |
| POST | char | Trạng thái post chứng từ |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| STATUS | bit | Trạng thái active/duyệt |
| REF_NO | varchar | Số tham chiếu chứng từ liên quan |
| REF_DATE | datetime | Ngày tham chiếu |
| ACTION | char | Mã thao tác |
