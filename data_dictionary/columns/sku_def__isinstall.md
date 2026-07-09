---
semantic_key: sku_def__isinstall
title: sku def · isinstall
display_names:
- IsInstall
kind: flag
tables:
- ref: db2:sku_def
  column: IsInstall
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột IsInstall
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for IsInstall
- 'db2:sku_def.IsInstall: top=False(1000)'
---

# sku def · isinstall

**Semantic key:** `sku_def__isinstall` · **Cột vật lý:** `IsInstall`

## Ý nghĩa nghiệp vụ

Cột ISINSTALL trên SKU_DEF. db2:sku_def: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `IsInstall` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.IsInstall`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Cột IsInstall
