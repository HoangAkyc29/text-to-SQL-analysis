---
semantic_key: refreshed_at
title: refreshed at
display_names:
- refreshed_at
kind: date
tables:
- ref: db2:webrpt_inventory_daily
  column: refreshed_at
  type: datetime
- ref: db2:webrpt_rfm_snapshot
  column: refreshed_at
  type: datetime
- ref: db2:webrpt_sales_sku_daily
  column: refreshed_at
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Thời điểm làm mới báo cáo
sources:
- table_md
- column_semantic_registry
- business_prose
---

# refreshed at

**Semantic key:** `refreshed_at` · **Cột vật lý:** `refreshed_at`

## Ý nghĩa nghiệp vụ

Thời điểm job refresh snapshot — kiểm tra độ mới dữ liệu báo cáo. (bảng WEBRPT_INVENTORY_DAILY).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `refreshed_at` | datetime | Thời điểm làm mới báo cáo |
| `db2:webrpt_rfm_snapshot` | `refreshed_at` | datetime | Thời điểm làm mới báo cáo |
| `db2:webrpt_sales_sku_daily` | `refreshed_at` | datetime | Thời điểm làm mới báo cáo |

## Ghi chú thêm

- Thời điểm làm mới báo cáo
