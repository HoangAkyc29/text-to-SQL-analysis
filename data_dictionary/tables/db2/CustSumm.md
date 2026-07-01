---
logical_table: CustSumm
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Tóm tắt KH + thẻ (denormalized).
column_count: 7
---

# CustSumm

Tóm tắt KH + thẻ (denormalized).

| column | type | description |
|--------|------|-------------|
| Card_ID | char | Cột Card_ID |
| Name | nvarchar | Tên khách (CustSumm) |
| Address | nvarchar | Cột Address |
| Phone | char | Điện thoại |
| Mobil | char | Di động |
| Amount | numeric | Tổng mua (CustSumm) |
| Remark | nvarchar | Cột Remark |
