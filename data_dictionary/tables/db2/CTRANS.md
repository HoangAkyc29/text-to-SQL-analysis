---
logical_table: CTRANS
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Dòng công nợ / thanh toán công nợ gắn chứng từ (DEBT_NO, ACCOUNT_ID); có thể TRANS_CODE=113.
column_count: 39
---

# CTRANS

Dòng công nợ / thanh toán công nợ gắn chứng từ (DEBT_NO, ACCOUNT_ID); có thể TRANS_CODE=113.

| column | type | description |
|--------|------|-------------|
| IDX | int | Số thứ tự dòng trong chứng từ |
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| TRAN_DATE | datetime | Ngày giao dịch (bảng live db2, không shard) |
| TRAN_TIME | char | Giờ giao dịch (HH:MM) |
| EF_DATE | datetime | Ngày hiệu lực |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| REF_NO | char | Số tham chiếu chứng từ liên quan |
| INV_TYPE | varchar | Loại hóa đơn |
| REF_DATE | datetime | Ngày tham chiếu |
| DEBT_NO | char | Số chứng từ công nợ |
| DEBT_DATE | datetime | Ngày phát sinh công nợ |
| DUE_DATE | datetime | Hạn thanh toán / hạn giao |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| TRANS_TYPE | char | Phân loại giao dịch thẻ |
| ACCOUNT_ID | char | Mã tài khoản công nợ |
| CYS | char | Loại tiền (VND) |
| CUST_ID | char | Mã khách hàng |
| TAX_CODE | char | Mã thuế |
| TAX_RATE | numeric | Thuế suất |
| TAX_AMT | numeric | Số tiềnTAX_AMT |
| AMOUNT | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| BILL | bit | Tham chiếu bill / chứng từ gốc |
| ACTION | char | Mã thao tác |
| DEP_CODE | char | MãDEP_CODE |
| NODE_ID | char | Mã node / chi nhánh hệ thống |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| STAFF_ID | char | Mã nhân viên |
| REF | char | Mã/tham chiếu nội bộ |
| POST | char | Trạng thái post chứng từ |
| WS_ID | int | Mã máy trạm |
| USER_ID | int | Mã user thao tác |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| STATUS | bit | Trạng thái active/duyệt |
| INV_CODE | varchar | Mã serial HĐ |
| INV_NO | varchar | Số hóa đơn |
| INV_DATE | datetime | Ngày hóa đơn |
| INV_REF | varchar | Tham chiếu hóa đơn |
| INV_POS | varchar | Vị trí / quầy HĐ |
| INV_TRANS | varchar | Hóa đơn: INV_TRANS |
