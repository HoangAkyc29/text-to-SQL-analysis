---
logical_table: ACCOUNT
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Tài khoản công nợ KH/NCC/NV.
column_count: 20
---

# ACCOUNT

Tài khoản công nợ KH/NCC/NV.

| column | type | description |
|--------|------|-------------|
| ACCOUNT_ID | char | Mã tài khoản công nợ |
| CYS | char | Loại tiền (VND) |
| ACCO_TYPE | char | Cột ACCO_TYPE |
| NAME | nvarchar | Tên |
| CUST_ID | char | Mã khách hàng |
| SUPP_ID | char | Mã nhà cung cấp |
| STAFF_ID | char | Mã nhân viên |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| OPEN_DATE | datetime | Ngày mở / tạo |
| PREV_DATE | datetime | NgàyPREV_DATE |
| LAST_DATE | datetime | Ngày giao dịch / cập nhật gần nhất |
| CR_LIMIT | numeric | Hạn mức tín dụng |
| CR_AMT | numeric | Dư nợ hiện tại |
| BEG_CREDIT | numeric | Số dư đầu kỳ: BEG_CREDIT |
| B_CREDIT | numeric | Cột B_CREDIT |
| Y_CREDIT | numeric | Cột Y_CREDIT |
| Y_DEBIT | numeric | Cột Y_DEBIT |
| STATUS | bit | Trạng thái active/duyệt |
| BANK_ACC | bit | Cột BANK_ACC |
| CLOSE_DATE | datetime | Ngày đóng |
