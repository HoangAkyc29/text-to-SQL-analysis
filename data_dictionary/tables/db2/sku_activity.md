---
logical_table: sku_activity
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Ngày bán/nhập đầu–cuối theo cửa hàng × SKU.
column_count: 7
---

# sku_activity

Ngày bán/nhập đầu–cuối theo cửa hàng × SKU.

| column | type | description |
|--------|------|-------------|
| stk_id | varchar | Mã cửa hàng |
| sku_id | varchar | Mã SKU |
| first_sale_date | date | Ngày bán đầu tiên |
| last_sale_date | date | Ngày bán gần nhất |
| first_receipt_date | date | Ngày nhập đầu tiên |
| last_receipt_date | date | Ngày nhập gần nhất |
| updated_at | datetime | Thời điểm cập nhật |
