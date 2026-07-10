---
semantic_key: skuname
title: skuname
display_names:
- skuname
kind: text
tables:
- ref: db2:webrpt_inventory_daily
  column: skuname
  type: nvarchar
- ref: db2:webrpt_sales_sku_daily
  column: skuname
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên sản phẩm
sources:
- table_md
- column_semantic_registry
- business_prose
---

# skuname

**Semantic key:** `skuname` · **Cột vật lý:** `skuname`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `skuname` | nvarchar | Tên sản phẩm |
| `db2:webrpt_sales_sku_daily` | `skuname` | nvarchar | Tên sản phẩm |

## Ghi chú thêm

- Tên sản phẩm
