---
logical_table: TRANSHDR_ARC
data_source: db1
physical_pattern: TRANSHDR_ARC
shard_key_column: TRAN_DATE
temporal_scope: history
temporal_rule: TRAN_DATE < cutoff (lịch sử từ tháng trước đó nữa trở về quá khứ).
description: "Archive header chứng từ giao dịch (nhiều TRANS_CODE: 113 bán lẻ, 221 thanh toán, …). Lọc TRANS_CODE=113 khi cần tổng bill bán."
column_count: 51
---

# TRANSHDR_ARC

Archive header chứng từ giao dịch (nhiều TRANS_CODE: 113 bán lẻ, 221 thanh toán, …). Lọc TRANS_CODE=113 khi cần tổng bill bán.

**Liên kết:** TRANS_NUM + TRANS_CODE → STRANS, PMTRANS

**Lưu ý:** Nhiều TRANS_CODE trong cùng bảng — lọc 113 cho bill bán. Chỉ giao dịch trước cutoff. cutoff = ngày 1 của tháng trước (so với ngày chạy query). Ví dụ hôm nay 22/06/2026 → cutoff = 2026-05-01.

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| IDX | numeric | Chỉ số dòng header (thường 0) |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| TRAN_DATE | datetime | Ngày giao dịch; chọn shard db1 theo YYYYMM |
| TRAN_TIME | char | Giờ giao dịch (HH:MM) |
| DUE_DATE | datetime | Hạn thanh toán / hạn giao |
| EF_DATE | datetime | Ngày hiệu lực |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| REF_NO | char | Số tham chiếu chứng từ liên quan |
| REF_DATE | datetime | Ngày tham chiếu |
| REF_TYPE | char | Cột REF_TYPE |
| POST | char | Trạng thái post chứng từ |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| STK_TYPE | char | Loại kho |
| SUPP_ID | char | Mã nhà cung cấp |
| SUPP_TYPE | char | Cột SUPP_TYPE |
| CUST_ID | char | Mã khách hàng |
| CUST_TYPE | char | Cột CUST_TYPE |
| IMP_ID | char | Nhập / import: IMP_ID |
| IMP_TYPE | char | Nhập / import: IMP_TYPE |
| EXP_ID | char | Xuất / export: EXP_ID |
| EXP_TYPE | char | Xuất / export: EXP_TYPE |
| AMOUNT | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| SURPLUS | numeric | Phụ phí / surplus |
| VAT_AMT | numeric | Tiền thuế VAT |
| DISCOUNT | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| COMM_AMT | numeric | Tiền hoa hồng |
| DEPOSIT | numeric | Cột DEPOSIT |
| PAID_AMT | numeric | Số tiền đã thanh toán |
| DEDUCT | numeric | Cột DEDUCT |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| STAFF_ID | char | Mã nhân viên |
| CARD_ID | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| REF | char | Mã/tham chiếu nội bộ |
| PMT_MODE | char | Chế độ thanh toán |
| UPDATED | bit | Đã cập nhật (bit) |
| COPIES | numeric | Cột COPIES |
| SHIFT | numeric | Ca làm việc |
| ACTION | char | Mã thao tác |
| INV_STATUS | char | Hóa đơn: INV_STATUS |
| IC_STATUS | char | Cột IC_STATUS |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| STATUS | char | Trạng thái active/duyệt |
| CTC_ID | char | Cột CTC_ID |
| PMT_TIME | char | Thời điểm thanh toán |
| CONTR_DT | datetime | Cột CONTR_DT |
| CONTR_NUM | varchar | Cột CONTR_NUM |
| CAR_ID | char | Cột CAR_ID |
| CONTR_BR | nvarchar | Cột CONTR_BR |
| REG_NUM | varchar | Cột REG_NUM |
