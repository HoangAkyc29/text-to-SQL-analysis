---
semantic_key: dept_id
title: dept id
display_names:
- DEPT_ID
kind: identifier
tables:
- ref: db2:sku_def
  column: DEPT_ID
  type: char
- ref: db2:supplier
  column: DEPT_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột DEPT_ID
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:sku_def.DEPT_ID: top=0101(899), 0200(34), 0601(20), 0300(11), 0800(10)'
- 'db2:supplier.DEPT_ID: top=0101(212)'
---

# dept id

**Semantic key:** `dept_id` · **Cột vật lý:** `DEPT_ID`

## Ý nghĩa nghiệp vụ

Cột DEPT_ID trên SKU_DEF, SUPPLIER. db2:sku_def: top 0101, 0301.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `DEPT_ID` | char | có dữ liệu |
| `db2:supplier` | `DEPT_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.DEPT_ID`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0101`×18, `0301`×2

## Ghi chú thêm

