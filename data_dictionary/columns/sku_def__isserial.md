---
semantic_key: sku_def__isserial
title: sku def · isserial
display_names:
- IsSerial
kind: flag
tables:
- ref: db2:sku_def
  column: IsSerial
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột IsSerial
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for IsSerial
- 'db2:sku_def.IsSerial: top=False(1000)'
---

# sku def · isserial

**Semantic key:** `sku_def__isserial` · **Cột vật lý:** `IsSerial`

## Ý nghĩa nghiệp vụ

Cột ISSERIAL trên SKU_DEF. db2:sku_def: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `IsSerial` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.IsSerial`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Cột IsSerial
