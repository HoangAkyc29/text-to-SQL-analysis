---
logical_table: WebRpt_inventory_daily
data_source: db2
temporal_scope: report
temporal_rule: Báo cáo tổng hợp trên db2 — lọc theo report_date / snapshot_date.
description: "Báo cáo tồn kho ngày: on-hand, DOI, trạng thái."
column_count: 17
---

# WebRpt_inventory_daily

Báo cáo tồn kho ngày: on-hand, DOI, trạng thái.

| column | type | description |
|--------|------|-------------|
| report_date | date | Ngày báo cáo |
| stk_id | varchar | Mã cửa hàng |
| sku_id | varchar | Mã SKU |
| grp_id | varchar | Mã nhóm hàng |
| skucode | varchar | Mã SKU hiển thị |
| stkname | nvarchar | Tên cửa hàng |
| grpname | nvarchar | Tên nhóm hàng |
| skuname | nvarchar | Tên sản phẩm |
| qty_onhand | decimal | Tồn kho hiện tại |
| value_onhand | decimal | Giá trị tồn |
| avg_daily_qty_30d | decimal | Cột avg_daily_qty_30d |
| doi_days | decimal | Days of inventory |
| days_no_sale | int | Số ngày không bán |
| days_since_receipt | int | Cột days_since_receipt |
| stock_status | varchar | Trạng thái tồn (WARN - Discontinued, INFO - Never Sold, …) |
| DMS | numeric | Chỉ số DMS (days of supply) |
| refreshed_at | datetime | Thời điểm làm mới báo cáo |
