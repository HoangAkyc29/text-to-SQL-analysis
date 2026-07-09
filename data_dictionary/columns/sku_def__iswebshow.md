---
semantic_key: sku_def__iswebshow
title: sku def · iswebshow
display_names:
- IsWebshow
kind: flag
tables:
- ref: db2:sku_def
  column: IsWebshow
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột IsWebshow
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for IsWebshow
- 'db2:sku_def.IsWebshow: top=False(1000)'
---

# sku def · iswebshow

**Semantic key:** `sku_def__iswebshow` · **Cột vật lý:** `IsWebshow`

## Ý nghĩa nghiệp vụ

Cột ISWEBSHOW trên SKU_DEF. db2:sku_def: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `IsWebshow` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.IsWebshow`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Cột IsWebshow
