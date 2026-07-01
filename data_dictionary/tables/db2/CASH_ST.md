---
logical_table: CASH_ST
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Kiểm đếm quỹ tiền mặt theo ca — đếm số tờ theo mệnh giá (TRANS_CODE=010).
column_count: 15
---

# CASH_ST

Kiểm đếm quỹ tiền mặt theo ca — đếm số tờ theo mệnh giá (TRANS_CODE=010).

| column | type | description |
|--------|------|-------------|
| TRAN_DATE | datetime | Ngày giao dịch (bảng live db2, không shard) |
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| PMT_CODE | char | Hình thức TT: CASH, CARD, BANK, OWNCP (có thể có space) |
| CYS | char | Loại tiền (VND) |
| VALUE | numeric | Mệnh giá tờ tiền (200, 500, 1000, … VND) |
| QTY | numeric | Số tờ theo mệnh giá trong ca |
| FOREX_RATE | numeric | Tỷ giá ngoại tệ |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| WS_ID | int | Mã máy trạm |
| POS_ID | int | Mã quầy POS |
| SHIFT | numeric | Ca làm việc |
| USER_ID | int | Mã user thao tác |
| STATUS | bit | Trạng thái active/duyệt |
