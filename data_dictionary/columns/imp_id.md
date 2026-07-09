---
semantic_key: imp_id
title: imp id
display_names:
- IMP_ID
kind: identifier
tables:
- ref: db1:transhdr_arc
  column: IMP_ID
  type: char
- ref: db2:transhdr
  column: IMP_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- 'Nhập / import: IMP_ID'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:transhdr_arc.IMP_ID: top=230000000001(50), 10001(37), 10004(11), 230000000025(4),
  10005(3)'
- 'db2:transhdr.IMP_ID: top=10001(15), 10005(13), 10004(11), 239010004531(2), 239010006471(2)'
---

# imp id

**Semantic key:** `imp_id` · **Cột vật lý:** `IMP_ID`

## Ý nghĩa nghiệp vụ

Cột IMP_ID trên TRANSHDR, TRANSHDR_ARC. db1:transhdr_arc: top 239010004972, 239010008028, 239010007615; db2:transhdr: top 10001, 10004, 10005.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `IMP_ID` | char | có dữ liệu |
| `db2:transhdr` | `IMP_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:transhdr_arc.IMP_ID`
- Null rate trong sample: 35%
- Distinct ≈13; top: `239010004972`×1, `239010008028`×1, `239010007615`×1, `239010008542`×1, `239010004296`×1, `230000032082`×1, `239010008562`×1, `239010006686`×1

### `db2:transhdr.IMP_ID`
- Null rate trong sample: 0%
- Distinct ≈3; top: `10001`×8, `10004`×8, `10005`×4

## Ghi chú thêm

- Nhập / import: IMP_ID
