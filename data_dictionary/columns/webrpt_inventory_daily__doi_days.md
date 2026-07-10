---
semantic_key: webrpt_inventory_daily__doi_days
title: Doi Days (WEBRPT_INVENTORY_DAILY)
display_names:
- doi_days
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: doi_days
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Days of inventory
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Doi Days (WEBRPT_INVENTORY_DAILY)

**Semantic key:** `webrpt_inventory_daily__doi_days` · **Cột vật lý:** `doi_days`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `doi_days` | decimal | Days of inventory |

## Ghi chú thêm

- Days of inventory
