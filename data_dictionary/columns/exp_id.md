---
semantic_key: exp_id
title: exp id
display_names:
- EXP_ID
kind: identifier
tables:
- ref: db1:transhdr_arc
  column: EXP_ID
  type: char
- ref: db2:transhdr
  column: EXP_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- 'Xuất / export: EXP_ID'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:transhdr_arc.EXP_ID: top=10001(629), 10004(252), 10005(72), 50240(3), 50426(3)'
- 'db2:transhdr.EXP_ID: top=10001(510), 10004(240), 10005(212), 50371(3), 51454(3)'
---

# exp id

**Semantic key:** `exp_id` · **Cột vật lý:** `EXP_ID`

## Ý nghĩa nghiệp vụ

Cột EXP_ID trên TRANSHDR, TRANSHDR_ARC. db1:transhdr_arc: top 10004; db2:transhdr: top 50747, 50855, 51547.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `EXP_ID` | char | có dữ liệu |
| `db2:transhdr` | `EXP_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:transhdr_arc.EXP_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10004`×20

### `db2:transhdr.EXP_ID`
- Null rate trong sample: 0%
- Distinct ≈11; top: `50747`×6, `50855`×4, `51547`×2, `51067`×1, `50565`×1, `50672`×1, `51449`×1, `50426`×1

## Ghi chú thêm

- Xuất / export: EXP_ID
