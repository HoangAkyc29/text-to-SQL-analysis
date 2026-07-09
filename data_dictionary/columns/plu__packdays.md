---
semantic_key: plu__packdays
title: plu · packdays
display_names:
- PACKDAYS
kind: measure
tables:
- ref: db2:plu
  column: PACKDAYS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột PACKDAYS
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for PACKDAYS
- 'db2:plu.PACKDAYS: top=0(1000)'
---

# plu · packdays

**Semantic key:** `plu__packdays` · **Cột vật lý:** `PACKDAYS`

## Ý nghĩa nghiệp vụ

Cột PACKDAYS trên PLU. db2:plu: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:plu` | `PACKDAYS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:plu.PACKDAYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

