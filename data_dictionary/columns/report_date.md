---
semantic_key: report_date
title: report date
display_names:
- report_date
kind: date
tables:
- ref: db2:webrpt_inventory_daily
  column: report_date
  type: date
- ref: db2:webrpt_sales_sku_daily
  column: report_date
  type: date
join_with: []
related_semantic_keys: []
facts:
- Ngày báo cáo
sources:
- table_md
- column_semantic_registry
- business_prose
---

# report date

**Semantic key:** `report_date` · **Cột vật lý:** `report_date`

## Ý nghĩa nghiệp vụ

Ngày snapshot báo cáo WebRpt — dùng filter khoảng thời gian phân tích. (bảng WEBRPT_INVENTORY_DAILY).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `report_date` | date | Ngày báo cáo |
| `db2:webrpt_sales_sku_daily` | `report_date` | date | Ngày báo cáo |

## Ghi chú thêm

- Ngày báo cáo
