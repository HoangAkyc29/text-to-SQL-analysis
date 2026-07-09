---
semantic_key: fine_rate
title: fine rate
display_names:
- FINE_RATE
- fine_rate
kind: measure
tables:
- ref: db2:partner
  column: fine_rate
  type: numeric
- ref: db2:supplier
  column: FINE_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tỷ lệFINE_RATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:partner.fine_rate: top=0.00(1000)'
- 'db2:supplier.FINE_RATE: top=0.00(1000)'
---

# fine rate

**Semantic key:** `fine_rate` · **Cột vật lý:** `FINE_RATE`, `fine_rate`

## Ý nghĩa nghiệp vụ

Cột FINE_RATE trên PARTNER, SUPPLIER. db2:partner: top 0.00; db2:supplier: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:partner` | `fine_rate` | numeric | có dữ liệu |
| `db2:supplier` | `FINE_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:partner.fine_rate`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:supplier.FINE_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Tỷ lệFINE_RATE
