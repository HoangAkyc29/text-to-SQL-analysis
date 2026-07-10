---
semantic_key: grpname
title: grpname
display_names:
- grpname
kind: text
tables:
- ref: db2:webrpt_inventory_daily
  column: grpname
  type: nvarchar
- ref: db2:webrpt_sales_sku_daily
  column: grpname
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên nhóm hàng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# grpname

**Semantic key:** `grpname` · **Cột vật lý:** `grpname`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_INVENTORY_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_inventory_daily` | `grpname` | nvarchar | Tên nhóm hàng |
| `db2:webrpt_sales_sku_daily` | `grpname` | nvarchar | Tên nhóm hàng |

## Ghi chú thêm

- Tên nhóm hàng
