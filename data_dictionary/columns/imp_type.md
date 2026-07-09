---
semantic_key: imp_type
title: imp type
display_names:
- IMP_TYPE
kind: text
tables:
- ref: db1:transhdr_arc
  column: IMP_TYPE
  type: char
- ref: db2:transhdr
  column: IMP_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- 'Nhập / import: IMP_TYPE'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:transhdr_arc.IMP_TYPE: top=03(939), 01(51)'
- 'db2:transhdr.IMP_TYPE: top=03(950), 01(39), 02(2), 05(1), 04(1)'
---

# imp type

**Semantic key:** `imp_type` · **Cột vật lý:** `IMP_TYPE`

## Ý nghĩa nghiệp vụ

Cột IMP_TYPE trên TRANSHDR, TRANSHDR_ARC. db1:transhdr_arc: top 03; db2:transhdr: top 01.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `IMP_TYPE` | char | có dữ liệu |
| `db2:transhdr` | `IMP_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:transhdr_arc.IMP_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `03`×20

### `db2:transhdr.IMP_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

## Ghi chú thêm

- Nhập / import: IMP_TYPE
