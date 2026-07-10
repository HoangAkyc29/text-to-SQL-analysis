---
semantic_key: stkname
title: stkname
display_names:
- stkname
kind: text
tables:
- ref: db2:webrpt_inventory_daily
  column: stkname
  type: nvarchar
- ref: db2:webrpt_sales_sku_daily
  column: stkname
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên cửa hàng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# stkname

**Semantic key:** `stkname` · **Cột vật lý:** `stkname`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `stkname` | nvarchar | Tên cửa hàng |
| `db2:webrpt_sales_sku_daily` | `stkname` | nvarchar | Tên cửa hàng |

## Ghi chú thêm

- Tên cửa hàng
