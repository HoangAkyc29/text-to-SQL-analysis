---
logical_table: DEBT
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Chứng từ công nợ.
column_count: 19
---

# DEBT

Chứng từ công nợ.

| column | type | description |
|--------|------|-------------|
| DEBT_NO | char | Số chứng từ công nợ |
| DEBT_DATE | datetime | Ngày phát sinh công nợ |
| CUST_ID | char | Mã khách hàng |
| ACCOUNT_ID | char | Mã tài khoản công nợ |
| CYS | char | Loại tiền (VND) |
| DEBT_AMT | numeric | Số tiền công nợ |
| PAID_AMT | numeric | Số tiền đã thanh toán |
| ACTION | char | Mã thao tác |
| DUE_DATE | datetime | Hạn thanh toán / hạn giao |
| LAST_DATE | datetime | Ngày giao dịch / cập nhật gần nhất |
| REF | char | Mã/tham chiếu nội bộ |
| FINE_AMT | numeric | Số tiềnFINE_AMT |
| INV_TYPE | varchar | Loại hóa đơn |
| INV_CODE | varchar | Mã serial HĐ |
| INV_NO | char | Số hóa đơn |
| INV_Date | datetime | Ngày hóa đơn |
| INV_VATAMT | numeric | VAT trên hóa đơn |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| STATUS | bit | Trạng thái active/duyệt |
