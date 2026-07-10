---
semantic_key: sku_def__grp_name
title: Tên grp (SKU_DEF)
display_names:
- GRP_NAME
kind: text
tables:
- ref: db2:sku_def
  column: GRP_NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tên grp (SKU_DEF)

**Semantic key:** `sku_def__grp_name` · **Cột vật lý:** `GRP_NAME`

## Ý nghĩa nghiệp vụ

Tên nhóm hàng (merchandise group) trên master SKU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `GRP_NAME` | nvarchar | Tên grp trên master sản phẩm (SKU) |
