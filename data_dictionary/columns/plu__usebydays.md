---
semantic_key: plu__usebydays
title: plu · usebydays
display_names:
- USEBYDAYS
kind: measure
tables:
- ref: db2:plu
  column: USEBYDAYS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột USEBYDAYS
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for USEBYDAYS
- 'db2:plu.USEBYDAYS: top=0(1000)'
---

# plu · usebydays

**Semantic key:** `plu__usebydays` · **Cột vật lý:** `USEBYDAYS`

## Ý nghĩa nghiệp vụ

Cột USEBYDAYS trên PLU. db2:plu: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:plu` | `USEBYDAYS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:plu.USEBYDAYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

