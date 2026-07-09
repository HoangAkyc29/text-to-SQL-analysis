---
semantic_key: deposit
title: deposit
display_names:
- DEPOSIT
kind: measure
tables:
- ref: db1:transhdr_arc
  column: DEPOSIT
  type: numeric
- ref: db2:transhdr
  column: DEPOSIT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột DEPOSIT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:transhdr_arc.DEPOSIT: top=0.00(1000)'
- 'db2:transhdr.DEPOSIT: top=0.00(1000)'
---

# deposit

**Semantic key:** `deposit` · **Cột vật lý:** `DEPOSIT`

## Ý nghĩa nghiệp vụ

Cột DEPOSIT trên TRANSHDR, TRANSHDR_ARC. db1:transhdr_arc: top 0.00; db2:transhdr: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `DEPOSIT` | numeric | có dữ liệu |
| `db2:transhdr` | `DEPOSIT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:transhdr_arc.DEPOSIT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:transhdr.DEPOSIT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

