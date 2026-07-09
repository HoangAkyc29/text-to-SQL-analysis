---
semantic_key: sku_def__isconsign
title: sku def · isconsign
display_names:
- IsConsign
kind: flag
tables:
- ref: db2:sku_def
  column: IsConsign
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột IsConsign
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for IsConsign
- 'db2:sku_def.IsConsign: top=False(1000)'
---

# sku def · isconsign

**Semantic key:** `sku_def__isconsign` · **Cột vật lý:** `IsConsign`

## Ý nghĩa nghiệp vụ

Cột ISCONSIGN trên SKU_DEF. db2:sku_def: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `IsConsign` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.IsConsign`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Cột IsConsign
