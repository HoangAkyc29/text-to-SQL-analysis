---
semantic_key: sku_def__isserial
title: Cờ thuộc tính (serial) (SKU_DEF)
display_names:
- IsSerial
kind: flag
tables:
- ref: db2:sku_def
  column: IsSerial
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (serial) (SKU_DEF)

**Semantic key:** `sku_def__isserial` · **Cột vật lý:** `IsSerial`

## Ý nghĩa nghiệp vụ

Cờ thuộc tính sản phẩm (serial) trên master SKU — yes/no.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `IsSerial` | bit | Cờ thuộc tính (serial) trên master sản phẩm (SKU) |
