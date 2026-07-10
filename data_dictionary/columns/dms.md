---
semantic_key: dms
title: dms
display_names:
- DMS
kind: measure
tables:
- ref: db2:sku_def
  column: DMS
  type: numeric
- ref: db2:st_order
  column: DMS
  type: numeric
- ref: db2:webrpt_inventory_daily
  column: DMS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Days of supply
sources:
- table_md
- column_semantic_registry
- business_prose
---

# dms

**Semantic key:** `dms` · **Cột vật lý:** `DMS`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `DMS` | numeric | Days of supply |
| `db2:st_order` | `DMS` | numeric | Days of supply |
| `db2:webrpt_inventory_daily` | `DMS` | numeric | Chỉ số DMS (days of supply) |

## Ghi chú thêm

- Days of supply
