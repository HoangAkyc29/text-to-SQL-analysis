---
semantic_key: sku_def__isconsign
title: Cờ thuộc tính (consign) (SKU_DEF)
display_names:
- IsConsign
kind: flag
tables:
- ref: db2:sku_def
  column: IsConsign
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (consign) (SKU_DEF)

**Semantic key:** `sku_def__isconsign` · **Cột vật lý:** `IsConsign`

## Ý nghĩa nghiệp vụ

Cờ thuộc tính sản phẩm (consign) trên master SKU — yes/no.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `IsConsign` | bit | Cờ thuộc tính (consign) trên master sản phẩm (SKU) |
