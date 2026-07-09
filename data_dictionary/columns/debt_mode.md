---
semantic_key: debt_mode
title: debt mode
display_names:
- DEBT_MODE
kind: flag
tables:
- ref: db2:customer
  column: DEBT_MODE
  type: bit
- ref: db2:partner
  column: DEBT_MODE
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột DEBT_MODE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:customer.DEBT_MODE: top=True(607), False(393)'
- 'db2:partner.DEBT_MODE: top=True(997), False(3)'
---

# debt mode

**Semantic key:** `debt_mode` · **Cột vật lý:** `DEBT_MODE`

## Ý nghĩa nghiệp vụ

Cột DEBT_MODE trên CUSTOMER, PARTNER. db2:customer: top False; db2:partner: top True.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `DEBT_MODE` | bit | có dữ liệu |
| `db2:partner` | `DEBT_MODE` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.DEBT_MODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:partner.DEBT_MODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

## Ghi chú thêm

