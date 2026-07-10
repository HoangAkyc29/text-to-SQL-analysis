---
semantic_key: sku_def__isinstall
title: Cờ thuộc tính (install) (SKU_DEF)
display_names:
- IsInstall
kind: flag
tables:
- ref: db2:sku_def
  column: IsInstall
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (install) (SKU_DEF)

**Semantic key:** `sku_def__isinstall` · **Cột vật lý:** `IsInstall`

## Ý nghĩa nghiệp vụ

Cờ thuộc tính sản phẩm (install) trên master SKU — yes/no.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `IsInstall` | bit | Cờ thuộc tính (install) trên master sản phẩm (SKU) |
