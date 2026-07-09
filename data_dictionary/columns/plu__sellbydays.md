---
semantic_key: plu__sellbydays
title: plu · sellbydays
display_names:
- SELLBYDAYS
kind: measure
tables:
- ref: db2:plu
  column: SELLBYDAYS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột SELLBYDAYS
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for SELLBYDAYS
- 'db2:plu.SELLBYDAYS: top=0(1000)'
---

# plu · sellbydays

**Semantic key:** `plu__sellbydays` · **Cột vật lý:** `SELLBYDAYS`

## Ý nghĩa nghiệp vụ

Cột SELLBYDAYS trên PLU. db2:plu: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:plu` | `SELLBYDAYS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:plu.SELLBYDAYS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

