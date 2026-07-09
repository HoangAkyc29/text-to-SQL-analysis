---
semantic_key: exp_type
title: exp type
display_names:
- EXP_TYPE
kind: text
tables:
- ref: db1:transhdr_arc
  column: EXP_TYPE
  type: char
- ref: db2:transhdr
  column: EXP_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- 'Xuất / export: EXP_TYPE'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:transhdr_arc.EXP_TYPE: top=01(954), 05(41), 06(4), 02(1)'
- 'db2:transhdr.EXP_TYPE: top=01(962), 05(35), 03(2), 02(1)'
---

# exp type

**Semantic key:** `exp_type` · **Cột vật lý:** `EXP_TYPE`

## Ý nghĩa nghiệp vụ

Cột EXP_TYPE trên TRANSHDR, TRANSHDR_ARC. db1:transhdr_arc: top 01; db2:transhdr: top 05.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `EXP_TYPE` | char | có dữ liệu |
| `db2:transhdr` | `EXP_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:transhdr_arc.EXP_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:transhdr.EXP_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `05`×20

## Ghi chú thêm

- Xuất / export: EXP_TYPE
