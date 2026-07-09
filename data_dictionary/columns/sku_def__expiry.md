---
semantic_key: sku_def__expiry
title: sku def · expiry
display_names:
- EXPIRY
kind: flag
tables:
- ref: db2:sku_def
  column: EXPIRY
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột EXPIRY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for EXPIRY
- 'db2:sku_def.EXPIRY: top=False(905), True(95)'
---

# sku def · expiry

**Semantic key:** `sku_def__expiry` · **Cột vật lý:** `EXPIRY`

## Ý nghĩa nghiệp vụ

Cột EXPIRY trên SKU_DEF. db2:sku_def: top False, True.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `EXPIRY` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.EXPIRY`
- Null rate trong sample: 0%
- Distinct ≈2; top: `False`×19, `True`×1

## Ghi chú thêm

