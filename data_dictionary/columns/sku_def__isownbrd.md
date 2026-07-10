---
semantic_key: sku_def__isownbrd
title: Cờ thuộc tính (ownbrd) (SKU_DEF)
display_names:
- IsOwnBrd
kind: flag
tables:
- ref: db2:sku_def
  column: IsOwnBrd
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (ownbrd) (SKU_DEF)

**Semantic key:** `sku_def__isownbrd` · **Cột vật lý:** `IsOwnBrd`

## Ý nghĩa nghiệp vụ

Cờ thuộc tính sản phẩm (ownbrd) trên master SKU — yes/no.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `IsOwnBrd` | bit | Cờ thuộc tính (ownbrd) trên master sản phẩm (SKU) |
