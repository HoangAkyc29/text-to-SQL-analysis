---
logical_table: WebRpt_sales_sku_daily
data_source: db2
temporal_scope: report
temporal_rule: Báo cáo tổng hợp trên db2 — lọc theo report_date / snapshot_date.
description: Báo cáo doanh thu SKU × cửa hàng × ngày (ưu tiên cho aggregate).
column_count: 24
---

# WebRpt_sales_sku_daily

Báo cáo doanh thu SKU × cửa hàng × ngày (ưu tiên cho aggregate).

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
| qty | decimal | Số lượng bán trong ngày |
| revenue | decimal | Doanh thu |
| cogs | decimal | Giá vốn |
| gross_profit | decimal | Lãi gộp |
| bill_count | int | Số bill trong ngày |
| refreshed_at | datetime | Thời điểm làm mới báo cáo |
| mdisc_total | decimal | Tổng chiết khấu manual |
| tdisc_total | decimal | Tổng chiết khấu transaction |
| cdisc_total | decimal | Tổng chiết khấu coupon |
| gdisc_total | decimal | Tổng chiết khấu gift |
| discount_total | decimal | Tổng chiết khấu |
| tdadd_total | decimal | Tổng phụ thu transaction |
| mdadd_total | decimal | Tổng phụ thu manual |
| gift_qty | decimal | Số lượng quà tặng |
| free_qty | decimal | Số lượng hàng tặng |
| free_cogs | decimal | Giá vốn hàng tặng |
