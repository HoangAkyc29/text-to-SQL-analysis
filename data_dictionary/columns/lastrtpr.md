---
semantic_key: lastrtpr
title: lastrtpr
display_names:
- LASTRTPR
kind: measure
tables:
- ref: db2:hisrtpr
  column: LASTRTPR
  type: numeric
- ref: db2:plu
  column: LASTRTPR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Giá bán lẻ gần nhất
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:hisrtpr.LASTRTPR: top=0.00(219), 35000.00(16), 45000.00(14), 20000.00(12),
  50000.00(12)'
- 'db2:plu.LASTRTPR: top=0.00(1000)'
---

# lastrtpr

**Semantic key:** `lastrtpr` · **Cột vật lý:** `LASTRTPR`

## Ý nghĩa nghiệp vụ

Cột LASTRTPR trên HISRTPR, PLU. db2:hisrtpr: top 0.00; db2:plu: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:hisrtpr` | `LASTRTPR` | numeric | có dữ liệu |
| `db2:plu` | `LASTRTPR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:hisrtpr.LASTRTPR`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:plu.LASTRTPR`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Giá bán lẻ gần nhất
