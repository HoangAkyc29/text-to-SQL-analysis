---
semantic_key: hissppr__spprice
title: hissppr · spprice
display_names:
- SPPRICE
kind: measure
tables:
- ref: db2:hissppr
  column: SPPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Giá mua NCC
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for SPPRICE
- 'db2:hissppr.SPPRICE: top=1.00(75), 0.00(23), 12000.00(16), 50000.00(14), 35000.00(11)'
---

# hissppr · spprice

**Semantic key:** `hissppr__spprice` · **Cột vật lý:** `SPPRICE`

## Ý nghĩa nghiệp vụ

Cột SPPRICE trên HISSPPR. db2:hissppr: top 30423.00, 26895.00, 49820.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:hissppr` | `SPPRICE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:hissppr.SPPRICE`
- Null rate trong sample: 0%
- Distinct ≈11; top: `30423.00`×4, `26895.00`×3, `49820.00`×2, `18636.00`×2, `20545.00`×2, `21455.00`×2, `155000.00`×1, `31698.34`×1

## Ghi chú thêm

- Giá mua NCC
