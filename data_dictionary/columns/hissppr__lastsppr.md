---
semantic_key: hissppr__lastsppr
title: hissppr · lastsppr
display_names:
- LASTSPPR
kind: measure
tables:
- ref: db2:hissppr
  column: LASTSPPR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Giá mua NCC gần nhất
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for LASTSPPR
- 'db2:hissppr.LASTSPPR: top=0.00(994), 51237.96(1), 14880.00(1), 7200.00(1), 27000.00(1)'
---

# hissppr · lastsppr

**Semantic key:** `hissppr__lastsppr` · **Cột vật lý:** `LASTSPPR`

## Ý nghĩa nghiệp vụ

Cột LASTSPPR trên HISSPPR. db2:hissppr: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:hissppr` | `LASTSPPR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:hissppr.LASTSPPR`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Giá mua NCC gần nhất
