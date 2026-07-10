---
semantic_key: sku_def__iswebshow
title: Cờ thuộc tính (webshow) (SKU_DEF)
display_names:
- IsWebshow
kind: flag
tables:
- ref: db2:sku_def
  column: IsWebshow
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (webshow) (SKU_DEF)

**Semantic key:** `sku_def__iswebshow` · **Cột vật lý:** `IsWebshow`

## Ý nghĩa nghiệp vụ

Cờ thuộc tính sản phẩm (webshow) trên master SKU — yes/no.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `IsWebshow` | bit | Cờ thuộc tính (webshow) trên master sản phẩm (SKU) |
