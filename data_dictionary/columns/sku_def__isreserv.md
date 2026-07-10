---
semantic_key: sku_def__isreserv
title: Cờ thuộc tính (reserv) (SKU_DEF)
display_names:
- IsReserv
kind: flag
tables:
- ref: db2:sku_def
  column: IsReserv
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (reserv) (SKU_DEF)

**Semantic key:** `sku_def__isreserv` · **Cột vật lý:** `IsReserv`

## Ý nghĩa nghiệp vụ

Cờ thuộc tính sản phẩm (reserv) trên master SKU — yes/no.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `IsReserv` | bit | Cờ thuộc tính (reserv) trên master sản phẩm (SKU) |
