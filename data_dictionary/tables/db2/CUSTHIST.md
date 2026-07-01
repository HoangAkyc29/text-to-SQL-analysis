---
logical_table: CUSTHIST
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Lịch sử mua theo SKU/khách.
column_count: 14
---

# CUSTHIST

Lịch sử mua theo SKU/khách.

| column | type | description |
|--------|------|-------------|
| ID | char | Cột ID |
| TYPE | char | Loại bản ghi (ngữ cảnh theo bảng) |
| SKU_ID | char | Mã sản phẩm nội bộ |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| IMPORT | bit | Cờ nhập / import |
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| TRAN_DATE | datetime | Ngày giao dịch (bảng live db2, không shard) |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| QTY | numeric | Số lượng |
| AMOUNT | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| SURP_AMT | numeric | Số tiềnSURP_AMT |
| VAT_AMT | numeric | Tiền thuế VAT |
| DISC_AMT | numeric | Số tiềnDISC_AMT |
| COMM_AMT | numeric | Tiền hoa hồng |
