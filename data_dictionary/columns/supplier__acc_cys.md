---
semantic_key: supplier__acc_cys
title: supplier · acc cys
display_names:
- ACC_CYS
kind: text
tables:
- ref: db2:supplier
  column: ACC_CYS
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột ACC_CYS
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ACC_CYS
- 'db2:supplier.ACC_CYS: top=VND(1000)'
---

# supplier · acc cys

**Semantic key:** `supplier__acc_cys` · **Cột vật lý:** `ACC_CYS`

## Ý nghĩa nghiệp vụ

Cột ACC_CYS trên SUPPLIER. db2:supplier: top VND.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:supplier` | `ACC_CYS` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:supplier.ACC_CYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `VND`×20

## Ghi chú thêm

