---
semantic_key: deduct
title: deduct
display_names:
- DEDUCT
kind: measure
tables:
- ref: db1:transhdr_arc
  column: DEDUCT
  type: numeric
- ref: db2:transhdr
  column: DEDUCT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột DEDUCT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:transhdr_arc.DEDUCT: top=0.00(1000)'
- 'db2:transhdr.DEDUCT: top=0.00(1000)'
---

# deduct

**Semantic key:** `deduct` · **Cột vật lý:** `DEDUCT`

## Ý nghĩa nghiệp vụ

Cột DEDUCT trên TRANSHDR, TRANSHDR_ARC. db1:transhdr_arc: top 0.00; db2:transhdr: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `DEDUCT` | numeric | có dữ liệu |
| `db2:transhdr` | `DEDUCT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:transhdr_arc.DEDUCT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:transhdr.DEDUCT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

