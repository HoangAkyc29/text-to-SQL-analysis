---
semantic_key: skucode
title: skucode
display_names:
- skucode
kind: text
tables:
- ref: db2:webrpt_inventory_daily
  column: skucode
  type: varchar
- ref: db2:webrpt_sales_sku_daily
  column: skucode
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Mã SKU hiển thị
sources:
- table_md
- column_semantic_registry
- business_prose
---

# skucode

**Semantic key:** `skucode` · **Cột vật lý:** `skucode`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `skucode` | varchar | Mã SKU hiển thị |
| `db2:webrpt_sales_sku_daily` | `skucode` | varchar | Mã SKU hiển thị |

## Ghi chú thêm

- Mã SKU hiển thị
