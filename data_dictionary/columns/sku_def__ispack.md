---
semantic_key: sku_def__ispack
title: Cờ thuộc tính (pack) (SKU_DEF)
display_names:
- IsPack
kind: flag
tables:
- ref: db2:sku_def
  column: IsPack
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (pack) (SKU_DEF)

**Semantic key:** `sku_def__ispack` · **Cột vật lý:** `IsPack`

## Ý nghĩa nghiệp vụ

Cờ thuộc tính sản phẩm (pack) trên master SKU — yes/no.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `IsPack` | bit | Cờ thuộc tính (pack) trên master sản phẩm (SKU) |
