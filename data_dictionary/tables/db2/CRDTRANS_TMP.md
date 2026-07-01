---
logical_table: CRDTRANS_TMP
data_source: db2
physical_pattern: CRDTRANS_TMP
temporal_scope: staging
temporal_rule: Dữ liệu tạm POS — không dùng báo cáo chính thức.
description: Staging giao dịch thẻ trước khi post — không dùng báo cáo chính thức.
column_count: 35
---

# CRDTRANS_TMP

Staging giao dịch thẻ trước khi post — không dùng báo cáo chính thức.

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| CARD_ID | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| ACML_CODE | char | Mã chương trình tích lũy |
| TRAN_DATE | datetime | Ngày giao dịch (bảng live db2, không shard) |
| TRAN_TIME | char | Giờ giao dịch (HH:MM) |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| TRANS_TYPE | char | Phân loại giao dịch thẻ |
| RS_CODE | char | Mã lý do (hủy, trả, …) |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| IDX | numeric | Số thứ tự dòng trong chứng từ |
| CUST_ID | char | Mã khách hàng |
| TYPE | char | Loại bản ghi (ngữ cảnh theo bảng) |
| DISCOUNT | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| AMOUNT | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| MARK | numeric | Điểm tích lũy; ~AMOUNT/50000 trên CRDTRANS 811 |
| MARK_VAL | numeric | Giá trị quy đổi điểm |
| MARK_MUL | numeric | Hệ số nhân điểm |
| RFN_AMT | numeric | Hoàn / refund điểm: RFN_AMT |
| RFN_MARK | numeric | Hoàn / refund điểm: RFN_MARK |
| RFN_RATE | numeric | Hoàn / refund điểm: RFN_RATE |
| RBT_AMT | numeric | Rebate: RBT_AMT |
| PRG_CODE | char | MãPRG_CODE |
| REF | char | Mã/tham chiếu nội bộ |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| STAFF_ID | char | Mã nhân viên |
| NOTES | nvarchar | Ghi chú bổ sung |
| RCV_DATE | datetime | NgàyRCV_DATE |
| RCV_TIME | char | Cột RCV_TIME |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| POST | char | Trạng thái post chứng từ |
| STATUS | bit | Trạng thái active/duyệt |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| VAT_AMT | numeric | Tiền thuế VAT |
| COMM_AMT | numeric | Tiền hoa hồng |
